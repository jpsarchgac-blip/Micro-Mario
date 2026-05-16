"use client";
import { useCallback, useEffect, useRef, useState } from "react";
import {
  BUILTIN_SPRITES,
  TILE_IDS,
  drawSprite,
  tileColor,
} from "@/lib/tiles";
import { entityColor, entityLabel } from "@/lib/entities";
import { BlockDef, Stage } from "@/lib/types";
import { computeJumpReach } from "@/lib/physics";

type Tool = "paint" | "erase" | "entity" | "start" | "goal";

interface Props {
  stage: Stage;
  customBlocks: BlockDef[];
  selectedTile: number;
  selectedEntity: string | null;
  tool: Tool;
  difficulty: "easy" | "normal" | "hard";
  showJumpReach: boolean;
  onMutate: (s: Stage) => void;
}

const SCALE = 16; // pixels per tile in editor

export function MapCanvas({
  stage,
  customBlocks,
  selectedTile,
  selectedEntity,
  tool,
  difficulty,
  showJumpReach,
  onMutate,
}: Props) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const wrapRef = useRef<HTMLDivElement>(null);
  const [hover, setHover] = useState<{ col: number; row: number } | null>(null);
  const [dragging, setDragging] = useState(false);

  // Build sprite lookup once
  const spriteFor = useCallback(
    (tid: number): number[] | undefined => {
      if (BUILTIN_SPRITES[tid]) return BUILTIN_SPRITES[tid];
      const cb = customBlocks.find((b) => b.id === tid);
      return cb?.sprite;
    },
    [customBlocks]
  );

  // Object list for current difficulty (or objects if no enemy_sets entry)
  const objectsForDifficulty = stage.objects ?? [];
  const enemyList =
    stage.enemy_sets?.[difficulty] && stage.enemy_sets[difficulty]!.length > 0
      ? stage.enemy_sets[difficulty]!
      : objectsForDifficulty.filter((o) => !o[2].startsWith("qblock") && o[2] !== "big_mushroom");
  const gimmicks = objectsForDifficulty.filter((o) =>
    o[2].startsWith("qblock") || o[2] === "big_mushroom"
  );

  const render = useCallback(() => {
    const c = canvasRef.current;
    if (!c) return;
    const ctx = c.getContext("2d");
    if (!ctx) return;
    const W = stage.width * SCALE;
    const H = stage.rows * SCALE;
    c.width = W;
    c.height = H;
    ctx.imageSmoothingEnabled = false;

    // background grid
    ctx.fillStyle = "#0a0a0d";
    ctx.fillRect(0, 0, W, H);
    ctx.strokeStyle = "#1f1f25";
    ctx.lineWidth = 1;
    for (let x = 0; x <= stage.width; x++) {
      ctx.beginPath();
      ctx.moveTo(x * SCALE, 0); ctx.lineTo(x * SCALE, H);
      ctx.stroke();
    }
    for (let y = 0; y <= stage.rows; y++) {
      ctx.beginPath();
      ctx.moveTo(0, y * SCALE); ctx.lineTo(W, y * SCALE);
      ctx.stroke();
    }

    // tiles
    for (let col = 0; col < stage.width; col++) {
      const colData = stage.terrain[col] ?? [];
      for (let row = 0; row < stage.rows; row++) {
        const t = colData[row] ?? 0;
        if (t === 0) continue;
        const spr = spriteFor(t);
        if (spr) {
          drawSprite(ctx, spr, col * SCALE, row * SCALE, SCALE / 8, tileColor(t));
        } else {
          ctx.fillStyle = tileColor(t);
          ctx.fillRect(col * SCALE, row * SCALE, SCALE, SCALE);
        }
      }
    }

    // start marker
    ctx.strokeStyle = "#3b82f6";
    ctx.lineWidth = 2;
    ctx.strokeRect(stage.start_col * SCALE, (stage.start_row - 2) * SCALE, SCALE, SCALE * 2);
    ctx.fillStyle = "#3b82f6";
    ctx.font = "10px monospace";
    ctx.fillText("S", stage.start_col * SCALE + 4, (stage.start_row - 2) * SCALE + 12);

    // goal marker
    if (stage.goal_col >= 0) {
      ctx.strokeStyle = "#a3e635";
      ctx.lineWidth = 2;
      ctx.strokeRect(stage.goal_col * SCALE, 0, SCALE, H);
      ctx.fillStyle = "#a3e635";
      ctx.fillText("G", stage.goal_col * SCALE + 4, 12);
    }

    // entities
    const drawEntity = (col: number, row: number, type: string) => {
      const cx = col * SCALE + SCALE / 2;
      const cy = row * SCALE + SCALE / 2;
      ctx.fillStyle = entityColor(type);
      ctx.beginPath();
      ctx.arc(cx, cy, SCALE / 2.5, 0, Math.PI * 2);
      ctx.fill();
      ctx.fillStyle = "#000";
      ctx.font = "bold 9px monospace";
      ctx.fillText(entityLabel(type).slice(0, 2), col * SCALE + 2, row * SCALE + 11);
    };
    for (const [c, r, t] of enemyList) drawEntity(c, r, t);
    for (const [c, r, t] of gimmicks) drawEntity(c, r, t);

    // jump reach overlay (from hover)
    if (showJumpReach && hover) {
      const reach = computeJumpReach(stage, customBlocks, hover.col, hover.row);
      ctx.fillStyle = "rgba(59,130,246,0.25)";
      reach.forEach((key) => {
        const [c, r] = key.split(",").map(Number);
        ctx.fillRect(c * SCALE, r * SCALE, SCALE, SCALE);
      });
    }

    // hover
    if (hover) {
      ctx.strokeStyle = "#facc15";
      ctx.lineWidth = 1.5;
      ctx.strokeRect(hover.col * SCALE, hover.row * SCALE, SCALE, SCALE);
    }
  }, [stage, customBlocks, hover, enemyList, gimmicks, spriteFor, showJumpReach]);

  useEffect(() => {
    render();
  }, [render]);

  const applyAt = useCallback(
    (col: number, row: number) => {
      if (col < 0 || col >= stage.width || row < 0 || row >= stage.rows) return;
      const next: Stage = JSON.parse(JSON.stringify(stage));
      if (tool === "paint") {
        const colData = next.terrain[col] ?? Array(next.rows).fill(0);
        colData[row] = selectedTile;
        next.terrain[col] = colData;
      } else if (tool === "erase") {
        const colData = next.terrain[col] ?? Array(next.rows).fill(0);
        colData[row] = 0;
        next.terrain[col] = colData;
      } else if (tool === "entity" && selectedEntity) {
        // Toggle: if same entity exists, remove; else add
        const isGimmick =
          selectedEntity === "qblock_random" || selectedEntity === "big_mushroom";
        if (isGimmick) {
          const idx = next.objects.findIndex(
            (o) => o[0] === col && o[1] === row && o[2] === selectedEntity
          );
          if (idx >= 0) next.objects.splice(idx, 1);
          else next.objects.push([col, row, selectedEntity]);
        } else {
          if (!next.enemy_sets[difficulty]) next.enemy_sets[difficulty] = [];
          const list = next.enemy_sets[difficulty]!;
          const idx = list.findIndex((o) => o[0] === col && o[1] === row);
          if (idx >= 0) list.splice(idx, 1);
          else list.push([col, row, selectedEntity]);
        }
      } else if (tool === "start") {
        next.start_col = col;
        next.start_row = row;
      } else if (tool === "goal") {
        next.goal_col = col;
        next.flag_col = col;
      }
      onMutate(next);
    },
    [stage, tool, selectedTile, selectedEntity, difficulty, onMutate]
  );

  const eventCell = (e: React.MouseEvent) => {
    const c = canvasRef.current;
    if (!c) return null;
    const rect = c.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    return { col: Math.floor((x / rect.width) * stage.width), row: Math.floor((y / rect.height) * stage.rows) };
  };

  return (
    <div
      ref={wrapRef}
      className="overflow-auto rounded border border-gray-800 bg-black"
      style={{ maxHeight: "70vh" }}
    >
      <canvas
        ref={canvasRef}
        className="pixel"
        style={{ display: "block", cursor: "crosshair" }}
        onMouseDown={(e) => {
          const c = eventCell(e); if (!c) return;
          setDragging(true);
          applyAt(c.col, c.row);
        }}
        onMouseMove={(e) => {
          const c = eventCell(e); if (!c) return;
          setHover(c);
          if (dragging && (tool === "paint" || tool === "erase")) applyAt(c.col, c.row);
        }}
        onMouseUp={() => setDragging(false)}
        onMouseLeave={() => { setHover(null); setDragging(false); }}
      />
    </div>
  );
}
