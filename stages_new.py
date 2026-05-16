# stages_new.py - NEWモード6ステージ + 地下サブステージ
import world_new as wn

A=wn.AIR;G=wn.GROUND;B=wn.BRICK;Q=wn.QBLOCK;C=wn.COIN;S=wn.SPIKE
PT=wn.PIPE_TL;PR=wn.PIPE_TR;PB=wn.PIPE_BL;PD=wn.PIPE_BR
CL=wn.CLOUD_PLAT;GO=wn.GOAL;MA=wn.MAGMA;GR=wn.GRASS;FL=wn.FLAG

def _c(rows,*ids):
    pad=[A]*(rows-len(ids))+list(ids)
    return bytes(pad)

def _flat(rows,n,top_id=A,bot_id=G,bot_n=2):
    c=_c(rows,*([top_id]*(rows-bot_n)),*([bot_id]*bot_n))
    return[c]*n

def _hole(rows,n=1):
    return[bytes([A]*rows)]*n

# ============================================================
# ステージ物理メモ
#   R=12: 地面row10-11, プレイヤー頭row8, 最大ジャンプ高さ≈4タイル
#     → 直接届く浮島: row9(易),row8(普通),row7(やや難),row6(限界)
#     → row5以上は階段等で登った後にのみ届く
#   R=16: 地面row12-15, プレイヤー頭row10, 最大ジャンプ高さ≈4タイル
#     → 直接届く浮島: row11(易),row10(普通),row9(やや難),row8(限界)
# ============================================================

def _build_s1():
    R=12;t=[]

    # ===== Section A: ウォームアップ (col 0-24) =====
    t+=_flat(R,4)                                        # 0-3: 平地スタート
    t.append(_c(R,A,A,A,A,A,A,Q,A,A,A,G,G))             # 4: ?ブロックrow6
    t+=_flat(R,3)                                        # 5-7
    t+=_hole(R,2)                                        # 8-9: 最初の穴(落下死!)
    t+=_flat(R,3)                                        # 10-12
    t.append(_c(R,A,A,A,A,A,B,A,A,A,A,G,G))             # 13: レンガrow5
    t.append(_c(R,A,A,A,A,A,Q,A,A,A,A,G,G))             # 14: ?ブロックrow5
    t.append(_c(R,A,A,A,A,A,B,A,A,A,A,G,G))             # 15: レンガrow5
    t+=_flat(R,3)                                        # 16-18
    t+=_hole(R,1)                                        # 19: 穴
    t+=_flat(R,4)                                        # 20-23
    t.append(_c(R,A,A,A,A,A,A,Q,A,A,A,G,G))             # 24: ?ブロックrow6

    # ===== Section B: 浮き足場チャレンジ (col 25-54) =====
    # 地面から直接届く高さ(row7-9)の浮島でジャンプ力練習
    t+=_flat(R,2)                                        # 25-26
    t+=_hole(R,2)                                        # 27-28: 穴
    # 浮島1: row8 (地面から2タイル上, 易しい)
    t.append(_c(R,A,A,A,A,A,A,A,A,G,A,A,A))             # 29
    t.append(_c(R,A,A,A,A,A,A,C,A,G,A,A,A))             # 30: 上にコインrow6
    t.append(_c(R,A,A,A,A,A,A,A,A,G,A,A,A))             # 31
    t+=_hole(R,2)                                        # 32-33: 穴
    # 浮島2: row7 (3タイル上, やや難)
    t.append(_c(R,A,A,A,A,A,A,A,G,A,A,A,A))             # 34
    t.append(_c(R,A,A,A,A,A,A,C,G,A,A,A,A))             # 35: 上にコインrow6
    t.append(_c(R,A,A,A,A,A,A,A,G,A,A,A,A))             # 36
    t+=_hole(R,2)                                        # 37-38: 穴
    # 浮島3: row9 (1タイル上, 息抜き)
    t.append(_c(R,A,A,A,A,A,A,A,A,A,G,A,A))             # 39
    t.append(_c(R,A,A,A,A,A,A,A,A,A,G,A,A))             # 40
    t.append(_c(R,A,A,A,A,A,A,A,A,A,G,A,A))             # 41
    t+=_hole(R,2)                                        # 42-43: 穴
    t+=_flat(R,4)                                        # 44-47: 着地・安全地帯
    # ドカン(地下サブステージ入口)
    t.append(_c(R,A,A,A,A,A,A,A,PT,PB,A,G,G))           # 48
    t.append(_c(R,A,A,A,A,A,A,A,PR,PD,A,G,G))           # 49
    t+=_flat(R,5)                                        # 50-54: 広い休憩地帯

    # ===== Section C: ?ブロック回廊 + レンガ橋 (col 55-78) =====
    # コイン菱形
    t.append(_c(R,A,A,A,A,A,C,A,A,A,A,G,G))             # 55
    t.append(_c(R,A,A,A,A,C,A,C,A,A,A,G,G))             # 56
    t.append(_c(R,A,A,A,A,A,C,A,A,A,A,G,G))             # 57
    t+=_flat(R,2)                                        # 58-59
    # レンガ浮き橋(row7, void下): 3タイル上=ジャンプで届く
    t+=_hole(R,1)                                        # 60: 穴
    t.append(_c(R,A,A,A,A,A,A,A,B,A,A,A,A))             # 61: レンガrow7・void下
    t.append(_c(R,A,A,A,A,A,A,A,B,A,A,A,A))             # 62
    t.append(_c(R,A,A,A,A,A,A,A,B,A,A,A,A))             # 63
    t+=_hole(R,1)                                        # 64: 穴
    t+=_flat(R,3)                                        # 65-67
    # ?ブロック3連(row5-6: ジャンプで頭から叩ける)
    t.append(_c(R,A,A,A,A,A,Q,A,A,A,A,G,G))             # 68: row5
    t+=_flat(R,1)                                        # 69
    t.append(_c(R,A,A,A,A,A,A,Q,A,A,A,G,G))             # 70: row6
    t+=_flat(R,1)                                        # 71
    t.append(_c(R,A,A,A,A,A,Q,A,A,A,A,G,G))             # 72: row5
    t+=_flat(R,2)                                        # 73-74
    # スパイク地帯
    t.append(_c(R,A,A,A,A,A,A,A,A,A,S,G,G))             # 75: スパイク
    t.append(_c(R,A,A,A,A,A,A,A,A,A,S,G,G))             # 76
    t+=_flat(R,2)                                        # 77-78

    # ===== Section D: 階段登り + row6高所浮島 (col 79-102) =====
    # 階段を登って高所へ(階段上からなら row6 浮島に届く)
    t.append(_c(R,A,A,A,A,A,A,A,A,A,G,G,G))             # 79: row9
    t.append(_c(R,A,A,A,A,A,A,A,A,G,G,G,G))             # 80: row8
    t.append(_c(R,A,A,A,A,A,A,A,G,G,G,G,G))             # 81: row7
    t.append(_c(R,A,A,A,A,A,A,G,G,G,G,G,G))             # 82: row6 最高点
    # row6浮島群(直上に?ブロック): 階段から直接渡れる
    t.append(_c(R,A,A,A,A,A,A,G,A,A,A,A,A))             # 83: 浮島row6
    t.append(_c(R,A,A,A,A,Q,A,G,A,A,A,A,A))             # 84: ?ブロックrow4・浮島row6
    t.append(_c(R,A,A,A,A,A,A,G,A,A,A,A,A))             # 85: 浮島row6
    t+=_hole(R,2)                                        # 86-87: 空中の穴
    t.append(_c(R,A,A,A,A,A,A,G,A,A,A,A,A))             # 88: 浮島row6
    t.append(_c(R,A,A,A,A,A,A,G,A,A,A,A,A))             # 89: 浮島row6
    t+=_hole(R,2)                                        # 90-91: 空中の穴
    # 降下スロープで地面へ
    t.append(_c(R,A,A,A,A,A,A,G,G,G,G,G,G))             # 92
    t.append(_c(R,A,A,A,A,A,A,A,G,G,G,G,G))             # 93
    t.append(_c(R,A,A,A,A,A,A,A,A,G,G,G,G))             # 94
    t+=_flat(R,5)                                        # 95-99
    t+=_hole(R,1)                                        # 100: 穴
    t+=_flat(R,2)                                        # 101-102

    # ===== Section E: 最終突破 + ゴール (col 103-127) =====
    # コイン密集帯
    t.append(_c(R,A,A,A,A,C,C,C,A,A,A,G,G))             # 103
    t.append(_c(R,A,A,A,A,C,A,C,A,A,A,G,G))             # 104
    t.append(_c(R,A,A,A,A,C,C,C,A,A,A,G,G))             # 105
    t+=_flat(R,2)                                        # 106-107
    t+=_hole(R,2)                                        # 108-109: 穴
    t+=_flat(R,2)                                        # 110-111
    # 最終階段(登り)
    t.append(_c(R,A,A,A,A,A,A,A,A,A,G,G,G))             # 112
    t.append(_c(R,A,A,A,A,A,A,A,A,G,G,G,G))             # 113
    t.append(_c(R,A,A,A,A,A,A,A,G,G,G,G,G))             # 114
    t.append(_c(R,A,A,A,A,A,A,G,G,G,G,G,G))             # 115: 最高点
    t+=_flat(R,2)                                        # 116-117
    # ゴール旗
    t.append(_c(R,A,A,A,A,FL,FL,FL,FL,FL,FL,G,G))       # 118: FLAG
    while len(t)<128:t+=_flat(R,1)
    t=t[:128]
    return{
        'name':'1-1 GREEN HILL','bgm':'overworld','width':128,'rows':R,
        'time_limit':100,'terrain':t,'water':False,'gravity_scale':1.0,
        'start_col':2,'start_row':R-4,'goal_col':118,'flag_col':117,
        'pipe_col':38,'pipe_dest':'substage','pipe_return_col':64,
        'objects':[
            (4,6,'qblock_random'),(14,5,'qblock_random'),(24,6,'qblock_random'),
            (68,5,'qblock_random'),(70,6,'qblock_random'),(72,5,'qblock_random'),
            (84,4,'qblock_random'),
        ],
        'enemy_sets':{
            'easy': [
                (22,R-3,'goomba'),
                (66,R-3,'goomba'),
            ],
            'normal': [
                (12,R-3,'goomba'),(22,R-3,'goomba'),
                (45,R-3,'goomba'),
                (78,R-3,'goomba'),(97,R-3,'goomba'),
            ],
            'hard': [
                (12,R-3,'goomba'),(22,R-3,'goomba'),
                (45,R-3,'goomba'),
                (66,R-3,'goomba'),(78,R-3,'goomba'),
                (97,R-3,'goomba'),
            ],
        },
    }


def _build_s2():
    R=12;t=[]
    # 地下: 天井row0-1, 地面row10-11
    def uc(*mid):
        # mid は row2~row9 (8タイル)
        return _c(R,G,G,*list(mid),G,G)

    # ===== Phase1: 入口 + 仕掛けの予感 (col 0-24) =====
    for _ in range(5): t.append(uc(A,A,A,A,A,A,A,A))
    # 天井コイン(高ジャンプで取れる)
    t.append(_c(R,G,C,A,A,A,A,A,A,A,A,G,G))
    t.append(_c(R,G,C,A,A,A,A,A,A,A,A,G,G))
    t.append(_c(R,G,C,A,A,A,A,A,A,A,A,G,G))
    # 床レンガ壁
    t.append(uc(A,A,A,A,A,A,B,A))
    t.append(uc(A,A,A,A,A,A,B,A))
    for _ in range(3): t.append(uc(A,A,A,A,A,A,A,A))
    # Phase2: トゲ地帯(25-49)
    for _ in range(5): t.append(uc(A,A,A,A,A,A,A,A))
    t.append(_c(R,G,G,A,A,A,A,A,A,A,S,G,G))  # トゲ
    t.append(_c(R,G,G,A,A,A,A,A,A,A,S,G,G))
    for _ in range(6): t.append(uc(A,A,A,A,A,A,A,A))  # 休憩
    t.append(uc(A,A,A,Q,A,A,A,A))  # ?ブロック
    for _ in range(5): t.append(uc(A,A,A,A,A,A,A,A))
    # コイン広場
    for _ in range(3): t.append(_c(R,G,G,A,C,A,C,A,C,A,A,G,G))

    # ===== Phase4: 難所 + ゴール (col 75-127) =====
    for _ in range(5): t.append(uc(A,A,A,A,A,A,A,A))
    for _ in range(4): t.append(_c(R,G,G,B,A,A,A,A,B,A,A,G,G))  # 狭路
    for _ in range(8): t.append(uc(A,A,A,A,A,A,A,A))  # 休憩
    t.append(_c(R,G,G,A,A,A,A,A,A,A,S,G,G))  # トゲ
    t.append(_c(R,G,G,A,A,A,A,A,A,A,S,G,G))
    for _ in range(5): t.append(uc(A,A,A,A,A,A,A,A))
    # 最後の?ブロック
    t.append(uc(A,A,A,Q,A,A,A,A))
    for _ in range(5): t.append(uc(A,A,A,A,A,A,A,A))
    # ゴール
    t.append(_c(R,G,G,GO,GO,GO,GO,GO,GO,GO,GO,G,G))
    while len(t)<128: t.append(uc(A,A,A,A,A,A,A,A))
    t=t[:128]
    return{
        'name':'1-2 UNDERGROUND','bgm':'underground','width':128,'rows':R,
        'time_limit':90,'terrain':t,'water':False,'gravity_scale':1.0,
        'start_col':2,'start_row':R-4,'goal_col':98,
        'objects':[
            (29,5,'qblock_random'),(30,2,'qblock_random'),
        ],
        'enemy_sets':{
            'easy': [
                (30,R-3,'goomba'),
                (72,R-3,'goomba'),
            ],
            'normal': [
                (15,R-3,'goomba'),(30,R-3,'goomba'),
                (45,3,'bat'),
                (72,R-3,'goomba'),
            ],
            'hard': [
                (15,R-3,'goomba'),(30,R-3,'goomba'),
                (45,3,'bat'),(60,3,'bat'),
                (72,R-3,'goomba'),(88,R-3,'goomba'),
            ],
        },
    }


def _build_s3():
    R=16;t=[]
    for i in range(128):
        if i<5:
            t.append(_c(R,G,G,A,A,A,A,A,A,A,A,A,A,A,A,G,G))
        elif i<10:
            if i%2==0: t.append(_c(R,G,G,A,C,A,A,A,A,A,A,A,A,C,A,G,G))
            else:       t.append(_c(R,G,G,A,A,A,A,A,A,A,A,A,A,A,A,G,G))
        elif i<20:
            if i==12:   t.append(_c(R,G,G,A,A,B,B,B,A,A,A,A,A,A,A,G,G))
            elif i==16: t.append(_c(R,G,G,A,A,A,A,A,B,B,B,A,A,A,A,G,G))
            else:       t.append(_c(R,G,G,A,A,A,A,A,A,A,A,A,A,A,A,G,G))
        elif i<30:
            t.append(_c(R,G,G,A,A,A,A,A,A,A,A,A,A,A,A,G,G))
        elif i<36:
            if i%2==0:  t.append(_c(R,G,G,A,A,C,A,A,A,A,A,A,A,A,A,G,G))
            else:       t.append(_c(R,G,G,A,A,A,A,A,A,A,C,A,A,A,A,G,G))
        elif i==38:
            t.append(_c(R,G,G,A,A,A,Q,A,A,A,A,A,A,A,A,G,G))
        elif i<50:
            t.append(_c(R,G,G,A,A,A,A,A,A,A,A,A,A,A,A,G,G))
        elif i<60:
            if i==52:   t.append(_c(R,G,G,A,A,A,A,B,B,B,A,A,A,A,A,G,G))
            elif i==57: t.append(_c(R,G,G,A,B,B,B,A,A,A,A,A,A,A,A,G,G))
            else:       t.append(_c(R,G,G,A,A,A,A,A,A,A,A,A,A,A,A,G,G))
        elif i<80:
            if i%5==0:  t.append(_c(R,G,G,A,C,A,A,A,A,A,A,A,C,A,A,G,G))
            else:       t.append(_c(R,G,G,A,A,A,A,A,A,A,A,A,A,A,A,G,G))
        elif i<100:
            if i%4==0:  t.append(_c(R,G,G,A,A,A,A,B,A,A,A,A,B,A,A,G,G))
            elif i%4==2:t.append(_c(R,G,G,A,C,A,A,A,A,A,A,A,A,C,A,G,G))
            else:       t.append(_c(R,G,G,A,A,A,A,A,A,A,A,A,A,A,A,G,G))
        elif i==110:
            t.append(_c(R,G,G,GO,GO,GO,GO,GO,GO,GO,GO,GO,GO,GO,GO,G,G))
        else:
            t.append(_c(R,G,G,A,A,A,A,A,A,A,A,A,A,A,A,G,G))
    t=t[:128]
    return{
        'name':'1-3 UNDERWATER','bgm':'water','width':128,'rows':R,
        'time_limit':120,'terrain':t,'water':True,'gravity_scale':0.2,
        'start_col':2,'start_row':6,'goal_col':110,
        'objects':[
            (38,5,'qblock_random'),
        ],
        'enemy_sets':{
            'easy': [
                (25,10,'fish'),
                (65,6,'fish'),
                (100,6,'fish'),
            ],
            'normal': [
                (10,6,'fish'),(25,10,'fish'),(45,8,'fish'),
                (65,6,'fish'),(85,10,'fish'),(100,6,'fish'),
            ],
            'hard': [
                (10,6,'fish'),(20,10,'fish'),(35,8,'fish'),
                (55,6,'fish'),(70,10,'fish'),(85,8,'fish'),(100,6,'fish'),
            ],
        },
    }


def _build_s4():
    R=16;t=[]
    # SKY ZONE: 真の落下死あり。足場は孤立した雲/固定台のみ。
    # R=16: 地面row12-15, 最大ジャンプ≈4タイル
    # 直接届く足場: row11(易),row10(普通),row9(やや難),row8(限界)
    # row6-7は高台から到達

    # スタート安全島(col 0-7): 地面あり
    for _ in range(8):
        t.append(_c(R,A,A,A,A,A,A,A,A,A,A,A,A,G,G,G,G))

    # ===== Section A: 低雲から中雲へ (col 8-40) =====
    # row10雲(易) → row8固定台(やや難)
    t.append(_c(R,A,A,A,A,A,A,A,A,A,A,CL,A,A,A,A,A))    # 8: CL row10
    t.append(_c(R,A,A,A,A,A,A,A,A,A,A,CL,A,A,A,A,A))    # 9
    t+=_hole(R,2)                                         # 10-11
    t.append(_c(R,A,A,A,A,A,A,A,A,A,A,CL,A,A,A,A,A))    # 12
    t.append(_c(R,A,A,A,A,A,A,A,A,A,A,CL,A,A,A,A,A))    # 13
    t.append(_c(R,A,A,A,A,A,A,A,A,A,A,CL,A,A,A,A,A))    # 14
    t+=_hole(R,2)                                         # 15-16
    # row8固定台(地面から4タイル=限界)
    t.append(_c(R,A,A,A,A,A,A,A,A,G,A,A,A,A,A,A,A))     # 17: G row8
    t.append(_c(R,A,A,A,A,A,A,A,A,G,A,A,A,A,A,A,A))     # 18
    t+=_hole(R,2)                                         # 19-20
    t.append(_c(R,A,A,A,A,A,A,A,A,CL,A,A,A,A,A,A,A))    # 21: CL row8
    t.append(_c(R,A,A,A,A,A,A,A,A,CL,A,A,A,A,A,A,A))    # 22
    t+=_hole(R,3)                                         # 23-25: 幅広い穴!
    t.append(_c(R,A,A,A,A,A,A,A,A,G,A,A,A,A,A,A,A))     # 26: G row8
    t.append(_c(R,A,A,A,A,Q,A,A,A,G,A,A,A,A,A,A,A))     # 27: ?ブロックrow4・台row8
    t.append(_c(R,A,A,A,A,A,A,A,A,G,A,A,A,A,A,A,A))     # 28
    t+=_hole(R,2)                                         # 29-30
    t.append(_c(R,A,A,A,A,A,A,A,A,CL,A,A,A,A,A,A,A))    # 31
    t.append(_c(R,A,A,A,A,A,A,A,A,CL,A,A,A,A,A,A,A))    # 32
    t+=_hole(R,2)                                         # 33-34
    # row8台→row6台へ段階的上昇(row8から2タイル上=余裕)
    t.append(_c(R,A,A,A,A,A,A,G,A,A,A,A,A,A,A,A,A))     # 35: G row6
    t.append(_c(R,A,A,A,A,A,A,G,A,A,A,A,A,A,A,A,A))     # 36
    t+=_hole(R,2)                                         # 37-38
    t.append(_c(R,A,A,A,A,A,A,G,A,A,A,A,A,A,A,A,A))     # 39
    t+=_hole(R,1)                                         # 40

    # ===== Section B: row6高所 + 1枚足場難所 (col 41-70) =====
    # row6固定台(ここから来ると行き先はrow6レベル)
    t.append(_c(R,A,A,A,A,A,A,G,G,A,A,A,A,A,A,A,A))     # 41: 2枚重ね台
    t.append(_c(R,A,A,A,A,A,A,G,G,A,A,A,A,A,A,A,A))     # 42
    t.append(_c(R,A,A,A,A,A,A,G,G,A,A,A,A,A,A,A,A))     # 43
    t+=_hole(R,2)                                         # 44-45
    # 1タイル幅の極小足場(難関!)
    t.append(_c(R,A,A,A,A,A,A,A,G,A,A,A,A,A,A,A,A))     # 46: 1枚足場 row7
    t+=_hole(R,2)                                         # 47-48
    t.append(_c(R,A,A,A,A,A,A,A,G,A,A,A,A,A,A,A,A))     # 49
    t+=_hole(R,2)                                         # 50-51
    t.append(_c(R,A,A,A,A,A,A,A,G,A,A,A,A,A,A,A,A))     # 52
    t.append(_c(R,A,A,A,A,A,A,A,G,A,A,A,A,A,A,A,A))     # 53
    t+=_hole(R,2)                                         # 54-55
    # 安定台 + ?ブロック
    t.append(_c(R,A,A,A,A,A,A,A,G,A,A,A,A,A,A,A,A))     # 56
    t.append(_c(R,A,A,A,A,Q,A,A,G,A,A,A,A,A,A,A,A))     # 57: ?ブロックrow4
    t.append(_c(R,A,A,A,A,A,A,A,G,A,A,A,A,A,A,A,A))     # 58
    t+=_hole(R,2)                                         # 59-60
    # CL雲 + コイン
    t.append(_c(R,A,A,A,A,A,A,A,CL,A,A,A,A,A,A,A,A))    # 61: CL row7
    t.append(_c(R,A,A,A,A,C,A,A,CL,A,A,A,A,A,A,A,A))    # 62: コインrow4上
    t.append(_c(R,A,A,A,A,A,A,A,CL,A,A,A,A,A,A,A,A))    # 63
    t+=_hole(R,3)                                         # 64-66: 広い穴!
    t.append(_c(R,A,A,A,A,A,A,A,G,A,A,A,A,A,A,A,A))     # 67: row7
    t.append(_c(R,A,A,A,A,A,A,A,G,A,A,A,A,A,A,A,A))     # 68
    t+=_hole(R,2)                                         # 69-70

    # ===== Section C: コイン雲回廊 + 段違い降下 (col 71-100) =====
    t.append(_c(R,A,A,A,A,A,A,A,CL,A,A,A,A,A,A,A,A))    # 71: CL row7
    t.append(_c(R,A,A,A,A,A,C,A,CL,A,A,A,A,A,A,A,A))    # 72: コイン上
    t.append(_c(R,A,A,A,A,A,C,A,CL,A,A,A,A,A,A,A,A))    # 73
    t.append(_c(R,A,A,A,A,A,C,A,CL,A,A,A,A,A,A,A,A))    # 74
    t+=_hole(R,2)                                         # 75-76
    # 段違い降下(row7→row8→row10)
    t.append(_c(R,A,A,A,A,A,A,A,G,A,A,A,A,A,A,A,A))     # 77: row7
    t+=_hole(R,1)                                         # 78
    t.append(_c(R,A,A,A,A,A,A,A,A,G,A,A,A,A,A,A,A))     # 79: row8
    t+=_hole(R,1)                                         # 80
    t.append(_c(R,A,A,A,A,A,A,A,A,A,A,G,A,A,A,A,A))     # 81: row10
    t.append(_c(R,A,A,A,A,A,A,A,A,A,A,G,A,A,A,A,A))     # 82
    t+=_hole(R,2)                                         # 83-84
    t.append(_c(R,A,A,A,A,A,A,A,A,A,A,G,A,A,A,A,A))     # 85
    t.append(_c(R,A,A,A,A,A,A,A,A,A,A,G,A,A,A,A,A))     # 86
    t.append(_c(R,A,A,A,A,A,A,A,A,A,A,G,A,A,A,A,A))     # 87
    t+=_hole(R,3)                                         # 88-90: 大穴!
    # 広い台 + ?ブロック
    t.append(_c(R,A,A,A,A,A,A,A,A,A,A,G,A,A,A,A,A))     # 91: row10
    t.append(_c(R,A,A,A,A,Q,A,A,A,A,A,G,A,A,A,A,A))     # 92: ?ブロックrow4
    t.append(_c(R,A,A,A,A,A,A,A,A,A,A,G,A,A,A,A,A))     # 93
    t+=_hole(R,2)                                         # 94-95
    t.append(_c(R,A,A,A,A,A,A,A,A,A,A,CL,A,A,A,A,A))    # 96: CL row10
    t.append(_c(R,A,A,A,A,A,A,A,A,A,A,CL,A,A,A,A,A))    # 97
    t+=_hole(R,2)                                         # 98-99
    t.append(_c(R,A,A,A,A,A,A,A,A,A,A,G,G,A,A,A,A))     # 100: row10-11

    # ===== Section D: ゴール塔へ上昇 (col 101-127) =====
    t.append(_c(R,A,A,A,A,A,A,A,A,A,A,G,G,A,A,A,A))     # 101
    t.append(_c(R,A,A,A,A,A,A,A,A,A,A,G,G,A,A,A,A))     # 102
    t+=_hole(R,2)                                         # 103-104
    # row8台(row10から4タイル上=限界ジャンプ)
    t.append(_c(R,A,A,A,A,A,A,A,A,G,A,A,A,A,A,A,A))     # 105: row8
    t.append(_c(R,A,A,A,A,A,A,A,A,G,A,A,A,A,A,A,A))     # 106
    t+=_hole(R,1)                                         # 107
    # row6台(row8から2タイル上=余裕)
    t.append(_c(R,A,A,A,A,A,A,G,A,A,A,A,A,A,A,A,A))     # 108: row6
    t.append(_c(R,A,A,A,A,A,A,G,A,A,A,A,A,A,A,A,A))     # 109
    t.append(_c(R,A,A,A,A,A,A,G,A,A,A,A,A,A,A,A,A))     # 110
    t+=_hole(R,1)                                         # 111
    # ゴール島(row6-11に地面, FLAG row4)
    t.append(_c(R,A,A,A,A,FL,A,G,G,G,G,G,G,A,A,A,A))    # 112: FLAG+台
    t.append(_c(R,A,A,A,A,A,A,G,G,G,G,G,G,A,A,A,A))     # 113
    t.append(_c(R,A,A,A,A,A,A,G,G,G,G,G,G,A,A,A,A))     # 114
    while len(t)<128:t+=_hole(R,1)
    t=t[:128]
    return{
        'name':'1-4 SKY ZONE','bgm':'sky','width':128,'rows':R,
        'time_limit':120,'terrain':t,'water':False,'gravity_scale':1.0,
        'start_col':2,'start_row':R-6,'goal_col':110,'flag_col':110,
        'objects':[
            (27,4,'qblock_random'),
            (57,4,'qblock_random'),
            (92,4,'qblock_random'),
        ],
        'enemy_sets':{
            'easy': [
                (36,6,'pata_new'),
                (65,6,'pata_new'),
                (22,9,'big_mushroom'),(85,9,'big_mushroom'),
            ],
            'normal': [
                (17,6,'pata_new'),(36,6,'pata_new'),
                (50,7,'killer_spawn'),
                (65,6,'pata_new'),
                (96,9,'pata_new'),
                (22,9,'big_mushroom'),(85,9,'big_mushroom'),
            ],
            'hard': [
                (17,6,'pata_new'),(36,6,'pata_new'),
                (50,7,'killer_spawn'),
                (65,6,'pata_new'),(80,5,'killer_spawn'),
                (96,9,'pata_new'),
            ],
        },
    }


def _build_s5():
    R=12;t=[]
    for i in range(128):
        if i<5:
            t.append(_c(R,A,A,A,A,A,A,A,A,A,A,G,G))
        elif i<12:
            if i%3==0: t.append(_c(R,A,A,A,A,A,A,A,A,A,A,MA,MA))
            else:       t.append(_c(R,A,A,A,A,A,A,A,A,A,A,G,G))
        elif i<25:
            if i%4==0:   t.append(_c(R,A,A,A,A,A,A,A,A,A,A,MA,MA))
            elif i%4==2: t.append(_c(R,A,A,A,A,A,G,A,A,A,A,MA,MA))
            else:         t.append(_c(R,A,A,A,A,A,A,A,A,A,A,G,G))
        elif i<35:
            if i%3==0:   t.append(_c(R,S,A,A,A,A,A,A,A,A,A,MA,MA))
            elif i%3==1: t.append(_c(R,A,A,A,A,A,B,A,A,A,A,MA,MA))
            else:         t.append(_c(R,A,A,A,A,A,B,A,A,A,A,G,G))
        elif i==38:
            t.append(_c(R,A,A,A,A,A,Q,A,A,A,A,G,G))
        elif i<50:
            if i%4==0:   t.append(_c(R,A,A,A,A,A,A,A,A,A,A,MA,MA))
            elif i%3==0: t.append(_c(R,A,A,A,A,A,A,CL,A,A,A,MA,MA))
            else:         t.append(_c(R,A,A,A,A,A,A,A,A,A,A,G,G))
        elif i<60:
            if i%2==0: t.append(_c(R,A,A,A,A,A,A,A,A,A,S,G,G))
            else:       t.append(_c(R,A,A,A,A,A,A,A,A,A,A,G,G))
        elif i==62:
            t.append(_c(R,A,A,A,A,A,Q,A,A,A,A,G,G))
        elif i<75:
            if i%4==0:   t.append(_c(R,A,A,A,A,A,A,A,A,A,A,MA,MA))
            elif i%4==2: t.append(_c(R,A,A,A,B,A,A,A,A,A,A,MA,MA))
            else:         t.append(_c(R,A,A,A,A,A,A,A,A,A,A,G,G))
        elif i<90:
            if i%5==0:   t.append(_c(R,S,A,A,A,A,A,A,A,A,A,MA,MA))
            elif i%5==2: t.append(_c(R,A,A,A,A,B,A,A,A,A,A,MA,MA))
            elif i%5==4: t.append(_c(R,A,A,A,A,A,A,A,A,A,A,MA,MA))
            else:         t.append(_c(R,A,A,A,A,A,A,A,A,A,A,G,G))
        elif i<100:
            t.append(_c(R,A,A,A,A,A,A,A,A,A,A,G,G))
        elif i==100: t.append(_c(R,A,A,A,A,A,A,A,A,A,G,G,G))      # 階段row9
        elif i==101: t.append(_c(R,A,A,A,A,A,A,A,A,G,G,G,G))      # row8
        elif i==102: t.append(_c(R,A,A,A,A,A,A,A,G,G,G,G,G))      # row7
        elif i==103: t.append(_c(R,A,A,A,A,A,A,G,G,G,G,G,G))      # row6 最高
        elif i==104: t.append(_c(R,A,A,A,A,A,A,A,A,A,A,G,G))      # 降下口
        elif i==105:
            t.append(_c(R,A,A,A,A,FL,FL,FL,FL,FL,FL,G,G))
        else:
            t.append(_c(R,A,A,A,A,A,A,A,A,A,A,G,G))
    t=t[:128]
    return{
        'name':'1-5 CASTLE WALL','bgm':'castle','width':128,'rows':R,
        'time_limit':100,'terrain':t,'water':False,'gravity_scale':1.0,
        'start_col':2,'start_row':R-4,'goal_col':110,'flag_col':110,
        'objects':[
            (38,5,'qblock_random'),(62,5,'qblock_random'),
        ],
        'enemy_sets':{
            'easy': [
                (35,R-3,'goomba'),
                (98,R-3,'goomba'),
            ],
            'normal': [
                (18,R-3,'goomba'),(35,R-3,'goomba'),
                (55,4,'killer_spawn'),
                (98,R-3,'goomba'),
            ],
            'hard': [
                (18,R-3,'goomba'),(35,R-3,'goomba'),
                (55,4,'killer_spawn'),
                (72,R-3,'goomba'),(85,4,'killer_spawn'),
                (98,R-3,'goomba'),
            ],
        },
    }


def _build_s6():
    # 城内ボス戦アリーナ。32x8 → 48x8 に拡張、足場・トゲ・天井障害を追加
    R=8;t=[]
    # 入口
    t.append(_c(R,G,G,G,G,G,G,G,G))          # 0: 左壁
    for _ in range(3): t.append(_c(R,A,A,A,A,A,A,G,G))   # 1-3: 平地
    # 入口の天井ブリック(マグマ地帯の演出)
    t.append(_c(R,B,A,A,A,A,A,G,G))          # 4: 天井レンガ
    t.append(_c(R,B,A,A,A,Q,A,G,G))          # 5: ?ブロック中段
    t.append(_c(R,B,A,A,A,A,A,G,G))          # 6
    t.append(_c(R,A,A,A,A,A,A,G,G))          # 7
    # マグマ地帯1: 下部マグマ + 浮島
    for i in range(8,12):
        if i==9 or i==10:
            t.append(_c(R,A,A,A,A,A,G,MA,MA))    # 浮島row5・下マグマ
        else:
            t.append(_c(R,A,A,A,A,A,A,MA,MA))    # マグマ単独
    # 中央広場 (col 12-22): 主戦場
    for i in range(12,23):
        if i==17:
            t.append(_c(R,A,A,B,A,A,A,G,G))     # 中央天井レンガ row2
        else:
            t.append(_c(R,A,A,A,A,A,A,G,G))
    # マグマ地帯2: 上下からの圧力
    for i in range(23,28):
        if i==24 or i==26:
            t.append(_c(R,B,A,A,A,A,A,MA,MA))   # 天井レンガ + マグマ床
        else:
            t.append(_c(R,A,A,A,A,A,A,MA,MA))
    # 最終足場
    for _ in range(3): t.append(_c(R,A,A,A,A,A,A,G,G))   # 28-30
    # ボス本陣
    for _ in range(15): t.append(_c(R,A,A,A,A,A,A,G,G))  # 31-45
    t.append(_c(R,G,G,G,G,G,G,G,G))          # 46: 右壁
    t.append(_c(R,G,G,G,G,G,G,G,G))          # 47
    while len(t)<48: t.append(_c(R,G,G,G,G,G,G,G,G))
    t=t[:48]
    return{
        'name':'BOSS - KING KOOPA','bgm':'boss','width':48,'rows':R,
        'time_limit':250,'terrain':t,'water':False,'gravity_scale':1.0,
        'start_col':2,'start_row':R-3,'goal_col':-1,
        'objects':[(5,4,'qblock_random'),(40,4,'boss')],
        'enemy_sets':{},
    }


def _build_pipe_sub():
    R=8;t=[]
    t.append(_c(R,G,G,G,G,G,G,G,G))
    for i in range(30):
        if i%4==0:   t.append(_c(R,G,A,C,A,A,C,A,G))
        elif i%4==1: t.append(_c(R,G,A,A,A,C,A,C,G))
        elif i%4==2: t.append(_c(R,G,A,C,A,C,A,A,G))
        else:        t.append(_c(R,G,A,A,A,A,A,A,G))
    t.append(_c(R,G,G,G,G,G,G,G,G))
    return{
        'name':'BONUS ROOM','bgm':'underground','width':32,'rows':R,
        'time_limit':30,'terrain':t,'water':False,'gravity_scale':1.0,
        'start_col':2,'start_row':R-3,'goal_col':-1,
        'exit_col':30,
        'objects':[],
        'enemy_sets':{},
    }


STAGES_NEW=[_build_s1(),_build_s2(),_build_s3(),_build_s4(),_build_s5(),_build_s6()]
PIPE_SUBSTAGE=_build_pipe_sub()

def get_stage_new(num):
    if 1<=num<=len(STAGES_NEW): return STAGES_NEW[num-1]
    return None
