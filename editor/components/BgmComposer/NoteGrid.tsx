"use client";
import { useEffect, useRef, useState } from "react";
import { NOTE_ROWS } from "@/lib/notes";
import { BgmTrack, NoteEntry } from "@/lib/types";
import { beepNote } from "@/lib/audio";

interface Props {
  track: BgmTrack;
  onChange: (t: BgmTrack) => void;
  stepDur: number; // default duration ms for newly placed notes
}

const ROW_H = 12;
const COL_W = 24;

export function NoteGrid({ track, onChange, stepDur }: Props) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [hover, setHover] = useState<{ col: number; row: number } | null>(null);

  const rows = [...NOTE_ROWS].reverse(); // top = highest pitch

  // Toggle / set the note at column = position index in track
  const setNoteAt = (idx: number, pitch: string) => {
    const next = [...track];
    while (next.length <= idx) next.push(["-", stepDur]);
    next[idx] = [pitch, next[idx][1] ?? stepDur];
    onChange(next);
    if (pitch !== "-") beepNote(pitch, 80);
  };

  const setDurAt = (idx: number, d: number) => {
    const next = [...track];
    while (next.length <= idx) next.push(["-", stepDur]);
    next[idx] = [next[idx][0], d];
    onChange(next);
  };

  const removeAt = (idx: number) => {
    const next = track.filter((_, i) => i !== idx);
    onChange(next);
  };

  const insertAt = (idx: number) => {
    const next = [...track];
    next.splice(idx, 0, ["-", stepDur] as NoteEntry);
    onChange(next);
  };

  const totalCols = Math.max(32, track.length + 4);

  // Scroll horizontally on wheel deltaY
  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;
    const onWheel = (e: WheelEvent) => {
      if (e.shiftKey || Math.abs(e.deltaY) < Math.abs(e.deltaX)) return;
      el.scrollLeft += e.deltaY;
      e.preventDefault();
    };
    el.addEventListener("wheel", onWheel, { passive: false });
    return () => el.removeEventListener("wheel", onWheel);
  }, []);

  return (
    <div className="rounded border border-gray-800 bg-black">
      <div
        ref={containerRef}
        className="relative overflow-auto"
        style={{ maxHeight: 520 }}
      >
        <table style={{ borderCollapse: "collapse" }}>
          <tbody>
            {rows.map((pitch, ri) => (
              <tr key={pitch} style={{ height: ROW_H }}>
                <td
                  className="sticky left-0 z-10 border-b border-r border-gray-800 bg-panel px-2 text-[10px] font-mono text-gray-400"
                  style={{ width: 44, textAlign: "right" }}
                >
                  {pitch}
                </td>
                {Array.from({ length: totalCols }).map((_, ci) => {
                  const cur = track[ci];
                  const active = cur && cur[0] === pitch;
                  const isHover = hover?.col === ci && hover?.row === ri;
                  const isBlack = pitch.endsWith("s");
                  return (
                    <td
                      key={ci}
                      style={{
                        width: COL_W,
                        height: ROW_H,
                        background: active
                          ? "#facc15"
                          : isHover
                          ? "#374151"
                          : isBlack
                          ? "#111"
                          : "#1a1a20",
                        borderRight: ci % 4 === 3 ? "1px solid #333" : "1px solid #222",
                        borderBottom: "1px solid #222",
                        cursor: "pointer",
                      }}
                      onMouseEnter={() => setHover({ col: ci, row: ri })}
                      onMouseLeave={() => setHover(null)}
                      onClick={() => setNoteAt(ci, pitch)}
                      title={`Col ${ci} ${pitch}`}
                    />
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>

        {/* Duration row below grid */}
        <div className="flex bg-panel" style={{ paddingLeft: 44 }}>
          {Array.from({ length: totalCols }).map((_, ci) => (
            <div
              key={ci}
              style={{ width: COL_W }}
              className="border-r border-gray-800 px-0.5 py-1"
            >
              <input
                type="number"
                min={20}
                max={2000}
                step={20}
                value={track[ci]?.[1] ?? ""}
                placeholder="-"
                onChange={(e) => setDurAt(ci, parseInt(e.target.value) || stepDur)}
                className="w-full bg-transparent text-center text-[9px] text-gray-400 outline-none"
              />
              <div className="flex gap-0.5">
                <button
                  onClick={() => insertAt(ci)}
                  className="flex-1 rounded bg-panel2 text-[8px] text-gray-400 hover:bg-gray-700"
                  title="Insert before"
                >
                  +
                </button>
                <button
                  onClick={() => removeAt(ci)}
                  className="flex-1 rounded bg-panel2 text-[8px] text-danger hover:bg-gray-700"
                  title="Delete this column"
                >
                  ✕
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
