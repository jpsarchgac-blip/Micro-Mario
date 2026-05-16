"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useProject } from "@/lib/project-context";
import { downloadJson, toCustomDatJson, readJsonFile } from "@/lib/persist";
import { useRef } from "react";

const NAV = [
  { href: "/", label: "Home" },
  { href: "/map-editor", label: "Map" },
  { href: "/block-editor", label: "Block" },
  { href: "/bgm-composer", label: "BGM" },
  { href: "/play", label: "Play" },
];

export function Header() {
  const path = usePathname();
  const { project, setProject } = useProject();
  const fileRef = useRef<HTMLInputElement>(null);

  const onExport = () => {
    const data = toCustomDatJson(project);
    downloadJson(data, "custom.dat");
  };

  const onImport = async (file: File) => {
    try {
      const json = (await readJsonFile(file)) as Record<string, unknown>;
      // Decode blocks (hex -> bytes) and re-add stages as-is.
      const blocks = (json.blocks as Array<Record<string, unknown>> | undefined ?? []).map((b) => ({
        id: Number(b.id),
        name: String(b.name),
        behavior: b.behavior as "solid" | "platform" | "lethal" | "passable",
        sprite:
          typeof b.sprite === "string"
            ? hexToBytes(b.sprite as string)
            : (b.sprite as number[]),
      }));
      const bgm = (json.bgm as Record<string, [string | number, number][]> | undefined) ?? {};
      const stages = (json.stages as Array<Record<string, unknown>> | undefined ?? []).map((s) => decodeStage(s));
      setProject({
        version: 1,
        blocks,
        bgm,
        stages,
      });
    } catch (e) {
      alert("Import failed: " + (e as Error).message);
    }
  };

  return (
    <header className="border-b border-gray-800 bg-panel">
      <div className="mx-auto flex max-w-7xl items-center gap-4 px-4 py-3">
        <Link href="/" className="text-lg font-semibold text-accent">
          MICRO-MARIO <span className="text-gray-500">/ EDITOR</span>
        </Link>
        <nav className="flex gap-1 text-sm">
          {NAV.map((n) => (
            <Link
              key={n.href}
              href={n.href}
              className={
                "rounded px-3 py-1.5 transition " +
                (path === n.href
                  ? "bg-accent text-black"
                  : "text-gray-300 hover:bg-panel2")
              }
            >
              {n.label}
            </Link>
          ))}
        </nav>
        <div className="ml-auto flex items-center gap-2 text-xs">
          <span className="text-gray-500">
            {project.stages.length} stages / {project.blocks.length} blocks /{" "}
            {Object.keys(project.bgm).length} bgm
          </span>
          <input
            ref={fileRef}
            type="file"
            accept="application/json"
            className="hidden"
            onChange={(e) => {
              const f = e.target.files?.[0];
              if (f) onImport(f);
              e.target.value = "";
            }}
          />
          <button
            className="rounded bg-panel2 px-3 py-1.5 hover:bg-gray-700"
            onClick={() => fileRef.current?.click()}
          >
            Import
          </button>
          <button
            className="rounded bg-accent2 px-3 py-1.5 font-semibold text-black hover:opacity-90"
            onClick={onExport}
          >
            Export custom.dat
          </button>
        </div>
      </div>
    </header>
  );
}

function hexToBytes(hex: string): number[] {
  const out: number[] = [];
  for (let i = 0; i + 1 < hex.length; i += 2) {
    out.push(parseInt(hex.substr(i, 2), 16));
  }
  return out;
}

function decodeStage(s: Record<string, unknown>) {
  const rows = Number(s.rows ?? 12);
  const terrainSrc = (s.terrain as string[] | undefined) ?? [];
  const terrain = terrainSrc.map((col) => decodeCol(col, rows));
  return {
    name: String(s.name ?? "STAGE"),
    bgm: String(s.bgm ?? "overworld"),
    rows,
    width: Number(s.width ?? terrain.length),
    terrain,
    time_limit: Number(s.time_limit ?? 100),
    water: Boolean(s.water ?? false),
    gravity_scale: Number(s.gravity_scale ?? 1.0),
    start_col: Number(s.start_col ?? 2),
    start_row: Number(s.start_row ?? rows - 4),
    goal_col: Number(s.goal_col ?? terrain.length - 5),
    flag_col: s.flag_col != null ? Number(s.flag_col) : undefined,
    pipe_col: s.pipe_col != null ? Number(s.pipe_col) : undefined,
    pipe_return_col: s.pipe_return_col != null ? Number(s.pipe_return_col) : undefined,
    objects: (s.objects as Array<[number, number, string]> | undefined) ?? [],
    enemy_sets: (s.enemy_sets as { easy?: any[]; normal?: any[]; hard?: any[] }) ?? {},
  };
}

function decodeCol(s: string, rows: number): number[] {
  if (s.includes(",")) {
    const parts = s.split(",").map((p) => p.trim());
    const ids = parts.map((p) => (p.startsWith("0x") ? parseInt(p, 16) : parseInt(p, 10)));
    while (ids.length < rows) ids.unshift(0);
    return ids.slice(0, rows);
  }
  if (s.length === rows * 2) {
    const ids: number[] = [];
    for (let i = 0; i < rows * 2; i += 2) ids.push(parseInt(s.substr(i, 2), 16));
    return ids;
  }
  let str = s;
  if (str.length < rows) str = "0".repeat(rows - str.length) + str;
  return str.slice(0, rows).split("").map((c) => parseInt(c, 16) || 0);
}
