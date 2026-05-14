# player.py - プレイヤーの物理・状態・操作
#
# 設計上のこだわり:
#   1. コヨーテタイム: 足場を離れて N フレーム以内ならジャンプ可
#   2. ジャンプバッファ: 着地前 N フレーム以内のSW1入力を予約しておく
#   3. 可変重力: ジャンプボタン押下中は重力軽減 → 長押しで高く飛ぶ
#   4. ショートジャンプ: ボタン早離しで上昇速度を半減 → タップで小ジャンプ
#   5. ジャンプ慣性カット: 横入力ゼロでも空中で前進維持
#
# これがマリオ系アクションの"気持ちよさ"の正体。
import config as C
import stages as st


STATE_SMALL = 'small'
STATE_BIG   = 'big'
STATE_FIRE  = 'fire'
STATE_DEAD  = 'dead'


class Player:
    def __init__(self, world, start_col=1):
        self.world = world
        self.x = float(start_col * C.TILE)
        self.y = float((C.ROWS - 3) * C.TILE)  # 地面の上
        self.vx = 0.0
        self.vy = 0.0
        self.facing = 1   # 1=右, -1=左
        self.on_ground = False

        self.state = STATE_SMALL
        # 判定サイズ:
        #   w=6: 横は両側1px細くしてタイル角に引っかかりにくくする
        #   h=8: 縦はタイル整数倍(地面y=48に底辺をぴったり乗せる)
        self.w = 6
        self.h = 8
        self._sync_size()

        # タイマ
        self.coyote = 0       # 0より大きい間ジャンプ可
        self.jump_buf = 0     # 押された残量
        self.invincible = 0   # 無敵フレーム残量
        self.powerup_anim = 0 # 変身演出
        self.dead_timer = 0
        self.run_charge = 0   # ダッシュ加速チャージ

        # 物理パラメータ(ステージで上書き可能)
        self.gravity_scale = 1.0
        self.is_water = False

        # アニメ用
        self.anim_tick = 0

    def _sync_size(self):
        if self.state == STATE_SMALL:
            self.h = 8
        else:
            self.h = 16   # 8x16

    def apply_stage(self, stage_data):
        self.gravity_scale = stage_data.get('gravity_scale', 1.0)
        self.is_water = stage_data.get('water', False)
        self.x = float(stage_data.get('start_col', 1) * C.TILE)
        self.y = float((C.ROWS - 3) * C.TILE)

    # ----- パワーアップ -----
    def powerup_mushroom(self):
        if self.state == STATE_SMALL:
            self.state = STATE_BIG
            # 頭を1タイル分上げる(8→16になるので位置調整)
            self.y -= 8
            self._sync_size()
            self.powerup_anim = C.POWERUP_FR

    def powerup_fire(self):
        if self.state == STATE_SMALL:
            self.state = STATE_BIG
            self.y -= 8
            self._sync_size()
        self.state = STATE_FIRE
        self.powerup_anim = C.POWERUP_FR

    def take_damage(self):
        """被ダメ。返り値: 死亡したか"""
        if self.invincible > 0 or self.powerup_anim > 0:
            return False
        if self.state == STATE_FIRE or self.state == STATE_BIG:
            self.state = STATE_SMALL
            self.y += 8  # 縮んだ分下げる
            self._sync_size()
            self.invincible = C.INVINCIBLE_FR
            return False
        # SMALLで被弾 → 死亡
        self.state = STATE_DEAD
        self.vy = -3.5
        self.vx = 0
        self.dead_timer = C.DYING_FR
        return True

    def kill_by_fall(self):
        self.state = STATE_DEAD
        self.dead_timer = C.DYING_FR // 2

    def can_shoot_fire(self):
        return self.state == STATE_FIRE and self.powerup_anim == 0

    # ----- 更新 -----
    def update(self, inp, fired_callback):
        """毎フレーム呼ぶ。
        inp: Input オブジェクト
        fired_callback: ファイアボール発射時に呼ぶ callable(x, y, dir)
        """
        # 死亡演出: 上昇→落下
        if self.state == STATE_DEAD:
            self.y += self.vy
            self.vy += 0.3
            self.dead_timer -= 1
            return

        # パワーアップ演出中は操作不可
        if self.powerup_anim > 0:
            self.powerup_anim -= 1
            self.vx = 0
            return

        # 無敵タイマ減算
        if self.invincible > 0:
            self.invincible -= 1

        # ---- 水平入力 ----
        # 今回は左右ボタンがないので、自動右移動(あるいは速度可変)
        # 設計: SW3=ダッシュで速度UP、押さなければ通常歩行
        run = inp.held(2)
        if run:
            if self.run_charge < C.RUN_ACCEL_FR:
                self.run_charge += 1
        else:
            if self.run_charge > 0:
                self.run_charge -= 1

        # ダッシュ加速度補間
        t = self.run_charge / C.RUN_ACCEL_FR
        target_vx = C.WALK_SPEED + (C.RUN_SPEED - C.WALK_SPEED) * t
        self.vx = target_vx
        self.facing = 1

        # ---- ジャンプ入力(コヨーテ + バッファ) ----
        if inp.pressed(0):
            self.jump_buf = C.JUMP_BUFFER
        elif self.jump_buf > 0:
            self.jump_buf -= 1

        if self.on_ground:
            self.coyote = C.COYOTE_FRAMES
        elif self.coyote > 0:
            self.coyote -= 1

        # ジャンプ発動
        if self.jump_buf > 0 and self.coyote > 0:
            if self.is_water:
                self.vy = C.WATER_JUMP
            else:
                self.vy = C.JUMP_VELOCITY
            self.jump_buf = 0
            self.coyote = 0
            self.on_ground = False
            # SFXは Game 側で発火(踏みつけ・水中等で音違う)
            self._just_jumped = True
        else:
            self._just_jumped = False

        # ショートジャンプ: 上昇中にボタン離したら速度カット
        if not inp.held(0) and self.vy < 0:
            self.vy *= C.SHORT_JUMP_CUT

        # ---- ファイアボール ----
        self._fire_request = False
        if inp.pressed(1) and self.can_shoot_fire():
            self._fire_request = True
            fx_y = self.y + 4 if self.state == STATE_FIRE else self.y
            fired_callback(self.x + (8 if self.facing > 0 else -4), fx_y, self.facing)

        # ---- 重力 ----
        if self.is_water:
            grav = C.WATER_GRAVITY
            term = C.WATER_TERMVEL
        else:
            if self.vy < 0 and inp.held(0):
                grav = C.GRAVITY_UP
            else:
                grav = C.GRAVITY_DOWN
            term = C.TERMINAL_VEL
        grav *= self.gravity_scale
        self.vy += grav
        if self.vy > term:
            self.vy = term

        # ---- 衝突処理(X→Yの順) ----
        new_x = self.world.collide_x(self.x, self.y, self.w, self.h, self.vx)
        self.x = new_x

        new_y, on_ground, head_col = self.world.collide_y(
            self.x, self.y, self.w, self.h, self.vy
        )
        # 上方向衝突判定: 期待移動量より少なく動けてなければ天井ヒット
        # (self.y を更新する前に判定する)
        if self.vy < 0 and new_y > self.y + self.vy + 0.001:
            self.vy = 0
        self.y = new_y
        if on_ground:
            self.vy = 0
            self.on_ground = True
        else:
            self.on_ground = False

        self.head_hit_col = head_col   # Gameが見て?ブロック処理

        # ---- 致死タイル ----
        if self.world.touches_lethal(self.x, self.y, self.w, self.h):
            self.state = STATE_DEAD
            self.dead_timer = C.DYING_FR

        # ---- 落下死 ----
        fall_limit = getattr(self.world, 'map_h_px', C.SCREEN_H) + 8
        if self.y > fall_limit:
            self.state = STATE_DEAD
            self.dead_timer = C.DYING_FR

        self.anim_tick += 1

    # ----- 描画 -----
    def draw(self, oled, bank, cam_x, cam_y=0):
        # AABBは幅6だがスプライトは幅8、中央揃えで1px左に寄せる
        sx = int(self.x) - cam_x - 1
        sy = int(self.y) - cam_y

        # 無敵時は半透明風に1フレーム置きに非表示
        if self.invincible > 0 and (self.anim_tick & 1):
            return

        fb = bank.fb
        if self.state == STATE_DEAD:
            oled.blit(fb['mario_dead'], sx, sy)
            return

        if self.state == STATE_SMALL:
            if not self.on_ground:
                key = 'mario_s_jump'
            else:
                # 歩行アニメ
                if (self.anim_tick >> 2) & 1:
                    key = 'mario_s_r2' if self.facing > 0 else 'mario_s_l2'
                else:
                    key = 'mario_s_r' if self.facing > 0 else 'mario_s_l'
            oled.blit(fb[key], sx, sy)
        else:
            # BIG / FIRE: 8x16(上下2枚)
            if not self.on_ground:
                top_key = 'mario_b_top_jump'
                bot_key = 'mario_b_bot_jump'
            else:
                top_key = 'mario_f_top' if self.state == STATE_FIRE else 'mario_b_top'
                bot_key = 'mario_b_bot2' if (self.anim_tick >> 2) & 1 else 'mario_b_bot'
            oled.blit(fb[top_key], sx, sy)
            oled.blit(fb[bot_key], sx, sy + 8)

    # ----- AABB getter -----
    def aabb(self):
        return (self.x, self.y, self.w, self.h)
