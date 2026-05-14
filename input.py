# input.py - スイッチのポーリングとエッジ検出
#
# 設計: 物理ピンの値はそのまま使わない。前フレームと現フレームの比較で
# pressed / held / released を出す。これでジャンプの長押し判定や
# メニュー操作のチャタリングを潰す。
from machine import Pin
import config as C


class Input:
    def __init__(self):
        self.sw = [
            Pin(C.PIN_SW1, Pin.IN, Pin.PULL_UP),
            Pin(C.PIN_SW2, Pin.IN, Pin.PULL_UP),
            Pin(C.PIN_SW3, Pin.IN, Pin.PULL_UP),
        ]
        # PULL_UP: 押下=0, 開放=1
        self.prev = [1, 1, 1]
        self.curr = [1, 1, 1]

    def update(self):
        self.prev[0] = self.curr[0]
        self.prev[1] = self.curr[1]
        self.prev[2] = self.curr[2]
        self.curr[0] = self.sw[0].value()
        self.curr[1] = self.sw[1].value()
        self.curr[2] = self.sw[2].value()

    def pressed(self, i):
        """このフレームに押し始められた。"""
        return self.prev[i] == 1 and self.curr[i] == 0

    def held(self, i):
        """押し続けられている。"""
        return self.curr[i] == 0

    def released(self, i):
        """このフレームに離された。"""
        return self.prev[i] == 0 and self.curr[i] == 1

    def any_pressed(self):
        return self.pressed(0) or self.pressed(1) or self.pressed(2)
