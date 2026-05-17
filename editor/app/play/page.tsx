"use client";
import { useState } from "react";
import { useProject } from "@/lib/project-context";
import { PyodideEmulator } from "@/components/Emulator/PyodideEmulator";
import { Emulator } from "@/components/Emulator/Emulator";
import { GameCanvas } from "@/components/GamePlayer/GameCanvas";
import Link from "next/link";

type Mode = "real" | "preview" | "stage";

export default function PlayPage() {
  const { project } = useProject();
  const [mode, setMode] = useState<Mode>("real");
  const [previewIdx, setPreviewIdx] = useState<number>(0);
  const previewStage = project.stages[previewIdx];

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Play</h1>
        <div className="flex gap-1 rounded-lg border border-gray-800 bg-panel p-1">
          <ModeBtn active={mode === "real"} onClick={() => setMode("real")}>
            🎮 REAL (Pyodide)
          </ModeBtn>
          <ModeBtn active={mode === "preview"} onClick={() => setMode("preview")}>
            🕹️ EMULATOR (TS)
          </ModeBtn>
          <ModeBtn active={mode === "stage"} onClick={() => setMode("stage")}>
            🔬 STAGE PREVIEW
          </ModeBtn>
        </div>
      </div>

      {mode === "real" && (
        <>
          <p className="text-sm text-gray-400">
            <strong className="text-accent">実機の Python ソースをそのまま実行</strong>します。
            <code className="ml-1 rounded bg-panel2 px-1.5 py-0.5">player.py</code>{" "}
            <code className="rounded bg-panel2 px-1.5 py-0.5">game_new.py</code>{" "}
            <code className="rounded bg-panel2 px-1.5 py-0.5">music.py</code>{" "}
            等が Pyodide (WASM Python) で動き、ブラウザは OLED/SW/PWM/LED だけをエミュレートします。
          </p>
          <PyodideEmulator />
        </>
      )}

      {mode === "preview" && (
        <>
          <p className="text-sm text-gray-400">
            軽量版 (TypeScript 物理ミラー)。Pyodide 不要で即起動。物理は本物に近いがスプライト等は簡易表示。
          </p>
          <Emulator />
        </>
      )}

      {mode === "stage" && (
        <>
          {project.stages.length === 0 ? (
            <div className="rounded-lg border border-gray-800 bg-panel p-12 text-center">
              <p className="text-gray-400">
                <Link href="/map-editor" className="text-accent underline">Map Editor</Link>
                {" "}でステージを作成してください
              </p>
            </div>
          ) : (
            <>
              <p className="text-sm text-gray-400">
                単体ステージのカラー版クイックプレビュー。
              </p>
              <div className="flex flex-wrap gap-2">
                {project.stages.map((s, i) => (
                  <button
                    key={i}
                    onClick={() => setPreviewIdx(i)}
                    className={
                      "rounded px-3 py-1.5 text-sm " +
                      (previewIdx === i ? "bg-accent text-black" : "bg-panel2 hover:bg-gray-700")
                    }
                  >
                    {i + 1}. {s.name}
                  </button>
                ))}
              </div>
              {previewStage && (
                <GameCanvas
                  stage={previewStage}
                  customBlocks={project.blocks}
                  bgmTrack={project.bgm[previewStage.bgm]}
                />
              )}
            </>
          )}
        </>
      )}
    </div>
  );
}

function ModeBtn({
  active,
  onClick,
  children,
}: {
  active: boolean;
  onClick: () => void;
  children: React.ReactNode;
}) {
  return (
    <button
      onClick={onClick}
      className={
        "rounded px-3 py-1.5 text-sm " +
        (active ? "bg-accent text-black" : "text-gray-300 hover:bg-panel2")
      }
    >
      {children}
    </button>
  );
}
