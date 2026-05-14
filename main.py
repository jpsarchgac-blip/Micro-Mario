# main.py - エントリポイント
#
# 役割:
#   1. ハードウェア初期化(I2C, OLED, NeoPixel, スイッチ, PWM)
#   2. SpriteBank の構築(全スプライトを起動時に FrameBuffer 化)
#   3. メインループ: 33ms 固定フレーム
#
# 設計:
#   - time.sleep_ms はフレーム余り時間にしか使わない
#   - 例外時はスピーカ・LEDを必ず止める(try/finally)
import time
import gc
from machine import Pin, I2C
from ssd1306 import SSD1306_I2C

import config as C
from input import Input
from audio import AudioEngine
from fx import FxEngine
from render import SpriteBank
from game import Game


def init_hardware():
    """ハードウェア初期化。失敗時は例外を投げてユーザーに気づかせる。"""
    # I2C: 設計書通りGP0/GP1を明示指定(GP4のSW3との競合回避)
    i2c = I2C(0)
    oled = SSD1306_I2C(C.SCREEN_W, C.SCREEN_H, i2c)
    return oled


def main():
    print('[MICRO MARIO] boot')
    oled = init_hardware()
    oled.text('LOADING...', 24, 28)
    oled.show()

    bank = SpriteBank()
    inp  = Input()
    audio = AudioEngine()
    fx   = FxEngine()

    # NEWモードで起動(モード選択画面を含む)
    from fx_new import FxNew
    from game_new import GameNew
    fx_new = FxNew()
    game = GameNew(oled, bank, inp, audio, fx_new)
    use_old = False

    gc.collect()
    print('[MICRO MARIO] free mem: {}'.format(gc.mem_free()))

    frame_target = C.FRAME_MS
    next_frame = time.ticks_ms()
    frames = 0
    fps_log_tick = time.ticks_ms()

    try:
        while True:
            now = time.ticks_ms()
            result = game.update()
            # モード選択でOLDが選ばれた場合
            if result == 'OLD' and not use_old:
                use_old = True
                game = Game(oled, bank, inp, audio, fx)
                gc.collect()
            game.draw()
            frames += 1

            if time.ticks_diff(now, fps_log_tick) >= 10_000:
                print('FPS:', frames / 10.0, ' mem:', gc.mem_free())
                frames = 0
                fps_log_tick = now
                gc.collect()

            next_frame = time.ticks_add(next_frame, frame_target)
            sleep = time.ticks_diff(next_frame, time.ticks_ms())
            if sleep > 0:
                time.sleep_ms(sleep)
            elif sleep < -frame_target * 3:
                next_frame = time.ticks_ms()

    except KeyboardInterrupt:
        print('[MICRO MARIO] interrupted')
    except Exception as e:
        print('[MICRO MARIO] error:', e)
        import sys
        sys.print_exception(e)
    finally:
        audio.shutdown()
        fx_new.off()
        fx.off()
        oled.fill(0)
        oled.text('HALTED', 40, 28)
        oled.show()


if __name__ == '__main__':
    main()
