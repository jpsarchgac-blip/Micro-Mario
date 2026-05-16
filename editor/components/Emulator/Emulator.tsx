"use client";
import { useEffect, useRef, useState } from "react";
import { useProject } from "@/lib/project-context";
import { Stage, BlockDef, BgmTrack } from "@/lib/types";
import { loadBuiltinStages } from "@/lib/builtin-stages";
import { playBgm, stopBgm, beepNote, stopTone } from "@/lib/audio";
import { OledScreen } from "./OledScreen";
import { useKeys } from "./useKeys";
import {
  SCREEN_W, SCREEN_H, FG,
  clear, fillRect, strokeRect, hLine, blitTile,
  drawText, textCenterX, drawHeart,
} from "./drawing";
import {
  TILE, createPlayer, stepPlayer, PlayerState, Input,
} from "@/lib/physics";
import {
  Enemy, buildEnemies, stepEnemies, resolveCollisions, collectCoins, eachVisibleEnemy,
  Fireball, makeFireball, stepFireballs, resolveFireballs, rollQItem, QItemId,
} from "@/lib/enemies";
import { powerupMushroom, powerupFire } from "@/lib/physics";
import { spriteFor } from "@/lib/enemy-sprites";
import { blitSprite } from "./drawing";

const SCALE = 4;
const FPS = 30;

// =====================================================================
// State machine
// =====================================================================
type EmuKind =
  | "title"
  | "mode_select"
  | "diff_select"
  | "old_stub"
  | "music"
  | "option"
  | "test_stub"
  | "custom_select"
  | "stage_intro"
  | "playing"
  | "stage_clear"
  | "game_over";

interface EmuState {
  kind: EmuKind;
  t: number;             // frames since entering state
  cursor: number;        // generic cursor for menus
  /** Selected diff index (0=easy, 1=normal, 2=hard) */
  diffIdx: number;
  /** Selected stage number (1-indexed) */
  stageNum: number;
  isCustom: boolean;
  /** Loaded stage data for the current play (cloned terrain) */
  stage: Stage | null;
  player: PlayerState | null;
  enemies: Enemy[];
  fireballs: Fireball[];
  /** Star invincibility timer (frames, 30=1s) */
  starT: number;
  /** Item-acquired flash (frames). RGB hint based on item type. */
  itemFlash: number;
  itemFlashColor: string;
  lives: number;
  score: number;
  coins: number;
  tl: number;
  tsf: number;
  musicPlaying: boolean;
  volume: number;        // 0..20
  quitHold: number;
  prevJump: boolean;
  /** difficulty for enemy building */
  diffKey: "easy" | "normal" | "hard";
}

const initialState = (): EmuState => ({
  kind: "title",
  t: 0,
  cursor: 1,
  diffIdx: 1,
  stageNum: 1,
  isCustom: false,
  stage: null,
  player: null,
  enemies: [],
  fireballs: [],
  starT: 0,
  itemFlash: 0,
  itemFlashColor: "#facc15",
  lives: 3,
  score: 0,
  coins: 0,
  tl: 100,
  tsf: 0,
  musicPlaying: false,
  volume: 10,
  quitHold: 0,
  prevJump: false,
  diffKey: "normal",
});

const MODE_LABELS = ["OLD MODE", "NEW MODE", "CUSTOM MODE", "MUSIC MODE", "OPTION MODE", "TEST MODE"];
const DIFFICULTIES = ["EASY", "NORMAL", "HARD"];

// =====================================================================
// Main component
// =====================================================================
export function Emulator() {
  const { project } = useProject();
  const canvasRef = useRef<HTMLCanvasElement>(null);

  // Project + builtin data refs
  const projectRef = useRef(project);
  projectRef.current = project;
  const builtinRef = useRef<Stage[]>([]);

  // Custom block sprite lookup (for tile rendering)
  const customSpritesRef = useRef<Map<number, number[]>>(new Map());
  useEffect(() => {
    const m = new Map<number, number[]>();
    for (const b of project.blocks) m.set(b.id, b.sprite);
    customSpritesRef.current = m;
  }, [project.blocks]);

  // All BGM names (built-in + custom)
  const bgmNamesRef = useRef<string[]>([]);
  useEffect(() => {
    const builtin = ["overworld", "underground", "water", "castle", "sky", "boss", "star", "ending", "fanfare"];
    bgmNamesRef.current = [...builtin, ...Object.keys(project.bgm)];
  }, [project.bgm]);

  // State: a single mutable ref + force-render trigger
  const stRef = useRef<EmuState>(initialState());
  const [, force] = useState(0);
  const rerender = () => force((n) => n + 1);

  // Update + rerender (use when state changes need React UI updates outside canvas)
  const updateState = (patch: Partial<EmuState>) => {
    stRef.current = { ...stRef.current, ...patch };
    rerender();
  };
  const transitionTo = (kind: EmuKind, patch: Partial<EmuState> = {}) => {
    stRef.current = { ...stRef.current, kind, t: 0, ...patch };
    rerender();
  };

  // Load built-in stages once
  useEffect(() => {
    loadBuiltinStages().then((d) => {
      builtinRef.current = d.stages;
      rerender();
    });
  }, []);

  // =====================================================================
  // Key handling (edge-triggered for menus)
  // =====================================================================
  const { heldRef, consume } = useKeys((btn) => handleButtonPress(btn));

  function handleButtonPress(btn: 0 | 1 | 2) {
    const s = stRef.current;
    switch (s.kind) {
      case "title":
        stopBgm();
        transitionTo("mode_select", { cursor: 1 });
        beepNote("E5", 50);
        return;

      case "mode_select":
        if (btn === 1) updateState({ cursor: (s.cursor + MODE_LABELS.length - 1) % MODE_LABELS.length });
        else if (btn === 2) updateState({ cursor: (s.cursor + 1) % MODE_LABELS.length });
        else if (btn === 0) {
          beepNote("G5", 50);
          if (s.cursor === 0) transitionTo("old_stub");
          else if (s.cursor === 1) transitionTo("diff_select", { cursor: 1 });
          else if (s.cursor === 2) transitionTo("custom_select", { cursor: 0 });
          else if (s.cursor === 3) transitionTo("music", { cursor: 0, musicPlaying: false });
          else if (s.cursor === 4) transitionTo("option");
          else if (s.cursor === 5) transitionTo("test_stub");
        }
        return;

      case "diff_select":
        if (btn === 1) updateState({ cursor: (s.cursor + 2) % 3 });
        else if (btn === 2) updateState({ cursor: (s.cursor + 1) % 3 });
        else if (btn === 0) {
          beepNote("C5", 50);
          if (builtinRef.current.length > 0) {
            startStage(1, false, s.cursor);
          }
        }
        return;

      case "custom_select": {
        const stages = projectRef.current.stages;
        if (stages.length === 0) {
          if (btn === 0 || btn === 1) transitionTo("mode_select", { cursor: 2 });
          return;
        }
        if (btn === 1) updateState({ cursor: (s.cursor + stages.length - 1) % stages.length });
        else if (btn === 2) updateState({ cursor: (s.cursor + 1) % stages.length });
        else if (btn === 0) {
          beepNote("C5", 50);
          startStage(s.cursor + 1, true, s.diffIdx);
        }
        return;
      }

      case "old_stub":
      case "test_stub":
        if (btn === 0) transitionTo("mode_select", { cursor: s.kind === "old_stub" ? 0 : 5 });
        return;

      case "music": {
        const names = bgmNamesRef.current;
        if (names.length === 0) return;
        if (btn === 1) {
          stopBgm();
          updateState({ cursor: (s.cursor + names.length - 1) % names.length, musicPlaying: false });
        } else if (btn === 2) {
          stopBgm();
          updateState({ cursor: (s.cursor + 1) % names.length, musicPlaying: false });
        } else if (btn === 0) {
          if (s.musicPlaying) {
            stopBgm();
            updateState({ musicPlaying: false });
          } else {
            const name = names[s.cursor];
            const track = getBgmTrack(name, projectRef.current.bgm);
            if (track) {
              playBgm(track, { loop: true });
              updateState({ musicPlaying: true });
            }
          }
        }
        return;
      }

      case "option":
        if (btn === 1) updateState({ volume: Math.max(0, s.volume - 1) });
        else if (btn === 2) updateState({ volume: Math.min(20, s.volume + 1) });
        else if (btn === 0) { beepNote("G5", 50); transitionTo("mode_select", { cursor: 4 }); }
        return;

      case "stage_clear":
      case "game_over":
        if (btn === 0) {
          stopBgm();
          transitionTo("mode_select", { cursor: 0 });
        }
        return;
    }
  }

  function startStage(num: number, isCustom: boolean, diffIdx: number) {
    const stages = isCustom ? projectRef.current.stages : builtinRef.current;
    if (num < 1 || num > stages.length) return;
    stopBgm();
    const diffKey = (["easy", "normal", "hard"] as const)[diffIdx];
    transitionTo("stage_intro", {
      stageNum: num,
      isCustom,
      diffIdx,
      diffKey,
      lives: 3,
      score: 0,
      coins: 0,
      tsf: 0,
      tl: stages[num - 1].time_limit,
      stage: null,
      player: null,
      enemies: [],
      fireballs: [],
      starT: 0,
      itemFlash: 0,
      itemFlashColor: "#facc15",
      prevJump: false,
      quitHold: 0,
    });
  }

  /** Apply an item to player + emit feedback. Mirrors game_new._apply_pending_item. */
  function applyItem(it: QItemId, s: EmuState) {
    if (!s.player) return;
    switch (it) {
      case 0: // mushroom
        if (s.player.state === "small") {
          powerupMushroom(s.player);
          s.itemFlash = 18; s.itemFlashColor = "#22c55e";
        } else {
          s.score += 100; s.coins += 1;
          s.itemFlash = 10; s.itemFlashColor = "#fbbf24";
        }
        playBgm([["C5", 60], ["E5", 60], ["G5", 60], ["C6", 60], ["E6", 200]], { loop: false });
        break;
      case 1: // fire flower
        powerupFire(s.player);
        s.itemFlash = 18; s.itemFlashColor = "#fb923c";
        playBgm([["C5", 60], ["E5", 60], ["G5", 60], ["C6", 60], ["E6", 60], ["G6", 250]], { loop: false });
        break;
      case 2: // 1-UP
        s.lives = Math.min(9, s.lives + 1);
        s.itemFlash = 20; s.itemFlashColor = "#34d399";
        playBgm([["E5", 80], ["G5", 80], ["C6", 80], ["E6", 80], ["C6", 80], ["D6", 200]], { loop: false });
        break;
      case 3: // bonus coin
        s.score += 100; s.coins += 1;
        s.itemFlash = 8; s.itemFlashColor = "#fde047";
        beepNote("E5", 80);
        break;
      case 4: // star
        s.starT = 300; // 10 sec @ 30 fps
        s.itemFlash = 30; s.itemFlashColor = "#f472b6";
        // Switch BGM to star track immediately
        const starTrack = getBgmTrack("star", projectRef.current.bgm);
        if (starTrack) playBgm(starTrack, { loop: true });
        break;
    }
  }

  // =====================================================================
  // Render loop (30 fps fixed step)
  // =====================================================================
  useEffect(() => {
    let raf = 0;
    let last = performance.now();
    let accum = 0;
    const stepMs = 1000 / FPS;

    const tick = (now: number) => {
      raf = requestAnimationFrame(tick);
      let dt = now - last;
      last = now;
      if (dt > 200) dt = stepMs; // tab was inactive, don't catch up
      accum += dt;
      let dirtyKind = false;
      while (accum >= stepMs) {
        accum -= stepMs;
        if (advance()) dirtyKind = true;
        consume();
      }
      if (dirtyKind) rerender();
      render();
    };

    // Returns true if state.kind changed (caller should rerender)
    function advance(): boolean {
      const s = stRef.current;
      s.t++;
      switch (s.kind) {
        case "title":
          if (s.t >= 90) { stRef.current = { ...s, kind: "mode_select", t: 0, cursor: 1 }; return true; }
          return false;
        case "stage_intro": {
          if (s.t === 1) {
            // Initialize stage (with cloned terrain so coin pickups don't persist) + player + enemies
            const stages = s.isCustom ? projectRef.current.stages : builtinRef.current;
            const orig = stages[s.stageNum - 1];
            if (!orig) { stRef.current = { ...s, kind: "mode_select", t: 0 }; return true; }
            const stage: Stage = { ...orig, terrain: orig.terrain.map((c) => [...c]) };
            const player = createPlayer(stage);
            const enemies = buildEnemies(stage, s.diffKey);
            stRef.current = { ...s, stage, player, enemies, fireballs: [], starT: 0, tl: stage.time_limit, tsf: 0, itemFlash: 0 };
            // BGM
            const tr = getBgmTrack(stage.bgm, projectRef.current.bgm);
            if (tr) playBgm(tr, { loop: true });
          }
          if (s.t >= 60) { stRef.current = { ...stRef.current, kind: "playing", t: 0 }; return true; }
          return false;
        }
        case "playing": {
          if (!s.stage || !s.player) return false;
          const inp: Input = {
            jumpHeld: heldRef.current[0],
            jumpPressed: heldRef.current[0] && !s.prevJump,
            duckHeld: heldRef.current[1],
            dashHeld: heldRef.current[2],
          };
          s.prevJump = heldRef.current[0];
          // 3-button hold = quit
          if (heldRef.current[0] && heldRef.current[1] && heldRef.current[2]) {
            s.quitHold++;
            if (s.quitHold >= FPS * 2) {
              stopBgm();
              stRef.current = { ...s, kind: "mode_select", t: 0, quitHold: 0 };
              return true;
            }
          } else {
            s.quitHold = 0;
          }
          const res = stepPlayer(s.stage, projectRef.current.blocks, s.player, inp);

          // Q-block / Brick head bump
          if (res.headHit) {
            const { col: hc, row: hr, tileId } = res.headHit;
            if (tileId === 3) {
              // QBLOCK → QUSED, roll item, apply
              s.stage.terrain[hc][hr] = 12;
              s.score += 50;
              beepNote("B4", 60);
              const item = rollQItem();
              applyItem(item, s);
            } else if (tileId === 2) {
              // BRICK: break if not SMALL
              if (s.player.state !== "small") {
                s.stage.terrain[hc][hr] = 0;
                s.score += 50;
                beepNote("F3", 80);
              } else {
                beepNote("F3", 40);
              }
            }
          }

          // Fireball: SW2 press while FIRE → spawn
          if (res.firePressed && s.fireballs.filter((f) => f.alive).length < 2) {
            const dir: 1 | -1 = 1;
            s.fireballs.push(makeFireball(s.player.x + 8, s.player.y + 4, dir));
            beepNote("A5", 60);
            beepNote("E5", 40);
            s.itemFlash = 4; s.itemFlashColor = "#fb923c";
          }

          // Coin pickup (tile-based)
          const collected = collectCoins(s.stage, projectRef.current.blocks, s.player);
          if (collected > 0) {
            s.score += 100 * collected;
            s.coins += collected;
            beepNote("E5", 40);
          }

          // Enemy AI + collision
          stepEnemies(s.stage, projectRef.current.blocks, s.enemies);
          const starActive = s.starT > 0;
          const col = resolveCollisions(s.player, s.enemies, starActive);
          if (col.stomped > 0) {
            s.score += 200 * col.stomped;
            beepNote("G5", 50);
          }
          if (col.bounced) beepNote("C6", 80);
          if (col.damaged) beepNote("A3", 200);

          // Fireballs update + hit enemies
          stepFireballs(s.stage, projectRef.current.blocks, s.fireballs);
          const fbKilled = resolveFireballs(s.fireballs, s.enemies);
          if (fbKilled > 0) {
            s.score += 400 * fbKilled;
            beepNote("G5", 60);
          }
          s.fireballs = s.fireballs.filter((f) => f.alive);

          // Clean dead enemies
          if (s.enemies.length > 0 && s.enemies.some((e) => !e.alive)) {
            s.enemies = s.enemies.filter((e) => e.alive);
          }

          // Star timer
          if (s.starT > 0) {
            s.starT--;
            if (s.starT === 0) {
              // Restore stage BGM
              const tr = getBgmTrack(s.stage.bgm, projectRef.current.bgm);
              if (tr) playBgm(tr, { loop: true });
            }
          }
          // Item flash decay
          if (s.itemFlash > 0) s.itemFlash--;

          // Time tick
          s.tsf++;
          if (s.tsf >= FPS) { s.tsf = 0; s.tl--; if (s.tl <= 0) { stopBgm(); stRef.current = { ...s, kind: "game_over", t: 0 }; return true; } }
          if (res.died || col.killed || s.player.state === "dead") {
            stopBgm();
            s.lives--;
            if (s.lives <= 0) { stRef.current = { ...s, kind: "game_over", t: 0 }; return true; }
            stRef.current = { ...s, kind: "stage_intro", t: 0 };
            return true;
          }
          if (res.clearedGoal) {
            stopBgm();
            playBgm([["G4", 180], ["C5", 180], ["E5", 180], ["G5", 360], ["E5", 140], ["G5", 540]], { loop: false });
            s.score += s.tl * 50;
            const stages = s.isCustom ? projectRef.current.stages : builtinRef.current;
            if (s.stageNum >= stages.length) {
              stRef.current = { ...s, kind: "stage_clear", t: 0 };
              return true;
            } else {
              stRef.current = { ...s, kind: "stage_intro", t: 0, stageNum: s.stageNum + 1 };
              return true;
            }
          }
          return false;
        }
        case "stage_clear":
        case "game_over":
          if (s.t >= 30 * 10) { // auto-return after 10s
            stopBgm();
            stRef.current = { ...s, kind: "mode_select", t: 0, cursor: 0 };
            return true;
          }
          return false;
        default:
          return false;
      }
    }

    function render() {
      const c = canvasRef.current;
      if (!c) return;
      const ctx = c.getContext("2d");
      if (!ctx) return;
      ctx.imageSmoothingEnabled = false;
      const s = stRef.current;
      clear(ctx, SCALE);
      switch (s.kind) {
        case "title":        drawTitle(ctx, s.t); break;
        case "mode_select":  drawModeSelect(ctx, s.cursor); break;
        case "diff_select":  drawDiffSelect(ctx, s.cursor); break;
        case "old_stub":     drawStub(ctx, "OLD MODE", "DEVICE ONLY"); break;
        case "test_stub":    drawStub(ctx, "TEST MODE", "DEVICE ONLY"); break;
        case "music":        drawMusic(ctx, bgmNamesRef.current[s.cursor] ?? "(none)", s.musicPlaying); break;
        case "option":       drawOption(ctx, s.volume); break;
        case "custom_select":drawCustomSelect(ctx, projectRef.current.stages, s.cursor); break;
        case "stage_intro":  drawStageIntro(ctx, s.stageNum, s.lives, s.isCustom); break;
        case "playing":      drawPlaying(ctx, s, customSpritesRef.current, projectRef.current.blocks); break;
        case "stage_clear":  drawClear(ctx, s.score); break;
        case "game_over":    drawGameOver(ctx, s.score); break;
      }
    }

    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Cleanup audio on unmount
  useEffect(() => () => { stopBgm(); stopTone(); }, []);

  return (
    <div className="space-y-4">
      <div className="flex justify-center">
        <OledScreen ref={canvasRef} scale={SCALE} />
      </div>
      <div className="mx-auto flex max-w-2xl items-stretch justify-center gap-3 text-center text-xs">
        <KeyButton label="A / ←" desc="SW1 (jump / select)" />
        <KeyButton label="S / ↓" desc="SW2 (duck / prev)" />
        <KeyButton label="D / →" desc="SW3 (dash / next)" />
      </div>
      <p className="text-center text-xs text-gray-500">
        プレイ中: <kbd className="rounded bg-panel2 px-1">A+S+D</kbd> を2秒長押しでモード選択へ戻る
      </p>
    </div>
  );
}

function KeyButton({ label, desc }: { label: string; desc: string }) {
  return (
    <div className="flex-1 rounded-lg border border-gray-700 bg-panel px-3 py-2">
      <div className="text-sm font-bold text-accent">{label}</div>
      <div className="mt-0.5 text-[10px] text-gray-400">{desc}</div>
    </div>
  );
}

// =====================================================================
// Audio: BGM fallback patterns for built-in track names
// =====================================================================
function getBgmTrack(name: string, customBgm: Record<string, BgmTrack>): BgmTrack | null {
  if (customBgm[name]) return customBgm[name];
  const FALLBACK: Record<string, BgmTrack> = {
    overworld: [["E5",120],["E5",120],["-",120],["E5",120],["-",120],["C5",120],["E5",240],["G5",240],["-",240]],
    underground: [["C4",100],["D4s",100],["C4",100],["D4s",150],["E5",80],["D5s",80],["D5",80],["C5s",80],["C5",80],["B4",80],["A4s",160]],
    water: [["E5",300],["D5",300],["C5",300],["G4",900],["-",300],["C4",300],["E4",300],["G4",300],["C5",900]],
    castle: [["D4",100],["D5",100],["E4",100],["E5",100],["F4",100],["F5",100],["D4s",100],["D5s",100]],
    sky: [["F5",100],["C5",100],["A4",100],["F4",100],["D5",100],["A4",100]],
    boss: [["G3",100],["G3",100],["A3",100],["A3",100],["A3s",100],["A3s",100],["B3",100],["B3",100]],
    star: [["G4",80],["A4",80],["B4",80],["C5",80],["D5",80],["E5",80],["F5s",80],["G5",160]],
    ending: [["G4",200],["C5",200],["E5",200],["G5",400]],
    fanfare: [["G4",180],["C5",180],["E5",180],["G5",360]],
  };
  return FALLBACK[name] ?? null;
}

// =====================================================================
// Screen renderers
// =====================================================================
function drawTitle(ctx: CanvasRenderingContext2D, t: number) {
  strokeRect(ctx, 2, 2, 124, 60, SCALE);
  drawText(ctx, "MICRO MARIO", textCenterX("MICRO MARIO"), 12, SCALE);
  drawText(ctx, "EMULATOR", textCenterX("EMULATOR"), 24, SCALE);
  if ((t >> 3) & 1) drawText(ctx, "PRESS ANY KEY", textCenterX("PRESS ANY KEY"), 46, SCALE);
  drawText(ctx, "A:JUMP S:DUCK D:DASH", textCenterX("A:JUMP S:DUCK D:DASH"), 55, SCALE);
}

function drawModeSelect(ctx: CanvasRenderingContext2D, cursor: number) {
  strokeRect(ctx, 2, 2, 124, 60, SCALE);
  drawText(ctx, "MICRO MARIO", textCenterX("MICRO MARIO"), 4, SCALE);
  hLine(ctx, 2, 13, 124, SCALE);
  for (let i = 0; i < MODE_LABELS.length; i++) {
    const y = 15 + i * 8;
    if (cursor === i) fillRect(ctx, 18, y, 4, 7, SCALE);
    drawText(ctx, MODE_LABELS[i], textCenterX(MODE_LABELS[i]), y, SCALE);
  }
}

function drawDiffSelect(ctx: CanvasRenderingContext2D, cursor: number) {
  strokeRect(ctx, 4, 4, 120, 56, SCALE);
  drawText(ctx, "DIFFICULTY", textCenterX("DIFFICULTY"), 8, SCALE);
  hLine(ctx, 4, 18, 120, SCALE);
  DIFFICULTIES.forEach((lb, i) => {
    const y = 24 + i * 12;
    drawText(ctx, lb, textCenterX(lb), y, SCALE);
    if (cursor === i) fillRect(ctx, 20, y, 4, 7, SCALE);
  });
}

function drawMusic(ctx: CanvasRenderingContext2D, name: string, playing: boolean) {
  strokeRect(ctx, 2, 2, 124, 60, SCALE);
  drawText(ctx, "MUSIC PLAYER", textCenterX("MUSIC PLAYER"), 6, SCALE);
  hLine(ctx, 2, 16, 124, SCALE);
  drawText(ctx, "TRACK:", 10, 26, SCALE);
  drawText(ctx, name.toUpperCase().slice(0, 13), 10, 34, SCALE);
  const stat = playing ? "PLAYING" : "STOPPED";
  drawText(ctx, stat, textCenterX(stat), 44, SCALE);
  drawText(ctx, "A:PLAY/STOP", 2, 56, SCALE);
  drawText(ctx, "S/D:PREV/NEXT", 64, 56, SCALE);
}

function drawOption(ctx: CanvasRenderingContext2D, vol: number) {
  strokeRect(ctx, 2, 2, 124, 60, SCALE);
  drawText(ctx, "OPTION", textCenterX("OPTION"), 6, SCALE);
  hLine(ctx, 2, 16, 124, SCALE);
  drawText(ctx, "VOLUME", textCenterX("VOLUME"), 24, SCALE);
  const bw = 80, bx = 24, by = 36;
  strokeRect(ctx, bx, by, bw, 6, SCALE);
  const fw = Math.floor((vol / 20) * bw);
  if (fw > 0) fillRect(ctx, bx, by, fw, 6, SCALE);
  drawText(ctx, "A:SAVE EXIT", textCenterX("A:SAVE EXIT"), 50, SCALE);
}

function drawStub(ctx: CanvasRenderingContext2D, title: string, msg: string) {
  strokeRect(ctx, 4, 10, 120, 36, SCALE);
  drawText(ctx, title, textCenterX(title), 18, SCALE);
  drawText(ctx, msg, textCenterX(msg), 30, SCALE);
  drawText(ctx, "A:BACK", textCenterX("A:BACK"), 52, SCALE);
}

function drawCustomSelect(ctx: CanvasRenderingContext2D, stages: Stage[], cursor: number) {
  strokeRect(ctx, 2, 2, 124, 60, SCALE);
  drawText(ctx, "CUSTOM STAGES", textCenterX("CUSTOM STAGES"), 4, SCALE);
  hLine(ctx, 2, 13, 124, SCALE);
  if (stages.length === 0) {
    drawText(ctx, "NO STAGES",  textCenterX("NO STAGES"), 22, SCALE);
    drawText(ctx, "USE EDITOR", textCenterX("USE EDITOR"), 32, SCALE);
    drawText(ctx, "ANY:BACK",   textCenterX("ANY:BACK"), 50, SCALE);
    return;
  }
  const start = Math.floor(cursor / 5) * 5;
  for (let i = start; i < Math.min(start + 5, stages.length); i++) {
    const y = 15 + (i - start) * 8;
    const name = stages[i].name.slice(0, 18);
    if (cursor === i) fillRect(ctx, 6, y, 4, 7, SCALE);
    drawText(ctx, name, 14, y, SCALE);
  }
  drawText(ctx, "A:GO  S/D:NAV", textCenterX("A:GO  S/D:NAV"), 56, SCALE);
}

function drawStageIntro(ctx: CanvasRenderingContext2D, num: number, lives: number, isCustom: boolean) {
  strokeRect(ctx, 6, 4, 116, 40, SCALE);
  drawText(ctx, "STAGE", textCenterX("STAGE"), 8, SCALE);
  drawText(ctx, String(num), 60, 18, SCALE);
  drawText(ctx, "LIFE", 24, 30, SCALE);
  for (let i = 0; i < Math.min(lives, 5); i++) drawHeart(ctx, 50 + i * 7, 30, SCALE);
  const mode = isCustom ? "CUSTOM" : "NORMAL";
  drawText(ctx, mode, textCenterX(mode), 38, SCALE);
  drawText(ctx, "A:JUMP S:DUCK D:DASH", textCenterX("A:JUMP S:DUCK D:DASH"), 50, SCALE);
  drawText(ctx, "HOLD A+S+D=BACK", textCenterX("HOLD A+S+D=BACK"), 57, SCALE);
}

function drawPlaying(
  ctx: CanvasRenderingContext2D,
  s: EmuState,
  customSprites: Map<number, number[]>,
  _blocks: BlockDef[]
) {
  const stage = s.stage!;
  const player = s.player!;
  // Camera
  const maxX = Math.max(0, stage.width * TILE - SCREEN_W);
  const maxY = Math.max(0, stage.rows * TILE - SCREEN_H);
  const camX = Math.max(0, Math.min(player.x - 40, maxX));
  const camY = Math.max(0, Math.min(player.y - SCREEN_H / 2, maxY));

  // Tiles (skip header area until later)
  const startCol = Math.max(0, Math.floor(camX / TILE));
  const endCol = Math.min(stage.width, Math.ceil((camX + SCREEN_W) / TILE) + 1);
  const startRow = Math.max(0, Math.floor(camY / TILE));
  const endRow = Math.min(stage.rows, Math.ceil((camY + SCREEN_H) / TILE) + 1);
  for (let c = startCol; c < endCol; c++) {
    const col = stage.terrain[c];
    if (!col) continue;
    for (let r = startRow; r < endRow; r++) {
      const t = col[r];
      if (!t) continue;
      blitTile(ctx, t, c * TILE - camX, r * TILE - camY, SCALE, customSprites);
    }
  }

  // Fireballs (player-fired projectiles)
  for (const f of s.fireballs) {
    if (!f.alive) continue;
    const fx = (f.x - camX) * SCALE;
    const fy = (f.y - camY) * SCALE;
    ctx.fillStyle = FG;
    // Flickering 4x4 pixel ball with rotating cross pattern
    if ((f.anim >> 1) & 1) {
      ctx.fillRect(fx, fy, 4 * SCALE, 4 * SCALE);
    } else {
      ctx.fillRect(fx + SCALE, fy, 2 * SCALE, 4 * SCALE);
      ctx.fillRect(fx, fy + SCALE, 4 * SCALE, 2 * SCALE);
    }
  }

  // Live enemies (AI-driven)
  eachVisibleEnemy(s.enemies, (e) => {
    const sx = e.x - camX;
    const sy = e.y - camY;
    if (sx < -8 || sx > SCREEN_W || sy < -8 || sy > SCREEN_H) return;
    if (e.type === "boss") {
      // 24x24 boss: tile 3x3
      const spr = spriteFor(e.type, false, e.anim);
      for (let by = 0; by < 3; by++)
        for (let bx = 0; bx < 3; bx++)
          blitSprite(ctx, spr, Math.floor(sx) + bx * 8, Math.floor(sy) + by * 8, SCALE);
      return;
    }
    const spr = spriteFor(e.type, e.squashedT > 0, e.anim);
    blitSprite(ctx, spr, Math.floor(sx), Math.floor(sy), SCALE);
  });

  // Player (invincible: blink every other frame; star: rainbow tint)
  const blink = player.invincible > 0 && ((player.invincible & 2) === 0);
  if (!blink) {
    const px = (player.x - camX) * SCALE;
    const py = (player.y - camY) * SCALE;
    if (s.starT > 0) {
      const colors = ["#fef9c3", "#fb923c", "#22c55e", "#3b82f6", "#a855f7", "#ef4444"];
      ctx.fillStyle = colors[s.starT % colors.length];
    } else if (player.state === "fire") {
      ctx.fillStyle = "#fb923c"; // orange tint for Fire Mario
    } else if (player.state === "big") {
      ctx.fillStyle = FG;
    } else {
      ctx.fillStyle = FG;
    }
    ctx.fillRect(px, py, player.w * SCALE, player.h * SCALE);
    // Fire-state shoulder indicator
    if (player.state === "fire") {
      ctx.fillStyle = "#fef9c3";
      ctx.fillRect(px + 2 * SCALE, py, 2 * SCALE, SCALE);
    }
  }

  // Star aura: thin flickering border around player
  if (s.starT > 0 && (s.starT & 1) === 0) {
    const px = (player.x - camX) * SCALE;
    const py = (player.y - camY) * SCALE;
    ctx.fillStyle = "#fde047";
    ctx.fillRect(px - SCALE, py, SCALE, player.h * SCALE);
    ctx.fillRect(px + player.w * SCALE, py, SCALE, player.h * SCALE);
    ctx.fillRect(px, py - SCALE, player.w * SCALE, SCALE);
    ctx.fillRect(px, py + player.h * SCALE, player.w * SCALE, SCALE);
  }

  // Item-acquired full-screen flash (frames decrement after use)
  if (s.itemFlash > 0 && (s.itemFlash & 1) === 1) {
    ctx.fillStyle = s.itemFlashColor;
    ctx.globalAlpha = 0.25;
    ctx.fillRect(0, 0, SCREEN_W * SCALE, SCREEN_H * SCALE);
    ctx.globalAlpha = 1.0;
  }

  // HUD: clear top 8 rows + redraw text
  fillRect(ctx, 0, 0, 128, 8, SCALE, false);
  drawText(ctx, padNum(s.score, 5), 0, 0, SCALE);
  drawText(ctx, String(s.stageNum), 50, 0, SCALE);
  drawText(ctx, "T", 75, 0, SCALE);
  drawText(ctx, padNum(s.tl, 3), 81, 0, SCALE);
  drawText(ctx, "C", 105, 0, SCALE);
  drawText(ctx, padNum(s.coins, 2), 111, 0, SCALE);
  hLine(ctx, 0, 8, 128, SCALE);
}

function padNum(n: number, w: number): string {
  return Math.max(0, Math.floor(n)).toString().padStart(w, "0");
}

function drawClear(ctx: CanvasRenderingContext2D, score: number) {
  strokeRect(ctx, 4, 6, 120, 52, SCALE);
  drawText(ctx, "STAGE CLEAR!", textCenterX("STAGE CLEAR!"), 12, SCALE);
  hLine(ctx, 4, 22, 120, SCALE);
  drawText(ctx, "SCORE", 8, 30, SCALE);
  drawText(ctx, padNum(score, 6), 58, 30, SCALE);
  drawText(ctx, "A:TITLE", textCenterX("A:TITLE"), 50, SCALE);
}

function drawGameOver(ctx: CanvasRenderingContext2D, score: number) {
  strokeRect(ctx, 4, 10, 120, 36, SCALE);
  drawText(ctx, "GAME OVER", textCenterX("GAME OVER"), 18, SCALE);
  drawText(ctx, "SCORE", 24, 30, SCALE);
  drawText(ctx, padNum(score, 5), 54, 30, SCALE);
  drawText(ctx, "A:TITLE", textCenterX("A:TITLE"), 50, SCALE);
}
