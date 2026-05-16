"use client";
import { useEffect, useRef, useState } from "react";
import {
  BUILTIN_SPRITES,
  drawSprite,
  tileColor,
} from "@/lib/tiles";
import { entityColor } from "@/lib/entities";
import { BlockDef, Stage } from "@/lib/types";
import {
  Input,
  PlayerState,
  TILE,
  createPlayer,
  stepPlayer,
} from "@/lib/physics";
import { playBgm, stopBgm } from "@/lib/audio";

interface Props {
  stage: Stage;
  customBlocks: BlockDef[];
  bgmTrack?: import("@/lib/types").BgmTrack;
}

const SCREEN_W = 128;
const SCREEN_H = 64;
const VIEW_SCALE = 4; // display each game pixel as 4 screen pixels

export function GameCanvas({ stage, customBlocks, bgmTrack }: Props) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [running, setRunning] = useState(false);
  const [status, setStatus] = useState<string>("READY");
  const playerRef = useRef<PlayerState | null>(null);
  const inputRef = useRef<Input>({
    jumpHeld: false,
    jumpPressed: false,
    duckHeld: false,
    dashHeld: false,
  });
  const keyDownRef = useRef<Set<string>>(new Set());

  const start = () => {
    playerRef.current = createPlayer(stage);
    setStatus("PLAYING");
    setRunning(true);
    if (bgmTrack && bgmTrack.length) playBgm(bgmTrack, { loop: true });
  };

  const reset = () => {
    setRunning(false);
    stopBgm();
    setStatus("READY");
    playerRef.current = createPlayer(stage);
  };

  // Keyboard handlers (X = jump, Z = dash, DOWN = duck, R = reset)
  useEffect(() => {
    const onDown = (e: KeyboardEvent) => {
      const k = e.key.toLowerCase();
      if (keyDownRef.current.has(k)) return;
      keyDownRef.current.add(k);
      if (k === "x" || k === " " || k === "arrowup") {
        inputRef.current.jumpPressed = true;
        inputRef.current.jumpHeld = true;
      }
      if (k === "z" || k === "shift") inputRef.current.dashHeld = true;
      if (k === "arrowdown" || k === "c") inputRef.current.duckHeld = true;
      if (k === "r") reset();
    };
    const onUp = (e: KeyboardEvent) => {
      const k = e.key.toLowerCase();
      keyDownRef.current.delete(k);
      if (k === "x" || k === " " || k === "arrowup") inputRef.current.jumpHeld = false;
      if (k === "z" || k === "shift") inputRef.current.dashHeld = false;
      if (k === "arrowdown" || k === "c") inputRef.current.duckHeld = false;
    };
    window.addEventListener("keydown", onDown);
    window.addEventListener("keyup", onUp);
    return () => {
      window.removeEventListener("keydown", onDown);
      window.removeEventListener("keyup", onUp);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [stage.name]);

  // Game loop (30 FPS via requestAnimationFrame throttling)
  useEffect(() => {
    if (!running) return;
    let raf = 0;
    let last = performance.now();
    const accum = { t: 0 };
    const stepMs = 1000 / 30;

    const spriteFor = (tid: number) =>
      BUILTIN_SPRITES[tid] ?? customBlocks.find((b) => b.id === tid)?.sprite;

    const render = (p: PlayerState) => {
      const c = canvasRef.current;
      if (!c) return;
      const ctx = c.getContext("2d");
      if (!ctx) return;
      ctx.imageSmoothingEnabled = false;
      ctx.fillStyle = "#0a0a0d";
      ctx.fillRect(0, 0, c.width, c.height);

      // Camera follows player horizontally
      const camX = Math.max(0, Math.min(p.x - 40, stage.width * TILE - SCREEN_W));
      const camY = Math.max(0, Math.min(p.y - SCREEN_H / 2, stage.rows * TILE - SCREEN_H));

      const startCol = Math.max(0, Math.floor(camX / TILE));
      const endCol = Math.min(stage.width, Math.ceil((camX + SCREEN_W) / TILE) + 1);
      const startRow = Math.max(0, Math.floor(camY / TILE));
      const endRow = Math.min(stage.rows, Math.ceil((camY + SCREEN_H) / TILE) + 1);

      for (let col = startCol; col < endCol; col++) {
        for (let row = startRow; row < endRow; row++) {
          const t = stage.terrain[col]?.[row] ?? 0;
          if (t === 0) continue;
          const sx = (col * TILE - camX) * VIEW_SCALE;
          const sy = (row * TILE - camY) * VIEW_SCALE;
          const spr = spriteFor(t);
          if (spr) drawSprite(ctx, spr, sx, sy, VIEW_SCALE, tileColor(t));
          else {
            ctx.fillStyle = tileColor(t);
            ctx.fillRect(sx, sy, TILE * VIEW_SCALE, TILE * VIEW_SCALE);
          }
        }
      }

      // Entities (just colored markers, no AI)
      for (const [c2, r2, t2] of stage.objects) {
        const sx = (c2 * TILE - camX) * VIEW_SCALE;
        const sy = (r2 * TILE - camY) * VIEW_SCALE;
        ctx.fillStyle = entityColor(t2);
        ctx.fillRect(sx + VIEW_SCALE, sy + VIEW_SCALE, TILE * VIEW_SCALE - 2 * VIEW_SCALE, TILE * VIEW_SCALE - 2 * VIEW_SCALE);
      }
      const enemies = stage.enemy_sets?.normal ?? [];
      for (const [c2, r2, t2] of enemies) {
        const sx = (c2 * TILE - camX) * VIEW_SCALE;
        const sy = (r2 * TILE - camY) * VIEW_SCALE;
        ctx.fillStyle = entityColor(t2);
        ctx.beginPath();
        ctx.arc(sx + TILE * VIEW_SCALE / 2, sy + TILE * VIEW_SCALE / 2, (TILE * VIEW_SCALE) / 3, 0, Math.PI * 2);
        ctx.fill();
      }

      // Player
      const px = (p.x - camX) * VIEW_SCALE;
      const py = (p.y - camY) * VIEW_SCALE;
      ctx.fillStyle = p.state === "dead" ? "#999" : (p.crouching ? "#22c55e" : "#facc15");
      ctx.fillRect(px, py, p.w * VIEW_SCALE, p.h * VIEW_SCALE);

      // HUD
      ctx.fillStyle = "rgba(0,0,0,0.7)";
      ctx.fillRect(0, 0, c.width, 24);
      ctx.fillStyle = "#fff";
      ctx.font = "12px monospace";
      ctx.fillText(`X:${Math.floor(p.x)} Y:${Math.floor(p.y)} VY:${p.vy.toFixed(1)}`, 4, 16);
      ctx.fillText(status, c.width - 100, 16);
    };

    const loop = (now: number) => {
      raf = requestAnimationFrame(loop);
      const dt = now - last;
      last = now;
      accum.t += dt;
      while (accum.t >= stepMs) {
        accum.t -= stepMs;
        const p = playerRef.current!;
        const r = stepPlayer(stage, customBlocks, p, inputRef.current);
        inputRef.current.jumpPressed = false;
        if (r.died) {
          setStatus(`DIED: ${r.died.toUpperCase()}`);
          setRunning(false);
          stopBgm();
        } else if (r.clearedGoal) {
          setStatus("CLEAR!");
          setRunning(false);
          stopBgm();
        }
      }
      if (playerRef.current) render(playerRef.current);
    };
    raf = requestAnimationFrame(loop);
    return () => cancelAnimationFrame(raf);
  }, [running, stage, customBlocks, status]);

  // Initial render
  useEffect(() => {
    if (!playerRef.current) playerRef.current = createPlayer(stage);
    const c = canvasRef.current;
    if (c) {
      const ctx = c.getContext("2d");
      if (ctx) {
        ctx.fillStyle = "#000";
        ctx.fillRect(0, 0, c.width, c.height);
        ctx.fillStyle = "#fff";
        ctx.font = "20px monospace";
        ctx.fillText("PRESS PLAY", 130, 130);
      }
    }
  }, [stage]);

  useEffect(() => () => stopBgm(), []);

  return (
    <div className="space-y-3">
      <canvas
        ref={canvasRef}
        width={SCREEN_W * VIEW_SCALE}
        height={SCREEN_H * VIEW_SCALE}
        className="pixel rounded border-2 border-gray-700"
      />
      <div className="flex items-center gap-3">
        {!running ? (
          <button
            onClick={start}
            className="rounded bg-accent2 px-5 py-2 font-semibold text-black hover:opacity-90"
          >
            ▶ Play
          </button>
        ) : (
          <button
            onClick={reset}
            className="rounded bg-danger px-5 py-2 font-semibold text-white hover:opacity-90"
          >
            ■ Stop
          </button>
        )}
        <button
          onClick={reset}
          className="rounded bg-panel2 px-3 py-2 text-sm hover:bg-gray-700"
        >
          ↻ Reset (R)
        </button>
        <div className="ml-auto text-xs text-gray-400">
          <div><kbd className="rounded bg-panel2 px-1.5">X</kbd> / <kbd className="rounded bg-panel2 px-1.5">Space</kbd> / <kbd className="rounded bg-panel2 px-1.5">↑</kbd> Jump (SW1)</div>
          <div><kbd className="rounded bg-panel2 px-1.5">↓</kbd> / <kbd className="rounded bg-panel2 px-1.5">C</kbd> Duck (SW2)</div>
          <div><kbd className="rounded bg-panel2 px-1.5">Z</kbd> / <kbd className="rounded bg-panel2 px-1.5">Shift</kbd> Dash (SW3)</div>
        </div>
      </div>
    </div>
  );
}
