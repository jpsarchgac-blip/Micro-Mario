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

class FxNew:
    def __init__(self):
        self.np=NeoPixel(Pin(C.PIN_NEOPIXEL,Pin.OUT),3)
        self.last=[(0,0,0)]*3
        # LED1 event
        self.ev_color=(0,0,0);self.ev_timer=0;self.ev_rainbow=0
        # LED2 player
        self.p_state='big';self.star_mode=False;self.beat_boost=0
        self.inv_timer=0;self.dmg_flash=0
        # LED3 map
        self.stage_num=1

    def set_player_state(self,s):self.p_state=s
    def set_star(self,on):self.star_mode=on
    def set_stage(self,n):self.stage_num=n
    def set_invincible(self,f):self.inv_timer=f
    def set_damage(self):self.dmg_flash=6
    def beat(self):self.beat_boost=4
    def event_flash(self,c,f=8):self.ev_color=c;self.ev_timer=f
    def rainbow(self,f=30):self.ev_rainbow=f

    def update(self,frame):
        # LED1: イベント
        if self.ev_rainbow>0:
            cy=(30-self.ev_rainbow)%6
            rt=[(40,0,0),(40,20,0),(35,35,0),(0,40,0),(0,20,40),(25,0,40)]
            led0=rt[cy];self.ev_rainbow-=1
        elif self.ev_timer>0:
            led0=self.ev_color;self.ev_timer-=1
        else:
            led0=(0,0,0)

        # LED2: マリオ+BGM
        if self.dmg_flash>0:
            led1=(C.LED_MAX_BRIGHT,)*3;self.dmg_flash-=1
        elif self.star_mode:
            rt=[(40,0,0),(40,20,0),(35,35,0),(0,40,0),(0,20,40),(25,0,40)]
            led1=rt[frame%6]
        elif self.inv_timer>0:
            self.inv_timer-=1
            cs=[(40,40,40),(40,40,0),(40,0,0),(0,40,40)]
            led1=cs[frame&3]
        else:
            s=self.p_state
            if s=='small':led1=(4,18,6)
            elif s=='big':led1=(30,30,0)
            elif s=='fire':base=(35,5,0);led1=(40,18,0)if self.beat_boost>0 else base
            elif s=='dead':led1=(40,0,0)
            else:led1=(0,0,0)
        if self.beat_boost>0:
            led1=(_clamp(led1[0]+10),_clamp(led1[1]+10),_clamp(led1[2]+10))
            self.beat_boost-=1

        # LED3: マップ
        amb=STAGE_COLOR.get(self.stage_num,(10,10,10))
        ph=(frame>>2)&31;tri=ph if ph<16 else 31-ph
        sc=70+tri*2
        led2=_scale(amb,min(sc,130))

        leds=[
            tuple(_clamp(v)for v in led0),
            tuple(_clamp(v)for v in led1),
            tuple(_clamp(v)for v in led2),
        ]
        ch=False
        for i in range(3):
            if leds[i]!=self.last[i]:
                self.np[i]=leds[i];self.last[i]=leds[i];ch=True
        if ch:self.np.write()

    def off(self):
        for i in range(3):self.np[i]=(0,0,0);self.last[i]=(0,0,0)
        self.np.write()
