// Simplified port of player.py physics for the in-browser GamePlayer.
// Auto-runner: Mario always moves right at WALK or RUN speed; player controls jump + duck.
import { Stage } from "./types";
import { behaviorOf } from "./tiles";

export const TILE = 8;
export const FPS = 30;
export const WALK_SPEED = 1.2;
export const RUN_SPEED = 2.4;
export const RUN_ACCEL_FR = 15;
export const JUMP_VELOCITY = -3.4;
export const GRAVITY_UP = 0.18;
export const GRAVITY_DOWN = 0.38;
export const TERMINAL_VEL = 4.5;
export const SHORT_JUMP_CUT = 0.45;
export const COYOTE_FRAMES = 6;
export const JUMP_BUFFER = 6;
export const CROUCH_WALK_SPEED = 0.35;

export interface PlayerState {
  x: number;
  y: number;
  vx: number;
  vy: number;
  w: number;
  h: number;
  onGround: boolean;
  state: "small" | "big" | "fire" | "dead";
  crouching: boolean;
  coyote: number;
  jumpBuf: number;
  runCharge: number;
  invincible: number;
  deadTimer: number;
}

export interface Input {
  jumpHeld: boolean;
  jumpPressed: boolean;
  duckHeld: boolean;
  dashHeld: boolean;
}

export function createPlayer(stage: Stage): PlayerState {
  const sc = stage.start_col ?? 2;
  const sr = stage.start_row ?? stage.rows - 4;
  const h = 16;
  return {
    x: sc * TILE,
    y: sr * TILE - h,
    vx: 0,
    vy: 0,
    w: 6,
    h,
    onGround: false,
    state: "big",
    crouching: false,
    coyote: 0,
    jumpBuf: 0,
    runCharge: 0,
    invincible: 0,
    deadTimer: 0,
  };
}

function tileAt(stage: Stage, col: number, row: number): number {
  if (col < 0 || col >= stage.width) return 1; // ground bounds
  if (row < 0 || row >= stage.rows) return 0;
  return stage.terrain[col]?.[row] ?? 0;
}

function isSolid(stage: Stage, col: number, row: number, blocks: import("./types").BlockDef[]): boolean {
  const t = tileAt(stage, col, row);
  const b = behaviorOf(t, blocks);
  return b === "solid" || b === "ice";
}

function isPlatform(stage: Stage, col: number, row: number, blocks: import("./types").BlockDef[]): boolean {
  const t = tileAt(stage, col, row);
  const b = behaviorOf(t, blocks);
  return b === "platform" || b === "bounce";
}

function isLethal(stage: Stage, col: number, row: number, blocks: import("./types").BlockDef[]): boolean {
  const t = tileAt(stage, col, row);
  return behaviorOf(t, blocks) === "lethal";
}

function tileBehaviorAt(stage: Stage, col: number, row: number, blocks: import("./types").BlockDef[]) {
  return behaviorOf(tileAt(stage, col, row), blocks);
}

function collideX(stage: Stage, blocks: import("./types").BlockDef[], px: number, py: number, w: number, h: number, dx: number): number {
  let nx = px + dx;
  if (dx === 0) return nx;
  const front = dx > 0 ? Math.floor((nx + w - 1) / TILE) : Math.floor(nx / TILE);
  const top = Math.floor(py / TILE);
  const bot = Math.floor((py + h - 1) / TILE);
  for (let r = top; r <= bot; r++) {
    if (isSolid(stage, front, r, blocks)) {
      nx = dx > 0 ? front * TILE - w : (front + 1) * TILE;
      return nx;
    }
  }
  return nx;
}

function collideY(
  stage: Stage,
  blocks: import("./types").BlockDef[],
  px: number, py: number, w: number, h: number, dy: number
): { newY: number; onGround: boolean } {
  let ny = py + dy;
  let onGround = false;
  if (dy === 0) {
    const footRow = Math.floor((py + h) / TILE);
    const left = Math.floor(px / TILE);
    const right = Math.floor((px + w - 1) / TILE);
    for (let c = left; c <= right; c++) {
      if (isSolid(stage, c, footRow, blocks)) { onGround = true; break; }
      if (isPlatform(stage, c, footRow, blocks) && ((py + h) % TILE === 0)) {
        onGround = true; break;
      }
    }
    return { newY: ny, onGround };
  }
  const front = dy > 0 ? Math.floor((ny + h - 1) / TILE) : Math.floor(ny / TILE);
  const left = Math.floor(px / TILE);
  const right = Math.floor((px + w - 1) / TILE);
  for (let c = left; c <= right; c++) {
    if (isSolid(stage, c, front, blocks)) {
      if (dy > 0) {
        ny = front * TILE - h;
        onGround = true;
      } else {
        ny = (front + 1) * TILE;
      }
      return { newY: ny, onGround };
    }
    if (dy > 0 && isPlatform(stage, c, front, blocks)) {
      const topEdge = front * TILE;
      if (py + h <= topEdge + 1) {
        ny = topEdge - h;
        onGround = true;
        return { newY: ny, onGround };
      }
    }
  }
  return { newY: ny, onGround };
}

/** Advance physics by one frame. Returns updated PlayerState (mutated in place). */
export function stepPlayer(
  stage: Stage,
  blocks: import("./types").BlockDef[],
  p: PlayerState,
  inp: Input
): { died?: "fall" | "lethal" | "time"; clearedGoal?: boolean } {
  if (p.state === "dead") {
    p.y += p.vy;
    p.vy += 0.3;
    p.deadTimer -= 1;
    return {};
  }
  if (p.invincible > 0) p.invincible -= 1;

  // Horizontal: dash charge & crouch
  if (inp.dashHeld) {
    if (p.runCharge < RUN_ACCEL_FR) p.runCharge += 1;
  } else {
    if (p.runCharge > 0) p.runCharge -= 1;
  }
  const t = p.runCharge / RUN_ACCEL_FR;
  const baseVx = WALK_SPEED + (RUN_SPEED - WALK_SPEED) * t;

  const wantCrouch = inp.duckHeld && p.onGround && (p.state === "big" || p.state === "fire");
  if (wantCrouch) {
    if (!p.crouching) {
      p.crouching = true;
      p.h = 8;
      p.y += 8;
    }
    p.vx = CROUCH_WALK_SPEED;
  } else if (p.crouching) {
    const headRow = Math.floor((p.y - 8) / TILE);
    const left = Math.floor(p.x / TILE);
    const right = Math.floor((p.x + p.w - 1) / TILE);
    let blocked = false;
    for (let c = left; c <= right; c++) if (isSolid(stage, c, headRow, blocks)) { blocked = true; break; }
    if (!blocked) {
      p.crouching = false;
      p.h = 16;
      p.y -= 8;
      p.vx = baseVx;
    } else {
      p.vx = CROUCH_WALK_SPEED;
    }
  } else {
    p.vx = baseVx;
  }

  // Jump: buffer + coyote
  if (inp.jumpPressed) p.jumpBuf = JUMP_BUFFER;
  else if (p.jumpBuf > 0) p.jumpBuf -= 1;
  if (p.onGround) p.coyote = COYOTE_FRAMES;
  else if (p.coyote > 0) p.coyote -= 1;
  if (p.jumpBuf > 0 && p.coyote > 0) {
    p.vy = JUMP_VELOCITY;
    p.jumpBuf = 0;
    p.coyote = 0;
    p.onGround = false;
  }
  if (!inp.jumpHeld && p.vy < 0) p.vy *= SHORT_JUMP_CUT;

  // Gravity
  const grav = (p.vy < 0 && inp.jumpHeld) ? GRAVITY_UP : GRAVITY_DOWN;
  p.vy += grav * (stage.gravity_scale ?? 1.0);
  if (p.vy > TERMINAL_VEL) p.vy = TERMINAL_VEL;

  // Collide
  p.x = collideX(stage, blocks, p.x, p.y, p.w, p.h, p.vx);
  const cy = collideY(stage, blocks, p.x, p.y, p.w, p.h, p.vy);
  p.y = cy.newY;
  if (cy.onGround) { p.vy = 0; p.onGround = true; } else p.onGround = false;

  // Special tile feedback (BOUNCE / ICE) - check feet row
  if (p.onGround) {
    const footRow = Math.floor((p.y + p.h) / TILE);
    const lc = Math.floor(p.x / TILE);
    const rc = Math.floor((p.x + p.w - 1) / TILE);
    let bounced = false;
    (p as PlayerState & { onIce?: boolean }).onIce = false;
    for (let c = lc; c <= rc; c++) {
      const b = tileBehaviorAt(stage, c, footRow, blocks);
      if (b === "bounce") bounced = true;
      if (b === "ice") (p as PlayerState & { onIce?: boolean }).onIce = true;
    }
    if (bounced) {
      p.vy = -5.2;
      p.onGround = false;
    }
  }

  // Lethal tile
  const left = Math.floor(p.x / TILE);
  const right = Math.floor((p.x + p.w - 1) / TILE);
  const top = Math.floor(p.y / TILE);
  const bot = Math.floor((p.y + p.h - 1) / TILE);
  for (let c = left; c <= right; c++) {
    for (let r = top; r <= bot; r++) {
      if (isLethal(stage, c, r, blocks)) {
        p.state = "dead"; p.vy = -3.5; p.deadTimer = 60;
        return { died: "lethal" };
      }
    }
  }

  // Fall death
  if (p.y > stage.rows * TILE + 8) {
    p.state = "dead"; p.deadTimer = 30;
    return { died: "fall" };
  }

  // Goal
  if (stage.goal_col > 0 && p.x >= stage.goal_col * TILE - 4) {
    return { clearedGoal: true };
  }
  return {};
}

/** Approximate jump reach overlay: returns set of "col,row" cells reachable in one jump from start tile. */
export function computeJumpReach(
  stage: Stage,
  blocks: import("./types").BlockDef[],
  startCol: number,
  startRow: number,
  dashFrames = 12
): Set<string> {
  const out = new Set<string>();
  // Simulate jump from edge of start tile, going right (auto-runner direction)
  const startX = startCol * TILE + TILE / 2;
  const startY = startRow * TILE - 1;
  const vx = WALK_SPEED + (RUN_SPEED - WALK_SPEED) * Math.min(1, dashFrames / RUN_ACCEL_FR);
  let x = startX, y = startY, vy = JUMP_VELOCITY;
  for (let f = 0; f < 60; f++) {
    x += vx;
    vy += (vy < 0) ? GRAVITY_UP : GRAVITY_DOWN;
    if (vy > TERMINAL_VEL) vy = TERMINAL_VEL;
    y += vy;
    if (y > stage.rows * TILE) break;
    const c = Math.floor(x / TILE);
    const r = Math.floor(y / TILE);
    if (c < 0 || c >= stage.width || r < 0 || r >= stage.rows) continue;
    out.add(`${c},${r}`);
  }
  return out;
}
