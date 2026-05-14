# make_art.py - 15枚のうごメモ風ピクセルアート（128x64）を生成して保存する
import framebuf
import os
import gc

# ディレクトリ作成
try:
    os.mkdir('art')
except OSError:
    pass

def draw_stick_mario(fb, x, y):
    fb.fill_rect(x, y, 6, 6, 1) # head
    fb.hline(x-2, y+2, 10, 1) # brim
    fb.vline(x+3, y+6, 6, 1) # body
    fb.line(x-2, y+8, x+3, y+8, 1) # arm L
    fb.line(x+3, y+8, x+8, y+8, 1) # arm R
    fb.line(x+3, y+12, x, y+16, 1) # leg L
    fb.line(x+3, y+12, x+6, y+16, 1) # leg R

def draw_stick_bowser(fb, x, y):
    fb.fill_rect(x, y, 10, 10, 1) # head
    fb.fill_rect(x-5, y+10, 20, 15, 1) # body
    fb.fill_rect(x-5, y+10, 5, 5, 0) # spike detail
    fb.line(x-10, y+12, x-5, y+12, 1) # arm L
    fb.line(x+20, y+12, x+25, y+12, 1) # arm R
    fb.line(x, y+25, x, y+30, 1) # leg L
    fb.line(x+10, y+25, x+10, y+30, 1) # leg R

def draw_stick_peach(fb, x, y):
    fb.fill_rect(x, y, 6, 6, 1) # head
    fb.hline(x, y-2, 6, 1) # crown
    fb.line(x+3, y+6, x-2, y+16, 1) # dress L
    fb.line(x+3, y+6, x+8, y+16, 1) # dress R
    fb.hline(x-2, y+16, 11, 1) # dress bot
    fb.hline(x-1, y+10, 8, 1) # arms

def draw_castle(fb, x, y):
    fb.rect(x, y, 30, 20, 1)
    fb.rect(x-5, y+10, 40, 10, 1)
    fb.fill_rect(x+10, y+12, 10, 8, 0) # door
    fb.rect(x+10, y+12, 10, 8, 1)

def text(fb, msg, x, y):
    fb.text(msg, x, y, 1)

buf = bytearray(1024)
fb = framebuf.FrameBuffer(buf, 128, 64, framebuf.MONO_VLSB)

SCENES = {
    'A1': lambda: (draw_stick_mario(fb, 40, 30), draw_stick_bowser(fb, 70, 20), fb.line(46,38,65,32,1), text(fb, "I FORGIVE YOU", 16, 8)),
    'A2': lambda: (draw_castle(fb, 50, 30), draw_stick_mario(fb, 30, 40), draw_stick_peach(fb, 20, 40), draw_stick_bowser(fb, 90, 30), text(fb, "REBUILDING...", 20, 8)),
    'A3': lambda: (draw_castle(fb, 50, 40), fb.ellipse(64, 64, 60, 40, 1), text(fb, "PEACE AT LAST", 16, 16)),
    
    'B1': lambda: (draw_stick_mario(fb, 30, 30), draw_stick_bowser(fb, 80, 20), text(fb, "VS", 56, 30), text(fb, "ROUND 2!", 36, 8)),
    'B2': lambda: (fb.rect(20, 40, 20, 10, 1), fb.rect(80, 40, 20, 10, 1), text(fb, "RACING!", 36, 16)),
    'B3': lambda: (fb.rect(50, 20, 28, 30, 1), fb.hline(40, 50, 48, 1), draw_stick_mario(fb, 20, 30), draw_stick_bowser(fb, 90, 20), text(fb, "ETERNAL RIVALS", 12, 4)),
    
    'C1': lambda: (draw_stick_peach(fb, 60, 30), draw_stick_mario(fb, 20, 30), draw_stick_bowser(fb, 90, 20), text(fb, "STOP FIGHTING!", 10, 8)),
    'C2': lambda: (fb.rect(40, 30, 48, 20, 1), fb.rect(50, 20, 28, 10, 1), fb.vline(64, 15, 5, 1), text(fb, "GIANT CAKE", 24, 4)),
    'C3': lambda: (draw_stick_mario(fb, 30, 40), draw_stick_peach(fb, 60, 40), draw_stick_bowser(fb, 90, 30), text(fb, "BEST FRIENDS", 16, 16)),
    
    'R1': lambda: (draw_stick_mario(fb, 60, 20), fb.ellipse(64, 50, 40, 20, 1), text(fb, "COIN POOL!", 24, 4)),
    'R2': lambda: (fb.rect(50, 10, 28, 40, 1), fb.hline(40, 50, 48, 1), text(fb, "GOLDEN STATUE", 16, 56)),
    'R3': lambda: (draw_stick_bowser(fb, 64, 20), fb.rect(50, 50, 28, 10, 1), text(fb, "CASHIER BOWSER", 8, 4)),
    
    'L1': lambda: (draw_stick_mario(fb, 64, 30), fb.ellipse(67, 38, 20, 20, 1), text(fb, "FLAWLESS!", 28, 8)),
    'L2': lambda: (fb.rect(0, 50, 128, 14, 1), text(fb, "CONFETTI!", 28, 20)),
    'L3': lambda: (fb.hline(40, 50, 48, 1), fb.rect(60, 40, 8, 10, 1), text(fb, "LEGENDARY HERO", 8, 16)),
}

for name, draw_fn in SCENES.items():
    fb.fill(0)
    draw_fn()
    # Dither or just save raw binary
    with open('art/{}.bin'.format(name), 'wb') as f:
        f.write(buf)
    print("Generated art/{}.bin".format(name))
    gc.collect()

print("All art generated successfully!")
