# fx.py - LED演出 & パーティクル
#
# LEDは「状態表示」ではなく「演出パート」として扱う(設計書6章)。
#   LED[0]: プレイヤー状態
#   LED[1]: ステージ雰囲気(BGMビートで脈動)
#   LED[2]: イベントフラッシュ
#
# write() は色が変わったときだけ呼ぶ。
from machine import Pin
from neopixel import NeoPixel
import config as C


def _clamp(v):
    if v < 0: return 0
    if v > C.LED_MAX_BRIGHT: return C.LED_MAX_BRIGHT
    return v


def _scale(rgb, factor):
    """factor: 0..100(%) で色をスケール"""
    return (rgb[0] * factor // 100, rgb[1] * factor // 100, rgb[2] * factor // 100)


# ステージごとの基調色(LED[1])
STAGE_AMBIENT = {
    1: (10, 25, 15),   # 緑(地上)
    2: (20, 0, 30),    # 紫(地下)
    3: (0, 15, 30),    # 水色(水中)
    4: (30, 12, 0),    # 橙(城壁)
    5: (25, 25, 30),   # 白(空)
    6: (35, 0, 0),     # 赤(ボス)
}


class FxEngine:
    def __init__(self):
        self.np = NeoPixel(Pin(C.PIN_NEOPIXEL, Pin.OUT), 3)
        self.last = [(0,0,0), (0,0,0), (0,0,0)]

        # LED[0] プレイヤー状態
        self.player_state = 'small'
        self.invincible_timer = 0
        self.damage_flash = 0

        # LED[1] ステージ雰囲気
        self.stage_num = 1
        self.beat_boost = 0   # ビートでパッと明るくなる残量

        # LED[2] イベント
        self.event_color = (0, 0, 0)
        self.event_timer = 0
        self.event_rainbow = 0  # パワーアップ時の虹色カウンタ

    # ----- 状態通知 -----
    def set_player_state(self, state):
        self.player_state = state

    def set_invincible(self, frames):
        self.invincible_timer = frames

    def set_damage(self):
        self.damage_flash = 6

    def set_stage(self, num):
        self.stage_num = num

    def beat(self):
        """BGMの音符が進んだフレームに呼ぶ → 短い明滅"""
        self.beat_boost = 4

    def event_flash(self, color, frames=8):
        self.event_color = color
        self.event_timer = frames

    def rainbow(self, frames=30):
        self.event_rainbow = frames

    # ----- フレーム更新 -----
    def update(self, frame_count):
        # ---- LED[0] プレイヤー ----
        if self.damage_flash > 0:
            led0 = (C.LED_MAX_BRIGHT, C.LED_MAX_BRIGHT, C.LED_MAX_BRIGHT)
            self.damage_flash -= 1
        elif self.invincible_timer > 0:
            self.invincible_timer -= 1
            # 高速点滅(白/黄/赤/シアン)
            colors = [(40,40,40), (40,40,0), (40,0,0), (0,40,40)]
            led0 = colors[frame_count & 3]
        else:
            s = self.player_state
            if s == 'small':
                led0 = (4, 18, 6)
            elif s == 'big':
                led0 = (0, 35, 0)
            elif s == 'fire':
                # ビートで脈動
                base = (35, 5, 0)
                if self.beat_boost > 0:
                    led0 = (40, 18, 0)
                else:
                    led0 = base
            elif s == 'dead':
                led0 = (40, 0, 0)
            else:
                led0 = (0, 0, 0)

        # ---- LED[1] 雰囲気 ----
        amb = STAGE_AMBIENT.get(self.stage_num, (10, 10, 10))
        # ゆっくり脈動(sin波もどき = ノコギリ)
        phase = (frame_count >> 2) & 31   # 0..31
        # 三角波 0..15..0
        tri = phase if phase < 16 else (31 - phase)
        scale = 70 + tri * 2  # 70..100
        if self.beat_boost > 0:
            scale += 20
            self.beat_boost -= 1
        led1 = _scale(amb, min(scale, 130))

        # ---- LED[2] イベント ----
        if self.event_rainbow > 0:
            # 虹: フレームごとに色を変える
            cycle = (30 - self.event_rainbow) % 6
            rainbow_table = [
                (40, 0, 0), (40, 20, 0), (35, 35, 0),
                (0, 40, 0), (0, 20, 40), (25, 0, 40),
            ]
            led2 = rainbow_table[cycle]
            self.event_rainbow -= 1
        elif self.event_timer > 0:
            led2 = self.event_color
            self.event_timer -= 1
        else:
            led2 = (0, 0, 0)

        # 全LEDに反映(変化があった時だけwrite)
        leds = [
            (_clamp(led0[0]), _clamp(led0[1]), _clamp(led0[2])),
            (_clamp(led1[0]), _clamp(led1[1]), _clamp(led1[2])),
            (_clamp(led2[0]), _clamp(led2[1]), _clamp(led2[2])),
        ]
        changed = False
        for i in range(3):
            if leds[i] != self.last[i]:
                self.np[i] = leds[i]
                self.last[i] = leds[i]
                changed = True
        if changed:
            self.np.write()

    def off(self):
        for i in range(3):
            self.np[i] = (0, 0, 0)
            self.last[i] = (0, 0, 0)
        self.np.write()


# ========== パーティクル ==========
# コインの吸い込み、敵撃破、破壊レンガの破片用。
# プール方式: 起動時にN個確保、再利用。dictは新規作らない。

class ParticlePool:
    MAX = 12

    def __init__(self):
        # 各パーティクル: [active, x, y, vx, vy, life]
        self.pool = [[False, 0.0, 0.0, 0.0, 0.0, 0] for _ in range(self.MAX)]

    def spawn(self, x, y, vx, vy, life):
        for p in self.pool:
            if not p[0]:
                p[0] = True
                p[1] = float(x)
                p[2] = float(y)
                p[3] = float(vx)
                p[4] = float(vy)
                p[5] = life
                return

    def burst(self, x, y, count=6):
        """敵撃破の爆発"""
        speeds = [(-1.5,-1.8), (1.5,-1.8), (-0.8,-2.2), (0.8,-2.2), (-2.0,-1.0), (2.0,-1.0)]
        for i in range(min(count, len(speeds))):
            vx, vy = speeds[i]
            self.spawn(x, y, vx, vy, 18)

    def brick(self, x, y):
        """レンガ破片4個"""
        self.spawn(x, y, -1.2, -2.4, 24)
        self.spawn(x+4, y, 1.2, -2.4, 24)
        self.spawn(x, y+4, -1.5, -1.8, 24)
        self.spawn(x+4, y+4, 1.5, -1.8, 24)

    def update_and_draw(self, oled, cam_x):
        pixel = oled.pixel
        for p in self.pool:
            if not p[0]:
                continue
            p[1] += p[3]
            p[2] += p[4]
            p[4] += 0.25   # 重力
            p[5] -= 1
            if p[5] <= 0 or p[2] > 64:
                p[0] = False
                continue
            sx = int(p[1]) - cam_x
            sy = int(p[2])
            if 0 <= sx < 128 and 0 <= sy < 64:
                pixel(sx, sy, 1)
                # 2x2にして見やすくする
                if sx+1 < 128: pixel(sx+1, sy, 1)
                if sy+1 < 64:  pixel(sx, sy+1, 1)
                if sx+1 < 128 and sy+1 < 64: pixel(sx+1, sy+1, 1)
