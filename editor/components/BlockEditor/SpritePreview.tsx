"use client";
import { useEffect, useRef } from "react";
import { drawSprite } from "@/lib/tiles";

export function SpritePreview({ bytes, scale = 4 }: { bytes: number[]; scale?: number }) {
  const ref = useRef<HTMLCanvasElement>(null);
  useEffect(() => {
    const c = ref.current;
    if (!c) return;
    const ctx = c.getContext("2d");
    if (!ctx) return;
    ctx.clearRect(0, 0, c.width, c.height);
    drawSprite(ctx, bytes, 0, 0, scale, "#e5e7eb", "#0f0f12");
  }, [bytes, scale]);
  return (
    <canvas
      ref={ref}
      width={8 * scale}
      height={8 * scale}
      className="pixel rounded border border-gray-700"
    />
  );
}
