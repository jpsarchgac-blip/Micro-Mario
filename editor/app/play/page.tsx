"use client";
import { useState } from "react";
import { useProject } from "@/lib/project-context";
import { Emulator } from "@/components/Emulator/Emulator";
import { GameCanvas } from "@/components/GamePlayer/GameCanvas";
import Link from "next/link";

type Mode = "emulator" | "preview";

export default function PlayPage() {
  const { project } = useProject();
  const [mode, setMode] = useState<Mode>("emulator");
  const [previewIdx, setPreviewIdx] = useState<number>(0);
  const previewStage = project.stages[previewIdx];

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Play</h1>
        <div className="flex gap-1 rounded-lg border border-gray-800 bg-panel p-1">
          <button
            onClick={() => setMode("emulator")}
            className={
              "rounded px-3 py-1.5 text-sm " +
              (mode === "emulator" ? "bg-accent text-black" : "text-gray-300 hover:bg-panel2")
            }
          >
            🕹️ EMULATOR
          </button>
          <button
            onClick={() => setMode("preview")}
            className={
              "rounded px-3 py-1.5 text-sm " +
              (mode === "preview" ? "bg-accent text-black" : "text-gray-300 hover:bg-panel2")
            }
          >
            🔬 STAGE PREVIEW
          </button>
        </div>
      </div>

      {mode === "emulator" && (
        <>
          <p className="text-sm text-gray-400">
            実機と同じフロー (タイトル → モード選択 → プレイ)。
            <strong className="text-accent">NEW MODE</strong> はビルトインステージ、
            <strong className="text-accent">CUSTOM MODE</strong> は Map Editor で作成したステージ、
            <strong className="text-accent">MUSIC MODE</strong> は BGM 再生ができます。
          </p>
          <Emulator />
        </>
      )}

      {mode === "preview" && (
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
                単体ステージのクイックプレビュー (カラー表示・物理のみ)。
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
