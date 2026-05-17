# neopixel.py - NeoPixel stub. RGB values forwarded to JS via __mm_leds.write(i, r, g, b)
import js
_leds = js.globalThis.__mm_leds


class NeoPixel:
    def __init__(self, pin, n, bpp=3, timing=1):
        self.n = n
        self._buf = [(0, 0, 0)] * n

    def __setitem__(self, i, rgb):
        # rgb may be tuple or list
        r = int(rgb[0]); g = int(rgb[1]); b = int(rgb[2])
        self._buf[i] = (r, g, b)

    def __getitem__(self, i):
        return self._buf[i]

    def __len__(self):
        return self.n

    def fill(self, rgb):
        r = int(rgb[0]); g = int(rgb[1]); b = int(rgb[2])
        for i in range(self.n):
            self._buf[i] = (r, g, b)

    def write(self):
        try:
            for i, (r, g, b) in enumerate(self._buf):
                _leds.write(i, r, g, b)
        except Exception:
            pass
