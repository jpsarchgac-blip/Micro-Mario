# custom_stages.py - ユーザー定義カスタムステージ + ブロック + BGM
#
# 編集方法:
#   1. このファイル下部の _stage_example() を改造、または新しい関数を追加
#   2. BUILTIN_BLOCKS / BUILTIN_BGM に新規ブロック・BGMを追記
#   3. もしくは custom.dat (JSON) をデバイスのルートに置く (起動時自動読み込み)
#
# 詳細は docs/MAP_GUIDE.md を参照。
import world_new as wn

A=wn.AIR;G=wn.GROUND;B=wn.BRICK;Q=wn.QBLOCK;C=wn.COIN;S=wn.SPIKE
PT=wn.PIPE_TL;PR=wn.PIPE_TR;PB=wn.PIPE_BL;PD=wn.PIPE_BR
CL=wn.CLOUD_PLAT;GO=wn.GOAL;MA=wn.MAGMA;GR=wn.GRASS;FL=wn.FLAG

# カスタムブロックID用に16〜31を予約
ICE       = 16
SAND      = 17
BOUNCE    = 18
THORN     = 19
DARK_GR   = 20


def _c(rows,*ids):
    pad=[A]*(rows-len(ids))+list(ids)
    return bytes(pad)

def _flat(rows,n,top_id=A,bot_id=G,bot_n=2):
    c=_c(rows,*([top_id]*(rows-bot_n)),*([bot_id]*bot_n))
    return [c]*n

def _hole(rows,n=1):
    return [bytes([A]*rows)]*n


# ====================================================================
# 組み込みカスタムブロック定義
# ====================================================================
# 各エントリ: {
#   'id': タイルID(16-255),
#   'name': スプライト名(SpriteBank登録キー),
#   'behavior': 'solid'|'platform'|'lethal'|'passable',
#   'sprite': 8バイト (MONO_VLSB 8x8 ビットマップ)
# }
BUILTIN_BLOCKS = [
    # ICE: 滑る氷(挙動はsolidと同じ、見た目だけ差別化)
    {'id': ICE, 'name': 'tile_ice', 'behavior': 'solid',
     'sprite': bytes([0xFF, 0x81, 0xBD, 0xA5, 0xA5, 0xBD, 0x81, 0xFF])},
    # SAND: 砂ブロック(solid、点描パターン)
    {'id': SAND, 'name': 'tile_sand', 'behavior': 'solid',
     'sprite': bytes([0xAA, 0x55, 0xAA, 0x55, 0xAA, 0x55, 0xAA, 0x55])},
    # BOUNCE: 半固体跳ねるプラットフォーム
    {'id': BOUNCE, 'name': 'tile_bounce', 'behavior': 'platform',
     'sprite': bytes([0x18, 0x3C, 0x7E, 0xFF, 0xFF, 0x7E, 0x3C, 0x18])},
    # THORN: 横向きトゲ(lethal、立て横二段スパイク)
    {'id': THORN, 'name': 'tile_thorn', 'behavior': 'lethal',
     'sprite': bytes([0x99, 0x42, 0xA5, 0x42, 0xA5, 0x42, 0xA5, 0x99])},
    # DARK_GR: 暗い地面(solid、夜ステージ用)
    {'id': DARK_GR, 'name': 'tile_dark_gr', 'behavior': 'solid',
     'sprite': bytes([0x00, 0x42, 0x24, 0x18, 0x18, 0x24, 0x42, 0x00])},
]


# ====================================================================
# 組み込みカスタムBGM定義
# ====================================================================
# 各エントリは [音名 or 周波数Hz, 長さms] のリスト。
# 音名は music.NOTES に登録されているものを使用 (C3-G6, sharps as 'Xs')。
# '-' は休符。
BUILTIN_BGM = {
    # ICE FIELD: 高音中心の煌めいた曲
    'ice_field': [
        ['E5', 150], ['G5', 150], ['C6', 150], ['G5', 150],
        ['A5', 150], ['C6', 150], ['E6', 300], ['-', 100],
        ['D6', 150], ['B5', 150], ['G5', 150], ['B5', 150],
        ['C6', 150], ['E6', 150], ['G6', 300], ['-', 100],
        ['F5s', 120], ['G5s', 120], ['A5s', 120], ['C6', 240],
        ['B5', 120], ['A5', 120], ['G5', 240], ['-', 120],
        ['C5', 200], ['E5', 200], ['G5', 200], ['C6', 400],
        ['B5', 200], ['G5', 200], ['E5', 200], ['C5', 400],
        ['-', 200],
    ],
    # DESERT: 砂漠風の不思議スケール
    'desert': [
        ['D4', 200], ['F4s', 200], ['G4', 200], ['A4', 400],
        ['G4', 200], ['F4s', 200], ['D4', 400], ['-', 200],
        ['A4', 200], ['B4', 200], ['D5', 200], ['F5s', 400],
        ['D5', 200], ['B4', 200], ['A4', 400], ['-', 200],
        ['G4', 150], ['A4', 150], ['B4', 150], ['D5', 150],
        ['F5s', 150], ['G5', 150], ['A5', 300], ['-', 100],
        ['F5', 200], ['D5', 200], ['B4', 200], ['G4', 400],
        ['-', 300],
    ],
}


# ====================================================================
# サンプルカスタムステージ1: シンプルな平地+少しのギミック
# ====================================================================
def _stage_example():
    R=12;t=[]
    t+=_flat(R,5)
    t.append(_c(R,A,A,A,A,A,A,Q,A,A,A,G,G))
    t+=_flat(R,4)
    t.append(_c(R,A,A,A,A,A,C,A,A,A,A,G,G))
    t.append(_c(R,A,A,A,A,C,A,C,A,A,A,G,G))
    t.append(_c(R,A,A,A,A,A,C,A,A,A,A,G,G))
    t+=_flat(R,3)
    t+=_hole(R,2)
    t+=_flat(R,4)
    t.append(_c(R,A,A,A,A,A,A,A,G,A,A,A,A))
    t.append(_c(R,A,A,A,A,A,C,A,G,A,A,A,A))
    t.append(_c(R,A,A,A,A,A,A,A,G,A,A,A,A))
    t+=_hole(R,2)
    t.append(_c(R,A,A,A,A,A,Q,A,A,A,A,G,G))
    t+=_flat(R,6)
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
# サンプルカスタムステージ2: カスタムブロック使用デモ
# ====================================================================
def _stage_icefield():
    R=12;t=[]
    # 氷の地面 (ICE) cols 0-7
    for _ in range(8):
        t.append(_c(R,A,A,A,A,A,A,A,A,A,A,ICE,ICE))
    # 砂のブロック (cols 8-10)
    t.append(_c(R,A,A,A,A,A,A,A,A,SAND,SAND,ICE,ICE))
    t.append(_c(R,A,A,A,A,A,A,A,A,A,A,ICE,ICE))
    t.append(_c(R,A,A,A,A,A,A,A,A,SAND,SAND,ICE,ICE))
    # 穴 (cols 11-12)
    t+=_hole(R,2)
    # 跳ねるプラットフォーム (cols 13-15)
    t.append(_c(R,A,A,A,A,A,A,A,BOUNCE,A,A,ICE,ICE))
    t.append(_c(R,A,A,A,A,A,A,A,BOUNCE,A,A,ICE,ICE))
    t.append(_c(R,A,A,A,A,A,A,A,BOUNCE,A,A,ICE,ICE))
    # 穴 (cols 16-17)
    t+=_hole(R,2)
    # 横向きトゲ地帯 (cols 18-20)
    for _ in range(3):
        t.append(_c(R,A,A,A,A,A,A,A,A,A,THORN,ICE,ICE))
    # 平地 (cols 21-25)
    for _ in range(5):
        t.append(_c(R,A,A,A,A,A,A,A,A,A,A,ICE,ICE))
    # 暗い地面 (cols 26-29)
    for _ in range(4):
        t.append(_c(R,A,A,A,A,A,A,A,A,A,A,DARK_GR,DARK_GR))
    # 階段+旗 (cols 30-34)
    t.append(_c(R,A,A,A,A,A,A,A,A,A,ICE,ICE,ICE))
    t.append(_c(R,A,A,A,A,A,A,A,A,ICE,ICE,ICE,ICE))
    t.append(_c(R,A,A,A,A,A,A,A,ICE,ICE,ICE,ICE,ICE))
    t.append(_c(R,A,A,A,A,FL,FL,FL,FL,FL,FL,ICE,ICE))   # col 33: FLAG
    while len(t)<48: t.append(_c(R,A,A,A,A,A,A,A,A,A,A,ICE,ICE))
    t=t[:48]
    return{
        'name':'ICE FIELD','bgm':'ice_field','width':48,'rows':R,
        'time_limit':80,'terrain':t,'water':False,'gravity_scale':1.0,
        'start_col':2,'start_row':R-4,'goal_col':33,'flag_col':33,
        'objects':[
            (5,R-3,'goomba'),(22,R-3,'goomba'),
        ],
        'enemy_sets':{},
    }


# ====================================================================
# ブロック / BGM 登録ヘルパ
# ====================================================================
def _register_block(bank, b):
    """ブロック定義を world_new と SpriteBank に登録する。"""
    bid = int(b['id'])
    name = b.get('name', 'tile_custom_%d' % bid)
    spr = b.get('sprite')
    if spr is not None and bank is not None:
        try:
            import framebuf
            if isinstance(spr, str):
                spr = bytes.fromhex(spr)
            if len(spr) == 8:
                bank.fb[name] = framebuf.FrameBuffer(bytearray(spr), 8, 8, framebuf.MONO_VLSB)
        except Exception as e:
            print('block sprite reg err:', e)
    # タイル名マップ (世界描画が参照)
    wn._TILE_NAME[bid] = name
    behavior = b.get('behavior', 'solid')
    # 一度登録したIDは既存セットから外して再分類
    wn.SOLID_TILES.discard(bid)
    wn.PLATFORM_TILES.discard(bid)
    wn.LETHAL_TILES.discard(bid)
    if behavior == 'solid':
        wn.SOLID_TILES.add(bid)
    elif behavior == 'platform':
        wn.PLATFORM_TILES.add(bid)
    elif behavior == 'lethal':
        wn.LETHAL_TILES.add(bid)
    # passable は何処にも入れない


def _register_bgm(name, notes):
    """BGM定義を music.BGM に登録する。"""
    import music
    track = []
    for entry in notes:
        f = entry[0]; d = entry[1]
        if isinstance(f, str):
            f = music.NOTES.get(f, 0)
        track.append((int(f), int(d)))
    music.BGM[name] = track


def _parse_col(s, R):
    """terrain 列文字列をタイルIDリストに変換。
    フォーマット:
      - カンマ区切り: "0,0,1,16,1" (各値は10進または16進prefix)
      - 2hex/タイル: "00000110" (R*2 文字、ID 0-255対応)
      - 1hex/タイル: "00011" (R 以下文字、ID 0-15、先頭はAIR補完)
    """
    if ',' in s:
        parts = [p.strip() for p in s.split(',')]
        ids = []
        for p in parts:
            if not p:
                ids.append(0); continue
            try:
                if p.startswith('0x') or p.startswith('0X'):
                    ids.append(int(p, 16))
                else:
                    ids.append(int(p))
            except ValueError:
                ids.append(0)
        # AIR前パディング
        if len(ids) < R:
            ids = [0]*(R-len(ids)) + ids
        return ids[:R]
    if len(s) == R*2:
        ids = []
        for i in range(0, R*2, 2):
            try:
                ids.append(int(s[i:i+2], 16))
            except ValueError:
                ids.append(0)
        return ids
    # 1 hex char (デフォルト)
    if len(s) < R:
        s = '0'*(R-len(s)) + s
    ids = []
    for ch in s[:R]:
        try:
            ids.append(int(ch, 16))
        except ValueError:
            ids.append(0)
    return ids


# ====================================================================
# JSON ステージのパース (Next.js エディタ出力 custom.dat 用)
# ====================================================================
def _parse_json_stage(s):
    """JSON定義をstages_new.py互換のdictに変換する。

    JSON format:
        {
            "name": "STAGE NAME",
            "bgm": "overworld" | "ice_field" | カスタム名,
            "rows": 12,
            "terrain": ["00000000000BB", "1,1,1,1,1,1", "00000000000011"],
              # 各文字列 = 1列。3形式サポート:
              #   1) "000011"      - 1文字=1タイル(0-F)、IDは0-15のみ
              #   2) "00000110"    - 2文字=1タイル(00-FF)、長さ=rows*2
              #   3) "0,0,1,16,1"  - カンマ区切り、10進または16進
            ...
        }
    """
    R=int(s.get('rows',12))
    cols=[]
    for col_str in s.get('terrain',[]):
        ids = _parse_col(col_str, R)
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


# ====================================================================
# 一括ロード
# ====================================================================
def load_custom_stages(bank=None):
    """組み込みブロック/BGM/ステージ + custom.dat (JSON) を全部読み込む。

    bank: SpriteBank インスタンス (カスタムブロックのスプライト登録に必要)
    返り値: ステージdictのリスト (CUSTOM MODE のステージ選択画面で使用)
    """
    # 組み込みブロック登録
    for b in BUILTIN_BLOCKS:
        try:
            _register_block(bank, b)
        except Exception as e:
            print('builtin block err:', e)
    # 組み込みBGM登録
    for name, notes in BUILTIN_BGM.items():
        try:
            _register_bgm(name, notes)
        except Exception as e:
            print('builtin bgm err:', e)
    # 組み込みステージ
    stages=[_stage_example(), _stage_icefield()]
    # JSON 読み込み
    try:
        import ujson as json
    except ImportError:
        import json
    try:
        with open('custom.dat','r') as f:
            data=json.load(f)
        # JSON 内のブロック登録 (ステージパースより先)
        for b in data.get('blocks',[]):
            try:
                _register_block(bank, b)
            except Exception as e:
                print('json block err:', e)
        # JSON 内のBGM登録
        for name, notes in data.get('bgm',{}).items():
            try:
                _register_bgm(name, notes)
            except Exception as e:
                print('json bgm err:', e)
        # JSON 内のステージ
        for s in data.get('stages',[]):
            try:
                stages.append(_parse_json_stage(s))
            except Exception as e:
                print('json stage err:', e)
    except Exception:
        pass
    return stages
