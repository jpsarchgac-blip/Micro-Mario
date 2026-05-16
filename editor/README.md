# Micro-Mario Editor

Next.js 14 で作られたカスタムコンテンツ作成ツール。
**マップ作成 / ブロック作成 / BGM 作曲 / ブラウザ試遊** を1つのアプリに統合し、
最終的に Pico に転送する `custom.dat` (JSON) を書き出します。

## セットアップ

```bash
cd editor
npm install
npm run dev
```

ブラウザで http://localhost:3000 を開いてください。

## 機能

| ツール | パス | 説明 |
|---|---|---|
| Map Editor | `/map-editor` | タイルを配置してステージを作成。エンティティ・スタート・ゴール・物理プレビュー(Jump reach overlay) |
| Block Designer | `/block-editor` | 8x8 ピクセルアートで新しいタイルを作成。挙動 4種類 (solid/platform/lethal/passable) |
| BGM Composer | `/bgm-composer` | ピアノロール形式で BGM を作曲。Web Audio で即プレビュー、ループ再生対応 |
| Play | `/play` | 編集中のステージを矢印キー+X/Z でテストプレイ。物理は `player.py` の TS ポート |

## エクスポート/インポート

- 右上 **Export custom.dat** で JSON ダウンロード → Pico のルートに `custom.dat` として配置
- 右上 **Import** で既存の `custom.dat` を読み込んで編集再開可
- データは LocalStorage にも自動保存 (キー: `micro-mario:project:v1`)

## 操作 (Play モード)

| キー | 機能 |
|---|---|
| X / Space / ↑ | ジャンプ (SW1) |
| ↓ / C | しゃがみ (SW2) |
| Z / Shift | ダッシュ (SW3) |
| R | リセット |

## 仕様

- ステージ・ブロック・BGM のフォーマット詳細は `../docs/MAP_GUIDE.md` を参照
- 物理パラメータ (`lib/physics.ts`) は `player.py` の値と同期している
- カスタムブロック ID は 16-255 (16-20 は組み込みが予約)
- terrain エンコードは自動: 全 ID ≤15 なら 1-hex/タイル、それ以外は 2-hex/タイル

## アーキテクチャ

```
editor/
├── app/                Next.js App Router pages
│   ├── layout.tsx     共通レイアウト+Header+ProjectProvider
│   ├── page.tsx       Home (ツール選択+プロジェクト概要)
│   ├── map-editor/
│   ├── block-editor/
│   ├── bgm-composer/
│   └── play/
├── components/        UI コンポーネント
│   ├── shared/Header.tsx       ナビ+Import/Export
│   ├── MapEditor/              タイル・エンティティパレット、Canvas
│   ├── BlockEditor/            8x8 ピクセルグリッド、プレビュー
│   ├── BgmComposer/            ピアノロール
│   └── GamePlayer/             ゲームキャンバス
└── lib/               共通ロジック
    ├── types.ts                CustomProject / Stage / BlockDef / NoteEntry
    ├── tiles.ts                ビルトインタイル定義・スプライト
    ├── notes.ts                NOTES 辞書 (music.py ミラー)
    ├── entities.ts             エンティティ種別
    ├── audio.ts                Web Audio 再生
    ├── physics.ts              物理 (player.py ミラー)
    ├── persist.ts              LocalStorage I/O + JSON シリアライズ
    └── project-context.tsx     React Context
```

## 制限・既知の挙動

- Play モードの敵AIは未実装(表示のみ)。地形・ジャンプ・致死タイルは本物どおり
- 和音不可(PWM 1ch 制約のため、BGM コンポーザもメロディラインのみ)
- カスタムブロックを使ったステージは Pico 側でも `custom_stages.py` の `_register_block()` 経由で同じスプライトが登録される
