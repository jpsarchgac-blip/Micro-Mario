"use client";
import { Stage } from "@/lib/types";

interface Props {
  stage: Stage;
  bgmOptions: string[];
  onChange: (s: Stage) => void;
}

const BUILTIN_BGM = ["overworld", "underground", "water", "castle", "sky", "boss", "star", "ending", "fanfare"];

export function StageProperties({ stage, bgmOptions, onChange }: Props) {
  const update = <K extends keyof Stage>(k: K, v: Stage[K]) => onChange({ ...stage, [k]: v });

  const resize = (newWidth: number, newRows: number) => {
    const w = Math.max(8, Math.min(256, newWidth));
    const r = newRows === 8 || newRows === 12 || newRows === 16 ? newRows : stage.rows;
    const terrain: number[][] = [];
    for (let c = 0; c < w; c++) {
      const old = stage.terrain[c] ?? [];
      const col: number[] = Array(r).fill(0);
      // Anchor to bottom: keep bottom rows when shrinking, prepend zeros when expanding
      const minLen = Math.min(r, old.length);
      for (let i = 0; i < minLen; i++) {
        col[r - 1 - i] = old[old.length - 1 - i];
      }
      terrain.push(col);
    }
    onChange({ ...stage, width: w, rows: r, terrain });
  };

  return (
    <div className="space-y-2 text-sm">
      <label className="block">
        <span className="text-gray-400">Name</span>
        <input
          value={stage.name}
          onChange={(e) => update("name", e.target.value)}
          className="mt-1 w-full rounded bg-panel2 px-2 py-1.5 font-mono"
        />
      </label>
      <div className="grid grid-cols-2 gap-2">
        <label>
          <span className="text-gray-400">Width</span>
          <input
            type="number"
            min={8}
            max={256}
            value={stage.width}
            onChange={(e) => resize(parseInt(e.target.value) || 8, stage.rows)}
            className="mt-1 w-full rounded bg-panel2 px-2 py-1.5"
          />
        </label>
        <label>
          <span className="text-gray-400">Rows</span>
          <select
            value={stage.rows}
            onChange={(e) => resize(stage.width, parseInt(e.target.value))}
            className="mt-1 w-full rounded bg-panel2 px-2 py-1.5"
          >
            <option value={8}>8</option>
            <option value={12}>12</option>
            <option value={16}>16</option>
          </select>
        </label>
      </div>
      <div className="grid grid-cols-2 gap-2">
        <label>
          <span className="text-gray-400">Start Col</span>
          <input
            type="number"
            value={stage.start_col}
            onChange={(e) => update("start_col", parseInt(e.target.value) || 0)}
            className="mt-1 w-full rounded bg-panel2 px-2 py-1.5"
          />
        </label>
        <label>
          <span className="text-gray-400">Start Row</span>
          <input
            type="number"
            value={stage.start_row}
            onChange={(e) => update("start_row", parseInt(e.target.value) || 0)}
            className="mt-1 w-full rounded bg-panel2 px-2 py-1.5"
          />
        </label>
      </div>
      <div className="grid grid-cols-2 gap-2">
        <label>
          <span className="text-gray-400">Goal Col</span>
          <input
            type="number"
            value={stage.goal_col}
            onChange={(e) => update("goal_col", parseInt(e.target.value) || 0)}
            className="mt-1 w-full rounded bg-panel2 px-2 py-1.5"
          />
        </label>
        <label>
          <span className="text-gray-400">Flag Col</span>
          <input
            type="number"
            value={stage.flag_col ?? stage.goal_col}
            onChange={(e) => update("flag_col", parseInt(e.target.value) || 0)}
            className="mt-1 w-full rounded bg-panel2 px-2 py-1.5"
          />
        </label>
      </div>
      <div className="grid grid-cols-2 gap-2">
        <label>
          <span className="text-gray-400">Time Limit (s)</span>
          <input
            type="number"
            value={stage.time_limit}
            onChange={(e) => update("time_limit", parseInt(e.target.value) || 100)}
            className="mt-1 w-full rounded bg-panel2 px-2 py-1.5"
          />
        </label>
        <label>
          <span className="text-gray-400">Gravity Scale</span>
          <input
            type="number"
            step={0.1}
            value={stage.gravity_scale}
            onChange={(e) => update("gravity_scale", parseFloat(e.target.value) || 1.0)}
            className="mt-1 w-full rounded bg-panel2 px-2 py-1.5"
          />
        </label>
      </div>
      <label className="flex items-center gap-2">
        <input
          type="checkbox"
          checked={stage.water}
          onChange={(e) => update("water", e.target.checked)}
        />
        <span className="text-gray-300">Water Stage</span>
      </label>
      <label className="block">
        <span className="text-gray-400">BGM</span>
        <select
          value={stage.bgm}
          onChange={(e) => update("bgm", e.target.value)}
          className="mt-1 w-full rounded bg-panel2 px-2 py-1.5"
        >
          <optgroup label="Built-in">
            {BUILTIN_BGM.map((b) => <option key={b} value={b}>{b}</option>)}
          </optgroup>
          {bgmOptions.length > 0 && (
            <optgroup label="Custom">
              {bgmOptions.map((b) => <option key={b} value={b}>{b}</option>)}
            </optgroup>
          )}
        </select>
      </label>
    </div>
  );
}
