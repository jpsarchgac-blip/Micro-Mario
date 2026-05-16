// LocalStorage persistence + JSON export/import for CustomProject.
import { CustomProject, PROJECT_VERSION, newProject } from "./types";

const KEY = "micro-mario:project:v1";

export function loadProject(): CustomProject {
  if (typeof window === "undefined") return newProject();
  try {
    const raw = localStorage.getItem(KEY);
    if (!raw) return newProject();
    const parsed = JSON.parse(raw) as CustomProject;
    if (!parsed.version || parsed.version > PROJECT_VERSION) return newProject();
    return {
      version: PROJECT_VERSION,
      blocks: parsed.blocks ?? [],
      bgm: parsed.bgm ?? {},
      stages: parsed.stages ?? [],
    };
  } catch (e) {
    console.error("loadProject failed", e);
    return newProject();
  }
}

export function saveProject(p: CustomProject) {
  if (typeof window === "undefined") return;
  try {
    localStorage.setItem(KEY, JSON.stringify(p));
  } catch (e) {
    console.error("saveProject failed", e);
  }
}

/** Convert in-memory CustomProject to the JSON shape expected by custom_stages.py. */
export function toCustomDatJson(p: CustomProject): unknown {
  return {
    blocks: p.blocks.map((b) => ({
      id: b.id,
      name: b.name,
      behavior: b.behavior,
      sprite: bytesToHex(b.sprite),
    })),
    bgm: p.bgm,
    stages: p.stages.map((s) => ({
      name: s.name,
      bgm: s.bgm,
      rows: s.rows,
      width: s.width,
      time_limit: s.time_limit,
      water: s.water,
      gravity_scale: s.gravity_scale,
      start_col: s.start_col,
      start_row: s.start_row,
      goal_col: s.goal_col,
      flag_col: s.flag_col,
      pipe_col: s.pipe_col,
      pipe_return_col: s.pipe_return_col,
      terrain: encodeTerrain(s.terrain, s.rows),
      objects: s.objects,
      enemy_sets: s.enemy_sets,
    })),
  };
}

/** Encode terrain[col][row] as list of column strings.
 *  Uses 1-hex/tile if all IDs <= 15, else 2-hex/tile (matches _parse_col fmt). */
export function encodeTerrain(terrain: number[][], rows: number): string[] {
  const max = terrain.reduce(
    (m, col) => col.reduce((a, v) => Math.max(a, v), m),
    0
  );
  const wide = max > 15;
  return terrain.map((col) => {
    const padded = col.length < rows ? [...Array(rows - col.length).fill(0), ...col] : col;
    if (wide) {
      return padded
        .map((v) => v.toString(16).toUpperCase().padStart(2, "0"))
        .join("");
    }
    return padded.map((v) => v.toString(16).toUpperCase()).join("");
  });
}

export function bytesToHex(bytes: number[]): string {
  return bytes.map((b) => b.toString(16).toUpperCase().padStart(2, "0")).join("");
}

export function hexToBytes(hex: string): number[] {
  const out: number[] = [];
  for (let i = 0; i + 1 < hex.length; i += 2) {
    out.push(parseInt(hex.substr(i, 2), 16));
  }
  return out;
}

/** Trigger a browser file download. */
export function downloadJson(data: unknown, filename: string) {
  const blob = new Blob([JSON.stringify(data, null, 2)], {
    type: "application/json",
  });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

export async function readJsonFile(file: File): Promise<unknown> {
  const text = await file.text();
  return JSON.parse(text);
}
