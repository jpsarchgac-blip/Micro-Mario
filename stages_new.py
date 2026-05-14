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

def _build_s1():
    R=12;t=[]
    # Phase1: 平地スタート(col0-24)
    t+=_flat(R,8)  # 平地8
    t+=[_c(R,A,A,A,A,A,A,Q,A,A,A,G,G)]  # ?ブロック col8
    t+=_flat(R,6)  # 平地
    t+=[_c(R,A,A,A,A,A,A,A,A,A,A,A,A)]*2  # 穴 col15-16
    t+=_flat(R,8)  # 平地 col17-24
    # Phase2: 土管+レンガ(col25-49)
    t+=[_c(R,A,A,A,A,A,B,A,A,A,A,G,G)]  # レンガ
    t+=[_c(R,A,A,A,A,A,B,A,A,A,A,G,G)]
    t+=[_c(R,A,A,A,A,A,B,A,A,A,A,G,G)]
    t+=_flat(R,4)  # 休憩
    t+=[_c(R,A,A,A,A,A,C,A,A,A,A,G,G)]  # コイン
    t+=[_c(R,A,A,A,A,A,C,A,A,A,A,G,G)]
    t+=[_c(R,A,A,A,A,A,C,A,A,A,A,G,G)]
    t+=_flat(R,3)
    # ドカン col38-39(上向き口)
    t+=[_c(R,A,A,A,A,A,A,A,PT,PB,A,G,G)]
    t+=[_c(R,A,A,A,A,A,A,A,PR,PD,A,G,G)]
    t+=_flat(R,6)  # 休憩
    t+=_flat(R,4)  # col46-49
    # Phase3: 階段(col50-74)
    t+=_flat(R,5)  # 平地
    t+=[_c(R,A,A,A,A,A,A,A,A,A,G,G,G)]  # 階段1
    t+=[_c(R,A,A,A,A,A,A,A,A,G,G,G,G)]  # 階段2
    t+=[_c(R,A,A,A,A,A,A,A,G,G,G,G,G)]  # 階段3
    t+=[_c(R,A,A,A,A,A,A,G,G,G,G,G,G)]  # 階段4
    t+=[_c(R,A,A,A,A,A,A,A,A,A,A,A,A)]*2  # 穴
    t+=_flat(R,8)  # 休憩
    t+=_flat(R,6)  # col69-74
    # Phase4: コイン+敵(col75-99)
    t+=_flat(R,5)
    t+=[_c(R,A,A,A,A,A,C,C,A,A,A,G,G)]*3  # 縦コイン
    t+=_flat(R,6)  # 休憩
    t+=[_c(R,A,A,A,A,A,A,A,A,A,A,A,A)]*2  # 穴
    t+=_flat(R,9)
    # Phase5: ゴール(col100-127)
    t+=_flat(R,10)  # 平地
    t+=[_c(R,A,A,A,A,A,A,A,A,A,G,G,G)]
    t+=[_c(R,A,A,A,A,A,A,A,A,G,G,G,G)]
    t+=[_c(R,A,A,A,A,A,A,A,G,G,G,G,G)]
    t+=_flat(R,4)
    # ゴール旗
    t+=[_c(R,A,A,A,A,FL,FL,FL,FL,FL,FL,G,G)]
    t+=_flat(R,10)
    # パディング
    while len(t)<128:
        t+=_flat(R,1)
    t=t[:128]
    return{
        'name':'1-1 GREEN HILL','bgm':'overworld','width':128,'rows':R,
        'time_limit':100,'terrain':t,'water':False,'gravity_scale':1.0,
        'start_col':2,'start_row':R-4,'goal_col':118,'flag_col':117,
        'pipe_col':38,'pipe_dest':'substage','pipe_return_col':64,
        'objects':[
            (8,6,'qblock_random'),
            (20,R-3,'goomba'),(35,R-3,'goomba'),(55,R-3,'goomba'),
            (70,R-3,'goomba'),(90,R-3,'goomba'),(105,R-3,'goomba'),
        ],
        'enemy_sets':{'easy':[(20,R-3,'goomba'),(70,R-3,'goomba'),(105,R-3,'goomba')],
                      'hard':[(25,R-3,'goomba'),(45,R-3,'goomba'),(85,R-3,'goomba')]},
    }

def _build_s2():
    R=12;t=[]
    # 地下: 天井row0-1, 地面row10-11
    ceil=[G,G];floor=[G,G]
    def uc(*mid):
        return _c(R,*ceil,*list(mid),*floor)
    # Phase1: 入口(0-24)
    for _ in range(5): t.append(uc(A,A,A,A,A,A,A,A))
    for _ in range(3): t.append(uc(A,C,A,A,A,A,A,A))  # 天井コイン
    for _ in range(4): t.append(uc(A,A,A,A,A,A,A,A))
    for _ in range(3): t.append(uc(B,A,A,A,A,A,A,A))  # レンガ天井
    for _ in range(6): t.append(uc(A,A,A,A,A,A,A,A))  # 休憩
    for _ in range(3): t.append(uc(A,A,A,A,A,A,A,A))
    # Phase2: トゲ地帯(25-49)
    for _ in range(5): t.append(uc(A,A,A,A,A,A,A,A))
    t.append(_c(R,G,G,A,A,A,A,A,A,S,A,G,G))  # トゲ
    t.append(_c(R,G,G,A,A,A,A,A,A,S,A,G,G))
    for _ in range(6): t.append(uc(A,A,A,A,A,A,A,A))  # 休憩
    t.append(uc(A,A,A,Q,A,A,A,A))  # ?ブロック
    for _ in range(5): t.append(uc(A,A,A,A,A,A,A,A))
    for _ in range(6): t.append(uc(A,A,A,A,A,A,A,A))
    # Phase3: 狭路(50-74)
    for _ in range(5): t.append(uc(A,A,A,A,A,A,A,A))
    for _ in range(4): t.append(_c(R,G,G,B,A,A,A,A,B,A,A,G,G))  # 狭路
    for _ in range(8): t.append(uc(A,A,A,A,A,A,A,A))  # 休憩
    t.append(_c(R,G,G,A,A,A,A,A,A,S,A,G,G))  # トゲ
    t.append(_c(R,G,G,A,A,A,A,A,A,S,A,G,G))
    for _ in range(5): t.append(uc(A,A,A,A,A,A,A,A))
    # Phase4-5: ゴール(75-127)
    for _ in range(10): t.append(uc(A,A,A,A,A,A,A,A))
    for _ in range(3): t.append(uc(A,C,A,C,A,A,A,A))  # コイン
    for _ in range(10): t.append(uc(A,A,A,A,A,A,A,A))
    t.append(_c(R,G,G,GO,GO,GO,GO,GO,GO,GO,GO,G,G))  # ゴール
    while len(t)<128: t.append(uc(A,A,A,A,A,A,A,A))
    t=t[:128]
    return{
        'name':'1-2 UNDERGROUND','bgm':'underground','width':128,'rows':R,
        'time_limit':90,'terrain':t,'water':False,'gravity_scale':1.0,
        'start_col':2,'start_row':R-4,'goal_col':98,
        'objects':[
            (38,5,'qblock_random'),
            (15,R-3,'goomba'),(28,R-3,'goomba'),(45,4,'bat'),
            (60,R-3,'goomba'),(72,4,'bat'),(88,R-3,'goomba'),
        ],
        'enemy_sets':{'easy':[(15,R-3,'goomba'),(60,R-3,'goomba')],
                      'hard':[(35,R-3,'goomba'),(50,4,'bat'),(80,R-3,'goomba')]},
    }

def _build_s3():
    R=16;t=[]
    # 水中: 海面row0-1, 海底row14-15
    def wc(*mid):
        ids=[G,G]+list(mid)+[G,G]
        while len(ids)<R: ids.insert(2,A)
        return _c(R,*ids[:R])
    # 128列
    for i in range(128):
        if i<5: t.append(wc(A,A,A,A,A,A,A,A,A,A,A,A))
        elif i<15:  # コイン縦配置
            if i%3==0: t.append(_c(R,G,G,A,A,C,A,A,A,A,A,C,A,A,A,G,G))
            else: t.append(_c(R,G,G,A,A,A,A,A,A,A,A,A,A,A,A,G,G))
        elif i<25: t.append(_c(R,G,G,A,A,A,A,A,A,A,A,A,A,A,A,G,G))
        elif i<30:  # 障害物
            if i==27: t.append(_c(R,G,G,A,A,A,B,B,A,A,A,A,A,A,A,G,G))
            else: t.append(_c(R,G,G,A,A,A,A,A,A,A,A,A,A,A,A,G,G))
        elif i==40: t.append(_c(R,G,G,A,A,A,Q,A,A,A,A,A,A,A,A,G,G))
        elif i<60:  # コイン+障害
            if i%5==0: t.append(_c(R,G,G,A,A,A,A,C,A,A,C,A,A,A,A,G,G))
            else: t.append(_c(R,G,G,A,A,A,A,A,A,A,A,A,A,A,A,G,G))
        elif i<80: t.append(_c(R,G,G,A,A,A,A,A,A,A,A,A,A,A,A,G,G))
        elif i<100:
            if i%4==0: t.append(_c(R,G,G,A,C,A,A,A,A,A,A,A,A,C,A,G,G))
            else: t.append(_c(R,G,G,A,A,A,A,A,A,A,A,A,A,A,A,G,G))
        elif i==110: t.append(_c(R,G,G,GO,GO,GO,GO,GO,GO,GO,GO,GO,GO,GO,GO,G,G))
        else: t.append(_c(R,G,G,A,A,A,A,A,A,A,A,A,A,A,A,G,G))
    t=t[:128]
    return{
        'name':'1-3 UNDERWATER','bgm':'water','width':128,'rows':R,
        'time_limit':120,'terrain':t,'water':True,'gravity_scale':0.2,
        'start_col':2,'start_row':6,'goal_col':110,
        'objects':[
            (40,5,'qblock_random'),
            (12,6,'fish'),(25,10,'fish'),(45,8,'fish'),
            (65,6,'fish'),(80,10,'fish'),(95,8,'fish'),
        ],
        'enemy_sets':{'easy':[(25,10,'fish'),(65,6,'fish')],
                      'hard':[(35,8,'fish'),(55,6,'fish'),(85,10,'fish')]},
    }

def _build_s4():
    R=16;t=[]
    for i in range(128):
        if i<5: t.append(_c(R,A,A,A,A,A,A,A,A,A,A,A,A,G,G,G,G))
        elif i<10:
            if i%2==0: t.append(_c(R,A,A,A,A,A,A,A,A,A,A,CL,A,A,A,A,A))
            else: t.append(_c(R,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A))
        elif i<20:
            if i%3==0: t.append(_c(R,A,A,A,A,A,A,A,CL,A,A,A,A,A,A,A,A))
            elif i%3==1: t.append(_c(R,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A))
            else: t.append(_c(R,A,A,A,A,A,A,A,A,A,CL,A,A,A,A,A,A))
        elif i<30:  # 雲の道
            if i%2==0: t.append(_c(R,A,A,A,A,A,CL,A,A,A,A,A,A,A,A,A,A))
            else: t.append(_c(R,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A))
        elif i==35: t.append(_c(R,A,A,A,A,A,A,Q,A,A,A,A,A,A,A,A,A))
        elif i<50:
            if i%3==0: t.append(_c(R,A,A,A,A,A,A,A,CL,A,A,A,A,G,G,G,G))
            elif i%4==0: t.append(_c(R,A,A,A,A,CL,A,A,A,A,A,A,A,A,A,A,A))
            else: t.append(_c(R,A,A,A,A,A,A,A,A,A,A,A,A,G,G,G,G))
        elif i<70:
            if i%3==0: t.append(_c(R,A,A,A,CL,A,A,A,A,A,A,A,A,A,A,A,A))
            elif i%5==0: t.append(_c(R,A,A,A,A,A,A,A,A,CL,A,A,A,A,A,A,A))
            else: t.append(_c(R,A,A,A,A,A,A,A,A,A,A,A,A,G,G,G,G))
        elif i<90:
            if i%2==0: t.append(_c(R,A,A,A,A,A,A,CL,A,A,A,A,A,A,A,A,A))
            else: t.append(_c(R,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A,A))
        elif i<100: t.append(_c(R,A,A,A,A,A,A,A,A,A,A,A,A,G,G,G,G))
        elif i==110: t.append(_c(R,A,A,A,A,FL,FL,FL,FL,FL,FL,FL,FL,G,G,G,G))
        else: t.append(_c(R,A,A,A,A,A,A,A,A,A,A,A,A,G,G,G,G))
    t=t[:128]
    return{
        'name':'1-4 SKY ZONE','bgm':'sky','width':128,'rows':R,
        'time_limit':120,'terrain':t,'water':False,'gravity_scale':1.0,
        'start_col':2,'start_row':R-6,'goal_col':110,'flag_col':110,
        'objects':[
            (35,6,'qblock_random'),
            (15,8,'pata_new'),(30,4,'pata_new'),(50,6,'killer_spawn'),
            (65,3,'pata_new'),(80,5,'killer_spawn'),(95,4,'pata_new'),
            (25,R-5,'big_mushroom'),(60,R-5,'big_mushroom'),
        ],
        'enemy_sets':{'easy':[(30,4,'pata_new'),(65,3,'pata_new')],
                      'hard':[(40,6,'killer_spawn'),(70,5,'pata_new'),(85,4,'killer_spawn')]},
    }

def _build_s5():
    R=12;t=[]
    for i in range(128):
        if i<5: t.append(_c(R,A,A,A,A,A,A,A,A,A,A,G,G))
        elif i<15:
            if i%3==0: t.append(_c(R,A,A,A,A,A,A,A,A,A,A,A,A))  # 穴→マグマ下
            else: t.append(_c(R,A,A,A,A,A,A,A,A,A,A,G,G))
        elif i<30:
            if i%4==0: t.append(_c(R,A,A,A,A,A,A,A,A,A,A,MA,MA))  # マグマ
            elif i%4==2: t.append(_c(R,A,A,A,A,A,A,A,A,A,A,A,A))
            else: t.append(_c(R,A,A,A,A,A,A,A,A,A,A,G,G))
        elif i<50:
            if i%3==0: t.append(_c(R,A,A,A,A,A,B,A,A,A,A,MA,MA))
            elif i%5==0: t.append(_c(R,A,A,A,A,A,A,A,A,A,A,A,A))
            else: t.append(_c(R,A,A,A,A,A,A,A,A,A,A,G,G))
        elif i==55: t.append(_c(R,A,A,A,A,A,Q,A,A,A,A,G,G))
        elif i<80:
            if i%4==0: t.append(_c(R,A,A,A,A,A,A,A,A,A,A,MA,MA))
            elif i%3==0: t.append(_c(R,A,A,A,A,A,A,CL,A,A,A,MA,MA))
            else: t.append(_c(R,A,A,A,A,A,A,A,A,A,A,G,G))
        elif i<100:
            if i%3==0: t.append(_c(R,A,A,A,A,A,A,A,A,A,A,MA,MA))
            else: t.append(_c(R,A,A,A,A,A,A,A,A,A,A,G,G))
        elif i==110: t.append(_c(R,A,A,A,A,FL,FL,FL,FL,FL,FL,G,G))
        else: t.append(_c(R,A,A,A,A,A,A,A,A,A,A,G,G))
    t=t[:128]
    return{
        'name':'1-5 CASTLE WALL','bgm':'castle','width':128,'rows':R,
        'time_limit':100,'terrain':t,'water':False,'gravity_scale':1.0,
        'start_col':2,'start_row':R-4,'goal_col':110,'flag_col':110,
        'objects':[
            (55,5,'qblock_random'),
            (20,R-3,'goomba'),(40,R-3,'goomba'),(50,4,'killer_spawn'),
            (70,R-3,'goomba'),(85,4,'killer_spawn'),(100,R-3,'goomba'),
        ],
        'enemy_sets':{'easy':[(20,R-3,'goomba'),(70,R-3,'goomba')],
                      'hard':[(35,R-3,'goomba'),(60,4,'killer_spawn'),(90,R-3,'goomba')]},
    }

def _build_s6():
    R=8;t=[]
    t.append(_c(R,G,G,G,G,G,G,G,G))  # 左壁
    for _ in range(30):
        t.append(_c(R,A,A,A,A,A,A,G,G))
    t.append(_c(R,G,G,G,G,G,G,G,G))  # 右壁
    return{
        'name':'BOSS - KING KOOPA','bgm':'boss','width':32,'rows':R,
        'time_limit':200,'terrain':t,'water':False,'gravity_scale':1.0,
        'start_col':2,'start_row':R-4,'goal_col':-1,
        'objects':[(24,4,'boss')],
        'enemy_sets':{},
    }

def _build_pipe_sub():
    R=8;t=[]
    t.append(_c(R,G,G,G,G,G,G,G,G))  # 左壁
    for i in range(30):
        if i%3==1: t.append(_c(R,G,A,A,C,A,C,A,G))
        elif i%3==2: t.append(_c(R,G,A,C,A,C,A,A,G))
        else: t.append(_c(R,G,A,A,A,A,A,A,G))
    t.append(_c(R,G,G,G,G,G,G,G,G))  # 右壁(出口)
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
