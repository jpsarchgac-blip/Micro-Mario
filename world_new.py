# world_new.py - 縦スクロール対応タイルマップと衝突判定(NEWモード専用)
#
# OLDモードのworld.pyとは独立。行数が可変(8/12/16行)で、
# cam_yによる縦スクロールに対応する。
import config as C

# タイルID (stages_new.pyと共有)
AIR    = 0
GROUND = 1
BRICK  = 2
QBLOCK = 3
PIPE_TL= 4
PIPE_TR= 5
PIPE_BL= 6
PIPE_BR= 7
COIN   = 8
SPIKE  = 9
GOAL   = 10
CLOUD_PLAT = 11
QUSED  = 12
MAGMA  = 13
GRASS  = 14
FLAG   = 15

SOLID_TILES = {GROUND, BRICK, QBLOCK, PIPE_TL, PIPE_TR, PIPE_BL, PIPE_BR, QUSED, GRASS}
PLATFORM_TILES = {CLOUD_PLAT}
LETHAL_TILES = {SPIKE, MAGMA}

# タイルID → スプライト名
_TILE_NAME = {
    GROUND:     'ground',
    BRICK:      'brick',
    QBLOCK:     'qblock',
    QUSED:      'qblock_used',
    PIPE_TL:    'pipe_tl',
    PIPE_TR:    'pipe_tr',
    PIPE_BL:    'pipe_bl',
    PIPE_BR:    'pipe_br',
    COIN:       'coin',
    SPIKE:      'spike',
    CLOUD_PLAT: 'cloud_plat',
    GOAL:       'goal_zone',
    GRASS:      'grass',
    FLAG:       'goal',
}


class WorldNew:
    def __init__(self, stage_data):
        self.data = stage_data
        self.width = stage_data['width']
        self.rows = stage_data.get('rows', 8)
        self.terrain = [bytearray(c) for c in stage_data['terrain']]
        self.map_h_px = self.rows * C.TILE

    # ----- タイル取得 -----
    def tile_at(self, col, row):
        if col < 0 or col >= self.width:
            return GROUND
        if row < 0:
            return AIR
        if row >= self.rows:
            return AIR
        return self.terrain[col][row]

    def set_tile(self, col, row, tid):
        if 0 <= col < self.width and 0 <= row < self.rows:
            self.terrain[col][row] = tid

    def is_solid(self, col, row):
        return self.tile_at(col, row) in SOLID_TILES

    def is_platform(self, col, row):
        return self.tile_at(col, row) in PLATFORM_TILES

    def is_lethal(self, col, row):
        return self.tile_at(col, row) in LETHAL_TILES

    # ----- AABB衝突 -----
    def collide_x(self, px, py, w, h, dx):
        new_x = px + dx
        if dx == 0:
            return new_x
        if dx > 0:
            front = int(new_x + w - 1) // C.TILE
        else:
            front = int(new_x) // C.TILE
        top = int(py) // C.TILE
        bot = int(py + h - 1) // C.TILE
        for row in range(top, bot + 1):
            if self.is_solid(front, row):
                if dx > 0:
                    new_x = front * C.TILE - w
                else:
                    new_x = (front + 1) * C.TILE
                return new_x
        return new_x

    def collide_y(self, px, py, w, h, dy):
        new_y = py + dy
        on_ground = False
        head_col = -1

        if dy == 0:
            foot_row = int(py + h) // C.TILE
            left = int(px) // C.TILE
            right = int(px + w - 1) // C.TILE
            for col in range(left, right + 1):
                if self.is_solid(col, foot_row) or (
                    self.is_platform(col, foot_row) and (int(py + h) % C.TILE == 0)
                ):
                    on_ground = True
                    break
            return new_y, on_ground, head_col

        if dy > 0:
            front = int(new_y + h - 1) // C.TILE
        else:
            front = int(new_y) // C.TILE

        left = int(px) // C.TILE
        right = int(px + w - 1) // C.TILE

        for col in range(left, right + 1):
            if self.is_solid(col, front):
                if dy > 0:
                    new_y = front * C.TILE - h
                    on_ground = True
                else:
                    new_y = (front + 1) * C.TILE
                    head_col = col
                return new_y, on_ground, head_col
            if dy > 0 and self.is_platform(col, front):
                top_edge = front * C.TILE
                if py + h <= top_edge + 1:
                    new_y = top_edge - h
                    on_ground = True
                    return new_y, on_ground, head_col

        return new_y, on_ground, head_col

    def touches_lethal(self, px, py, w, h):
        left = int(px) // C.TILE
        right = int(px + w - 1) // C.TILE
        top = int(py) // C.TILE
        bot = int(py + h - 1) // C.TILE
        for c in range(left, right + 1):
            for r in range(top, bot + 1):
                if self.is_lethal(c, r):
                    return True
        return False

    # ----- コイン数カウント -----
    def count_coins(self):
        total = 0
        for col_data in self.terrain:
            for tid in col_data:
                if tid == COIN:
                    total += 1
        return total

    # ----- 描画(cam_x, cam_y対応) -----
    def draw(self, oled, bank, cam_x, cam_y, frame=0):
        blit = oled.blit
        fb = bank.fb
        start_col = max(0, cam_x // C.TILE)
        end_col = min(self.width, (cam_x + C.SCREEN_W) // C.TILE + 2)
        start_row = max(0, cam_y // C.TILE)
        end_row = min(self.rows, (cam_y + C.SCREEN_H) // C.TILE + 2)

        for col in range(start_col, end_col):
            colbytes = self.terrain[col]
            sx = col * C.TILE - cam_x
            for row in range(start_row, end_row):
                tid = colbytes[row]
                if tid == AIR:
                    continue
                sy = row * C.TILE - cam_y
                if tid == MAGMA:
                    # 波打ちアニメ
                    key = 'magma_2' if ((frame >> 3) + col) & 1 else 'magma_1'
                    blit(fb[key], sx, sy)
                else:
                    name = _TILE_NAME.get(tid)
                    if name is not None:
                        blit(fb[name], sx, sy)
