# entity.py - 敵・アイテム・ファイアボール
#
# 設計: 全エンティティは共通インタフェース(update / draw / aabb / on_stomp / on_fireball)
# プールではなく動的リスト管理だが、各ステージ内で数が限られるので問題なし。
import config as C
import stages as st


# ========== 基底 ==========
class Entity:
    alive = True
    solid_for_player = True   # プレイヤーと当たり判定するか

    def aabb(self):
        return (self.x, self.y, self.w, self.h)

    def update(self, world, player):
        pass

    def draw(self, oled, bank, cam_x, cam_y=0):
        pass

    def on_stomp(self):
        """踏まれたとき。返り値: 踏みつけ成功(プレイヤーが小ジャンプする)"""
        return False

    def on_fireball(self):
        """ファイアボール被弾。返り値: 撃破成功"""
        return False

    def on_collide(self, player):
        """踏みでない接触。プレイヤーをダメージさせるなど。
        返り値: 'damage' / None
        """
        return None


# ========== クリボー ==========
class Goomba(Entity):
    w = 8
    h = 8
    def __init__(self, col, row):
        self.x = float(col * C.TILE)
        self.y = float(row * C.TILE)
        self.vx = -0.5
        self.vy = 0.0
        self.squashed_timer = 0
        self.anim = 0

    def update(self, world, player):
        if self.squashed_timer > 0:
            self.squashed_timer -= 1
            if self.squashed_timer == 0:
                self.alive = False
            return

        # 重力
        self.vy = min(self.vy + 0.4, C.TERMINAL_VEL)
        # 横移動
        target_x = self.x + self.vx
        new_x = world.collide_x(self.x, self.y, self.w, self.h, self.vx)
        if abs(new_x - target_x) > 0.01:
            self.vx = -self.vx   # 壁で反転
        self.x = new_x
        # 縦移動
        new_y, on_ground, _ = world.collide_y(self.x, self.y, self.w, self.h, self.vy)
        self.y = new_y
        if on_ground:
            self.vy = 0
            # 端で落下するか? → 進行方向の足元が空なら反転
            front_col = int(self.x + (self.w if self.vx > 0 else 0)) // C.TILE
            below_row = int(self.y + self.h) // C.TILE
            if not (world.is_solid(front_col, below_row) or world.is_platform(front_col, below_row)):
                self.vx = -self.vx
        # 画面下に落ちたら死
        fall_limit = getattr(world, 'map_h_px', 80)
        if self.y > fall_limit + 16:
            self.alive = False

        self.anim += 1

    def draw(self, oled, bank, cam_x, cam_y=0):
        sx = int(self.x) - cam_x
        sy = int(self.y) - cam_y
        if sx < -8 or sx > 128 or sy < -8 or sy > 64:
            return
        fb = bank.fb
        if self.squashed_timer > 0:
            oled.blit(fb['goomba_sq'], sx, sy)
        else:
            key = 'goomba_2' if (self.anim >> 3) & 1 else 'goomba_1'
            oled.blit(fb[key], sx, sy)

    def on_stomp(self):
        self.squashed_timer = 15
        self.solid_for_player = False
        return True

    def on_fireball(self):
        self.alive = False
        return True

    def on_collide(self, player):
        if self.squashed_timer > 0:
            return None
        return 'damage'


# ========== コウモリ(ジグザグ飛行) ==========
class Bat(Entity):
    w = 8
    h = 8
    def __init__(self, col, row):
        self.x = float(col * C.TILE)
        self.y = float(row * C.TILE)
        self.base_y = self.y
        self.vx = -0.7
        self.t = 0
        self.anim = 0

    def update(self, world, player):
        self.x += self.vx
        # 上下にウェーブ
        self.t += 1
        self.y = self.base_y + (10 * ((self.t % 60) - 30) // 30)
        if self.x < -8:
            self.alive = False
        # 壁でも反転(地下ステージ用)
        col_check = int(self.x) // C.TILE
        row_check = int(self.y) // C.TILE
        if world.is_solid(col_check, row_check):
            self.vx = -self.vx
        self.anim += 1

    def draw(self, oled, bank, cam_x, cam_y=0):
        sx = int(self.x) - cam_x
        sy = int(self.y) - cam_y
        if sx < -8 or sx > 128 or sy < -8 or sy > 64:
            return
        key = 'bat_2' if (self.anim >> 2) & 1 else 'bat_1'
        oled.blit(bank.fb[key], sx, sy)

    def on_stomp(self):
        # 飛行敵は踏めない設計
        return False

    def on_fireball(self):
        self.alive = False
        return True

    def on_collide(self, player):
        return 'damage'


# ========== プクプク(水中、上下移動) ==========
class Fish(Entity):
    w = 8
    h = 8
    def __init__(self, col, row):
        self.x = float(col * C.TILE)
        self.y = float(row * C.TILE)
        self.base_y = self.y
        self.vx = -0.4
        self.t = 0
        self.anim = 0

    def update(self, world, player):
        self.x += self.vx
        self.t += 1
        self.y = self.base_y + (8 * ((self.t % 80) - 40) // 40)
        if self.x < -8:
            self.alive = False
        self.anim += 1

    def draw(self, oled, bank, cam_x, cam_y=0):
        sx = int(self.x) - cam_x
        sy = int(self.y) - cam_y
        if sx < -8 or sx > 128 or sy < -8 or sy > 64:
            return
        key = 'fish_l' if self.vx < 0 else 'fish_r'
        oled.blit(bank.fb[key], sx, sy)

    def on_stomp(self):
        return False

    def on_fireball(self):
        self.alive = False
        return True

    def on_collide(self, player):
        return 'damage'


# ========== パタパタ(飛行、上下) ==========
class Parakoopa(Entity):
    w = 8
    h = 8
    def __init__(self, col, row):
        self.x = float(col * C.TILE)
        self.y = float(row * C.TILE)
        self.base_y = self.y
        self.vx = -0.8
        self.t = 0
        self.anim = 0

    def update(self, world, player):
        self.x += self.vx
        self.t += 1
        self.y = self.base_y + (12 * ((self.t % 90) - 45) // 45)
        if self.x < -8:
            self.alive = False
        self.anim += 1

    def draw(self, oled, bank, cam_x, cam_y=0):
        sx = int(self.x) - cam_x
        sy = int(self.y) - cam_y
        if sx < -8 or sx > 128:
            return
        key = 'parakoopa_2' if (self.anim >> 2) & 1 else 'parakoopa_1'
        oled.blit(bank.fb[key], sx, sy)

    def on_stomp(self):
        # 踏むと撃破(クリボー扱い)
        self.alive = False
        return True

    def on_fireball(self):
        self.alive = False
        return True

    def on_collide(self, player):
        return 'damage'


# ========== 投げナイフ敵(空中) ==========
class Ninja(Entity):
    w = 8
    h = 8
    def __init__(self, col, row):
        self.x = float(col * C.TILE)
        self.y = float(row * C.TILE)
        self.vx = -0.3
        self.fire_cooldown = 60
        self.anim = 0
        self.knives = []   # 各ナイフ: [x, y, vx]

    def update(self, world, player):
        self.x += self.vx
        if self.x < -8:
            self.alive = False
        # ナイフ投擲
        self.fire_cooldown -= 1
        if self.fire_cooldown <= 0:
            self.fire_cooldown = 90
            self.knives.append([self.x, self.y + 2, -1.5])
        # ナイフ移動
        alive_knives = []
        for k in self.knives:
            k[0] += k[2]
            if -8 < k[0] < 200:
                alive_knives.append(k)
        self.knives = alive_knives
        self.anim += 1

    def draw(self, oled, bank, cam_x, cam_y=0):
        sx = int(self.x) - cam_x
        sy = int(self.y) - cam_y
        if -8 <= sx <= 128:
            oled.blit(bank.fb['ninja'], sx, sy)
        # ナイフ
        for k in self.knives:
            kx = int(k[0]) - cam_x
            ky = int(k[1])
            if -8 <= kx <= 128:
                oled.blit(bank.fb['ninja_knife'], kx, ky)

    def on_stomp(self):
        self.alive = False
        return True

    def on_fireball(self):
        self.alive = False
        return True

    def on_collide(self, player):
        # 本体接触
        return 'damage'

    def knife_hits(self, px, py, pw, ph):
        for k in self.knives:
            if (k[0] < px + pw and k[0] + 8 > px and
                k[1] < py + ph and k[1] + 4 > py):
                return True
        return False


# ========== ボス(キングクッパ風) 24x24 ==========
class Boss(Entity):
    w = 22
    h = 22
    def __init__(self, col, row):
        self.x = float(col * C.TILE)
        self.y = float(row * C.TILE)
        self.spawn_y = self.y
        self.hp = 5
        self.phase = 1
        self.vx = -0.4
        self.vy = 0.0
        self.fire_cooldown = 80
        self.hit_flash = 0
        self.fireballs = []   # 各: [x, y, vx, vy]
        self.t = 0
        self.invuln = 0
        self.dying_timer = 0

    def _update_phase(self):
        if self.hp >= 4:
            self.phase = 1
        elif self.hp >= 2:
            self.phase = 2
        else:
            self.phase = 3

    def update(self, world, player):
        if self.hp <= 0:
            self.dying_timer += 1
            self.y += 0.5  # ゆっくり沈む
            if self.dying_timer > 60:
                self.alive = False
            return

        self.t += 1
        self._update_phase()
        # 速度倍率
        spd_mul = 1.0
        if self.phase == 2: spd_mul = 1.5
        if self.phase == 3: spd_mul = 2.0

        # 左右往復
        self.x += self.vx * spd_mul
        # アリーナ範囲(2-19列の間)
        left_limit = 3 * C.TILE
        right_limit = 18 * C.TILE
        if self.x < left_limit:
            self.x = left_limit
            self.vx = -self.vx
        elif self.x + self.w > right_limit + C.TILE:
            self.x = right_limit + C.TILE - self.w
            self.vx = -self.vx

        # ジャンプ攻撃(Phase 2+)
        if self.phase >= 2:
            if self.vy == 0 and (self.t % 90 == 0):
                self.vy = -3.0
        self.vy += 0.3 * spd_mul
        new_y, og, _ = world.collide_y(self.x, self.y, self.w, self.h, self.vy)
        self.y = new_y
        if og:
            self.vy = 0

        # 火球攻撃
        self.fire_cooldown -= 1
        if self.fire_cooldown <= 0:
            self.fire_cooldown = max(30, 90 - 15 * (self.phase - 1))
            # 扇状3発(Phase 1は1発、2は2発、3は3発)
            n = 1 + self.phase - 1
            for i in range(n):
                vy = -1.0 + 0.5 * i
                self.fireballs.append([self.x, self.y + 8, -2.0, vy])

        # 火球進行
        alive_f = []
        for f in self.fireballs:
            f[0] += f[2]
            f[1] += f[3]
            f[3] += 0.15
            # 床でバウンド
            if f[1] >= 6 * C.TILE - 4:
                f[1] = 6 * C.TILE - 4
                f[3] = -2.5
            if -10 < f[0] < 200:
                alive_f.append(f)
        self.fireballs = alive_f

        if self.invuln > 0:
            self.invuln -= 1
        if self.hit_flash > 0:
            self.hit_flash -= 1

    def draw(self, oled, bank, cam_x, cam_y=0):
        sx = int(self.x) - cam_x
        sy = int(self.y) - cam_y
        # ヒット中は点滅
        if self.hit_flash > 0 and (self.hit_flash & 1):
            pass  # 1フレームスキップ
        else:
            # ボス本体(9枚blit)
            fb = bank.fb
            for r in range(3):
                for c in range(3):
                    oled.blit(fb['boss_{}{}'.format(c, r)], sx + c * 8, sy + r * 8)
        # 火球描画
        for f in self.fireballs:
            fx = int(f[0]) - cam_x
            fy = int(f[1]) - cam_y
            if -8 <= fx <= 128:
                oled.blit(bank.fb['boss_fire'], fx, fy)

    def on_stomp(self):
        # 踏み攻撃を許可するのはPhase 3のみ(設計書通り)
        if self.invuln > 0:
            return False
        if self.phase != 3:
            # 踏もうとしてもダメージ食らう
            return False
        self.hp -= 1
        self.hit_flash = 12
        self.invuln = 30
        return True

    def on_fireball(self):
        if self.invuln > 0:
            return False
        self.hp -= 1
        self.hit_flash = 12
        self.invuln = 20
        return False   # 消えない(撃破はhp判定)

    def on_collide(self, player):
        # 本体接触はダメージ
        return 'damage'

    def fire_hits(self, px, py, pw, ph):
        for f in self.fireballs:
            if (f[0] < px + pw and f[0] + 8 > px and
                f[1] < py + ph and f[1] + 8 > py):
                return True
        return False

    def is_dying(self):
        return self.hp <= 0


# ========== アイテム ==========
class Mushroom(Entity):
    w = 8
    h = 8
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.vx = 0.8
        self.vy = -0.5   # 出現時に少し上に
        self.spawned = False
        self.spawn_anim = 16   # 少し上昇してから動き出す

    def update(self, world, player):
        if self.spawn_anim > 0:
            self.spawn_anim -= 1
            self.y -= 0.5
            return
        self.vy = min(self.vy + 0.3, C.TERMINAL_VEL)
        target_x = self.x + self.vx
        new_x = world.collide_x(self.x, self.y, self.w, self.h, self.vx)
        if abs(new_x - target_x) > 0.01:
            self.vx = -self.vx
        self.x = new_x
        new_y, og, _ = world.collide_y(self.x, self.y, self.w, self.h, self.vy)
        self.y = new_y
        if og:
            self.vy = 0
        if self.x < -10 or self.y > 80:
            self.alive = False

    def draw(self, oled, bank, cam_x, cam_y=0):
        sx = int(self.x) - cam_x
        sy = int(self.y) - cam_y
        if -8 <= sx <= 128:
            oled.blit(bank.fb['mushroom'], sx, sy)


class FireFlower(Entity):
    w = 8
    h = 8
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.spawn_anim = 16

    def update(self, world, player):
        if self.spawn_anim > 0:
            self.spawn_anim -= 1
            self.y -= 0.5

    def draw(self, oled, bank, cam_x, cam_y=0):
        sx = int(self.x) - cam_x
        sy = int(self.y) - cam_y
        if -8 <= sx <= 128:
            oled.blit(bank.fb['fire_flower'], sx, sy)


class OneUp(Entity):
    w = 8
    h = 8
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.vx = 1.0
        self.vy = -1.0

    def update(self, world, player):
        self.vy = min(self.vy + 0.3, C.TERMINAL_VEL)
        target_x = self.x + self.vx
        new_x = world.collide_x(self.x, self.y, self.w, self.h, self.vx)
        if abs(new_x - target_x) > 0.01:
            self.vx = -self.vx
        self.x = new_x
        new_y, og, _ = world.collide_y(self.x, self.y, self.w, self.h, self.vy)
        self.y = new_y
        if og:
            self.vy = -2.0   # バウンド
        if self.y > 80:
            self.alive = False

    def draw(self, oled, bank, cam_x, cam_y=0):
        sx = int(self.x) - cam_x
        sy = int(self.y) - cam_y
        if -8 <= sx <= 128:
            oled.blit(bank.fb['one_up'], sx, sy)


# ========== ファイアボール(プレイヤー発射) ==========
class Fireball(Entity):
    w = 6
    h = 6
    def __init__(self, x, y, direction):
        self.x = float(x)
        self.y = float(y)
        self.vx = 3.0 * direction
        self.vy = 1.0
        self.anim = 0

    def update(self, world, player):
        # 重力 & バウンド
        self.vy = min(self.vy + 0.3, 3.0)
        new_x = world.collide_x(self.x, self.y, self.w, self.h, self.vx)
        if new_x == self.x:
            self.alive = False   # 壁で消滅
            return
        self.x = new_x
        new_y, og, _ = world.collide_y(self.x, self.y, self.w, self.h, self.vy)
        self.y = new_y
        if og:
            self.vy = -2.5   # バウンド
        if self.x < -8 or self.x > 1000 or self.y > 80:
            self.alive = False
        self.anim += 1

    def draw(self, oled, bank, cam_x, cam_y=0):
        sx = int(self.x) - cam_x
        sy = int(self.y) - cam_y
        if -8 <= sx <= 128:
            key = 'fireball_2' if (self.anim >> 1) & 1 else 'fireball_1'
            oled.blit(bank.fb[key], sx, sy)


# ========== ファクトリ ==========
def make_entity(type_str, col, row):
    """stages.py の objects 文字列から Entity を生成。"""
    if type_str == 'goomba':       return Goomba(col, row)
    if type_str == 'bat':          return Bat(col, row)
    if type_str == 'fish':         return Fish(col, row)
    if type_str == 'parakoopa':    return Parakoopa(col, row)
    if type_str == 'ninja':        return Ninja(col, row)
    if type_str == 'boss':         return Boss(col, row)
    return None
