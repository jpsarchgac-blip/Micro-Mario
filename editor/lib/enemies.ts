// Enemy AI + collision for the in-browser emulator.
// Mirrors entity.py / entity_new.py at a simplified level (no sprites).
import { Stage, BlockDef } from "./types";
import { behaviorOf } from "./tiles";

const TILE = 8;

export type EnemyType =
  | "goomba"
  | "pata_new"
  | "bat"
  | "fish"
  | "killer_spawn"
  | "killer"        // spawned by killer_spawn
  | "big_mushroom"
  | "boss";

export interface Enemy {
  type: EnemyType;
  x: number;
  y: number;
  vx: number;
  vy: number;
  w: number;
  h: number;
  alive: boolean;
  /** Squashed countdown for stomped Goombas (8 frames flat sprite). */
  squashedT: number;
  /** Animation tick. */
  anim: number;
  /** Optional: stomp/fire-resistant flag (Boss). */
  hp?: number;
  /** Bat/Fish sin-wave anchor */
  baseY?: number;
  /** Pata fall after stomp */
  falling?: boolean;
  /** Killer spawn timer */
  spawnTimer?: number;
  /** Killers spawned by a spawner (kept here for cleanup) */
  spawned?: Enemy[];
  /** Big mushroom bounce animation */
  bounceAnim?: number;
  /** True when enemy can no longer hurt player (e.g. squashed, falling) */
  harmless?: boolean;
}

const STOMP_TOLERANCE = 5;

// =====================================================================
// Construction
// =====================================================================
export function buildEnemies(stage: Stage, difficulty: "easy" | "normal" | "hard"): Enemy[] {
  const out: Enemy[] = [];
  // Gimmicks live in stage.objects (qblock_*, big_mushroom). Enemies live in enemy_sets.
  // If enemy_sets[diff] is missing/empty, fall back to objects-without-gimmicks.
  const objects = stage.objects ?? [];
  const enemyList =
    stage.enemy_sets?.[difficulty] && (stage.enemy_sets[difficulty] as unknown[]).length > 0
      ? (stage.enemy_sets[difficulty] as Array<[number, number, string]>)
      : objects.filter((o) => !o[2].startsWith("qblock") && o[2] !== "big_mushroom");
  const gimmicks = objects.filter((o) => o[2] === "big_mushroom");

  const diffMul = difficulty === "easy" ? 0.8 : difficulty === "hard" ? 1.2 : 1.0;

  for (const [col, row, type] of enemyList) {
    const e = spawnEnemy(type as EnemyType, col, row, diffMul);
    if (e) out.push(e);
  }
  for (const [col, row, type] of gimmicks) {
    const e = spawnEnemy(type as EnemyType, col, row, 1.0);
    if (e) out.push(e);
  }
  return out;
}

function spawnEnemy(type: EnemyType, col: number, row: number, diffMul: number): Enemy | null {
  const x = col * TILE;
  const y = row * TILE;
  switch (type) {
    case "goomba":
      return { type, x, y, vx: -0.5 * diffMul, vy: 0, w: 8, h: 8, alive: true, squashedT: 0, anim: 0 };
    case "pata_new":
      return { type, x, y, vx: 0.6 * diffMul, vy: 0, w: 8, h: 8, alive: true, squashedT: 0, anim: 0 };
    case "bat":
      return { type, x, y, vx: -0.4 * diffMul, vy: 0, w: 8, h: 8, alive: true, squashedT: 0, anim: 0, baseY: y };
    case "fish":
      return { type, x, y, vx: -0.6 * diffMul, vy: 0, w: 8, h: 8, alive: true, squashedT: 0, anim: 0, baseY: y };
    case "killer_spawn":
      return {
        type, x, y, vx: 0, vy: 0, w: 0, h: 0, alive: true, squashedT: 0, anim: 0,
        spawnTimer: 60, spawned: [],
      };
    case "big_mushroom":
      return {
        type, x, y, vx: 0, vy: 0, w: 8, h: 8, alive: true, squashedT: 0, anim: 0,
        bounceAnim: 0,
      };
    case "boss":
      return {
        type, x, y, vx: 0, vy: 0, w: 24, h: 24, alive: true, squashedT: 0, anim: 0, hp: 5,
      };
    default:
      return null;
  }
}

// =====================================================================
// Collision helpers (mirrored from physics.ts to avoid circular import)
// =====================================================================
function tileAt(stage: Stage, col: number, row: number): number {
  if (col < 0 || col >= stage.width) return 1;
  if (row < 0 || row >= stage.rows) return 0;
  return stage.terrain[col]?.[row] ?? 0;
}

function isSolidLike(stage: Stage, col: number, row: number, blocks: BlockDef[]): boolean {
  const b = behaviorOf(tileAt(stage, col, row), blocks);
  return b === "solid" || b === "ice";
}

function isPlatformLike(stage: Stage, col: number, row: number, blocks: BlockDef[]): boolean {
  const b = behaviorOf(tileAt(stage, col, row), blocks);
  return b === "platform" || b === "bounce";
}

function collideX(stage: Stage, blocks: BlockDef[], px: number, py: number, w: number, h: number, dx: number): number {
  let nx = px + dx;
  if (dx === 0) return nx;
  const front = dx > 0 ? Math.floor((nx + w - 1) / TILE) : Math.floor(nx / TILE);
  const top = Math.floor(py / TILE);
  const bot = Math.floor((py + h - 1) / TILE);
  for (let r = top; r <= bot; r++) {
    if (isSolidLike(stage, front, r, blocks)) {
      nx = dx > 0 ? front * TILE - w : (front + 1) * TILE;
      return nx;
    }
  }
  return nx;
}

function collideY(stage: Stage, blocks: BlockDef[], px: number, py: number, w: number, h: number, dy: number): { newY: number; onGround: boolean } {
  let ny = py + dy;
  let onGround = false;
  if (dy === 0) return { newY: ny, onGround };
  const front = dy > 0 ? Math.floor((ny + h - 1) / TILE) : Math.floor(ny / TILE);
  const left = Math.floor(px / TILE);
  const right = Math.floor((px + w - 1) / TILE);
  for (let c = left; c <= right; c++) {
    if (isSolidLike(stage, c, front, blocks)) {
      if (dy > 0) { ny = front * TILE - h; onGround = true; }
      else ny = (front + 1) * TILE;
      return { newY: ny, onGround };
    }
    if (dy > 0 && isPlatformLike(stage, c, front, blocks)) {
      const topEdge = front * TILE;
      if (py + h <= topEdge + 1) { ny = topEdge - h; onGround = true; return { newY: ny, onGround }; }
    }
  }
  return { newY: ny, onGround };
}

// =====================================================================
// AI update
// =====================================================================
export function stepEnemies(stage: Stage, blocks: BlockDef[], enemies: Enemy[]) {
  for (const e of enemies) {
    if (!e.alive) continue;
    stepOne(e, stage, blocks);
  }
}

function stepOne(e: Enemy, stage: Stage, blocks: BlockDef[]) {
  e.anim++;

  if (e.squashedT > 0) {
    e.squashedT--;
    if (e.squashedT === 0) e.alive = false;
    return;
  }

  switch (e.type) {
    case "goomba": {
      e.vy = Math.min(e.vy + 0.4, 4.5);
      // X
      const targetX = e.x + e.vx;
      const nx = collideX(stage, blocks, e.x, e.y, e.w, e.h, e.vx);
      if (Math.abs(nx - targetX) > 0.01) e.vx = -e.vx;
      e.x = nx;
      // Y
      const cy = collideY(stage, blocks, e.x, e.y, e.w, e.h, e.vy);
      e.y = cy.newY;
      if (cy.onGround) {
        e.vy = 0;
        // Edge reverse
        const footRow = Math.floor((e.y + e.h) / TILE);
        const frontCol = Math.floor((e.x + (e.vx > 0 ? e.w : 0)) / TILE);
        const ahead = tileAt(stage, frontCol, footRow);
        const b = behaviorOf(ahead, blocks);
        if (b === "air" || b === "passable" || b === "coin") e.vx = -e.vx;
      }
      if (e.y > stage.rows * TILE + 16) e.alive = false;
      return;
    }
    case "pata_new": {
      if (e.falling) {
        e.vy = Math.min(e.vy + 0.4, 4.5);
        e.y += e.vy;
        if (e.y > stage.rows * TILE + 16) e.alive = false;
        return;
      }
      // Horizontal patrol, no gravity (flies)
      const targetX = e.x + e.vx;
      const nx = collideX(stage, blocks, e.x, e.y, e.w, e.h, e.vx);
      if (Math.abs(nx - targetX) > 0.01) e.vx = -e.vx;
      e.x = nx;
      return;
    }
    case "bat": {
      // Sin wave Y around baseY, slow horizontal drift
      const targetX = e.x + e.vx;
      const nx = collideX(stage, blocks, e.x, e.y, e.w, e.h, e.vx);
      if (Math.abs(nx - targetX) > 0.01) e.vx = -e.vx;
      e.x = nx;
      e.y = (e.baseY ?? e.y) + Math.sin(e.anim / 8) * 6;
      return;
    }
    case "fish": {
      const targetX = e.x + e.vx;
      const nx = collideX(stage, blocks, e.x, e.y, e.w, e.h, e.vx);
      if (Math.abs(nx - targetX) > 0.01) e.vx = -e.vx;
      e.x = nx;
      e.y = (e.baseY ?? e.y) + Math.sin(e.anim / 6) * 8;
      return;
    }
    case "killer_spawn": {
      e.spawnTimer = (e.spawnTimer ?? 60) - 1;
      if (e.spawnTimer <= 0) {
        e.spawnTimer = 120;
        const k: Enemy = {
          type: "killer",
          x: e.x + TILE * 16, // off-screen right
          y: e.y,
          vx: -2.0,
          vy: 0,
          w: 8, h: 8,
          alive: true, squashedT: 0, anim: 0,
        };
        (e.spawned = e.spawned ?? []).push(k);
      }
      for (const k of e.spawned ?? []) {
        if (!k.alive) continue;
        k.anim++;
        k.x += k.vx;
        if (k.x < -16 || k.x > stage.width * TILE + 16) k.alive = false;
      }
      e.spawned = (e.spawned ?? []).filter((k) => k.alive);
      return;
    }
    case "killer": {
      e.anim++;
      e.x += e.vx;
      if (e.x < -16 || e.x > stage.width * TILE + 16) e.alive = false;
      return;
    }
    case "big_mushroom": {
      if ((e.bounceAnim ?? 0) > 0) e.bounceAnim = (e.bounceAnim ?? 0) - 1;
      return;
    }
    case "boss": {
      // Simple side-to-side pacing
      if (e.anim < 30) e.vx = 0;
      else {
        if (e.anim % 240 === 0) e.vx = -e.vx || -0.6;
        if (e.anim % 240 === 120) e.vx = 0.6;
      }
      const targetX = e.x + e.vx;
      const nx = collideX(stage, blocks, e.x, e.y, e.w, e.h, e.vx);
      if (Math.abs(nx - targetX) > 0.01) e.vx = -e.vx;
      e.x = nx;
      return;
    }
  }
}

// =====================================================================
// Collision: player vs enemies
// Returns events the caller should react to
// =====================================================================
export interface CollisionResult {
  stomped: number;      // number of enemies stomped this frame (score++)
  damaged: boolean;     // player took damage
  bounced: boolean;     // player bounced off something (big mushroom)
  killed: boolean;      // player killed (SMALL + damage)
}

export function resolveCollisions(
  player: {
    x: number; y: number; w: number; h: number; vx: number; vy: number;
    state: "small" | "big" | "fire" | "dead";
    invincible: number; crouching: boolean; onGround: boolean;
  },
  enemies: Enemy[],
  starMode = false
): CollisionResult {
  const result: CollisionResult = { stomped: 0, damaged: false, bounced: false, killed: false };
  if (player.state === "dead") return result;

  const px = player.x, py = player.y, pw = player.w, ph = player.h;

  const processHit = (e: Enemy) => {
    const ex = e.x, ey = e.y, ew = e.w, eh = e.h;
    if (!(px < ex + ew && px + pw > ex && py < ey + eh && py + ph > ey)) return;

    // Big mushroom: trampoline (always bounce)
    if (e.type === "big_mushroom") {
      if (player.vy > 0) {
        player.vy = -5.5;
        e.bounceAnim = 8;
        result.bounced = true;
      }
      return;
    }

    if (e.harmless || e.squashedT > 0 || e.falling) return;
    if (e.type === "killer_spawn") return; // spawner itself doesn't hit

    // Star mode: any contact kills enemy, no damage to player
    if (starMode && e.type !== "boss") {
      e.alive = false;
      result.stomped++;
      return;
    }

    // Stomp detection (player coming down + previous bottom <= enemy top + tolerance)
    const prevBottom = py + ph - player.vy;
    const isStomp = player.vy > 0 && prevBottom <= ey + STOMP_TOLERANCE;

    if (isStomp && e.type !== "boss") {
      // Stomp
      if (e.type === "goomba") {
        e.vx = 0; e.squashedT = 8;
        e.harmless = true;
      } else if (e.type === "pata_new") {
        e.falling = true; e.vy = 0;
        e.harmless = true;
      } else {
        e.alive = false;
      }
      player.vy = -2.6;
      result.stomped++;
    } else {
      // Damage
      if (player.invincible > 0) return;
      if (player.state === "fire" || player.state === "big") {
        player.state = "small";
        if (player.crouching) {
          player.crouching = false;
          player.h = 8;
        } else {
          player.y += 8;
          player.h = 8;
        }
        player.invincible = 90;
        result.damaged = true;
      } else {
        player.state = "dead";
        player.vy = -3.5;
        player.vx = 0;
        result.killed = true;
      }
    }
  };

  for (const e of enemies) {
    if (!e.alive) continue;
    if (e.type === "killer_spawn") {
      for (const k of e.spawned ?? []) {
        if (k.alive) processHit(k);
        if (result.killed) return result;
      }
    } else {
      processHit(e);
      if (result.killed) return result;
    }
  }
  return result;
}

/** Collect coin tiles touched by player AABB. Mutates stage.terrain. */
export function collectCoins(stage: Stage, blocks: BlockDef[], player: { x: number; y: number; w: number; h: number }): number {
  void blocks;
  const left = Math.floor(player.x / TILE);
  const right = Math.floor((player.x + player.w - 1) / TILE);
  const top = Math.floor(player.y / TILE);
  const bot = Math.floor((player.y + player.h - 1) / TILE);
  let n = 0;
  for (let c = left; c <= right; c++) {
    for (let r = top; r <= bot; r++) {
      if (c < 0 || c >= stage.width || r < 0 || r >= stage.rows) continue;
      if (stage.terrain[c]?.[r] === 8) {
        stage.terrain[c][r] = 0;
        n++;
      }
    }
  }
  return n;
}

/** Iterate all enemies including spawner-spawned killers (for drawing). */
export function eachVisibleEnemy(enemies: Enemy[], fn: (e: Enemy) => void) {
  for (const e of enemies) {
    if (!e.alive) continue;
    if (e.type === "killer_spawn") {
      for (const k of e.spawned ?? []) if (k.alive) fn(k);
    } else {
      fn(e);
    }
  }
}

// =====================================================================
// Fireballs (player-fired projectiles)
// =====================================================================
export interface Fireball {
  x: number; y: number;
  vx: number; vy: number;
  w: number; h: number;
  alive: boolean;
  anim: number;
}

export function makeFireball(x: number, y: number, dir: 1 | -1): Fireball {
  return { x, y, vx: 3 * dir, vy: 0, w: 4, h: 4, alive: true, anim: 0 };
}

export function stepFireballs(stage: Stage, blocks: BlockDef[], fbs: Fireball[]) {
  for (const f of fbs) {
    if (!f.alive) continue;
    f.anim++;
    f.vy = Math.min(f.vy + 0.35, 4.5);
    // X
    const nx = collideX(stage, blocks, f.x, f.y, f.w, f.h, f.vx);
    if (Math.abs(nx - (f.x + f.vx)) > 0.01) { f.alive = false; continue; }
    f.x = nx;
    // Y
    const cy = collideY(stage, blocks, f.x, f.y, f.w, f.h, f.vy);
    f.y = cy.newY;
    if (cy.onGround) f.vy = -3.0; // ground bounce
    if (f.y > stage.rows * 8 + 16 || f.x < -8 || f.x > stage.width * 8 + 8) f.alive = false;
  }
}

/** Resolve fireball vs enemy hits. Returns number of enemies killed. */
export function resolveFireballs(fbs: Fireball[], enemies: Enemy[]): number {
  let killed = 0;
  for (const f of fbs) {
    if (!f.alive) continue;
    const fx2 = f.x, fy2 = f.y, fw = f.w, fh = f.h;
    const processOne = (e: Enemy) => {
      if (!e.alive || e.harmless || e.type === "killer_spawn" || e.type === "big_mushroom") return;
      const ex = e.x, ey = e.y, ew = e.w, eh = e.h;
      if (fx2 < ex + ew && fx2 + fw > ex && fy2 < ey + eh && fy2 + fh > ey) {
        if (e.type === "boss") {
          if ((e.hp ?? 1) > 1) e.hp = (e.hp ?? 1) - 1;
          else e.alive = false;
        } else {
          e.alive = false;
        }
        f.alive = false;
        killed++;
      }
    };
    for (const e of enemies) {
      if (e.type === "killer_spawn") {
        for (const k of e.spawned ?? []) processOne(k);
      } else processOne(e);
      if (!f.alive) break;
    }
  }
  return killed;
}

// =====================================================================
// Q-block item rolling (mirrors config.QBLOCK_PROBS)
// =====================================================================
/** Item ID returned from a Q-block hit: 0=mushroom 1=fire 2=1up 3=coin 4=star */
export type QItemId = 0 | 1 | 2 | 3 | 4;

const QBLOCK_PROBS = [50, 65, 80, 90, 100];

export function rollQItem(): QItemId {
  const r = Math.floor(Math.random() * 100);
  for (let i = 0; i < QBLOCK_PROBS.length; i++) {
    if (r < QBLOCK_PROBS[i]) return i as QItemId;
  }
  return 4;
}
