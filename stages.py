# stages.py - ステージデータ
#
# マップ表現:
#   terrain: 各列を 8バイト = 上から下8タイル の bytes で持つ
#   タイルID: tile.py の定数を参照
#   objects: [(col, row, type_str, ...optional args), ...]
#
# 描画範囲は y=PLAY_TOP(8)〜y=64 の56px(=7タイル)+ 1行分の余白
# row 0..7 のうち、row 0 はヘッダ領域とは別に内部マップでは存在する
# (内部マップは8x8タイル前提、描画時にy=row*8でそのまま出す)
#
# ※実際には PLAY_TOP=8 ぶんオフセットして描く

# タイルID
AIR    = 0
GROUND = 1
BRICK  = 2
QBLOCK = 3
PIPE_TL= 4
PIPE_TR= 5
PIPE_BL= 6
PIPE_BR= 7
COIN   = 8
SPIKE  = 9
GOAL   = 10
CLOUD_PLAT = 11
QUSED  = 12   # 叩き済みQブロック

# 衝突属性
SOLID_TILES = {GROUND, BRICK, QBLOCK, PIPE_TL, PIPE_TR, PIPE_BL, PIPE_BR, QUSED}
# 上から踏むだけのタイル(雲足場)
PLATFORM_TILES = {CLOUD_PLAT}
# 即死
LETHAL_TILES = {SPIKE}


def col(*ids):
    """8タイル分のIDをbytesに変換するヘルパ。足りない場合はAIRで埋め、超過時はerror。"""
    if len(ids) > 8:
        raise ValueError("col() takes <=8 ids")
    pad = [AIR] * (8 - len(ids)) + list(ids)
    return bytes(pad)


# ============================================================
# ステージ1: 地上(1-1 GREEN HILL)
# ============================================================
def _build_stage1():
    """48列のステージ1を組む。歩いて、ジャンプして、土管を越え、ゴールへ。"""
    t = []
    # 0-3: 平地スタート
    for _ in range(4):
        t.append(col(AIR, AIR, AIR, AIR, AIR, AIR, GROUND, GROUND))
    # 4: ?ブロック(コイン)出現
    t.append(col(AIR, AIR, AIR, QBLOCK, AIR, AIR, GROUND, GROUND))
    # 5-7: 平地
    for _ in range(3):
        t.append(col(AIR, AIR, AIR, AIR, AIR, AIR, GROUND, GROUND))
    # 8-10: レンガx3 + ?ブロック(キノコ)+ レンガ
    t.append(col(AIR, AIR, AIR, BRICK, AIR, AIR, GROUND, GROUND))
    t.append(col(AIR, AIR, AIR, QBLOCK, AIR, AIR, GROUND, GROUND))  # キノコ
    t.append(col(AIR, AIR, AIR, BRICK, AIR, AIR, GROUND, GROUND))
    # 11-13: 平地、地上にクリボー
    for _ in range(3):
        t.append(col(AIR, AIR, AIR, AIR, AIR, AIR, GROUND, GROUND))
    # 14-15: 穴(2マス)! 落ちたら死
    t.append(col(AIR, AIR, AIR, AIR, AIR, AIR, AIR, AIR))
    t.append(col(AIR, AIR, AIR, AIR, AIR, AIR, AIR, AIR))
    # 16-19: 平地
    for _ in range(4):
        t.append(col(AIR, AIR, AIR, AIR, AIR, AIR, GROUND, GROUND))
    # 20: 土管 左(高さ2)
    t.append(col(AIR, AIR, AIR, AIR, PIPE_TL, PIPE_BL, GROUND, GROUND))
    t.append(col(AIR, AIR, AIR, AIR, PIPE_TR, PIPE_BR, GROUND, GROUND))
    # 22-24: 平地
    for _ in range(3):
        t.append(col(AIR, AIR, AIR, AIR, AIR, AIR, GROUND, GROUND))
    # 25: 階段1段
    t.append(col(AIR, AIR, AIR, AIR, AIR, GROUND, GROUND, GROUND))
    # 26: 階段2段
    t.append(col(AIR, AIR, AIR, AIR, GROUND, GROUND, GROUND, GROUND))
    # 27: 階段3段
    t.append(col(AIR, AIR, AIR, GROUND, GROUND, GROUND, GROUND, GROUND))
    # 28: 階段4段(頂上)
    t.append(col(AIR, AIR, GROUND, GROUND, GROUND, GROUND, GROUND, GROUND))
    # 29-30: 頂上から穴
    t.append(col(AIR, AIR, GROUND, GROUND, GROUND, GROUND, GROUND, GROUND))
    t.append(col(AIR, AIR, AIR, AIR, AIR, AIR, AIR, AIR))  # ジャンプ必須
    # 31: 着地
    t.append(col(AIR, AIR, AIR, AIR, AIR, AIR, GROUND, GROUND))
    # 32-34: 平地
    for _ in range(3):
        t.append(col(AIR, AIR, AIR, AIR, AIR, AIR, GROUND, GROUND))
    # 35: 高い?ブロック(ファイアフラワー)
    t.append(col(AIR, AIR, QBLOCK, AIR, AIR, AIR, GROUND, GROUND))
    # 36-38: 平地
    for _ in range(3):
        t.append(col(AIR, AIR, AIR, AIR, AIR, AIR, GROUND, GROUND))
    # 39: コイン3個並び
    t.append(col(AIR, AIR, AIR, COIN, AIR, AIR, GROUND, GROUND))
    t.append(col(AIR, AIR, AIR, COIN, AIR, AIR, GROUND, GROUND))
    t.append(col(AIR, AIR, AIR, COIN, AIR, AIR, GROUND, GROUND))
    # 42-44: 平地
    for _ in range(3):
        t.append(col(AIR, AIR, AIR, AIR, AIR, AIR, GROUND, GROUND))
    # 45: ゴール手前
    t.append(col(AIR, AIR, AIR, AIR, AIR, AIR, GROUND, GROUND))
    # 46: ゴールポール
    t.append(col(AIR, GOAL, GOAL, GOAL, GOAL, GOAL, GROUND, GROUND))
    # 47: 終端
    t.append(col(AIR, AIR, AIR, AIR, AIR, AIR, GROUND, GROUND))

    return {
        'name': '1-1 GREEN HILL',
        'bgm': 'overworld',
        'width': len(t),
        'time_limit': 100,
        'terrain': t,
        'objects': [
            (4,  3, 'qblock_coin'),
            (9,  3, 'qblock_mushroom'),
            (17, 6, 'goomba'),
            (22, 6, 'goomba'),
            (28, 6, 'goomba'),   # 階段直前
            (33, 6, 'goomba'),
            (35, 2, 'qblock_fire'),
            (42, 6, 'goomba'),
        ],
        'goal_col': 46,
        'start_col': 1,
        'water': False,
        'gravity_scale': 1.0,
    }


# ============================================================
# ステージ2: 地下
# ============================================================
def _build_stage2():
    t = []
    # 0-2: スタート部、天井あり
    for _ in range(3):
        t.append(col(GROUND, AIR, AIR, AIR, AIR, AIR, GROUND, GROUND))
    # 3-5: コイン列 + 天井
    for _ in range(3):
        t.append(col(GROUND, AIR, COIN, AIR, AIR, AIR, GROUND, GROUND))
    # 6-8: レンガ天井
    t.append(col(GROUND, BRICK, AIR, AIR, AIR, AIR, GROUND, GROUND))
    t.append(col(GROUND, BRICK, AIR, AIR, AIR, AIR, GROUND, GROUND))
    t.append(col(GROUND, BRICK, AIR, AIR, AIR, AIR, GROUND, GROUND))
    # 9-10: 段差
    t.append(col(GROUND, AIR, AIR, AIR, AIR, GROUND, GROUND, GROUND))
    t.append(col(GROUND, AIR, AIR, AIR, AIR, GROUND, GROUND, GROUND))
    # 11-13: 平地、コウモリ出現
    for _ in range(3):
        t.append(col(GROUND, AIR, AIR, AIR, AIR, AIR, GROUND, GROUND))
    # 14: トゲ罠
    t.append(col(GROUND, AIR, AIR, AIR, AIR, AIR, SPIKE, GROUND))
    # 15-17: 平地
    for _ in range(3):
        t.append(col(GROUND, AIR, AIR, AIR, AIR, AIR, GROUND, GROUND))
    # 18-19: 上下に狭い通路
    t.append(col(GROUND, GROUND, BRICK, AIR, AIR, BRICK, GROUND, GROUND))
    t.append(col(GROUND, GROUND, BRICK, AIR, AIR, BRICK, GROUND, GROUND))
    # 20-22: 広い空間
    for _ in range(3):
        t.append(col(GROUND, AIR, AIR, AIR, AIR, AIR, GROUND, GROUND))
    # 23: ?ブロック(キノコ)
    t.append(col(GROUND, AIR, AIR, QBLOCK, AIR, AIR, GROUND, GROUND))
    # 24-27: 平地
    for _ in range(4):
        t.append(col(GROUND, AIR, AIR, AIR, AIR, AIR, GROUND, GROUND))
    # 28-29: トゲ2マス
    t.append(col(GROUND, AIR, AIR, AIR, AIR, AIR, SPIKE, GROUND))
    t.append(col(GROUND, AIR, AIR, AIR, AIR, AIR, SPIKE, GROUND))
    # 30-32: 平地
    for _ in range(3):
        t.append(col(GROUND, AIR, AIR, AIR, AIR, AIR, GROUND, GROUND))
    # 33: ゴール
    t.append(col(GROUND, GOAL, GOAL, GOAL, GOAL, GOAL, GROUND, GROUND))
    # 34
    t.append(col(GROUND, AIR, AIR, AIR, AIR, AIR, GROUND, GROUND))

    return {
        'name': '1-2 UNDERGROUND',
        'bgm': 'underground',
        'width': len(t),
        'time_limit': 90,
        'terrain': t,
        'objects': [
            (5, 5, 'bat'),
            (11, 6, 'goomba'),
            (16, 4, 'bat'),
            (21, 6, 'goomba'),
            (23, 2, 'qblock_mushroom'),
            (25, 6, 'goomba'),
            (31, 6, 'goomba'),
        ],
        'goal_col': 33,
        'start_col': 1,
        'water': False,
        'gravity_scale': 1.0,
    }


# ============================================================
# ステージ3: 水中
# ============================================================
def _build_stage3():
    t = []
    # 水中ステージは天井も底もあり、浮力で常時ふわふわ
    for _ in range(3):
        t.append(col(GROUND, AIR, AIR, AIR, AIR, AIR, AIR, GROUND))
    # コイン群
    for _ in range(3):
        t.append(col(GROUND, AIR, COIN, AIR, COIN, AIR, AIR, GROUND))
    # 狭路
    t.append(col(GROUND, BRICK, BRICK, AIR, AIR, BRICK, BRICK, GROUND))
    t.append(col(GROUND, BRICK, AIR, AIR, AIR, AIR, BRICK, GROUND))
    t.append(col(GROUND, AIR, AIR, AIR, AIR, AIR, AIR, GROUND))
    # 魚出現エリア
    for _ in range(4):
        t.append(col(GROUND, AIR, AIR, AIR, AIR, AIR, AIR, GROUND))
    # 障害ブロック
    t.append(col(GROUND, AIR, AIR, BRICK, BRICK, AIR, AIR, GROUND))
    t.append(col(GROUND, AIR, AIR, AIR, AIR, AIR, AIR, GROUND))
    t.append(col(GROUND, AIR, AIR, AIR, AIR, AIR, AIR, GROUND))
    # 上段通路
    t.append(col(GROUND, AIR, AIR, BRICK, AIR, AIR, AIR, GROUND))
    t.append(col(GROUND, AIR, AIR, BRICK, AIR, AIR, AIR, GROUND))
    # ファイアフラワー
    t.append(col(GROUND, AIR, AIR, QBLOCK, AIR, AIR, AIR, GROUND))
    # 平地
    for _ in range(5):
        t.append(col(GROUND, AIR, AIR, AIR, AIR, AIR, AIR, GROUND))
    # ゴール
    t.append(col(GROUND, GOAL, GOAL, GOAL, GOAL, GOAL, GOAL, GROUND))
    t.append(col(GROUND, AIR, AIR, AIR, AIR, AIR, AIR, GROUND))

    return {
        'name': '1-3 UNDERWATER',
        'bgm': 'water',
        'width': len(t),
        'time_limit': 120,
        'terrain': t,
        'objects': [
            (5, 4, 'fish'),
            (10, 3, 'fish'),
            (15, 5, 'fish'),
            (18, 4, 'fish'),
            (21, 3, 'qblock_fire'),
            (24, 4, 'fish'),
        ],
        'goal_col': len([x for x in t]) - 2,
        'start_col': 1,
        'water': True,
        'gravity_scale': 0.3,
    }


# ============================================================
# ステージ4: 城壁(空中敵+トゲ)
# ============================================================
def _build_stage4():
    t = []
    for _ in range(3):
        t.append(col(AIR, AIR, AIR, AIR, AIR, AIR, GROUND, GROUND))
    # トゲ
    t.append(col(AIR, AIR, AIR, AIR, AIR, AIR, SPIKE, GROUND))
    t.append(col(AIR, AIR, AIR, AIR, AIR, AIR, GROUND, GROUND))
    # 浮き足場(雲)
    t.append(col(AIR, AIR, AIR, CLOUD_PLAT, AIR, AIR, AIR, AIR))  # 穴!
    t.append(col(AIR, AIR, CLOUD_PLAT, AIR, AIR, AIR, AIR, AIR))
    t.append(col(AIR, CLOUD_PLAT, AIR, AIR, AIR, AIR, AIR, AIR))
    t.append(col(AIR, AIR, AIR, AIR, AIR, AIR, AIR, AIR))  # 穴
    # 着地
    for _ in range(3):
        t.append(col(AIR, AIR, AIR, AIR, AIR, AIR, GROUND, GROUND))
    # トゲ3連
    t.append(col(AIR, AIR, AIR, AIR, AIR, AIR, SPIKE, GROUND))
    t.append(col(AIR, AIR, AIR, AIR, AIR, AIR, SPIKE, GROUND))
    t.append(col(AIR, AIR, AIR, AIR, AIR, AIR, SPIKE, GROUND))
    # 平地
    for _ in range(3):
        t.append(col(AIR, AIR, AIR, AIR, AIR, AIR, GROUND, GROUND))
    # ?ブロック
    t.append(col(AIR, AIR, QBLOCK, AIR, AIR, AIR, GROUND, GROUND))
    # 平地
    for _ in range(3):
        t.append(col(AIR, AIR, AIR, AIR, AIR, AIR, GROUND, GROUND))
    # 浮き足場連
    t.append(col(AIR, AIR, AIR, CLOUD_PLAT, AIR, AIR, AIR, AIR))
    t.append(col(AIR, AIR, AIR, AIR, AIR, AIR, AIR, AIR))
    t.append(col(AIR, AIR, CLOUD_PLAT, AIR, AIR, AIR, AIR, AIR))
    t.append(col(AIR, AIR, AIR, AIR, AIR, AIR, AIR, AIR))
    # 着地
    for _ in range(3):
        t.append(col(AIR, AIR, AIR, AIR, AIR, AIR, GROUND, GROUND))
    # ゴール
    t.append(col(AIR, GOAL, GOAL, GOAL, GOAL, GOAL, GROUND, GROUND))
    t.append(col(AIR, AIR, AIR, AIR, AIR, AIR, GROUND, GROUND))

    return {
        'name': '1-4 CASTLE WALL',
        'bgm': 'castle',
        'width': len(t),
        'time_limit': 100,
        'terrain': t,
        'objects': [
            (4, 3, 'parakoopa'),
            (10, 5, 'parakoopa'),
            (16, 3, 'parakoopa'),
            (20, 2, 'qblock_fire'),
            (22, 5, 'parakoopa'),
            (27, 3, 'parakoopa'),
        ],
        'goal_col': len(t) - 2,
        'start_col': 1,
        'water': False,
        'gravity_scale': 1.0,
    }


# ============================================================
# ステージ5: 空中(雲足場メイン)
# ============================================================
def _build_stage5():
    """ステージ5: 天空のアスレチック (64列の長編構成)"""
    t = []

    # --- Phase 1: Ascent (0-15) ---
    # 広いスタート地点
    for _ in range(4):
        t.append(col(AIR, AIR, AIR, AIR, AIR, AIR, GROUND, GROUND))
    # 地面の階段
    t.append(col(AIR, AIR, AIR, AIR, AIR, GROUND, GROUND, GROUND))
    t.append(col(AIR, AIR, AIR, AIR, GROUND, GROUND, GROUND, GROUND))
    t.append(col(AIR, AIR, AIR, GROUND, GROUND, GROUND, GROUND, GROUND))
    # 穴を越えて雲の階段へ
    t.append(col(AIR, AIR, AIR, AIR, AIR, AIR, AIR, AIR))
    t.append(col(AIR, AIR, AIR, CLOUD_PLAT, AIR, AIR, AIR, AIR))
    t.append(col(AIR, AIR, AIR, AIR, AIR, AIR, AIR, AIR))
    t.append(col(AIR, AIR, CLOUD_PLAT, AIR, AIR, AIR, AIR, AIR))
    t.append(col(AIR, AIR, AIR, AIR, AIR, AIR, AIR, AIR))
    t.append(col(AIR, CLOUD_PLAT, AIR, AIR, AIR, AIR, AIR, AIR))
    t.append(col(AIR, AIR, AIR, AIR, AIR, AIR, AIR, AIR))
    t.append(col(AIR, CLOUD_PLAT, AIR, AIR, AIR, AIR, AIR, AIR))

    # --- Phase 2: Aerial Ninja Duel (16-31) ---
    # 下段にも足場があるエリア
    for i in range(8):
        if i % 2 == 0:
            t.append(col(AIR, CLOUD_PLAT, AIR, AIR, AIR, CLOUD_PLAT, GROUND, GROUND))
        else:
            t.append(col(AIR, AIR, AIR, AIR, AIR, AIR, GROUND, GROUND))
    # 忍者の波
    for i in range(8):
        if i == 4:
            t.append(col(AIR, AIR, CLOUD_PLAT, AIR, AIR, AIR, AIR, AIR))
        else:
            t.append(col(AIR, AIR, AIR, AIR, AIR, AIR, GROUND, GROUND))

    # --- Phase 3: The Great Pit (32-47) ---
    # 高台
    for _ in range(3):
        t.append(col(AIR, AIR, AIR, AIR, GROUND, GROUND, GROUND, GROUND))
    # 大穴とコインのアーチ (8マス)
    t.append(col(AIR, AIR, AIR, AIR, AIR, AIR, AIR, AIR))
    t.append(col(AIR, AIR, COIN, AIR, AIR, AIR, AIR, AIR))
    t.append(col(AIR, COIN, AIR, AIR, AIR, AIR, AIR, AIR))
    t.append(col(COIN, AIR, AIR, AIR, AIR, AIR, AIR, AIR))
    t.append(col(COIN, AIR, AIR, AIR, AIR, AIR, AIR, AIR))
    t.append(col(AIR, COIN, AIR, AIR, AIR, AIR, AIR, AIR))
    t.append(col(AIR, AIR, COIN, AIR, AIR, AIR, AIR, AIR))
    t.append(col(AIR, AIR, AIR, AIR, AIR, AIR, AIR, AIR))
    # 着地地点
    for _ in range(5):
        t.append(col(AIR, AIR, AIR, AIR, AIR, AIR, GROUND, GROUND))

    # --- Phase 4: Spike Forest (48-59) ---
    # 地面がトゲ
    for i in range(12):
        if i % 3 == 0:
            t.append(col(AIR, AIR, CLOUD_PLAT, AIR, AIR, AIR, SPIKE, GROUND))
        else:
            t.append(col(AIR, AIR, AIR, AIR, AIR, AIR, SPIKE, GROUND))

    # --- Phase 5: Finale (60-64) ---
    # 空中の階段
    t.append(col(AIR, AIR, CLOUD_PLAT, AIR, AIR, AIR, AIR, AIR))
    t.append(col(AIR, CLOUD_PLAT, AIR, AIR, AIR, AIR, AIR, AIR))
    # ゴール
    t.append(col(AIR, GOAL, GOAL, GOAL, GOAL, GOAL, GROUND, GROUND))
    t.append(col(AIR, AIR, AIR, AIR, AIR, AIR, GROUND, GROUND))
    t.append(col(AIR, AIR, AIR, AIR, AIR, AIR, GROUND, GROUND))

    return {
        'name': '1-5 SKY ZONE',
        'bgm': 'sky',
        'width': len(t),
        'time_limit': 120,
        'terrain': t,
        'objects': [
            # Phase 1
            (11, 0, 'ninja'),
            # Phase 2
            (18, 0, 'ninja'),
            (22, 4, 'ninja'),
            (26, 0, 'ninja'),
            (30, 0, 'ninja'),
            # Phase 4
            (50, 1, 'ninja'),
            (55, 1, 'ninja'),
        ],
        'goal_col': 61,
        'start_col': 1,
        'water': False,
        'gravity_scale': 1.0,
    }



# ============================================================
# ステージ6: ボス戦アリーナ
# ============================================================
def _build_stage6():
    t = []
    # 22列の固定アリーナ
    # 左壁
    t.append(col(GROUND, GROUND, GROUND, GROUND, GROUND, GROUND, GROUND, GROUND))
    # アリーナ床
    for _ in range(20):
        t.append(col(AIR, AIR, AIR, AIR, AIR, AIR, GROUND, GROUND))
    # 右壁
    t.append(col(GROUND, GROUND, GROUND, GROUND, GROUND, GROUND, GROUND, GROUND))

    return {
        'name': 'BOSS - KING KOOPA',
        'bgm': 'boss',
        'width': len(t),
        'time_limit': 200,
        'terrain': t,
        'objects': [
            (16, 4, 'boss'),
        ],
        'goal_col': -1,  # ゴール無し、ボス撃破で終了
        'start_col': 2,
        'water': False,
        'gravity_scale': 1.0,
    }


# ステージ一覧
STAGES = [
    _build_stage1(),
    _build_stage2(),
    _build_stage3(),
    _build_stage4(),
    _build_stage5(),
    _build_stage6(),
]


def get_stage(num):
    """1始まりで取得"""
    if 1 <= num <= len(STAGES):
        return STAGES[num - 1]
    return None
