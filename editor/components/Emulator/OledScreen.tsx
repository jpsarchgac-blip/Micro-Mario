"use client";
import { forwardRef, ReactNode } from "react";

/** 128x64 OLED-style display, scaled up. Children draw into the inner canvas via ref. */
export const OledScreen = forwardRef<HTMLCanvasElement, { scale?: number; children?: ReactNode }>(
  function OledScreen({ scale = 4 }, ref) {
    return (
      <div className="inline-block rounded-2xl border-4 border-gray-800 bg-black p-2 shadow-2xl">
        <canvas
          ref={ref}
          width={128 * scale}
          height={64 * scale}
          className="pixel block"
          style={{ background: "#0a0a14" }}
        />
      </div>
    );
  }
);
