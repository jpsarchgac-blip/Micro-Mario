"use client";
import { useEffect, useRef } from "react";

/** 3-button (SW1/SW2/SW3) keyboard input emulating the Pico device.
 *
 * Mapping:
 *   ← / A → SW1 (jump / select)
 *   ↓ / S → SW2 (fire / cancel / duck)
 *   → / D → SW3 (dash / forward)
 *
 * Returns refs so render-loop callers don't trigger React re-renders.
 * - `pressedRef.current[i]` true for one frame after press edge (caller must consume + clear)
 * - `heldRef.current[i]`    true while button is held
 *
 * Optional handler: invoked on each new press (edge). Use this for menu navigation
 * where you want React state updates.
 */
export function useKeys(onPress?: (button: 0 | 1 | 2) => void) {
  const heldRef = useRef<[boolean, boolean, boolean]>([false, false, false]);
  const pressedRef = useRef<[boolean, boolean, boolean]>([false, false, false]);
  const handlerRef = useRef(onPress);
  handlerRef.current = onPress;

  useEffect(() => {
    const idxFor = (e: KeyboardEvent): 0 | 1 | 2 | null => {
      const k = e.key.toLowerCase();
      if (k === "a" || e.key === "ArrowLeft") return 0;
      if (k === "s" || e.key === "ArrowDown") return 1;
      if (k === "d" || e.key === "ArrowRight") return 2;
      return null;
    };
    const onDown = (e: KeyboardEvent) => {
      const i = idxFor(e);
      if (i === null) return;
      e.preventDefault();
      if (!heldRef.current[i]) {
        pressedRef.current[i] = true;
        handlerRef.current?.(i);
      }
      heldRef.current[i] = true;
    };
    const onUp = (e: KeyboardEvent) => {
      const i = idxFor(e);
      if (i === null) return;
      e.preventDefault();
      heldRef.current[i] = false;
    };
    window.addEventListener("keydown", onDown);
    window.addEventListener("keyup", onUp);
    return () => {
      window.removeEventListener("keydown", onDown);
      window.removeEventListener("keyup", onUp);
    };
  }, []);

  /** Consume + clear pressed flags. Returns snapshot. */
  const consume = () => {
    const p: [boolean, boolean, boolean] = [
      pressedRef.current[0],
      pressedRef.current[1],
      pressedRef.current[2],
    ];
    pressedRef.current = [false, false, false];
    return { pressed: p, held: [...heldRef.current] as [boolean, boolean, boolean] };
  };

  return { heldRef, pressedRef, consume };
}
