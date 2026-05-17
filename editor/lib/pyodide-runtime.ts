// Pyodide loader + Python VFS setup for the Micro-Mario emulator.
// Loads Pyodide from CDN (avoids bundling 10MB), mounts the project's .py files
// into Pyodide's filesystem, then exposes init/step bindings for the React layer.
import { installBridges } from "./hardware-bridge";

declare global {
  interface Window {
    loadPyodide?: (cfg?: { indexURL?: string }) => Promise<PyodideInstance>;
  }
}

const PYODIDE_VERSION = "0.26.4";
const PYODIDE_INDEX = `https://cdn.jsdelivr.net/pyodide/v${PYODIDE_VERSION}/full/`;

// Subset of Pyodide API we actually use.
export interface PyodideInstance {
  runPython: (code: string) => unknown;
  runPythonAsync: (code: string) => Promise<unknown>;
  loadPackage: (names: string | string[]) => Promise<void>;
  globals: {
    get: (name: string) => unknown;
    set: (name: string, value: unknown) => void;
  };
  FS: {
    mkdirTree: (path: string) => void;
    writeFile: (path: string, data: Uint8Array | string) => void;
    readdir: (path: string) => string[];
  };
}

let _instance: PyodideInstance | null = null;
let _loadingPromise: Promise<PyodideInstance> | null = null;

async function loadScript(src: string): Promise<void> {
  return new Promise((resolve, reject) => {
    if (document.querySelector(`script[data-src="${src}"]`)) {
      resolve();
      return;
    }
    const s = document.createElement("script");
    s.src = src;
    s.async = true;
    s.dataset.src = src;
    s.onload = () => resolve();
    s.onerror = () => reject(new Error(`Failed to load ${src}`));
    document.head.appendChild(s);
  });
}

async function fetchText(path: string): Promise<string> {
  const r = await fetch(path);
  if (!r.ok) throw new Error(`fetch ${path}: ${r.status}`);
  return r.text();
}

async function fetchJson<T>(path: string): Promise<T> {
  const r = await fetch(path);
  if (!r.ok) throw new Error(`fetch ${path}: ${r.status}`);
  return r.json() as Promise<T>;
}

/** Load Pyodide from CDN, mount sources, and return a singleton instance. */
export function loadPyodideRuntime(
  onProgress?: (msg: string) => void
): Promise<PyodideInstance> {
  if (_instance) return Promise.resolve(_instance);
  if (_loadingPromise) return _loadingPromise;

  _loadingPromise = (async () => {
    onProgress?.("Installing hardware bridges...");
    installBridges();

    onProgress?.("Loading Pyodide runtime (~6MB)...");
    await loadScript(`${PYODIDE_INDEX}pyodide.js`);
    if (!window.loadPyodide) throw new Error("Pyodide failed to attach loadPyodide");
    const py = await window.loadPyodide({ indexURL: PYODIDE_INDEX });

    onProgress?.("Mounting Python sources...");
    // Stubs go in /home/pyodide/stubs (added to sys.path first so they override).
    // Project sources go in /home/pyodide/game.
    py.FS.mkdirTree("/home/pyodide/stubs");
    py.FS.mkdirTree("/home/pyodide/game");

    const stubFiles = [
      "machine.py",
      "neopixel.py",
      "framebuf.py",
      "ssd1306.py",
      "time_shim.py",
      "urandom.py",
      "ujson.py",
      "micropython.py",
      "webloop.py",
    ];
    for (const f of stubFiles) {
      const text = await fetchText(`/python-stubs/${f}`);
      py.FS.writeFile(`/home/pyodide/stubs/${f}`, text);
    }

    const manifest = await fetchJson<string[]>(`/python/manifest.json`);
    for (const f of manifest) {
      if (f === "manifest.json") continue;
      // Skip ssd1306 (our stub above shadows the real driver)
      if (f === "ssd1306.py") continue;
      const text = await fetchText(`/python/${f}`);
      py.FS.writeFile(`/home/pyodide/game/${f}`, text);
    }

    onProgress?.("Configuring sys.path...");
    py.runPython(`
import sys
sys.path.insert(0, '/home/pyodide/stubs')
sys.path.insert(1, '/home/pyodide/game')
`);

    onProgress?.("Initialising game...");
    await py.runPythonAsync(`
import webloop
webloop.init()
`);

    _instance = py;
    onProgress?.("Ready!");
    return py;
  })();

  return _loadingPromise;
}

/** Call one frame of game logic. Returns true on success. */
export function stepPython(py: PyodideInstance): boolean {
  try {
    py.runPython("webloop.step()");
    return true;
  } catch (e) {
    console.error("[pyodide] step error:", e);
    return false;
  }
}

/** Force a full re-init of the game (returns to title). */
export async function resetPython(py: PyodideInstance) {
  try {
    await py.runPythonAsync(`
import webloop
webloop.reset()
webloop.init()
`);
  } catch (e) {
    console.error("[pyodide] reset error:", e);
  }
}
