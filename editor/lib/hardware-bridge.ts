// Hardware bridges between Pyodide Python and browser hardware emulation.
// These are exposed on globalThis so the Python stubs (machine.py, neopixel.py,
// ssd1306.py) can read/write them directly via `import js; js.globalThis.__mm_*`.

const SCREEN_W = 128;
const SCREEN_H = 64;

// =====================================================================
// OLED 128x64 monochrome canvas
// =====================================================================
export class OledBridge {
  canvas: HTMLCanvasElement | null = null;
  ctx: CanvasRenderingContext2D | null = null;
  scale = 4;
  fg = "#fef9c3";
  bg = "#0a0a14";
  /** Last buffer received from Python (MONO_VLSB, 1024 bytes). */
  private lastBuf: Uint8Array | null = null;
  /** ImageData reused per show for speed. */
  private imageData: ImageData | null = null;

  attach(canvas: HTMLCanvasElement, scale: number) {
    this.canvas = canvas;
    this.scale = scale;
    canvas.width = SCREEN_W * scale;
    canvas.height = SCREEN_H * scale;
    const c = canvas.getContext("2d");
    if (c) {
      c.imageSmoothingEnabled = false;
      this.ctx = c;
      // Pre-clear
      c.fillStyle = this.bg;
      c.fillRect(0, 0, canvas.width, canvas.height);
    }
    // Re-render last buffer (if any) so the new canvas shows the latest frame
    if (this.lastBuf) this.draw(this.lastBuf);
  }

  /** Called from Python ssd1306 stub: onShow(bytearray). */
  onShow(bufProxy: unknown) {
    // Pyodide passes bytearray as a proxy with toJs() yielding Uint8Array,
    // or it's already a Uint8Array depending on version.
    let buf: Uint8Array | null = null;
    if (bufProxy instanceof Uint8Array) {
      buf = bufProxy;
    } else if (bufProxy && typeof (bufProxy as { toJs?: () => Uint8Array }).toJs === "function") {
      const v = (bufProxy as { toJs: () => Uint8Array | ArrayBuffer | number[] }).toJs();
      if (v instanceof Uint8Array) buf = v;
      else if (v instanceof ArrayBuffer) buf = new Uint8Array(v);
      else if (Array.isArray(v)) buf = new Uint8Array(v);
    } else if (Array.isArray(bufProxy)) {
      buf = new Uint8Array(bufProxy as number[]);
    }
    if (!buf || buf.length < (SCREEN_W * SCREEN_H) / 8) return;
    // Copy so subsequent Python mutations don't affect us mid-draw
    this.lastBuf = new Uint8Array(buf.subarray(0, (SCREEN_W * SCREEN_H) / 8));
    this.draw(this.lastBuf);
  }

  /** Render a MONO_VLSB buffer to the canvas at current scale. */
  draw(buf: Uint8Array) {
    const ctx = this.ctx;
    if (!ctx) return;
    const scale = this.scale;
    // Direct pixel render via fillRect (simple, fast enough for 128x64)
    ctx.fillStyle = this.bg;
    ctx.fillRect(0, 0, SCREEN_W * scale, SCREEN_H * scale);
    ctx.fillStyle = this.fg;
    const pages = SCREEN_H / 8;
    for (let p = 0; p < pages; p++) {
      const yTop = p * 8;
      for (let x = 0; x < SCREEN_W; x++) {
        const byte = buf[p * SCREEN_W + x];
        if (!byte) continue;
        for (let bit = 0; bit < 8; bit++) {
          if (byte & (1 << bit)) {
            ctx.fillRect(x * scale, (yTop + bit) * scale, scale, scale);
          }
        }
      }
    }
  }
}

// =====================================================================
// NeoPixel 3 LEDs
// =====================================================================
export class LedBridge {
  /** RGB values for each LED (0..255 after scaling). */
  rgb: Array<[number, number, number]> = [[0, 0, 0], [0, 0, 0], [0, 0, 0]];
  private listeners: Array<(idx: number, r: number, g: number, b: number) => void> = [];

  /** Called from Python neopixel stub. Input range from game is 0..40 typically. */
  write(idx: number, r: number, g: number, b: number) {
    if (idx < 0 || idx >= this.rgb.length) return;
    // Scale up (max 40 → 255-ish) so the LED looks bright in browser
    const scale = 5.5;
    const R = Math.min(255, Math.round(r * scale));
    const G = Math.min(255, Math.round(g * scale));
    const B = Math.min(255, Math.round(b * scale));
    this.rgb[idx] = [R, G, B];
    for (const l of this.listeners) l(idx, R, G, B);
  }

  subscribe(fn: (idx: number, r: number, g: number, b: number) => void) {
    this.listeners.push(fn);
    return () => {
      const i = this.listeners.indexOf(fn);
      if (i >= 0) this.listeners.splice(i, 1);
    };
  }
}

// =====================================================================
// PWM audio (square wave, single channel)
// =====================================================================
export class AudioBridge {
  private ctx: AudioContext | null = null;
  private osc: OscillatorNode | null = null;
  private gain: GainNode | null = null;
  private currentFreq = 0;
  private currentDuty = 0;

  private ensure() {
    if (this.ctx) return this.ctx;
    const W = window as typeof window & { webkitAudioContext?: typeof AudioContext };
    this.ctx = new (W.AudioContext || W.webkitAudioContext!)();
    return this.ctx;
  }

  /** Resume on first user gesture (browser autoplay policy). */
  resume() {
    const c = this.ensure();
    if (c.state === "suspended") c.resume().catch(() => {});
  }

  /** Python calls: __mm_audio.set(freq, duty_u16). */
  set(freq: number, duty: number) {
    if (typeof freq !== "number" || typeof duty !== "number") return;
    this.currentFreq = freq;
    this.currentDuty = duty;
    const c = this.ctx;
    if (!c) return; // audio not yet resumed
    if (duty <= 0 || freq <= 0) {
      this.stopOsc();
      return;
    }
    if (!this.osc) {
      this.osc = c.createOscillator();
      this.osc.type = "square";
      this.gain = c.createGain();
      this.osc.connect(this.gain).connect(c.destination);
      try { this.osc.start(); } catch {}
    }
    try {
      this.osc.frequency.setValueAtTime(freq, c.currentTime);
    } catch {}
    if (this.gain) {
      // Map duty 0..65535 → gain 0..0.12 (avoid harsh peaks)
      const g = Math.min(0.12, (duty / 65535) * 0.4);
      this.gain.gain.setTargetAtTime(g, c.currentTime, 0.005);
    }
  }

  private stopOsc() {
    if (this.gain) {
      this.gain.gain.setTargetAtTime(0, this.ctx!.currentTime, 0.005);
    }
  }

  shutdown() {
    if (this.osc) {
      try { this.osc.stop(); } catch {}
      this.osc.disconnect();
      this.osc = null;
    }
    if (this.gain) {
      this.gain.disconnect();
      this.gain = null;
    }
    if (this.ctx) {
      this.ctx.close().catch(() => {});
      this.ctx = null;
    }
  }
}

// =====================================================================
// Key state (SW1/SW2/SW3 booleans)
// =====================================================================
export class KeyBridge {
  sw1 = false;
  sw2 = false;
  sw3 = false;
  /** Set up window keyboard listeners. Returns a cleanup function. */
  attachKeyboard(): () => void {
    const onDown = (e: KeyboardEvent) => {
      const k = e.key.toLowerCase();
      let hit = false;
      if (k === "a" || e.key === "ArrowLeft")  { this.sw1 = true; hit = true; }
      if (k === "s" || e.key === "ArrowDown")  { this.sw2 = true; hit = true; }
      if (k === "d" || e.key === "ArrowRight") { this.sw3 = true; hit = true; }
      if (hit) e.preventDefault();
    };
    const onUp = (e: KeyboardEvent) => {
      const k = e.key.toLowerCase();
      let hit = false;
      if (k === "a" || e.key === "ArrowLeft")  { this.sw1 = false; hit = true; }
      if (k === "s" || e.key === "ArrowDown")  { this.sw2 = false; hit = true; }
      if (k === "d" || e.key === "ArrowRight") { this.sw3 = false; hit = true; }
      if (hit) e.preventDefault();
    };
    window.addEventListener("keydown", onDown);
    window.addEventListener("keyup", onUp);
    return () => {
      window.removeEventListener("keydown", onDown);
      window.removeEventListener("keyup", onUp);
    };
  }

  /** Touch / pointer-style setter (for on-screen virtual buttons). */
  setKey(idx: 0 | 1 | 2, down: boolean) {
    if (idx === 0) this.sw1 = down;
    else if (idx === 1) this.sw2 = down;
    else if (idx === 2) this.sw3 = down;
  }
}

// =====================================================================
// Singleton wiring — exposed on globalThis for Python to read.
// =====================================================================
declare global {
  // eslint-disable-next-line no-var
  var __mm_oled: OledBridge | undefined;
  // eslint-disable-next-line no-var
  var __mm_leds: LedBridge | undefined;
  // eslint-disable-next-line no-var
  var __mm_audio: AudioBridge | undefined;
  // eslint-disable-next-line no-var
  var __mm_keys: KeyBridge | undefined;
}

let _wired = false;

export function installBridges(): {
  oled: OledBridge;
  leds: LedBridge;
  audio: AudioBridge;
  keys: KeyBridge;
} {
  if (!_wired) {
    globalThis.__mm_oled  = new OledBridge();
    globalThis.__mm_leds  = new LedBridge();
    globalThis.__mm_audio = new AudioBridge();
    globalThis.__mm_keys  = new KeyBridge();
    _wired = true;
  }
  return {
    oled:  globalThis.__mm_oled!,
    leds:  globalThis.__mm_leds!,
    audio: globalThis.__mm_audio!,
    keys:  globalThis.__mm_keys!,
  };
}
