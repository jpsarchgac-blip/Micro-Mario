"use client";
import Link from "next/link";
import { useProject } from "@/lib/project-context";

const TOOLS = [
  {
    href: "/map-editor",
    title: "Map Editor",
    desc: "タイルを置いてカスタムステージを作成。エンティティ配置・物理プレビュー付き。",
    icon: "🗺️",
  },
  {
    href: "/block-editor",
    title: "Block Designer",
    desc: "8x8 のドット絵で新しいタイル(ブロック)を作る。挙動はsolid/platform/lethal/passable。",
    icon: "🧱",
  },
  {
    href: "/bgm-composer",
    title: "BGM Composer",
    desc: "ピアノロール形式で BGM を作曲。Web Audio で即プレビュー。",
    icon: "🎵",
  },
  {
    href: "/play",
    title: "Emulator / Play",
    desc: "実機と同じ画面(128×64)・モード選択をブラウザで体験。A/S/D または ←↓→ で操作。",
    icon: "🎮",
  },
];

export default function Home() {
  const { project } = useProject();

  return (
    <div className="space-y-8">
      <section>
        <h1 className="text-3xl font-bold">Micro-Mario Editor</h1>
        <p className="mt-2 text-gray-400">
          NEW モード/CUSTOM モード用のステージ・ブロック・BGM を作成し、
          <code className="mx-1 rounded bg-panel2 px-1.5 py-0.5">custom.dat</code>
          として書き出します。Pico のルートに置けば CUSTOM MODE から遊べます。
        </p>
      </section>

      <section className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        {TOOLS.map((t) => (
          <Link
            key={t.href}
            href={t.href}
            className="block rounded-lg border border-gray-800 bg-panel p-5 transition hover:border-accent hover:bg-panel2"
          >
            <div className="text-3xl">{t.icon}</div>
            <div className="mt-2 text-lg font-semibold">{t.title}</div>
            <div className="mt-1 text-sm text-gray-400">{t.desc}</div>
          </Link>
        ))}
      </section>

      <section className="rounded-lg border border-gray-800 bg-panel p-5">
        <h2 className="mb-3 text-lg font-semibold">Current Project</h2>
        <div className="grid grid-cols-3 gap-4 text-sm">
          <div>
            <div className="text-gray-500">Stages</div>
            <div className="text-2xl font-semibold text-accent">{project.stages.length}</div>
            {project.stages.length > 0 && (
              <ul className="mt-2 space-y-1 text-gray-300">
                {project.stages.map((s, i) => (
                  <li key={i} className="truncate">
                    {i + 1}. {s.name} <span className="text-gray-500">({s.width}×{s.rows})</span>
                  </li>
                ))}
              </ul>
            )}
          </div>
          <div>
            <div className="text-gray-500">Custom Blocks</div>
            <div className="text-2xl font-semibold text-accent">{project.blocks.length}</div>
            {project.blocks.length > 0 && (
              <ul className="mt-2 space-y-1 text-gray-300">
                {project.blocks.map((b) => (
                  <li key={b.id} className="truncate">
                    #{b.id} {b.name} <span className="text-gray-500">({b.behavior})</span>
                  </li>
                ))}
              </ul>
            )}
          </div>
          <div>
            <div className="text-gray-500">BGM Tracks</div>
            <div className="text-2xl font-semibold text-accent">{Object.keys(project.bgm).length}</div>
            {Object.keys(project.bgm).length > 0 && (
              <ul className="mt-2 space-y-1 text-gray-300">
                {Object.keys(project.bgm).map((name) => (
                  <li key={name} className="truncate">
                    🎵 {name} <span className="text-gray-500">({project.bgm[name].length} notes)</span>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
      </section>

      <section className="rounded-lg border border-gray-800 bg-panel p-5 text-sm text-gray-400">
        <h2 className="mb-2 text-base font-semibold text-gray-200">使い方</h2>
        <ol className="list-decimal space-y-1 pl-5">
          <li>各エディタで作成したデータは自動的にブラウザの LocalStorage に保存される</li>
          <li>右上の <strong>Export custom.dat</strong> でJSONをダウンロード</li>
          <li>そのファイルを Pico のルートディレクトリ(<code>main.py</code> と同じ場所)に <code>custom.dat</code> として配置</li>
          <li>起動 → CUSTOM MODE を選ぶと、組み込みステージに続けて読み込まれる</li>
        </ol>
      </section>
    </div>
  );
}
