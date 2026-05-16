// Web Audio playback for BGM previews + simple SFX.
// Uses a single square-wave oscillator (mimics PWM speaker output).
import { freqOf } from "./notes";
import { BgmTrack } from "./types";

let ctx: AudioContext | null = null;
let osc: OscillatorNode | null = null;
let gain: GainNode | null = null;
let timer: number | null = null;

function ensureCtx(): AudioContext {
  if (!ctx) {
    const Win = window as typeof window & { webkitAudioContext?: typeof AudioContext };
    ctx = new (Win.AudioContext || Win.webkitAudioContext!)();
  }
  return ctx;
}

export function startTone(frequency: number, volume = 0.08) {
  const c = ensureCtx();
  stopTone();
  if (frequency <= 0) return;
  osc = c.createOscillator();
  osc.type = "square";
  osc.frequency.value = frequency;
  gain = c.createGain();
  gain.gain.value = volume;
  osc.connect(gain).connect(c.destination);
  osc.start();
}

export function stopTone() {
  if (osc) {
    try { osc.stop(); } catch {}
    osc.disconnect();
    osc = null;
  }
  if (gain) {
    gain.disconnect();
    gain = null;
  }
}

export function stopBgm() {
  stopTone();
  if (timer !== null) {
    window.clearTimeout(timer);
    timer = null;
  }
}

/** Play a track once or loop forever. Returns a stop function. */
export function playBgm(track: BgmTrack, opts: { loop?: boolean; volume?: number } = {}): () => void {
  stopBgm();
  if (!track.length) return () => {};
  let idx = 0;
  const loop = opts.loop ?? true;
  const vol = opts.volume ?? 0.08;
  const advance = () => {
    if (idx >= track.length) {
      if (loop) idx = 0;
      else { stopBgm(); return; }
    }
    const [pitch, dur] = track[idx];
    const f = freqOf(pitch);
    if (f > 0) startTone(f, vol); else stopTone();
    idx++;
    timer = window.setTimeout(advance, Math.max(20, dur));
  };
  advance();
  return stopBgm;
}

/** Beep one note (for note-grid editing). */
export function beepNote(pitch: string | number, durMs = 120, volume = 0.08) {
  const f = freqOf(pitch);
  if (f <= 0) return;
  startTone(f, volume);
  window.setTimeout(() => stopTone(), durMs);
}
