// Loader for the extracted stages_new.py JSON.
// Run `python3 tools/extract_stages.py` to regenerate editor/public/builtin-stages.json
import { Stage } from "./types";

let cache: { stages: Stage[]; pipeSubstage: Stage | null } | null = null;

interface RawStage {
  name?: string;
  bgm?: string;
  rows?: number;
  width?: number;
  terrain: number[][];
  time_limit?: number;
  water?: boolean;
  gravity_scale?: number;
  start_col?: number;
  start_row?: number;
  goal_col?: number;
  flag_col?: number | null;
  pipe_col?: number | null;
  pipe_return_col?: number | null;
  objects?: Array<[number, number, string]>;
  enemy_sets?: { easy?: any[]; normal?: any[]; hard?: any[] };
}

function normalize(s: RawStage): Stage {
  return {
    name: s.name ?? "STAGE",
    bgm: s.bgm ?? "overworld",
    rows: s.rows ?? 12,
    width: s.width ?? s.terrain.length,
    terrain: s.terrain,
    time_limit: s.time_limit ?? 100,
    water: s.water ?? false,
    gravity_scale: s.gravity_scale ?? 1.0,
    start_col: s.start_col ?? 2,
    start_row: s.start_row ?? (s.rows ?? 12) - 4,
    goal_col: s.goal_col ?? -1,
    flag_col: s.flag_col ?? undefined,
    pipe_col: s.pipe_col ?? undefined,
    pipe_return_col: s.pipe_return_col ?? undefined,
    objects: s.objects ?? [],
    enemy_sets: s.enemy_sets ?? {},
  };
}

export async function loadBuiltinStages(): Promise<{
  stages: Stage[];
  pipeSubstage: Stage | null;
}> {
  if (cache) return cache;
  try {
    const r = await fetch("/builtin-stages.json");
    if (!r.ok) throw new Error(`fetch failed: ${r.status}`);
    const json = (await r.json()) as { stages: RawStage[]; pipe_substage?: RawStage };
    cache = {
      stages: json.stages.map(normalize),
      pipeSubstage: json.pipe_substage ? normalize(json.pipe_substage) : null,
    };
    return cache;
  } catch (e) {
    console.error("loadBuiltinStages failed:", e);
    cache = { stages: [], pipeSubstage: null };
    return cache;
  }
}
