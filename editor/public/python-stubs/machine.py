# machine.py - MicroPython 'machine' module stub for Pyodide
# Hardware pins / I2C / PWM are routed to JavaScript via globalThis.__mm_*
import js

# JS-side bridges (set up by hardware-bridge.ts before Python runs).
# Keys: __mm_keys.sw1/sw2/sw3 (true = pressed)
# Audio: __mm_audio.set(freq, duty_u16)
_keys = js.globalThis.__mm_keys
_pwm  = js.globalThis.__mm_audio


class Pin:
    IN = 0
    OUT = 1
    PULL_UP = 2

    def __init__(self, pin, mode=IN, pull=None):
        self._pin = pin
        self._mode = mode

    def value(self, *args):
        # OUT mode write: ignore (no GPIO output emulated yet)
        if args:
            return None
        # PULL_UP semantics: pressed = 0, released = 1 (matches config.py)
        p = self._pin
        try:
            if p == 2:   return 0 if _keys.sw1 else 1
            if p == 3:   return 0 if _keys.sw2 else 1
            if p == 6:   return 0 if _keys.sw3 else 1
        except Exception:
            pass
        return 1

    def on(self):  self.value(1)
    def off(self): self.value(0)


class I2C:
    """Stub - the real OLED driver path bypasses I2C entirely (see ssd1306 stub)."""
    def __init__(self, id=0, *, sda=None, scl=None, freq=400_000):
        self._id = id
    def writeto(self, *a, **k): pass
    def writevto(self, *a, **k): pass
    def readfrom(self, *a, **k): return b""
    def scan(self): return []


class PWM:
    def __init__(self, pin, *a, **k):
        self._freq = 1000
        self._duty = 0

    def freq(self, f=None):
        if f is None:
            return self._freq
        self._freq = int(f)
        try:
            _pwm.set(self._freq, self._duty)
        except Exception:
            pass

    def duty_u16(self, d=None):
        if d is None:
            return self._duty
        self._duty = int(d)
        try:
            _pwm.set(self._freq, self._duty)
        except Exception:
            pass

    def deinit(self):
        self._duty = 0
        try:
            _pwm.set(self._freq, 0)
        except Exception:
            pass
