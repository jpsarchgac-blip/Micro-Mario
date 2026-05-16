"use client";
import { useEffect, useState } from "react";
import { useProject } from "@/lib/project-context";
import { NoteGrid } from "@/components/BgmComposer/NoteGrid";
import { BgmTrack } from "@/lib/types";
import { playBgm, stopBgm } from "@/lib/audio";

const PRESETS: Array<{ name: string; track: BgmTrack }> = [
  {
    name: "C major scale",
    track: [
      ["C5", 200], ["D5", 200], ["E5", 200], ["F5", 200],
      ["G5", 200], ["A5", 200], ["B5", 200], ["C6", 400],
    ],
  },
  {
    name: "Arpeggio loop",
    track: [
      ["C5", 150], ["E5", 150], ["G5", 150], ["C6", 150],
      ["G5", 150], ["E5", 150], ["C5", 300], ["-", 200],
    ],
  },
];

export default function BgmComposer() {
  const { project, setBgm, deleteBgm } = useProject();
  const [name, setName] = useState<string>("");
  const [stepDur, setStepDur] = useState<number>(200);
  const [playing, setPlaying] = useState(false);

  const trackNames = Object.keys(project.bgm);
  const currentTrack: BgmTrack = (name && project.bgm[name]) || [];

  useEffect(() => {
    if (!name && trackNames.length) setName(trackNames[0]);
  }, [trackNames, name]);

  const newTrack = () => {
    let nm = prompt("Track name (Python-safe identifier):", `track_${trackNames.length + 1}`);
    if (!nm) return;
    nm = nm.trim();
    if (project.bgm[nm]) {
      alert("Name already exists");
      return;
    }
    setBgm(nm, []);
    setName(nm);
  };

  const updateCurrent = (t: BgmTrack) => {
    if (!name) return;
    setBgm(name, t);
  };

  const onPlay = () => {
    if (!currentTrack.length) return;
    playBgm(currentTrack, { loop: true });
    setPlaying(true);
  };

  const onStop = () => {
    stopBgm();
    setPlaying(false);
  };

  useEffect(() => () => stopBgm(), []);

  const totalMs = currentTrack.reduce((a, [, d]) => a + d, 0);

  return (
    <div className="grid grid-cols-1 gap-6 lg:grid-cols-[260px_1fr]">
      <aside className="space-y-4">
        <section className="rounded-lg border border-gray-800 bg-panel p-3">
          <h2 className="mb-2 text-sm font-semibold text-gray-300">Tracks</h2>
          <button
            onClick={newTrack}
            className="mb-2 w-full rounded bg-accent2 px-2 py-1.5 text-sm font-semibold text-black hover:opacity-90"
          >
            + NEW TRACK
          </button>
          <div className="space-y-1">
            {trackNames.length === 0 && (
              <p className="text-xs text-gray-500">まだトラックがありません</p>
            )}
            {trackNames.map((nm) => (
              <div key={nm} className="flex items-center gap-1">
                <button
                  onClick={() => setName(nm)}
                  className={
                    "flex-1 truncate rounded px-2 py-1 text-left text-sm " +
                    (name === nm
                      ? "bg-accent text-black"
                      : "bg-panel2 hover:bg-gray-700")
                  }
                >
                  🎵 {nm}
                  <span className="ml-1 text-[10px] opacity-70">
                    ({project.bgm[nm].length})
                  </span>
                </button>
                <button
                  onClick={() => {
                    if (confirm(`Delete BGM "${nm}"?`)) {
                      deleteBgm(nm);
                      if (name === nm) setName("");
                    }
                  }}
                  className="rounded bg-danger/30 px-2 py-1 text-xs text-danger hover:bg-danger/50"
                >
                  ✕
                </button>
              </div>
            ))}
          </div>
        </section>

        <section className="rounded-lg border border-gray-800 bg-panel p-3">
          <h2 className="mb-2 text-sm font-semibold text-gray-300">Presets</h2>
          <div className="space-y-1">
            {PRESETS.map((p) => (
              <button
                key={p.name}
                onClick={() => name && updateCurrent(p.track)}
                disabled={!name}
                className="w-full rounded bg-panel2 px-2 py-1 text-left text-xs hover:bg-gray-700 disabled:opacity-50"
              >
                Load: {p.name}
              </button>
            ))}
          </div>
          <p className="mt-2 text-[10px] text-gray-500">
            選択中トラックを上書きします
          </p>
        </section>
      </aside>

      <section className="space-y-4">
        <div className="flex items-center gap-3 rounded-lg border border-gray-800 bg-panel p-3">
          <div className="flex-1">
            <div className="text-xs text-gray-400">Selected Track</div>
            <div className="text-lg font-semibold">{name || "(none)"}</div>
            <div className="text-xs text-gray-500">
              {currentTrack.length} notes / {(totalMs / 1000).toFixed(1)} s
            </div>
          </div>
          <label className="text-xs">
            <span className="text-gray-400">Default duration</span>
            <input
              type="number"
              min={20}
              step={20}
              value={stepDur}
              onChange={(e) => setStepDur(parseInt(e.target.value) || 200)}
              className="ml-2 w-20 rounded bg-panel2 px-2 py-1"
            />
            <span className="ml-1 text-gray-500">ms</span>
          </label>
          {!playing ? (
            <button
              onClick={onPlay}
              disabled={!currentTrack.length}
              className="rounded bg-accent2 px-4 py-2 text-sm font-semibold text-black hover:opacity-90 disabled:opacity-50"
            >
              ▶ Play (loop)
            </button>
          ) : (
            <button
              onClick={onStop}
              className="rounded bg-danger px-4 py-2 text-sm font-semibold text-white hover:opacity-90"
            >
              ■ Stop
            </button>
          )}
        </div>

        {name ? (
          <NoteGrid track={currentTrack} onChange={updateCurrent} stepDur={stepDur} />
        ) : (
          <div className="rounded-lg border border-gray-800 bg-panel p-12 text-center text-gray-400">
            左から「+ NEW TRACK」でトラックを作成してください
          </div>
        )}

        <details className="rounded-lg border border-gray-800 bg-panel p-3 text-sm">
          <summary className="cursor-pointer font-semibold text-gray-300">使い方</summary>
          <ul className="mt-2 list-disc space-y-1 pl-5 text-gray-400">
            <li>音名(C5, D5...)の縦軸 × 時間(列)の横軸。セルをクリックで音を配置</li>
            <li>各列の下にあるテキストボックスで個別の音の長さ(ms)を編集</li>
            <li>「+」=その位置に休符列を挿入 / 「✕」=その列を削除</li>
            <li>BPM 75 ≒ 200ms/拍。アクション=120ms、ホラー=300ms 推奨</li>
            <li>PWM 1ch のため和音不可。メロディラインのみ</li>
          </ul>
        </details>
      </section>
    </div>
  );
}
