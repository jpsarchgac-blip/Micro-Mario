"use client";
import { forwardRef, useEffect, useRef, useState } from "react";
import { LedBridge, KeyBridge } from "@/lib/hardware-bridge";

interface Props {
  scale?: number;
  leds: LedBridge;
  keys: KeyBridge;
  onUserGesture?: () => void;
}

/** Physical-device-style frame: OLED canvas + 3 NeoPixels + 3 buttons (A/S/D). */
export const HardwareDisplay = forwardRef<HTMLCanvasElement, Props>(
  function HardwareDisplay({ scale = 4, leds, keys, onUserGesture }, canvasRef) {
    const [ledColors, setLedColors] = useState<Array<[number, number, number]>>([
      [0, 0, 0], [0, 0, 0], [0, 0, 0],
    ]);

    useEffect(() => {
      // Subscribe to LED updates and reflect into local state for re-render
      const unsub = leds.subscribe(() => {
        setLedColors([leds.rgb[0], leds.rgb[1], leds.rgb[2]]);
      });
      return unsub;
    }, [leds]);

    const pressDown = (idx: 0 | 1 | 2) => {
      onUserGesture?.();
      keys.setKey(idx, true);
    };
    const pressUp = (idx: 0 | 1 | 2) => keys.setKey(idx, false);

    return (
      <div className="inline-block rounded-2xl border-4 border-gray-800 bg-gray-950 p-4 shadow-2xl">
        {/* LED strip (top) */}
        <div className="mx-auto mb-3 flex justify-center gap-3" style={{ width: 128 * scale }}>
          {ledColors.map((rgb, i) => (
            <Led key={i} rgb={rgb} label={`LED${i + 1}`} />
          ))}
        </div>

        {/* OLED panel */}
        <div
          className="overflow-hidden rounded border-2 border-gray-700"
          style={{ background: "#0a0a14" }}
          onMouseDown={() => onUserGesture?.()}
        >
          <canvas
            ref={canvasRef}
            width={128 * scale}
            height={64 * scale}
            className="pixel block"
            style={{ background: "#0a0a14" }}
          />
        </div>

        {/* Virtual buttons (bottom) - keyboard-friendly */}
        <div className="mx-auto mt-3 flex justify-between gap-2" style={{ width: 128 * scale }}>
          <VButton
            label="SW1"
            kbd="A / ←"
            desc="JUMP"
            onDown={() => pressDown(0)}
            onUp={() => pressUp(0)}
          />
          <VButton
            label="SW2"
            kbd="S / ↓"
            desc="DUCK / FIRE"
            onDown={() => pressDown(1)}
            onUp={() => pressUp(1)}
          />
          <VButton
            label="SW3"
            kbd="D / →"
            desc="DASH"
            onDown={() => pressDown(2)}
            onUp={() => pressUp(2)}
          />
        </div>
      </div>
    );
  }
);

function Led({ rgb, label }: { rgb: [number, number, number]; label: string }) {
  const [r, g, b] = rgb;
  const brightness = Math.max(r, g, b);
  const on = brightness > 0;
  const glow = on ? `0 0 ${brightness / 12}px rgb(${r},${g},${b})` : "none";
  return (
    <div className="flex flex-col items-center gap-1">
      <div
        className="h-5 w-5 rounded-full border border-gray-700"
        style={{
          background: on ? `rgb(${r},${g},${b})` : "#111",
          boxShadow: glow,
          transition: "background 100ms linear",
        }}
      />
      <span className="text-[9px] font-mono text-gray-500">{label}</span>
    </div>
  );
}

function VButton({
  label,
  kbd,
  desc,
  onDown,
  onUp,
}: {
  label: string;
  kbd: string;
  desc: string;
  onDown: () => void;
  onUp: () => void;
}) {
  const [pressed, setPressed] = useState(false);
  const handle = (down: boolean) => {
    setPressed(down);
    if (down) onDown();
    else onUp();
  };
  return (
    <button
      onPointerDown={(e) => { e.preventDefault(); handle(true); }}
      onPointerUp={(e) => { e.preventDefault(); handle(false); }}
      onPointerCancel={() => handle(false)}
      onPointerLeave={() => pressed && handle(false)}
      className={
        "flex-1 select-none rounded-lg border-2 px-3 py-2 text-center transition " +
        (pressed
          ? "border-accent bg-accent/30 text-accent"
          : "border-gray-700 bg-gray-800 text-gray-300 hover:bg-gray-700")
      }
    >
      <div className="text-sm font-bold">{label}</div>
      <div className="text-[10px] font-mono text-gray-400">{kbd}</div>
      <div className="text-[9px] uppercase text-gray-500">{desc}</div>
    </button>
  );
}
