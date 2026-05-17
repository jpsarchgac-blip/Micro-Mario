"use client";
import { useEffect, useRef, useState } from "react";
import { loadPyodideRuntime, PyodideInstance, resetPython, stepPython } from "@/lib/pyodide-runtime";
import { installBridges } from "@/lib/hardware-bridge";
import { HardwareDisplay } from "./HardwareDisplay";

const SCALE = 4;
const FPS = 30;

type LoadState =
  | { kind: "idle" }
  | { kind: "loading"; msg: string }
  | { kind: "ready"; py: PyodideInstance }
  | { kind: "error"; err: string };

export function PyodideEmulator() {
  const [state, setState] = useState<LoadState>({ kind: "idle" });
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const bridges = useRef(installBridges());

  // Wire canvas → OledBridge
  useEffect(() => {
    if (state.kind !== "ready") return;
    if (!canvasRef.current) return;
    bridges.current.oled.attach(canvasRef.current, SCALE);
  }, [state.kind]);

  // Wire keyboard
  useEffect(() => {
    return bridges.current.keys.attachKeyboard();
  }, []);

  // Cleanup audio on unmount
  useEffect(() => {
    return () => {
      bridges.current.audio.shutdown();
    };
  }, []);

  // Start loading
  const onLoad = async () => {
    bridges.current.audio.resume(); // user gesture → unlock audio
    setState({ kind: "loading", msg: "Starting..." });
    try {
      const py = await loadPyodideRuntime((msg) => {
        setState({ kind: "loading", msg });
      });
      setState({ kind: "ready", py });
    } catch (e) {
      setState({ kind: "error", err: (e as Error).message });
    }
  };

  const onReset = async () => {
    if (state.kind !== "ready") return;
    setState({ kind: "loading", msg: "Resetting..." });
    await resetPython(state.py);
    setState({ kind: "ready", py: state.py });
  };

  // 30 FPS game loop
  useEffect(() => {
    if (state.kind !== "ready") return;
    const py = state.py;
    let raf = 0;
    let last = performance.now();
    let accum = 0;
    const stepMs = 1000 / FPS;
    const tick = (now: number) => {
      raf = requestAnimationFrame(tick);
      let dt = now - last;
      last = now;
      if (dt > 250) dt = stepMs; // tab inactive — don't catch up
      accum += dt;
      while (accum >= stepMs) {
        accum -= stepMs;
        if (!stepPython(py)) {
          // stop on error; user can reset
          cancelAnimationFrame(raf);
          return;
        }
      }
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [state.kind]);

  return (
    <div className="space-y-4">
      <div className="flex justify-center">
        <HardwareDisplay
          ref={canvasRef}
          scale={SCALE}
          leds={bridges.current.leds}
          keys={bridges.current.keys}
          onUserGesture={() => bridges.current.audio.resume()}
        />
      </div>

      {state.kind === "idle" && (
        <div className="rounded-lg border border-gray-800 bg-panel p-6 text-center">
          <p className="text-sm text-gray-300">
            実機の Python ソースをそのまま Pyodide で実行します (初回 ~10MB)。
          </p>
          <p className="mt-1 text-xs text-gray-500">
            画面・スイッチ・PWMオーディオ・3つのNeoPixel LED だけがブラウザ側でエミュレートされます。
          </p>
          <button
            onClick={onLoad}
            className="mt-3 rounded bg-accent2 px-5 py-2 font-semibold text-black hover:opacity-90"
          >
            ▶ Boot Mario
          </button>
        </div>
      )}

      {state.kind === "loading" && (
        <div className="rounded-lg border border-gray-800 bg-panel p-6 text-center">
          <div className="mx-auto h-2 w-48 overflow-hidden rounded bg-gray-800">
            <div className="h-full w-1/3 animate-pulse bg-accent" />
          </div>
          <p className="mt-2 text-sm text-gray-300">{state.msg}</p>
          <p className="mt-1 text-xs text-gray-500">
            初回はランタイムを CDN からダウンロード中 (数秒〜30秒)。次回からはブラウザキャッシュで高速化。
          </p>
        </div>
      )}

      {state.kind === "error" && (
        <div className="rounded-lg border border-danger bg-danger/10 p-4 text-center">
          <p className="text-sm text-danger">起動失敗: {state.err}</p>
          <button
            onClick={onLoad}
            className="mt-2 rounded bg-panel2 px-4 py-1.5 text-sm hover:bg-gray-700"
          >
            Retry
          </button>
        </div>
      )}

      {state.kind === "ready" && (
        <div className="flex items-center justify-center gap-3">
          <button
            onClick={onReset}
            className="rounded bg-panel2 px-3 py-1.5 text-sm hover:bg-gray-700"
          >
            ↻ Reset to Title
          </button>
          <span className="text-xs text-gray-500">
            実機の Python が動作中 — 画面・操作・音はそのままミラー
          </span>
        </div>
      )}

      <div className="rounded-lg border border-gray-800 bg-panel p-3 text-xs text-gray-400">
        <p className="font-semibold text-gray-300">操作:</p>
        <ul className="mt-1 list-disc space-y-0.5 pl-5">
          <li><kbd className="rounded bg-panel2 px-1">A</kbd> / <kbd className="rounded bg-panel2 px-1">←</kbd> = SW1 (ジャンプ / 決定)</li>
          <li><kbd className="rounded bg-panel2 px-1">S</kbd> / <kbd className="rounded bg-panel2 px-1">↓</kbd> = SW2 (しゃがみ / ファイア / 戻る)</li>
          <li><kbd className="rounded bg-panel2 px-1">D</kbd> / <kbd className="rounded bg-panel2 px-1">→</kbd> = SW3 (ダッシュ / 進む)</li>
          <li>下部の SW1/SW2/SW3 ボタンをタップでも入力可</li>
          <li>プレイ中 A+S+D を3秒長押しでタイトルへ戻る (実機と同じ)</li>
        </ul>
      </div>
    </div>
  );
}
