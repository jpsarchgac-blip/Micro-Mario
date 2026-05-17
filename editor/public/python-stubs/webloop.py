# webloop.py - JS から呼ぶ Init / Step API
# main.py の while True ループの代わりに、ブラウザ rAF が step() を呼ぶ。
#
# 順序:
#   1. time_shim を最初に import して time モジュールに ticks_* を生やす
#   2. ハードウェア初期化 (machine/neopixel/ssd1306 はスタブ済)
#   3. SpriteBank / GameNew を構築
#
# JS 側は:
#   await pyodide.runPythonAsync("import webloop; webloop.init()")
#   毎フレ: pyodide.globals.get("webloop").step()
import time_shim  # noqa: F401  (must come first to patch time.*)
import gc

import config as C
from machine import I2C
from ssd1306 import SSD1306_I2C
from input import Input
from audio import AudioEngine
from render import SpriteBank

_game = None
_oled = None
_bank = None
_audio = None
_fx = None
_inp = None
_use_old = False
_last_result = None


def init():
    """Pyodide ロード完了後に1回だけ呼ぶ。"""
    global _game, _oled, _bank, _audio, _fx, _inp, _use_old
    _use_old = False

    # Hardware init (mirrors main.init_hardware but bypasses real I2C)
    i2c = I2C(0)
    _oled = SSD1306_I2C(C.SCREEN_W, C.SCREEN_H, i2c)
    _oled.fill(0)
    _oled.show()

    _bank = SpriteBank()
    _inp  = Input()
    _audio = AudioEngine()

    # NEWモードで起動 (main.py と同じ)
    from fx_new import FxNew
    from game_new import GameNew
    _fx = FxNew()
    _game = GameNew(_oled, _bank, _inp, _audio, _fx)

    gc.collect()
    return True


def step():
    """毎フレ呼ぶ。1フレ分のゲーム update + draw。"""
    global _game, _fx, _use_old, _last_result
    if _game is None:
        return False
    result = _game.update()
    _last_result = result

    # OLDモード切替 (main.py のロジック)
    if result == 'OLD' and not _use_old:
        from game import Game
        from fx import FxEngine
        _fx = FxEngine()
        _game = Game(_oled, _bank, _inp, _audio, _fx)
        _use_old = True
        gc.collect()

    _game.draw()
    return True


def reset():
    """完全リセット。"""
    global _game, _use_old
    _use_old = False
    if _oled is not None:
        _oled.fill(0)
        _oled.show()
    if _audio is not None:
        try:
            _audio.shutdown()
        except Exception:
            pass
    if _fx is not None:
        try:
            _fx.off()
        except Exception:
            pass
    _game = None
    gc.collect()
