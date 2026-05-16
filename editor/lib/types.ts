// Shared types for the Micro-Mario custom editor.
// JSON shape mirrors custom_stages.py / docs/MAP_GUIDE.md

export type BlockBehavior = "solid" | "platform" | "lethal" | "passable" | "bounce" | "ice";

export interface BlockDef {
  /** Tile ID (16..255 for custom blocks; 0..15 are built-in). */
  id: number;
  /** Sprite key registered into SpriteBank, e.g. "tile_ice". */
  name: string;
  behavior: BlockBehavior;
  /** 8 bytes, MONO_VLSB (1 byte = 8 vertical px, LSB = top). */
  sprite: number[];
}

/** Note entry: [pitch (name like "C5" or raw Hz), duration ms]. */
export type NoteEntry = [string | number, number];

export type BgmTrack = NoteEntry[];

export type EnemySet = Array<[number, number, string]>; // (col, row, type)

export interface Stage {
  name: string;
  bgm: string;
  rows: number;            // 8 | 12 | 16
  width: number;           // typically 32..128
  /** terrain[col][row] = tileId (0..255) */
  terrain: number[][];
  time_limit: number;
  water: boolean;
  gravity_scale: number;
  start_col: number;
  start_row: number;
  goal_col: number;
  flag_col?: number;
  pipe_col?: number;
  pipe_return_col?: number;
  objects: Array<[number, number, string]>;
  enemy_sets: {
    easy?: EnemySet;
    normal?: EnemySet;
    hard?: EnemySet;
  };
}

export interface CustomProject {
  version: number;
  blocks: BlockDef[];
  bgm: Record<string, BgmTrack>;
  stages: Stage[];
}

export const PROJECT_VERSION = 1;

export const newProject = (): CustomProject => ({
  version: PROJECT_VERSION,
  blocks: [],
  bgm: {},
  stages: [],
});
