# world.py - タイルマップと衝突判定
#
# 設計:
#   - 列ごとに bytes(8タイル) を保持(stages.py 形式)
#   - 動的書き換え(Qブロック叩いた後、レンガ破壊)用に bytearray にコピー
#   - 衝突は AABB を Y/X 分離で動かす(角貫通防止)
#   - 描画はカメラに映る列だけ走査
import config as C
import stages as st


class World:
    def __init__(self, stage_data):
        self.data = stage_data
        self.width = stage_data['width']
        # 動的書き換え可能にするため bytearray にコピー
        self.terrain = [bytearray(c) for c in stage_data['terrain']]
        # コイン取得などの状態を持たせる場合は別配列で。
        # 今回はタイルIDをAIRに書き換える(取得後はもう描かれない)

    # ----- タイル取得 -----
    def tile_at(self, col, row):
        if col < 0 or col >= self.width:
            return st.GROUND   # 画面外は壁扱い(押し出し用)
        if row < 0 or row >= 8:
            return st.AIR
        return self.terrain[col][row]

    def set_tile(self, col, row, tid):
        if 0 <= col < self.width and 0 <= row < 8:
            self.terrain[col][row] = tid

    # ----- 衝突補助 -----
    def is_solid(self, col, row):
        return self.tile_at(col, row) in st.SOLID_TILES

    def is_platform(self, col, row):
        return self.tile_at(col, row) in st.PLATFORM_TILES

    def is_lethal(self, col, row):
        return self.tile_at(col, row) in st.LETHAL_TILES

    # ----- AABB vs タイルマップ -----
    # プレイヤーAABB: (x, y, w, h) ピクセル単位
    # x/y はワールド座標(カメラ無視)

    def collide_x(self, px, py, w, h, dx):
        """X方向に dx 動かして、ソリッドにぶつかったら押し戻す。返り値: 新しい px。"""
        new_x = px + dx
        if dx == 0:
            return new_x

        # 進行方向の前縁
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
        """Y方向に動かして衝突処理。
        返り値: (新しいpy, on_ground_flag, head_hit_col)
        head_hit_col は上方向衝突時のタイル列(?ブロック叩き判定用)、無ければ -1。
        """
        new_y = py + dy
        on_ground = False
        head_col = -1

        if dy == 0:
            # 立っているか確認するため、足元1ピクセル下をチェック
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
            # ソリッドタイル衝突
            if self.is_solid(col, front):
                if dy > 0:
                    new_y = front * C.TILE - h
                    on_ground = True
                else:
                    new_y = (front + 1) * C.TILE
                    head_col = col
                return new_y, on_ground, head_col
            # 雲足場: 下方向落下時のみ、かつ「前フレームの足元がタイル境界の上」のときだけ衝突
            if dy > 0 and self.is_platform(col, front):
                # 足元が雲タイルの上端と一致するように調整
                top_edge = front * C.TILE
                if py + h <= top_edge + 1:  # 上から落下してきた
                    new_y = top_edge - h
                    on_ground = True
                    return new_y, on_ground, head_col

        return new_y, on_ground, head_col

    # ----- 致死判定 -----
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

    # ----- 描画 -----
    def draw(self, oled, bank, cam_x):
        """カメラ位置に応じてタイルを描画。
        ワールドのy座標(row*8)をそのまま画面y座標とする。
        ヘッダ(y=0..7)は最後にdraw_header()で上書きされるため、
        row=0 のタイルは見えなくなる(ステージ設計はそれを前提)。
        """
        blit = oled.blit
        fb = bank.fb
        # 描画範囲: cam_x .. cam_x+128 の列
        start_col = max(0, cam_x // C.TILE)
        end_col   = min(self.width, (cam_x + C.SCREEN_W) // C.TILE + 2)

        for col in range(start_col, end_col):
            colbytes = self.terrain[col]
            sx = col * C.TILE - cam_x
            for row in range(8):
                tid = colbytes[row]
                if tid == st.AIR:
                    continue
                sy = row * C.TILE
                name = _TILE_NAME.get(tid)
                if name is not None:
                    blit(fb[name], sx, sy)


# タイルID → スプライト名 マップ
_TILE_NAME = {
    st.GROUND:     'ground',
    st.BRICK:      'brick',
    st.QBLOCK:     'qblock',
    st.QUSED:      'qblock_used',
    st.PIPE_TL:    'pipe_tl',
    st.PIPE_TR:    'pipe_tr',
    st.PIPE_BL:    'pipe_bl',
    st.PIPE_BR:    'pipe_br',
    st.COIN:       'coin',
    st.SPIKE:      'spike',
    st.CLOUD_PLAT: 'cloud_plat',
    st.GOAL:       'goal',
}
