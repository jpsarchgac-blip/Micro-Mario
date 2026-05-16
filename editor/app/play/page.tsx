"use client";
import { useState } from "react";
import { useProject } from "@/lib/project-context";
import { GameCanvas } from "@/components/GamePlayer/GameCanvas";
import Link from "next/link";

export default function PlayPage() {
  const { project } = useProject();
  const [idx, setIdx] = useState<number>(0);
  const stage = project.stages[idx];

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">Test Play</h1>

      {project.stages.length === 0 ? (
        <div className="rounded-lg border border-gray-800 bg-panel p-12 text-center">
          <p className="text-gray-400">
            まずは <Link href="/map-editor" className="text-accent underline">Map Editor</Link> でステージを作成してください
          </p>
        </div>
      ) : (
        <>
          <div className="flex flex-wrap gap-2">
            {project.stages.map((s, i) => (
              <button
                key={i}
                onClick={() => setIdx(i)}
                className={
                  "rounded px-3 py-1.5 text-sm " +
                  (idx === i ? "bg-accent text-black" : "bg-panel2 hover:bg-gray-700")
                }
              >
                {i + 1}. {s.name}
              </button>
            ))}
          </div>

          {stage && (
            <GameCanvas
              stage={stage}
              customBlocks={project.blocks}
              bgmTrack={project.bgm[stage.bgm]}
            />
          )}

          <div className="rounded-lg border border-gray-800 bg-panel p-3 text-xs text-gray-400">
            <p className="font-semibold text-gray-300">注意:</p>
            <ul className="mt-1 list-disc space-y-0.5 pl-5">
              <li>このプレビューは <code>player.py</code> の物理を TypeScript にミラーしたもの</li>
              <li>敵AIや踏みつけ判定、ファイア・パワーアップ・スター無敵などはまだ未実装(表示のみ)</li>
              <li>地形・ジャンプ感覚・落下死・致死タイル・ゴール判定は本物どおり</li>
              <li>正式な動作確認は Pico 実機 + <code>custom.dat</code> 配置で行ってください</li>
            </ul>
          </div>
        </>
      )}
    </div>
  );
}
