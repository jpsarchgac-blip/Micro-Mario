#!/usr/bin/env python3
# tools/extract_stages.py
# stages_new.py のステージ定義を Next.js エディタが消費しやすい JSON に変換する。
# 出力先: editor/public/builtin-stages.json
#
# 実行方法:
#   python3 tools/extract_stages.py
# (Pico 上では実行不要。開発機で1度走らせて生成された JSON をコミット)
import json
import os
import sys

# MicroPython 互換のモジュールスタブを注入
class _StubFramebuf:
    MONO_VLSB = 0
    class FrameBuffer:
        def __init__(self, *a, **k): pass

sys.modules.setdefault('framebuf', _StubFramebuf())

# プロジェクトルートを sys.path に追加
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import stages_new as sn


def to_stage_json(s):
    """ステージdictをJSONシリアライズ可能な形式に変換。"""
    return {
        'name': s.get('name', 'STAGE'),
        'bgm': s.get('bgm', 'overworld'),
        'rows': s.get('rows', 12),
        'width': s.get('width', len(s['terrain'])),
        'terrain': [list(col) for col in s['terrain']],  # bytes → int list
        'time_limit': s.get('time_limit', 100),
        'water': s.get('water', False),
        'gravity_scale': s.get('gravity_scale', 1.0),
        'start_col': s.get('start_col', 2),
        'start_row': s.get('start_row', s.get('rows', 12) - 4),
        'goal_col': s.get('goal_col', -1),
        'flag_col': s.get('flag_col'),
        'pipe_col': s.get('pipe_col'),
        'pipe_return_col': s.get('pipe_return_col'),
        'objects': [list(o) for o in s.get('objects', [])],
        'enemy_sets': {
            k: [list(o) for o in v]
            for k, v in s.get('enemy_sets', {}).items()
        },
    }


def main():
    stages = [to_stage_json(s) for s in sn.STAGES_NEW]
    pipe_sub = to_stage_json(sn.PIPE_SUBSTAGE)
    out = {
        'version': 1,
        'stages': stages,
        'pipe_substage': pipe_sub,
    }
    out_path = os.path.join(ROOT, 'editor', 'public', 'builtin-stages.json')
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w') as f:
        json.dump(out, f, separators=(',', ':'))
    size = os.path.getsize(out_path)
    print(f'Wrote {len(stages)} stages + pipe substage to {out_path} ({size} bytes)')


if __name__ == '__main__':
    main()
