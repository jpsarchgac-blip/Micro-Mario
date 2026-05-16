# custom_stages.py - ユーザー定義カスタムステージ
#
# 編集方法:
#   1. 直接このファイルの _example_stage() を改造、または下に新しい関数を追加
#   2. もしくは Next.js エディタで生成した custom.dat (JSON) をデバイスのルートに置く
#      → 起動時に自動で読み込まれる
#
# 詳細は docs/MAP_GUIDE.md を参照。
import world_new as wn

A=wn.AIR;G=wn.GROUND;B=wn.BRICK;Q=wn.QBLOCK;C=wn.COIN;S=wn.SPIKE
PT=wn.PIPE_TL;PR=wn.PIPE_TR;PB=wn.PIPE_BL;PD=wn.PIPE_BR
CL=wn.CLOUD_PLAT;GO=wn.GOAL;MA=wn.MAGMA;GR=wn.GRASS;FL=wn.FLAG


def _c(rows,*ids):
    pad=[A]*(rows-len(ids))+list(ids)
    return bytes(pad)

def _flat(rows,n,top_id=A,bot_id=G,bot_n=2):
    c=_c(rows,*([top_id]*(rows-bot_n)),*([bot_id]*bot_n))
    return [c]*n

def _hole(rows,n=1):
    return [bytes([A]*rows)]*n


# ====================================================================
# サンプルカスタムステージ1: シンプルな平地+少しのギミック
# ====================================================================
def _stage_example():
    R=12;t=[]
    # 平地スタート
    t+=_flat(R,5)
    # ?ブロック
    t.append(_c(R,A,A,A,A,A,A,Q,A,A,A,G,G))
    t+=_flat(R,4)
    # コイントリオ
    t.append(_c(R,A,A,A,A,A,C,A,A,A,A,G,G))
    t.append(_c(R,A,A,A,A,C,A,C,A,A,A,G,G))
    t.append(_c(R,A,A,A,A,A,C,A,A,A,A,G,G))
    t+=_flat(R,3)
    # 穴1
    t+=_hole(R,2)
    t+=_flat(R,4)
    # 浮島
    t.append(_c(R,A,A,A,A,A,A,A,G,A,A,A,A))
    t.append(_c(R,A,A,A,A,A,C,A,G,A,A,A,A))
    t.append(_c(R,A,A,A,A,A,A,A,G,A,A,A,A))
    t+=_hole(R,2)
    # ?ブロック高所
    t.append(_c(R,A,A,A,A,A,Q,A,A,A,A,G,G))
    t+=_flat(R,6)
    # 階段+ゴール
    t.append(_c(R,A,A,A,A,A,A,A,A,A,G,G,G))
    t.append(_c(R,A,A,A,A,A,A,A,A,G,G,G,G))
    t.append(_c(R,A,A,A,A,A,A,A,G,G,G,G,G))
    t.append(_c(R,A,A,A,A,FL,FL,FL,FL,FL,FL,G,G))
    while len(t)<64: t+=_flat(R,1)
    t=t[:64]
    return{
        'name':'EXAMPLE 1','bgm':'overworld','width':64,'rows':R,
        'time_limit':100,'terrain':t,'water':False,'gravity_scale':1.0,
        'start_col':2,'start_row':R-4,'goal_col':56,'flag_col':56,
        'objects':[
            (6,6,'qblock_random'),
            (28,5,'qblock_random'),
            (15,R-3,'goomba'),
            (35,R-3,'goomba'),
        ],
        'enemy_sets':{},
    }


# ====================================================================
# JSON ステージのパース (Next.jsエディタ出力 custom.dat 用)
# ====================================================================
def _parse_json_stage(s):
    """JSON定義をstages_new.py互換のdictに変換する。

    JSON format (1ステージあたり):
        {
            "name": "STAGE NAME",
            "bgm": "overworld",
            "rows": 12,
            "terrain": ["AAAAAAAAAAGG", "AAAAAAAAAAGG", ...],
              # 各文字列 = 1列。1文字 = 1タイルID (16進0-F、Aは10)
              # 短い場合は先頭をAIR(0)でパディング
            "time_limit": 100,
            "water": false,
            "gravity_scale": 1.0,
            "start_col": 2,
            "start_row": 8,
            "goal_col": 60,
            "flag_col": 60,
            "pipe_col": -1,
            "pipe_return_col": 0,
            "objects": [[col,row,"goomba"], ...],
            "enemy_sets": {"easy":[...], "normal":[...], "hard":[...]}
        }
    """
    R=int(s.get('rows',12))
    cols=[]
    for col_str in s.get('terrain',[]):
        if len(col_str)<R:
            col_str='0'*(R-len(col_str))+col_str
        ids=[]
        for ch in col_str[:R]:
            try:
                ids.append(int(ch,16))
            except ValueError:
                ids.append(0)
        cols.append(bytes(ids))
    width=len(cols)
    return{
        'name':s.get('name','CUSTOM'),'bgm':s.get('bgm','overworld'),
        'width':width,'rows':R,
        'time_limit':int(s.get('time_limit',100)),
        'terrain':cols,
        'water':bool(s.get('water',False)),
        'gravity_scale':float(s.get('gravity_scale',1.0)),
        'start_col':int(s.get('start_col',2)),
        'start_row':int(s.get('start_row',R-4)),
        'goal_col':int(s.get('goal_col',width-5)),
        'flag_col':int(s.get('flag_col',s.get('goal_col',width-5))),
        'pipe_col':int(s.get('pipe_col',-1)),
        'pipe_return_col':int(s.get('pipe_return_col',0)),
        'objects':[tuple(o) for o in s.get('objects',[])],
        'enemy_sets':s.get('enemy_sets',{}),
    }


def load_custom_stages():
    """組み込みサンプル + custom.dat (JSON) からカスタムステージリストを返す。"""
    stages=[_stage_example()]
    try:
        import ujson as json
    except ImportError:
        import json
    try:
        with open('custom.dat','r') as f:
            data=json.load(f)
            for s in data.get('stages',[]):
                try:
                    stages.append(_parse_json_stage(s))
                except Exception as e:
                    print('custom stage parse error:',e)
    except Exception:
        # custom.dat が無くてもサンプルが残る
        pass
    return stages
