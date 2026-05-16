"use client";
import { useState, useEffect } from "react";
import { useProject } from "@/lib/project-context";
import { PixelGrid } from "@/components/BlockEditor/PixelGrid";
import { SpritePreview } from "@/components/BlockEditor/SpritePreview";
import { BUILTIN_BLOCKS } from "@/lib/tiles";
import { BlockDef, BlockBehavior } from "@/lib/types";
import { bytesToHex } from "@/lib/persist";

const BEHAVIORS: BlockBehavior[] = ["solid", "platform", "lethal", "bounce", "ice", "passable"];
const BEHAVIOR_DESC: Record<BlockBehavior, string> = {
  solid: "4方向衝突 (床・壁・天井)",
  platform: "上から着地のみ (雲足場)",
  lethal: "接触で死亡 (トゲ・マグマ)",
  bounce: "着地でバネジャンプ (vy=-5.2)",
  ice: "氷上: しゃがみ減速無効",
  passable: "当たり判定なし (装飾)",
};

const blank8 = (): number[] => [0, 0, 0, 0, 0, 0, 0, 0];

export default function BlockEditor() {
  const { project, addBlock, updateBlock, deleteBlock } = useProject();
  const [selected, setSelected] = useState<number>(-1);
  const [draft, setDraft] = useState<BlockDef>({
    id: 21,
    name: "tile_custom_21",
    behavior: "solid",
    sprite: blank8(),
  });

  // Pick a free ID >= 21 (avoiding built-in 16-20)
  useEffect(() => {
    if (selected >= 0) {
      setDraft({ ...project.blocks[selected] });
    } else {
      const usedIds = new Set([
        ...BUILTIN_BLOCKS.map((b) => b.id),
        ...project.blocks.map((b) => b.id),
      ]);
      let nid = 21;
      while (usedIds.has(nid) && nid < 256) nid++;
      setDraft({
        id: nid,
        name: `tile_custom_${nid}`,
        behavior: "solid",
        sprite: blank8(),
      });
    }
  }, [selected, project.blocks]);

  const save = () => {
    if (selected >= 0) updateBlock(selected, draft);
    else {
      addBlock(draft);
      setSelected(-1);
    }
  };

  const clearPixels = () => setDraft({ ...draft, sprite: blank8() });
  const invert = () => setDraft({ ...draft, sprite: draft.sprite.map((b) => (~b) & 0xff) });
  const fillAll = () => setDraft({ ...draft, sprite: Array(8).fill(0xff) });

  return (
    <div className="grid grid-cols-1 gap-6 lg:grid-cols-[280px_1fr]">
      <aside className="space-y-4">
        <section className="rounded-lg border border-gray-800 bg-panel p-3">
          <h2 className="mb-2 text-sm font-semibold text-gray-300">Built-in (ID 0-20)</h2>
          <div className="grid grid-cols-5 gap-1">
            {BUILTIN_BLOCKS.map((b) => (
              <button
                key={b.id}
                title={`#${b.id} ${b.name}\n${b.behavior}`}
                className="flex flex-col items-center rounded bg-panel2 p-1 hover:bg-gray-700"
                onClick={() => setDraft({ ...b, id: b.id })}
              >
                <SpritePreview bytes={b.sprite} scale={3} />
                <span className="mt-1 text-[10px] text-gray-500">#{b.id}</span>
              </button>
            ))}
          </div>
          <p className="mt-2 text-[11px] text-gray-500">
            クリックで draft にコピー (ID は既存のままなので必要なら 21+ に変更)
          </p>
        </section>

        <section className="rounded-lg border border-gray-800 bg-panel p-3">
          <h2 className="mb-2 text-sm font-semibold text-gray-300">
            Custom ({project.blocks.length})
          </h2>
          <div className="space-y-1">
            <button
              onClick={() => setSelected(-1)}
              className={
                "w-full rounded px-2 py-1 text-left text-sm " +
                (selected === -1 ? "bg-accent text-black" : "bg-panel2 hover:bg-gray-700")
              }
            >
              + NEW BLOCK
            </button>
            {project.blocks.map((b, i) => (
              <div key={b.id} className="flex items-center gap-2">
                <button
                  onClick={() => setSelected(i)}
                  className={
                    "flex flex-1 items-center gap-2 rounded px-2 py-1 text-left text-sm " +
                    (selected === i ? "bg-accent text-black" : "bg-panel2 hover:bg-gray-700")
                  }
                >
                  <SpritePreview bytes={b.sprite} scale={2} />
                  <span>
                    #{b.id} {b.name}
                  </span>
                </button>
                <button
                  onClick={() => {
                    if (confirm(`Delete block #${b.id} ${b.name}?`)) {
                      deleteBlock(i);
                      if (selected === i) setSelected(-1);
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
      </aside>

      <section className="rounded-lg border border-gray-800 bg-panel p-4">
        <div className="mb-4 flex items-center justify-between">
          <h1 className="text-lg font-semibold">
            {selected >= 0 ? `Edit Block #${draft.id}` : "New Custom Block"}
          </h1>
          <button
            onClick={save}
            className="rounded bg-accent2 px-4 py-1.5 font-semibold text-black hover:opacity-90"
          >
            {selected >= 0 ? "Update" : "Add Block"}
          </button>
        </div>

        <div className="grid grid-cols-1 gap-6 md:grid-cols-[auto_1fr]">
          <div>
            <div className="text-xs text-gray-400">Editor (click/drag to toggle)</div>
            <div className="mt-1">
              <PixelGrid bytes={draft.sprite} onChange={(s) => setDraft({ ...draft, sprite: s })} />
            </div>
            <div className="mt-2 flex gap-2 text-xs">
              <button className="rounded bg-panel2 px-2 py-1 hover:bg-gray-700" onClick={clearPixels}>
                Clear
              </button>
              <button className="rounded bg-panel2 px-2 py-1 hover:bg-gray-700" onClick={invert}>
                Invert
              </button>
              <button className="rounded bg-panel2 px-2 py-1 hover:bg-gray-700" onClick={fillAll}>
                Fill
              </button>
            </div>
            <div className="mt-3 text-xs text-gray-400">Preview (in-game scale)</div>
            <div className="mt-1 flex items-center gap-3">
              <SpritePreview bytes={draft.sprite} scale={1} />
              <SpritePreview bytes={draft.sprite} scale={2} />
              <SpritePreview bytes={draft.sprite} scale={4} />
            </div>
          </div>

          <div className="space-y-3">
            <label className="block text-sm">
              <span className="text-gray-400">Tile ID (16-255)</span>
              <input
                type="number"
                min={16}
                max={255}
                value={draft.id}
                onChange={(e) => setDraft({ ...draft, id: Math.max(16, Math.min(255, +e.target.value || 16)) })}
                className="mt-1 w-full rounded bg-panel2 px-2 py-1.5"
              />
            </label>
            <label className="block text-sm">
              <span className="text-gray-400">Sprite Name (Python identifier)</span>
              <input
                type="text"
                value={draft.name}
                onChange={(e) => setDraft({ ...draft, name: e.target.value })}
                className="mt-1 w-full rounded bg-panel2 px-2 py-1.5 font-mono"
              />
            </label>
            <div>
              <div className="text-sm text-gray-400">Behavior</div>
              <div className="mt-2 grid grid-cols-2 gap-2">
                {BEHAVIORS.map((b) => (
                  <button
                    key={b}
                    onClick={() => setDraft({ ...draft, behavior: b })}
                    className={
                      "rounded border p-2 text-left text-xs " +
                      (draft.behavior === b
                        ? "border-accent bg-accent/10 text-accent"
                        : "border-gray-700 bg-panel2 hover:border-gray-500")
                    }
                  >
                    <div className="font-semibold uppercase">{b}</div>
                    <div className="mt-0.5 text-gray-400">{BEHAVIOR_DESC[b]}</div>
                  </button>
                ))}
              </div>
            </div>

            <div>
              <div className="text-sm text-gray-400">Bytes (MONO_VLSB)</div>
              <code className="mt-1 block break-all rounded bg-black px-2 py-1.5 text-xs text-accent">
                bytes([
                {draft.sprite.map((b) => "0x" + b.toString(16).toUpperCase().padStart(2, "0")).join(", ")}
                ])
              </code>
              <code className="mt-1 block break-all rounded bg-black px-2 py-1.5 text-xs text-gray-400">
                hex: {bytesToHex(draft.sprite)}
              </code>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
