# framebuf.py - Pure-Python emulation of MicroPython's framebuf module.
# Only MONO_VLSB is supported (the only format used by Micro-Mario).
#
# MONO_VLSB layout:
#   1 byte = 8 vertical pixels
#   LSB = top, MSB = bottom
#   Bytes flow left-to-right per page, with `width` bytes per page,
#   `height // 8` pages stacked top-to-bottom.

MONO_VLSB = 0
MONO_HLSB = 3
MONO_HMSB = 4
RGB565    = 1
GS2_HMSB  = 5
GS4_HMSB  = 2
GS8       = 6


class FrameBuffer:
    def __init__(self, buffer, width, height, format=MONO_VLSB, stride=None):
        self.buffer = buffer  # bytearray
        self.width = width
        self.height = height
        self.format = format
        self.stride = stride if stride is not None else width

    # ---- pixel ----
    def pixel(self, x, y, color=None):
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return 0 if color is None else None
        idx = (y >> 3) * self.stride + x
        bit = 1 << (y & 7)
        if color is None:
            return 1 if (self.buffer[idx] & bit) else 0
        if color:
            self.buffer[idx] |= bit
        else:
            self.buffer[idx] &= 0xFF ^ bit

    # ---- fill ----
    def fill(self, color):
        b = 0xFF if color else 0
        for i in range(len(self.buffer)):
            self.buffer[i] = b

    def fill_rect(self, x, y, w, h, color):
        if w <= 0 or h <= 0: return
        if x < 0: w += x; x = 0
        if y < 0: h += y; y = 0
        if x >= self.width or y >= self.height: return
        if x + w > self.width:  w = self.width - x
        if y + h > self.height: h = self.height - y
        # Optimized byte-wise fill for MONO_VLSB
        stride = self.stride
        buf = self.buffer
        y_end = y + h
        page_start = y >> 3
        page_end = (y_end - 1) >> 3
        for page in range(page_start, page_end + 1):
            top = page << 3
            bot = top + 7
            mask = 0xFF
            if top < y:
                mask &= 0xFF << (y - top)
            if bot >= y_end:
                mask &= 0xFF >> (bot - y_end + 1)
            mask &= 0xFF
            base = page * stride + x
            if color:
                for i in range(w):
                    buf[base + i] |= mask
            else:
                nm = 0xFF ^ mask
                for i in range(w):
                    buf[base + i] &= nm

    # ---- rect / hline / vline / line ----
    def rect(self, x, y, w, h, color, fill=False):
        if fill:
            self.fill_rect(x, y, w, h, color)
            return
        self.fill_rect(x, y, w, 1, color)
        self.fill_rect(x, y + h - 1, w, 1, color)
        self.fill_rect(x, y, 1, h, color)
        self.fill_rect(x + w - 1, y, 1, h, color)

    def hline(self, x, y, w, color):
        self.fill_rect(x, y, w, 1, color)

    def vline(self, x, y, h, color):
        self.fill_rect(x, y, 1, h, color)

    def line(self, x1, y1, x2, y2, color):
        dx = abs(x2 - x1)
        dy = -abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx + dy
        while True:
            self.pixel(x1, y1, color)
            if x1 == x2 and y1 == y2:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x1 += sx
            if e2 <= dx:
                err += dx
                y1 += sy

    # ---- blit ----
    def blit(self, fb, x, y, key=-1, palette=None):
        # MONO_VLSB byte-aligned fast path
        if (
            isinstance(fb, FrameBuffer)
            and self.format == MONO_VLSB
            and fb.format == MONO_VLSB
            and (y & 7) == 0
            and (fb.height & 7) == 0
            and key == -1
        ):
            src = fb.buffer
            dst = self.buffer
            sw = fb.width
            sh = fb.height
            sx_start = 0
            sy_start = 0
            dx_start = x
            dy_start = y
            # Clip horizontally
            if dx_start < 0:
                sx_start = -dx_start
                sw -= sx_start
                dx_start = 0
            if dx_start + sw > self.width:
                sw = self.width - dx_start
            if sw <= 0:
                return
            # Pages
            pages = fb.height >> 3
            for p in range(pages):
                dpage = (dy_start >> 3) + p
                if dpage < 0 or dpage * 8 >= self.height:
                    continue
                src_base = p * fb.stride + sx_start
                dst_base = dpage * self.stride + dx_start
                for i in range(sw):
                    dst[dst_base + i] = src[src_base + i]
            return
        # Fallback: pixel-by-pixel
        sw = fb.width
        sh = fb.height
        for sy in range(sh):
            for sx in range(sw):
                p = fb.pixel(sx, sy)
                if key >= 0 and p == key:
                    continue
                if palette is not None:
                    p = palette.pixel(p, 0)
                self.pixel(x + sx, y + sy, p)

    # ---- text (no-op; project uses custom font via blit) ----
    def text(self, s, x, y, color=1):
        return

    def scroll(self, dx, dy):
        return
