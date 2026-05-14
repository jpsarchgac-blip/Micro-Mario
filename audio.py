# audio.py - オーディオエンジン
#
# 設計の肝:
#   - PWMは1chしか無いが、論理的に BGM と SFX の2chを持つ
#   - SFXが鳴っている間はBGMは「進めるけど音は出さない」
#   - SFX終了後にBGMが続きから自然に鳴る → 音切れがない
#   - 毎フレーム update() を1回呼ぶだけ。time.sleep等で止めない
import time
from machine import Pin, PWM
import config as C
import music


class AudioEngine:
    def __init__(self):
        self.pwm = PWM(Pin(C.PIN_SPEAKER))
        self.pwm.freq(1000)
        self.pwm.duty_u16(0)
        
        self.master_volume = 1.0

        # BGM state
        self.bgm_seq = None
        self.bgm_idx = 0
        self.bgm_next_tick = 0
        self.bgm_paused = False

        # SFX state(SFXはqueue)
        self.sfx_seq = None
        self.sfx_idx = 0
        self.sfx_next_tick = 0

        # 現在PWMに出力中のオーナー
        self.owner = None  # 'bgm' / 'sfx' / None

        # ビート同期用(LED連動)
        self.beat_pulse = 0   # update() でBGMが進んだフレームだけ1にする

    # ----- BGM -----

    def play_bgm(self, name):
        if name is None:
            self.bgm_seq = None
            return
        seq = music.BGM.get(name)
        if seq is None:
            return
        self.bgm_seq = seq
        self.bgm_idx = 0
        self.bgm_next_tick = time.ticks_ms()
        self.bgm_paused = False

    def stop_bgm(self):
        self.bgm_seq = None
        if self.owner == 'bgm':
            self.pwm.duty_u16(0)
            self.owner = None

    def pause_bgm(self):
        self.bgm_paused = True
        if self.owner == 'bgm':
            self.pwm.duty_u16(0)

    def resume_bgm(self):
        self.bgm_paused = False
        self.bgm_next_tick = time.ticks_ms()

    # ----- SFX -----

    def play_sfx(self, name):
        seq = music.SFX.get(name)
        if seq is None:
            return
        self.sfx_seq = seq
        self.sfx_idx = 0
        self.sfx_next_tick = time.ticks_ms()

    def stop_sfx(self):
        self.sfx_seq = None
        if self.owner == 'sfx':
            self.pwm.duty_u16(0)
            self.owner = None

    # ----- update() -----

    def update(self):
        """毎フレーム呼ぶ。SFX優先、BGMはバックグラウンド進行。"""
        now = time.ticks_ms()
        self.beat_pulse = 0

        # ---- SFX進行(優先) ----
        if self.sfx_seq is not None:
            if time.ticks_diff(self.sfx_next_tick, now) <= 0:
                if self.sfx_idx >= len(self.sfx_seq):
                    # SFX終了
                    self.sfx_seq = None
                    self.pwm.duty_u16(0)
                    self.owner = None
                    # BGMの次音を即座に強制再開させる
                    if self.bgm_seq is not None and not self.bgm_paused:
                        self.bgm_next_tick = now
                else:
                    freq, dur = self.sfx_seq[self.sfx_idx]
                    self.sfx_idx += 1
                    if freq > 0:
                        try:
                            self.pwm.freq(freq)
                        except ValueError:
                            pass
                        self.pwm.duty_u16(int(C.AUDIO_SFX_VOL * self.master_volume))
                        self.owner = 'sfx'
                    else:
                        self.pwm.duty_u16(0)
                        self.owner = None
                    self.sfx_next_tick = time.ticks_add(now, dur)
            return  # SFX中はBGM処理スキップ(時刻だけ保持)

        # ---- BGM進行 ----
        if self.bgm_seq is None or self.bgm_paused:
            if self.owner == 'bgm':
                self.pwm.duty_u16(0)
                self.owner = None
            return

        if time.ticks_diff(self.bgm_next_tick, now) <= 0:
            freq, dur = self.bgm_seq[self.bgm_idx]
            self.bgm_idx = (self.bgm_idx + 1) % len(self.bgm_seq)
            if freq > 0:
                try:
                    self.pwm.freq(freq)
                except ValueError:
                    pass
                self.pwm.duty_u16(int(C.AUDIO_BGM_VOL * self.master_volume))
                self.owner = 'bgm'
            else:
                self.pwm.duty_u16(0)
                self.owner = None
            self.bgm_next_tick = time.ticks_add(now, dur)
            self.beat_pulse = 1

    def shutdown(self):
        self.pwm.duty_u16(0)
