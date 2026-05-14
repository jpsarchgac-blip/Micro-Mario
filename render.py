# render.py - スプライト管理と描画ヘルパ
#
# 設計の核: pixel()を一切使わず、すべて FrameBuffer.blit() で描く。
# 起動時に全スプライトを FrameBuffer 化しておくことで、
# 描画コール1回あたり50〜200μs程度に抑える。
import framebuf
import sprites as sp


class SpriteBank:
    """全スプライトを起動時に FrameBuffer 化して保持する。"""

    def __init__(self):
        self.fb = {}   # name -> FrameBuffer (8x8 or 8x16)
        self._build_all()

    def _build_8x8(self, name, data):
        # MONO_VLSB: 8x8 = 8バイト
        buf = bytearray(data)
        self.fb[name] = framebuf.FrameBuffer(buf, 8, 8, framebuf.MONO_VLSB)

    def _build_8x16(self, name, data):
        buf = bytearray(data)
        self.fb[name] = framebuf.FrameBuffer(buf, 8, 16, framebuf.MONO_VLSB)

    def _build_all(self):
        for name, data in sp.TILE_SPRITES.items():
            if len(data) == 8:
                self._build_8x8(name, data)
            elif len(data) == 16:
                self._build_8x16(name, data)
            # それ以外は無視

        # ボス: 8x8を9枚として個別構築 (BOSS_BODYは8x24に並んだ8x8x9)
        boss = sp.BOSS_BODY
        names = ['boss_00','boss_10','boss_20',
                 'boss_01','boss_11','boss_21',
                 'boss_02','boss_12','boss_22']
        for i, n in enumerate(names):
            piece = bytes(boss[i*8:(i+1)*8])
            self._build_8x8(n, piece)

        # 小型フォント(4x8)
        self.font = {}
        for ch, data in sp.TINY_DIGITS.items():
            buf = bytearray(data)
            self.font[ch] = framebuf.FrameBuffer(buf, 4, 8, framebuf.MONO_VLSB)

        # ハート
        heart_buf = bytearray(sp.HEART_MINI)
        # 6x8として扱う(実データは6バイトしかないが、横6×縦8で配置)
        # FrameBuffer.MONO_VLSBは1バイト=縦8。横6=6バイト必要
        self.heart = framebuf.FrameBuffer(heart_buf, 6, 8, framebuf.MONO_VLSB)


# ----- 描画ユーティリティ -----

def draw_boss(oled, bank, x, y):
    """24x24のボスを9枚blitで描画。"""
    fb = bank.fb
    blit = oled.blit
    for row in range(3):
        for col in range(3):
            key = 'boss_{}{}'.format(col, row)
            blit(fb[key], x + col * 8, y + row * 8)


def draw_number(oled, bank, num, x, y, width=5):
    """右詰めで数字を描画。widthは最小桁数(ゼロパディング)。"""
    s = str(num)
    if len(s) < width:
        s = '0' * (width - len(s)) + s
    blit = oled.blit
    fb = bank.font
    cx = x
    for ch in s:
        if ch in fb:
            blit(fb[ch], cx, y)
        cx += 5   # 4px幅+1pxスペース


def draw_text(oled, bank, text, x, y):
    """数字+記号のみ対応の極小テキスト描画。"""
    blit = oled.blit
    fb = bank.font
    cx = x
    for ch in text:
        if ch in fb:
            blit(fb[ch], cx, y)
        cx += 5


def draw_hearts(oled, bank, count, x, y):
    """残機ハートを横並びで描画。"""
    blit = oled.blit
    heart = bank.heart
    for i in range(count):
        blit(heart, x + i * 7, y)
