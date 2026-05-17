# ssd1306.py - Overrides the project's real ssd1306.py.
# Provides SSD1306_I2C extending framebuf.FrameBuffer with show()
# pushing the buffer to JS via globalThis.__mm_oled.onShow.
import framebuf
import js
_oled = js.globalThis.__mm_oled


class SSD1306(framebuf.FrameBuffer):
    def __init__(self, width, height, external_vcc=False):
        self.width = width
        self.height = height
        self.external_vcc = external_vcc
        self.pages = height // 8
        self.buffer = bytearray(self.pages * width)
        super().__init__(self.buffer, width, height, framebuf.MONO_VLSB)

    def init_display(self): pass
    def poweroff(self): pass
    def poweron(self): pass
    def contrast(self, contrast): pass
    def invert(self, invert): pass
    def show(self):
        try:
            # Pass bytes (Pyodide auto-converts bytearray to Uint8Array proxy)
            _oled.onShow(self.buffer)
        except Exception:
            pass


class SSD1306_I2C(SSD1306):
    def __init__(self, width, height, i2c, addr=0x3C, external_vcc=False):
        self.i2c = i2c
        self.addr = addr
        super().__init__(width, height, external_vcc)


class SSD1306_SPI(SSD1306):
    def __init__(self, width, height, spi, dc, res, cs, external_vcc=False):
        super().__init__(width, height, external_vcc)
