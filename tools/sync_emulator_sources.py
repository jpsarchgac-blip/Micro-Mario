#!/usr/bin/env python3
# tools/sync_emulator_sources.py
# ルートの *.py を editor/public/python/ にコピーする。
# Pyodide ベースのエミュレーターが実機ソースを VFS に読み込めるようにする。
#
# 実行: python3 tools/sync_emulator_sources.py
# 自動: editor/package.json の predev / prebuild で呼ばれる
import os
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = ROOT
DST_DIR = os.path.join(ROOT, "editor", "public", "python")

# 同期しないファイル (テスト用 / 不要)
EXCLUDE = {
    "make_art.py",  # 開発用スクリプト
}


def main() -> int:
    if not os.path.isdir(os.path.join(ROOT, "editor")):
        print("error: editor/ not found relative to repo root", file=sys.stderr)
        return 1
    os.makedirs(DST_DIR, exist_ok=True)

    # 既存の .py を一旦削除 (削除されたファイルが残らないように)
    for old in os.listdir(DST_DIR):
        if old.endswith(".py"):
            os.remove(os.path.join(DST_DIR, old))

    count = 0
    for name in sorted(os.listdir(SRC_DIR)):
        if not name.endswith(".py"):
            continue
        if name in EXCLUDE:
            continue
        shutil.copy2(os.path.join(SRC_DIR, name), os.path.join(DST_DIR, name))
        count += 1

    # マニフェスト生成 (Pyodide 起動時の fetch 用)
    manifest = sorted(
        f for f in os.listdir(DST_DIR) if f.endswith(".py")
    )
    with open(os.path.join(DST_DIR, "manifest.json"), "w") as f:
        import json
        json.dump(manifest, f)

    print(f"Synced {count} Python files to {DST_DIR}")
    print(f"Manifest: {len(manifest)} entries")
    return 0


if __name__ == "__main__":
    sys.exit(main())
