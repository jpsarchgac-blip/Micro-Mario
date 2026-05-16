"use client";
import { ENTITY_TYPES } from "@/lib/entities";

interface Props {
  selected: string | null;
  onSelect: (id: string | null) => void;
}

export function EntityPalette({ selected, onSelect }: Props) {
  return (
    <div className="space-y-2">
      <button
        onClick={() => onSelect(null)}
        className={
          "w-full rounded px-2 py-1 text-left text-xs " +
          (selected === null ? "bg-accent text-black" : "bg-panel2 hover:bg-gray-700")
        }
      >
        ▢ (none)
      </button>
      {ENTITY_TYPES.map((e) => (
        <button
          key={e.id}
          onClick={() => onSelect(e.id)}
          className={
            "flex w-full items-center gap-2 rounded px-2 py-1 text-left text-xs " +
            (selected === e.id ? "bg-accent text-black" : "bg-panel2 hover:bg-gray-700")
          }
        >
          <span
            className="inline-block h-3 w-3 rounded-sm"
            style={{ background: e.color }}
          />
          {e.label}
          <span className="ml-auto text-[9px] opacity-60">{e.category}</span>
        </button>
      ))}
    </div>
  );
}
