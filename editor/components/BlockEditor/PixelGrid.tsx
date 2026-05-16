"use client";
import { useCallback, useRef } from "react";

interface Props {
  bytes: number[]; // 8 bytes
  onChange: (bytes: number[]) => void;
  scale?: number;
}

/** 8x8 MONO_VLSB pixel grid editor. */
export function PixelGrid({ bytes, onChange, scale = 28 }: Props) {
  const dragMode = useRef<0 | 1 | null>(null);

  const togglePixel = useCallback(
    (col: number, row: number, set?: 0 | 1) => {
      const b = [...bytes];
      while (b.length < 8) b.push(0);
      const cur = (b[col] >> row) & 1;
      const next = set ?? (cur ? 0 : 1);
      b[col] = next
        ? b[col] | (1 << row)
        : b[col] & ~(1 << row);
      onChange(b);
    },
    [bytes, onChange]
  );

  const handleDown = (col: number, row: number) => {
    const cur = (bytes[col] >> row) & 1;
    dragMode.current = cur ? 0 : 1;
    togglePixel(col, row, dragMode.current);
  };

  const handleEnter = (col: number, row: number) => {
    if (dragMode.current === null) return;
    togglePixel(col, row, dragMode.current);
  };

  const handleUp = () => {
    dragMode.current = null;
  };

  return (
    <div
      className="inline-block select-none rounded border border-gray-700 bg-black"
      style={{ width: scale * 8 + 2, height: scale * 8 + 2 }}
      onMouseUp={handleUp}
      onMouseLeave={handleUp}
    >
      <div className="grid grid-cols-8" style={{ gap: 1 }}>
        {Array.from({ length: 8 }, (_, row) =>
          Array.from({ length: 8 }, (_, col) => {
            const on = ((bytes[col] ?? 0) >> row) & 1;
            return (
              <div
                key={`${col}-${row}`}
                onMouseDown={() => handleDown(col, row)}
                onMouseEnter={() => handleEnter(col, row)}
                style={{
                  width: scale - 1,
                  height: scale - 1,
                  background: on ? "#fef3c7" : "#1f2937",
                }}
                className="cursor-pointer"
              />
            );
          })
        )}
      </div>
    </div>
  );
}
