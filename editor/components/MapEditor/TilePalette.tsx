"use client";
import { useEffect, useRef } from "react";
import { BUILTIN_BLOCKS, BUILTIN_SPRITES, TILE_LABELS, drawSprite } from "@/lib/tiles";
import { BlockDef } from "@/lib/types";

interface Props {
  customBlocks: BlockDef[];
  selected: number;
  onSelect: (id: number) => void;
}

const BUILTIN_IDS = [
  0, 1, 2, 3, 8, 9, 11, 13, 14, 15, // common
  4, 5, 6, 7,                       // pipe
  10, 12,                           // goal/qused
];

export function TilePalette({ customBlocks, selected, onSelect }: Props) {
  return (
    <div className="space-y-3">
      <section>
        <h3 className="mb-2 text-xs font-semibold uppercase text-gray-400">Built-in</h3>
        <div className="grid grid-cols-5 gap-1">
          {BUILTIN_IDS.map((id) => (
            <TileButton key={id} id={id} selected={selected === id} onSelect={onSelect} />
          ))}
        </div>
      </section>
      <section>
        <h3 className="mb-2 text-xs font-semibold uppercase text-gray-400">Built-in Custom</h3>
        <div className="grid grid-cols-5 gap-1">
          {BUILTIN_BLOCKS.map((b) => (
            <TileButton key={b.id} id={b.id} selected={selected === b.id} onSelect={onSelect} />
          ))}
        </div>
      </section>
      {customBlocks.length > 0 && (
        <section>
          <h3 className="mb-2 text-xs font-semibold uppercase text-gray-400">Project Custom</h3>
          <div className="grid grid-cols-5 gap-1">
            {customBlocks.map((b) => (
              <TileButton
                key={b.id}
                id={b.id}
                customSprite={b.sprite}
                label={b.name.replace(/^tile_/, "")}
                selected={selected === b.id}
                onSelect={onSelect}
              />
            ))}
          </div>
        </section>
      )}
    </div>
  );
}

function TileButton({
  id,
  selected,
  onSelect,
  customSprite,
  label,
}: {
  id: number;
  selected: boolean;
  onSelect: (id: number) => void;
  customSprite?: number[];
  label?: string;
}) {
  const ref = useRef<HTMLCanvasElement>(null);
  useEffect(() => {
    const c = ref.current;
    if (!c) return;
    const ctx = c.getContext("2d");
    if (!ctx) return;
    ctx.fillStyle = "#0f0f12";
    ctx.fillRect(0, 0, c.width, c.height);
    const sprite = customSprite ?? BUILTIN_SPRITES[id];
    if (sprite) drawSprite(ctx, sprite, 0, 0, 3, "#e5e7eb");
    else if (id === 0) {
      ctx.strokeStyle = "#444";
      ctx.beginPath();
      ctx.moveTo(0, 0); ctx.lineTo(24, 24);
      ctx.moveTo(24, 0); ctx.lineTo(0, 24);
      ctx.stroke();
    }
  }, [id, customSprite]);

  return (
    <button
      onClick={() => onSelect(id)}
      title={`#${id} ${label ?? TILE_LABELS[id] ?? "TILE"}`}
      className={
        "flex flex-col items-center rounded p-1 transition " +
        (selected ? "bg-accent" : "bg-panel2 hover:bg-gray-700")
      }
    >
      <canvas
        ref={ref}
        width={24}
        height={24}
        className="pixel rounded"
      />
      <span className="mt-0.5 text-[9px] text-gray-300">{label ?? TILE_LABELS[id] ?? id}</span>
    </button>
  );
}
