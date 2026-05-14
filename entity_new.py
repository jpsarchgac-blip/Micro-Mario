# entity_new.py - NEWモード追加エンティティ
# 既存entity.pyのGoomba/Bat/Fish/Boss等はそのまま再利用
import config as C
import world_new as wn

class Killer:
    """キラー: 横一直線に飛来。踏みつけ可能。"""
    w=8;h=8;alive=True;solid_for_player=True
    def __init__(self,x,y,d=-1):
        self.x=float(x);self.y=float(y);self.vx=2.0*d;self.anim=0
    def aabb(self): return(self.x,self.y,self.w,self.h)
    def update(self,world,player):
        self.x+=self.vx;self.anim+=1
        if self.x<-16 or self.x>world.width*C.TILE+16: self.alive=False
    def draw(self,oled,bank,cam_x,cam_y=0):
        sx=int(self.x)-cam_x;sy=int(self.y)-cam_y
        if-8<=sx<=128 and -8<=sy<=64:
            k='killer_2'if(self.anim>>2)&1 else'killer_1'
            oled.blit(bank.fb[k],sx,sy)
    def on_stomp(self): self.alive=False;return True
    def on_fireball(self): self.alive=False;return True
    def on_collide(self,player): return'damage'

class KillerSpawner:
    """キラー召喚ポイント: 一定間隔でKillerを生成"""
    w=0;h=0;alive=True;solid_for_player=False
    def __init__(self,col,row,interval=120):
        self.x=float(col*C.TILE);self.y=float(row*C.TILE)
        self.interval=interval;self.timer=60;self.spawned=[]
    def aabb(self): return(self.x,self.y,0,0)
    def update(self,world,player):
        self.timer-=1
        if self.timer<=0:
            self.timer=self.interval
            k=Killer(self.x+C.TILE*16,self.y,-1)
            self.spawned.append(k)
        self.spawned=[s for s in self.spawned if s.alive]
        for s in self.spawned: s.update(world,player)
    def draw(self,oled,bank,cam_x,cam_y=0):
        for s in self.spawned: s.draw(oled,bank,cam_x,cam_y)
    def on_stomp(self): return False
    def on_fireball(self): return False
    def on_collide(self,p): return None
    def get_killers(self): return self.spawned

class PatapataNew:
    """パタパタNEW: 横移動左右反転。踏むとバネジャンプ+敵落下"""
    w=8;h=8;alive=True;solid_for_player=True
    def __init__(self,col,row):
        self.x=float(col*C.TILE);self.y=float(row*C.TILE)
        self.vx=0.6;self.anim=0;self.falling=False;self.vy=0
    def aabb(self): return(self.x,self.y,self.w,self.h)
    def update(self,world,player):
        if self.falling:
            self.vy+=0.4;self.y+=self.vy
            if self.y>world.map_h_px+16: self.alive=False
            return
        self.x+=self.vx;self.anim+=1
        # 壁で反転
        nx=world.collide_x(self.x,self.y,self.w,self.h,self.vx)
        if nx==self.x and self.vx!=0: self.vx=-self.vx
        else: self.x=nx
    def draw(self,oled,bank,cam_x,cam_y=0):
        sx=int(self.x)-cam_x;sy=int(self.y)-cam_y
        if-8<=sx<=128 and -8<=sy<=64:
            k='pata_n2'if(self.anim>>2)&1 else'pata_n1'
            oled.blit(bank.fb[k],sx,sy)
    def on_stomp(self):
        self.falling=True;self.vy=0;self.solid_for_player=False
        return True
    def on_fireball(self): self.alive=False;return True
    def on_collide(self,player):
        if self.falling: return None
        return'damage'

class BigMushroom:
    """大きのこ: 静止トランポリン。触れると高ジャンプ。"""
    w=8;h=8;alive=True;solid_for_player=False
    def __init__(self,col,row):
        self.x=float(col*C.TILE);self.y=float(row*C.TILE)
        self.bounce_anim=0
    def aabb(self): return(self.x,self.y,self.w,self.h)
    def update(self,world,player):
        if self.bounce_anim>0: self.bounce_anim-=1
    def draw(self,oled,bank,cam_x,cam_y=0):
        sx=int(self.x)-cam_x;sy=int(self.y)-cam_y
        if-8<=sx<=128 and -8<=sy<=64:
            dy=-2 if self.bounce_anim>0 else 0
            oled.blit(bank.fb['big_mush'],sx,sy+dy)
    def on_bounce(self):
        self.bounce_anim=8
    def on_stomp(self): return False
    def on_fireball(self): return False
    def on_collide(self,p): return None

class StarItem:
    """スター: バウンド移動、取得で無敵付与"""
    w=8;h=8;alive=True;solid_for_player=False
    def __init__(self,x,y):
        self.x=float(x);self.y=float(y)
        self.vx=1.2;self.vy=-2.0;self.anim=0;self.spawn_anim=16
    def aabb(self): return(self.x,self.y,self.w,self.h)
    def update(self,world,player):
        if self.spawn_anim>0:
            self.spawn_anim-=1;self.y-=0.5;return
        self.vy=min(self.vy+0.3,C.TERMINAL_VEL)
        nx=world.collide_x(self.x,self.y,self.w,self.h,self.vx)
        if nx==self.x: self.vx=-self.vx
        else: self.x=nx
        ny,og,_=world.collide_y(self.x,self.y,self.w,self.h,self.vy)
        self.y=ny
        if og: self.vy=-3.0
        if self.y>world.map_h_px+16: self.alive=False
        self.anim+=1
    def draw(self,oled,bank,cam_x,cam_y=0):
        sx=int(self.x)-cam_x;sy=int(self.y)-cam_y
        if-8<=sx<=128 and -8<=sy<=64:
            k='star_2'if(self.anim>>2)&1 else'star_1'
            oled.blit(bank.fb[k],sx,sy)
    def on_stomp(self): return False
    def on_fireball(self): return False
    def on_collide(self,p): return None

def make_entity_new(type_str,col,row):
    """NEWモード用エンティティファクトリ"""
    # 既存のentity.pyのものも使う
    import entity as et
    if type_str=='goomba': return et.Goomba(col,row)
    if type_str=='bat': return et.Bat(col,row)
    if type_str=='fish': return et.Fish(col,row)
    if type_str=='boss': return et.Boss(col,row)
    if type_str=='pata_new': return PatapataNew(col,row)
    if type_str=='killer_spawn': return KillerSpawner(col,row)
    if type_str=='big_mushroom': return BigMushroom(col,row)
    return None
