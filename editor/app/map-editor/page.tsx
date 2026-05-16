"use client";
import { useEffect, useState } from "react";
import { useProject } from "@/lib/project-context";
import { Stage } from "@/lib/types";
import { TilePalette } from "@/components/MapEditor/TilePalette";
import { EntityPalette } from "@/components/MapEditor/EntityPalette";
import { MapCanvas } from "@/components/MapEditor/MapCanvas";
import { StageProperties } from "@/components/MapEditor/StageProperties";
import Link from "next/link";

const newStage = (): Stage => {
  const rows = 12;
  const width = 48;
  const terrain: number[][] = [];
  for (let c = 0; c < width; c++) {
    const col = Array(rows).fill(0);
    col[rows - 1] = 1;
    col[rows - 2] = 1;
    terrain.push(col);
  }
  return {
    name: "NEW STAGE",
    bgm: "overworld",
    rows, width,
    terrain,
    time_limit: 100,
    water: false,
    gravity_scale: 1.0,
    start_col: 2,
    start_row: rows - 2,
    goal_col: width - 5,
    flag_col: width - 5,
    objects: [],
    enemy_sets: { easy: [], normal: [], hard: [] },
  };
};

type Tool = "paint" | "erase" | "entity" | "start" | "goal";
const TOOLS: { id: Tool; label: string }[] = [
  { id: "paint", label: "🖌️ Paint" },
  { id: "erase", label: "🧹 Erase" },
  { id: "entity", label: "👾 Entity" },
  { id: "start", label: "🚩 Start" },
  { id: "goal", label: "🏁 Goal" },
];

export default function MapEditor() {
  const { project, addStage, updateStage, deleteStage } = useProject();
  const [stageIdx, setStageIdx] = useState<number>(-1);
  const [tool, setTool] = useState<Tool>("paint");
  const [selectedTile, setSelectedTile] = useState<number>(1);
  const [selectedEntity, setSelectedEntity] = useState<string | null>("goomba");
  const [difficulty, setDifficulty] = useState<"easy" | "normal" | "hard">("normal");
  const [showJumpReach, setShowJumpReach] = useState(false);

  const stage = stageIdx >= 0 ? project.stages[stageIdx] : null;

  useEffect(() => {
    if (stageIdx >= project.stages.length) setStageIdx(-1);
  }, [project.stages.length, stageIdx]);

  const createStage = () => {
    const s = newStage();
    addStage(s);
    setStageIdx(project.stages.length);
  };

  const mutate = (s: Stage) => {
    if (stageIdx >= 0) updateStage(stageIdx, s);
  };

  return (
    <div className="grid grid-cols-1 gap-4 lg:grid-cols-[260px_1fr_260px]">
      {/* Left: stage list + tile palette */}
      <aside className="space-y-3">
        <section className="rounded-lg border border-gray-800 bg-panel p-3">
          <h2 className="mb-2 text-sm font-semibold">Stages</h2>
          <button
            onClick={createStage}
            className="mb-2 w-full rounded bg-accent2 px-2 py-1.5 text-sm font-semibold text-black hover:opacity-90"
          >
            + NEW STAGE
          </button>
          <div className="space-y-1">
            {project.stages.map((s, i) => (
              <div key={i} className="flex gap-1">
                <button
                  onClick={() => setStageIdx(i)}
                  className={
                    "flex-1 truncate rounded px-2 py-1 text-left text-xs " +
                    (stageIdx === i ? "bg-accent text-black" : "bg-panel2 hover:bg-gray-700")
                  }
                >
                  {i + 1}. {s.name}
                  <span className="block text-[9px] opacity-60">{s.width}×{s.rows}</span>
                </button>
                <button
                  onClick={() => {
                    if (confirm(`Delete "${s.name}"?`)) {
                      deleteStage(i);
                      if (stageIdx === i) setStageIdx(-1);
                    }
                  }}
                  className="rounded bg-danger/30 px-2 text-xs text-danger hover:bg-danger/50"
                >
                  ✕
                </button>
              </div>
            ))}
            {project.stages.length === 0 && (
              <p className="text-xs text-gray-500">ステージ未作成</p>
            )}
          </div>
        </section>
        <section className="rounded-lg border border-gray-800 bg-panel p-3">
          <h2 className="mb-2 text-sm font-semibold">Tiles</h2>
          <TilePalette
            customBlocks={project.blocks}
            selected={selectedTile}
            onSelect={(id) => { setSelectedTile(id); setTool("paint"); }}
          />
          <p className="mt-2 text-[10px] text-gray-500">
            カスタムブロックは <Link href="/block-editor" className="text-accent underline">Block Editor</Link> で作成
          </p>
        </section>
        <section className="rounded-lg border border-gray-800 bg-panel p-3">
          <h2 className="mb-2 text-sm font-semibold">Entities</h2>
          <EntityPalette selected={selectedEntity} onSelect={(id) => { setSelectedEntity(id); setTool("entity"); }} />
        </section>
      </aside>

      {/* Center: canvas + tool bar */}
      <section className="space-y-3">
        {stage ? (
          <>
            <div className="flex items-center gap-2 rounded-lg border border-gray-800 bg-panel p-2">
              {TOOLS.map((t) => (
                <button
                  key={t.id}
                  onClick={() => setTool(t.id)}
                  className={
                    "rounded px-3 py-1.5 text-sm " +
                    (tool === t.id ? "bg-accent text-black" : "bg-panel2 hover:bg-gray-700")
                  }
                >
                  {t.label}
                </button>
              ))}
              <div className="ml-auto flex items-center gap-2 text-xs">
                <label className="flex items-center gap-1">
                  <input type="checkbox" checked={showJumpReach} onChange={(e) => setShowJumpReach(e.target.checked)} />
                  Jump reach
                </label>
                <span className="text-gray-500">|</span>
                <span className="text-gray-400">Difficulty:</span>
                <select
                  value={difficulty}
                  onChange={(e) => setDifficulty(e.target.value as "easy" | "normal" | "hard")}
                  className="rounded bg-panel2 px-2 py-1"
                >
                  <option value="easy">easy</option>
                  <option value="normal">normal</option>
                  <option value="hard">hard</option>
                </select>
              </div>
            </div>

            <MapCanvas
              stage={stage}
              customBlocks={project.blocks}
              selectedTile={selectedTile}
              selectedEntity={selectedEntity}
              tool={tool}
              difficulty={difficulty}
              showJumpReach={showJumpReach}
              onMutate={mutate}
            />

            <p className="text-xs text-gray-500">
              💡 ドラッグで連続ペイント / Entity ツールは同じ位置クリックで削除 / Jump reach は hover タイルからのジャンプ到達範囲
            </p>
          </>
        ) : (
          <div className="rounded-lg border border-gray-800 bg-panel p-12 text-center">
            <p className="text-gray-400">
              左から「+ NEW STAGE」でステージを作成、または既存ステージを選択
            </p>
          </div>
        )}
      </section>

      {/* Right: stage properties */}
      <aside className="rounded-lg border border-gray-800 bg-panel p-3">
        <h2 className="mb-2 text-sm font-semibold">Properties</h2>
        {stage ? (
          <StageProperties
            stage={stage}
            bgmOptions={Object.keys(project.bgm)}
            onChange={mutate}
          />
        ) : (
          <p className="text-xs text-gray-500">ステージを選択してください</p>
        )}
      </aside>
    </div>
  );
}
