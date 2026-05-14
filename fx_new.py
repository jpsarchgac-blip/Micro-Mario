# fx_new.py - NEWモード用LED演出
# LED1=イベント, LED2=マリオ状態+BGM振動, LED3=マップ状態
from machine import Pin
from neopixel import NeoPixel
import config as C

def _clamp(v):
    if v<0:return 0
    if v>C.LED_MAX_BRIGHT:return C.LED_MAX_BRIGHT
    return v

def _scale(rgb,f):
    return(rgb[0]*f//100,rgb[1]*f//100,rgb[2]*f//100)

STAGE_COLOR={
    1:(10,25,15),2:(20,0,30),3:(0,15,30),
    4:(25,25,30),5:(35,5,0),6:(35,0,0),
}

_SLOT_COLORS=[(35,35,0),(40,25,0),(40,15,0),(40,5,0),(40,15,0),(40,25,0)]
_RAINBOW=[(40,0,0),(40,20,0),(35,35,0),(0,40,0),(0,20,40),(25,0,40)]
_DMG_DECAY=[(40,0,0),(40,40,40),(40,0,0),(25,0,0),(12,0,0),(5,0,0),(2,0,0),(0,0,0)]

class FxNew:
    def __init__(self):
        self.np=NeoPixel(Pin(C.PIN_NEOPIXEL,Pin.OUT),3)
        self.last=[(0,0,0)]*3
        # LED1 event
        self.ev_color=(0,0,0);self.ev_timer=0;self.ev_rainbow=0
        self.slot_spin=False
        self.goal_flash=0
        # LED2 player
        self.p_state='big';self.star_mode=False;self.beat_boost=0
        self.inv_timer=0;self.dmg_flash=0
        # LED3 map
        self.stage_num=1;self.diff='NORMAL'

    def set_player_state(self,s):self.p_state=s
    def set_star(self,on):self.star_mode=on
    def set_stage(self,n):self.stage_num=n
    def set_invincible(self,f):self.inv_timer=f
    def set_damage(self):self.dmg_flash=8
    def beat(self):self.beat_boost=6
    def event_flash(self,c,f=8):self.ev_color=c;self.ev_timer=f
    def rainbow(self,f=30):self.ev_rainbow=f
    def set_slot_spin(self,on):self.slot_spin=on
    def set_goal_flash(self,f):self.goal_flash=f
    def set_difficulty(self,d):self.diff=d

    def update(self,frame):
        # LED1: イベント・スロット
        if self.goal_flash>0:
            self.goal_flash-=1
            # 3本が交互に白点滅（喜び）
            idx=(self.goal_flash>>2)%3
            led0=(C.LED_MAX_BRIGHT,)*3 if idx==0 else (0,0,0)
            led1=(C.LED_MAX_BRIGHT,)*3 if idx==1 else (0,0,0)
            led2=(C.LED_MAX_BRIGHT,)*3 if idx==2 else (0,0,0)
            self._write([led0,led1,led2]);return
        if self.slot_spin:
            led0=_SLOT_COLORS[(frame>>2)%6]
        elif self.ev_rainbow>0:
            led0=_RAINBOW[(30-self.ev_rainbow)%6];self.ev_rainbow-=1
        elif self.ev_timer>0:
            led0=self.ev_color;self.ev_timer-=1
        else:
            led0=(0,0,0)

        # LED2: マリオ状態
        if self.dmg_flash>0:
            # 赤→白→赤→暗 減衰フラッシュ
            led1=_DMG_DECAY[8-self.dmg_flash];self.dmg_flash-=1
        elif self.star_mode:
            # 高速2倍サイクル
            led1=_RAINBOW[(frame>>1)%6]
        elif self.inv_timer>0:
            self.inv_timer-=1
            led1=(C.LED_MAX_BRIGHT,C.LED_MAX_BRIGHT,C.LED_MAX_BRIGHT)if(frame&2)else(0,0,0)
        else:
            s=self.p_state
            if s=='small':led1=(4,18,6)
            elif s=='big':led1=(30,30,0)
            elif s=='fire':led1=(40,18,0)if self.beat_boost>0 else(35,5,0)
            elif s=='dead':led1=(40,0,0)
            else:led1=(0,0,0)

        # LED3: マップ + 難易度色調
        amb=STAGE_COLOR.get(self.stage_num,(10,10,10))
        ph=(frame>>2)&31;tri=ph if ph<16 else 31-ph
        sc=70+tri*2
        led2=_scale(amb,min(sc,130))
        if self.diff=='HARD':
            led2=(_clamp(led2[0]+6),led2[1],led2[2])
        elif self.diff=='EASY':
            led2=(led2[0],led2[1],_clamp(led2[2]+6))

        # ビートブースト: 全3本 +8
        if self.beat_boost>0:
            self.beat_boost-=1
            b=8
            led0=tuple(_clamp(v+b)for v in led0)
            led1=tuple(_clamp(v+b)for v in led1)
            led2=tuple(_clamp(v+b)for v in led2)

        self._write([
            tuple(_clamp(v)for v in led0),
            tuple(_clamp(v)for v in led1),
            tuple(_clamp(v)for v in led2),
        ])

    def _write(self,leds):
        ch=False
        for i in range(3):
            if leds[i]!=self.last[i]:
                self.np[i]=leds[i];self.last[i]=leds[i];ch=True
        if ch:self.np.write()

    def off(self):
        for i in range(3):self.np[i]=(0,0,0);self.last[i]=(0,0,0)
        self.np.write()
