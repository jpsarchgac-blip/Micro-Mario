// Low-level drawing helpers that emulate the SSD1306 + sprite drawing pipeline.
// All coordinates are in device pixels (128x64). Use `scale` to upscale.
import { BUILTIN_SPRITES } from "@/lib/tiles";

export const SCREEN_W = 128;
export const SCREEN_H = 64;

// OLED-style pixel color (cyan-white on near-black)
export const FG = "#fef9c3";
export const BG = "#0a0a14";

export function clear(ctx: CanvasRenderingContext2D, scale: number) {
  ctx.fillStyle = BG;
  ctx.fillRect(0, 0, SCREEN_W * scale, SCREEN_H * scale);
}

export function setPixel(ctx: CanvasRenderingContext2D, x: number, y: number, scale: number, on: boolean) {
  ctx.fillStyle = on ? FG : BG;
  ctx.fillRect(x * scale, y * scale, scale, scale);
}

export function fillRect(
  ctx: CanvasRenderingContext2D,
  x: number,
  y: number,
  w: number,
  h: number,
  scale: number,
  on = true
) {
  ctx.fillStyle = on ? FG : BG;
  ctx.fillRect(x * scale, y * scale, w * scale, h * scale);
}

export function strokeRect(
  ctx: CanvasRenderingContext2D,
  x: number,
  y: number,
  w: number,
  h: number,
  scale: number
) {
  ctx.fillStyle = FG;
  // top + bottom
  ctx.fillRect(x * scale, y * scale, w * scale, scale);
  ctx.fillRect(x * scale, (y + h - 1) * scale, w * scale, scale);
  // left + right
  ctx.fillRect(x * scale, y * scale, scale, h * scale);
  ctx.fillRect((x + w - 1) * scale, y * scale, scale, h * scale);
}

export function hLine(ctx: CanvasRenderingContext2D, x: number, y: number, w: number, scale: number) {
  fillRect(ctx, x, y, w, 1, scale);
}

export function vLine(ctx: CanvasRenderingContext2D, x: number, y: number, h: number, scale: number) {
  fillRect(ctx, x, y, 1, h, scale);
}

/** Draw a MONO_VLSB 8-byte sprite at (x,y) in device pixels. */
export function blitSprite(
  ctx: CanvasRenderingContext2D,
  sprite: number[],
  x: number,
  y: number,
  scale: number
) {
  ctx.fillStyle = FG;
  for (let col = 0; col < 8; col++) {
    const b = sprite[col] ?? 0;
    for (let row = 0; row < 8; row++) {
      if (b & (1 << row)) {
        ctx.fillRect((x + col) * scale, (y + row) * scale, scale, scale);
      }
    }
  }
}

/** Draw a tile by id, falling back to a colored block for unknown ids. */
export function blitTile(
  ctx: CanvasRenderingContext2D,
  tileId: number,
  x: number,
  y: number,
  scale: number,
  customSprites: Map<number, number[]>
) {
  if (tileId === 0) return;
  const spr = customSprites.get(tileId) ?? BUILTIN_SPRITES[tileId];
  if (spr) blitSprite(ctx, spr, x, y, scale);
}

// 4x6 mini font for text (digits + uppercase letters + space + punctuation)
// MONO_VLSB-like: 4 bytes per char, 6px tall, but we'll use a simple 5x8 ASCII bitmap
// to keep things compact. Each char = 5 bytes (col 0..4), each byte = 8 vertical px (LSB top).
//
// Source-inspired from public-domain 5x7 fonts (only digits/A-Z/symbols).
const FONT5: Record<string, number[]> = {
  " ": [0x00, 0x00, 0x00, 0x00, 0x00],
  "!": [0x00, 0x00, 0x5F, 0x00, 0x00],
  "'": [0x00, 0x03, 0x00, 0x00, 0x00],
  "(": [0x00, 0x1C, 0x22, 0x41, 0x00],
  ")": [0x00, 0x41, 0x22, 0x1C, 0x00],
  "+": [0x08, 0x08, 0x3E, 0x08, 0x08],
  ",": [0x00, 0x40, 0x30, 0x00, 0x00],
  "-": [0x08, 0x08, 0x08, 0x08, 0x08],
  ".": [0x00, 0x30, 0x30, 0x00, 0x00],
  "/": [0x20, 0x10, 0x08, 0x04, 0x02],
  "0": [0x3E, 0x51, 0x49, 0x45, 0x3E],
  "1": [0x00, 0x42, 0x7F, 0x40, 0x00],
  "2": [0x42, 0x61, 0x51, 0x49, 0x46],
  "3": [0x21, 0x41, 0x45, 0x4B, 0x31],
  "4": [0x18, 0x14, 0x12, 0x7F, 0x10],
  "5": [0x27, 0x45, 0x45, 0x45, 0x39],
  "6": [0x3C, 0x4A, 0x49, 0x49, 0x30],
  "7": [0x01, 0x71, 0x09, 0x05, 0x03],
  "8": [0x36, 0x49, 0x49, 0x49, 0x36],
  "9": [0x06, 0x49, 0x49, 0x29, 0x1E],
  ":": [0x00, 0x36, 0x36, 0x00, 0x00],
  ">": [0x00, 0x41, 0x22, 0x14, 0x08],
  "<": [0x00, 0x08, 0x14, 0x22, 0x41],
  "=": [0x14, 0x14, 0x14, 0x14, 0x14],
  "?": [0x02, 0x01, 0x51, 0x09, 0x06],
  "A": [0x7E, 0x11, 0x11, 0x11, 0x7E],
  "B": [0x7F, 0x49, 0x49, 0x49, 0x36],
  "C": [0x3E, 0x41, 0x41, 0x41, 0x22],
  "D": [0x7F, 0x41, 0x41, 0x22, 0x1C],
  "E": [0x7F, 0x49, 0x49, 0x49, 0x41],
  "F": [0x7F, 0x09, 0x09, 0x01, 0x01],
  "G": [0x3E, 0x41, 0x41, 0x51, 0x32],
  "H": [0x7F, 0x08, 0x08, 0x08, 0x7F],
  "I": [0x00, 0x41, 0x7F, 0x41, 0x00],
  "J": [0x20, 0x40, 0x41, 0x3F, 0x01],
  "K": [0x7F, 0x08, 0x14, 0x22, 0x41],
  "L": [0x7F, 0x40, 0x40, 0x40, 0x40],
  "M": [0x7F, 0x02, 0x04, 0x02, 0x7F],
  "N": [0x7F, 0x04, 0x08, 0x10, 0x7F],
  "O": [0x3E, 0x41, 0x41, 0x41, 0x3E],
  "P": [0x7F, 0x09, 0x09, 0x09, 0x06],
  "Q": [0x3E, 0x41, 0x51, 0x21, 0x5E],
  "R": [0x7F, 0x09, 0x19, 0x29, 0x46],
  "S": [0x46, 0x49, 0x49, 0x49, 0x31],
  "T": [0x01, 0x01, 0x7F, 0x01, 0x01],
  "U": [0x3F, 0x40, 0x40, 0x40, 0x3F],
  "V": [0x1F, 0x20, 0x40, 0x20, 0x1F],
  "W": [0x7F, 0x20, 0x18, 0x20, 0x7F],
  "X": [0x63, 0x14, 0x08, 0x14, 0x63],
  "Y": [0x03, 0x04, 0x78, 0x04, 0x03],
  "Z": [0x61, 0x51, 0x49, 0x45, 0x43],
};

export function drawChar(
  ctx: CanvasRenderingContext2D,
  ch: string,
  x: number,
  y: number,
  scale: number
) {
  const data = FONT5[ch.toUpperCase()];
  if (!data) return;
  ctx.fillStyle = FG;
  for (let col = 0; col < 5; col++) {
    const b = data[col];
    for (let row = 0; row < 7; row++) {
      if (b & (1 << row)) ctx.fillRect((x + col) * scale, (y + row) * scale, scale, scale);
    }
  }
}

export function drawText(
  ctx: CanvasRenderingContext2D,
  text: string,
  x: number,
  y: number,
  scale: number
) {
  let cx = x;
  for (const ch of text) {
    drawChar(ctx, ch, cx, y, scale);
    cx += 6; // 5px + 1 gap
  }
}

export function textCenterX(text: string, screenW = SCREEN_W) {
  return Math.floor((screenW - text.length * 6) / 2);
}

export function drawHeart(ctx: CanvasRenderingContext2D, x: number, y: number, scale: number) {
  ctx.fillStyle = FG;
  // 6x6 heart
  const HEART = [0x06, 0x0F, 0x07, 0x07, 0x0F, 0x06];
  for (let col = 0; col < 6; col++) {
    const b = HEART[col];
    for (let row = 0; row < 6; row++) {
      if (b & (1 << row)) ctx.fillRect((x + col) * scale, (y + row) * scale, scale, scale);
    }
  }
}
