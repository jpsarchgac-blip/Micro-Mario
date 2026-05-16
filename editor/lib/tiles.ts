// Built-in tile definitions, mirrored from world_new.py + sprites.py + custom_stages.py
// Sprite data is MONO_VLSB: 8 bytes, each byte = 8 vertical pixels (LSB top).
import type { BlockBehavior, BlockDef } from "./types";

export const TILE_IDS = {
  AIR: 0,
  GROUND: 1,
  BRICK: 2,
  QBLOCK: 3,
  PIPE_TL: 4,
  PIPE_TR: 5,
  PIPE_BL: 6,
  PIPE_BR: 7,
  COIN: 8,
  SPIKE: 9,
  GOAL: 10,
  CLOUD_PLAT: 11,
  QUSED: 12,
  MAGMA: 13,
  GRASS: 14,
  FLAG: 15,
  // Built-in custom blocks (custom_stages.py BUILTIN_BLOCKS)
  ICE: 16,
  SAND: 17,
  BOUNCE: 18,
  THORN: 19,
  DARK_GR: 20,
} as const;

// Sprite bitmaps (8 bytes each, MONO_VLSB).
// Most are copied from sprites.py; minor visual approximations kept identical to game.
export const BUILTIN_SPRITES: Record<number, number[]> = {
  [TILE_IDS.GROUND]:   [0xFF, 0xFD, 0xFB, 0xFF, 0xDF, 0xBF, 0xFF, 0x7F],
  [TILE_IDS.BRICK]:    [0xFF, 0x81, 0xFF, 0x81, 0xFF, 0x81, 0xFF, 0x81],
  [TILE_IDS.QBLOCK]:   [0xFF, 0x81, 0xBD, 0xA5, 0xB5, 0x95, 0x81, 0xFF],
  [TILE_IDS.QUSED]:    [0xFF, 0x81, 0x81, 0x81, 0x81, 0x81, 0x81, 0xFF],
  [TILE_IDS.PIPE_TL]:  [0xFC, 0x02, 0x01, 0xFD, 0xFD, 0xFD, 0xFD, 0xFD],
  [TILE_IDS.PIPE_TR]:  [0xFD, 0xFD, 0xFD, 0xFD, 0xFD, 0x01, 0x02, 0xFC],
  [TILE_IDS.PIPE_BL]:  [0xFF, 0x01, 0x01, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF],
  [TILE_IDS.PIPE_BR]:  [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0x01, 0x01, 0xFF],
  [TILE_IDS.COIN]:     [0x00, 0x3C, 0x66, 0x42, 0x42, 0x66, 0x3C, 0x00],
  [TILE_IDS.SPIKE]:    [0x80, 0xC0, 0xE0, 0xF8, 0xF8, 0xE0, 0xC0, 0x80],
  [TILE_IDS.CLOUD_PLAT]: [0x10, 0x38, 0x7C, 0xFE, 0xFE, 0x7C, 0x38, 0x10],
  [TILE_IDS.GOAL]:     [0x00, 0xFF, 0xFF, 0x00, 0x00, 0xFF, 0xFF, 0x00],
  [TILE_IDS.MAGMA]:    [0xC0, 0xE0, 0xF0, 0xF8, 0xF8, 0xF0, 0xE0, 0xC0],
  [TILE_IDS.GRASS]:    [0x1E, 0x3F, 0xFF, 0xFF, 0xFF, 0xFF, 0x3F, 0x1E],
  [TILE_IDS.FLAG]:     [0x00, 0xFF, 0xFF, 0x00, 0x00, 0x00, 0x00, 0x00],
  // Built-in custom
  [TILE_IDS.ICE]:      [0xFF, 0x81, 0xBD, 0xA5, 0xA5, 0xBD, 0x81, 0xFF],
  [TILE_IDS.SAND]:     [0xAA, 0x55, 0xAA, 0x55, 0xAA, 0x55, 0xAA, 0x55],
  [TILE_IDS.BOUNCE]:   [0x18, 0x3C, 0x7E, 0xFF, 0xFF, 0x7E, 0x3C, 0x18],
  [TILE_IDS.THORN]:    [0x99, 0x42, 0xA5, 0x42, 0xA5, 0x42, 0xA5, 0x99],
  [TILE_IDS.DARK_GR]:  [0x00, 0x42, 0x24, 0x18, 0x18, 0x24, 0x42, 0x00],
};

export const BUILTIN_BLOCKS: BlockDef[] = [
  // ID 16-20 mirrors custom_stages.py BUILTIN_BLOCKS
  { id: 16, name: "tile_ice",     behavior: "solid",    sprite: BUILTIN_SPRITES[16] },
  { id: 17, name: "tile_sand",    behavior: "solid",    sprite: BUILTIN_SPRITES[17] },
  { id: 18, name: "tile_bounce",  behavior: "platform", sprite: BUILTIN_SPRITES[18] },
  { id: 19, name: "tile_thorn",   behavior: "lethal",   sprite: BUILTIN_SPRITES[19] },
  { id: 20, name: "tile_dark_gr", behavior: "solid",    sprite: BUILTIN_SPRITES[20] },
];

export const TILE_LABELS: Record<number, string> = {
  0: "AIR",
  1: "GROUND",
  2: "BRICK",
  3: "QBLOCK",
  4: "PIPE_TL",
  5: "PIPE_TR",
  6: "PIPE_BL",
  7: "PIPE_BR",
  8: "COIN",
  9: "SPIKE",
  10: "GOAL",
  11: "CLOUD",
  12: "QUSED",
  13: "MAGMA",
  14: "GRASS",
  15: "FLAG",
  16: "ICE",
  17: "SAND",
  18: "BOUNCE",
  19: "THORN",
  20: "DARK_GR",
};

export const SOLID_BUILTIN = new Set<number>([1, 2, 3, 4, 5, 6, 7, 12, 14]);
export const PLATFORM_BUILTIN = new Set<number>([11]);
export const LETHAL_BUILTIN = new Set<number>([9, 13]);

export function behaviorOf(
  tileId: number,
  customBlocks: BlockDef[] = []
): BlockBehavior | "air" | "coin" | "goal" | "flag" {
  if (tileId === 0) return "air";
  if (tileId === 8) return "coin";
  if (tileId === 10) return "goal";
  if (tileId === 15) return "flag";
  if (SOLID_BUILTIN.has(tileId)) return "solid";
  if (PLATFORM_BUILTIN.has(tileId)) return "platform";
  if (LETHAL_BUILTIN.has(tileId)) return "lethal";
  const cb = customBlocks.find((b) => b.id === tileId);
  if (cb) return cb.behavior;
  return "passable";
}

// Render an 8x8 MONO_VLSB sprite to a Canvas (cell sized px*8 x px*8).
export function drawSprite(
  ctx: CanvasRenderingContext2D,
  sprite: number[],
  x: number,
  y: number,
  scale: number,
  fg = "#e5e7eb",
  bg = "transparent"
) {
  if (bg !== "transparent") {
    ctx.fillStyle = bg;
    ctx.fillRect(x, y, scale * 8, scale * 8);
  }
  ctx.fillStyle = fg;
  for (let col = 0; col < 8; col++) {
    const b = sprite[col] ?? 0;
    for (let row = 0; row < 8; row++) {
      if (b & (1 << row)) {
        ctx.fillRect(x + col * scale, y + row * scale, scale, scale);
      }
    }
  }
}

export function tileColor(tileId: number): string {
  // Quick color hints for the editor (AIR returns none).
  switch (tileId) {
    case 0: return "transparent";
    case 1: case 14: return "#a16207";       // ground / grass
    case 2: return "#92400e";                // brick
    case 3: return "#facc15";                // q-block
    case 12: return "#78716c";               // qused
    case 4: case 5: case 6: case 7: return "#22c55e"; // pipe
    case 8: return "#fde047";                // coin
    case 9: return "#ef4444";                // spike
    case 10: return "#a3e635";               // goal
    case 11: return "#cbd5e1";               // cloud
    case 13: return "#dc2626";               // magma
    case 15: return "#fb923c";               // flag
    case 16: return "#bae6fd";               // ice
    case 17: return "#fcd34d";               // sand
    case 18: return "#f472b6";               // bounce
    case 19: return "#ef4444";               // thorn
    case 20: return "#374151";               // dark gr
    default: return "#7c3aed";               // custom
  }
}
