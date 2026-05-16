import time,gc
import config as C
import player as pl
import entity as et
import render as rd
import world_new as wn
import stages_new as sn
import entity_new as en
import ui_new as ui
from auto_input import AutoInput

S_TITLE='t';S_MODE='m';S_DIFF='d';S_INTRO='i';S_PAN='pan'
S_PLAY='p';S_DIE='die';S_PAUSE='pau';S_CLEAR='cl'
S_OVER='ov';S_END='end';S_PIPE_IN='pi';S_PIPE_P='pp';S_PIPE_OUT='po'
S_MUSIC='mus';S_OPTION='opt';S_FLAG='fl';S_CUSTOM_SEL='cs';S_BOSS_INTRO='bi'

class GameNew:
 def __init__(s,oled,bank,inp,audio,fx):
  s.oled=oled;s.bank=bank;s.inp=inp;s.audio=audio;s.fx=fx
  s.st=S_TITLE;s.st_t=0;s.frame=0
  s.score=0;s.lives=3;s.sn=1;s.hi=0
  s.world=None;s.player=None;s.ents=[];s.fbs=[]
  s.cam_x=0;s.cam_y=0;s.tl=100;s.tsf=0
  s.mode_cur=1;s.diff_cur=1;s.diff=C.DIFF_NORMAL
  s.coins=0;s.coins_max=0;s.deaths=0
  s.crowns=_load_cr()
  s.star_t=0;s.slot_f=0;s.slot_r=0;s._pending_item=None
  s.test_mode=False;s._test_t=0
  s.vol_step=10;s._quit_hold=0
  s.pipe_f=0;s.pipe_world=None;s._pipe_near_exit=False
  s.main_world=None;s.main_cam=0;s.main_ents=[]
  s._ending=None
  s._load_vol()
  s.music_cur=0
  import music
  s.music_list=list(music.BGM.keys())
  s.music_playing=False
  # カスタムモード状態
  s.custom_mode=False
  s.custom_stages=[]
  s.custom_idx=0
 def _cs(s,ns):s.st=ns;s.st_t=0
 def update(s):
  s.inp.update();s.frame+=1;st=s.st
  if st==S_TITLE:s._u_title()
  elif st==S_MODE:
   r=s._u_mode()
   if r:
    s.audio.update();s.fx.update(s.frame)
    return r
  elif st==S_DIFF:s._u_diff()
  elif st==S_INTRO:s._u_intro()
  elif st==S_PAN:s._u_pan()
  elif st==S_PLAY:s._u_play()
  elif st==S_DIE:s._u_die()
  elif st==S_PAUSE:s._u_pause()
  elif st==S_CLEAR:s._u_clear()
  elif st==S_OVER:s._u_over()
  elif st==S_END:s._u_end()
  elif st==S_PIPE_IN:s._u_pipein()
  elif st==S_PIPE_P:s._u_pipep()
  elif st==S_PIPE_OUT:s._u_pipeout()
  elif st==S_MUSIC:s._u_music()
  elif st==S_OPTION:s._u_option()
  elif st==S_FLAG:s._u_flag()
  elif st==S_CUSTOM_SEL:s._u_custom_sel()
  elif st==S_BOSS_INTRO:s._u_boss_intro()
  s.audio.update()
  if s.audio.beat_pulse:s.fx.beat()
  s.fx.update(s.frame)
 def draw(s):
  o=s.oled;o.fill(0);st=s.st
  if st==S_TITLE or st==S_MODE:ui.draw_mode_select(o,s.bank,s.mode_cur,s.frame)
  elif st==S_DIFF:ui.draw_difficulty_select(o,s.bank,s.diff_cur,s.frame)
  elif st==S_INTRO:ui.draw_stage_intro_new(o,s.bank,s.sn,s.lives,s.diff['name'])
  elif st==S_PAN:s._d_play()
  elif st==S_PLAY or st==S_DIE:s._d_play()
  elif st==S_PAUSE:s._d_play();o.fill_rect(30,20,68,26,0);o.rect(30,20,68,26,1);rd.draw_text(o,s.bank,'PAUSE',51,23);rd.draw_text(o,s.bank,'123:TITLE',37,33)
  elif st==S_CLEAR:s._d_clear()
  elif st==S_OVER:s._d_over()
  elif st==S_PIPE_IN or st==S_PIPE_OUT:ui.draw_pipe_transition(o,s.bank,s.st_t,st==S_PIPE_IN)
  elif st==S_PIPE_P:s._d_play()
  elif st==S_MUSIC:ui.draw_music_player(o,s.bank,s.music_list[s.music_cur],s.music_playing)
  elif st==S_OPTION:ui.draw_option_menu(o,s.bank,s.vol_step)
  elif st==S_END:s._d_end()
  elif st==S_FLAG:s._d_flag()
  elif st==S_CUSTOM_SEL:
   if s.custom_stages:
    ui.draw_custom_select(o,s.bank,s.custom_stages,s.custom_idx,s.frame)
   else:
    ui.draw_custom_empty(o,s.bank)
  elif st==S_BOSS_INTRO:s._d_boss_intro()
  o.show()
 def _gst(s,num=None):
  """現在のモード(NEW or CUSTOM)に応じてステージdictを返す。"""
  if num is None:num=s.sn
  if s.custom_mode:
   if 1<=num<=len(s.custom_stages):return s.custom_stages[num-1]
   return None
  return sn.get_stage_new(num)
 def _start(s,num):
  sd=s._gst(num)
  if sd is None:s._cs(S_END);return
  s.sn=num;s.world=wn.WorldNew(sd)
  sr=sd.get('start_row',s.world.rows-3)
  sc=sd.get('start_col',1)
  s.player=pl.Player(s.world,sc)
  s.player.state=pl.STATE_BIG
  s.player._sync_size()
  # Big Mario h=16: 足がstart_rowの上に乗るようにy設定
  s.player.y=float(sr*C.TILE - s.player.h)
  s.player.gravity_scale=sd.get('gravity_scale',1.0)
  s.player.is_water=sd.get('water',False)
  s.ents=[];base_objs=sd['objects']
  es=sd.get('enemy_sets',{})
  dk=s.diff['name'].lower()
  # enemy_sets がある難易度はベース敵リストを差し替え(追加ではない)
  # qblock系エントリはどちらも entity 生成時にスキップされるので無視してよい
  if dk in es:
   objs=list(es[dk])
  else:
   objs=list(base_objs)
  spd=s.diff.get('speed_mul',1.0)
  for obj in objs:
   c,r,ts=obj[0],obj[1],obj[2]
   if ts.startswith('qblock'):continue
   e=en.make_entity_new(ts,c,r)
   if e:
    if spd!=1.0 and hasattr(e,'vx'):e.vx*=spd
    s.ents.append(e)
  s.fbs=[];s.cam_x=0;s.cam_y=0;s._test_t=0
  s.tl=sd.get('time_limit',100);s.tsf=0
  s.coins_max+=s.world.count_coins()
  if not s.custom_mode and num==6 and s.player.state!=pl.STATE_FIRE:
   s.player.state=pl.STATE_FIRE;s.player._sync_size()
  s.fx.set_stage(num);s.fx.set_player_state(s.player.state)
  s.audio.play_bgm(sd['bgm']);gc.collect()
 def _u_title(s):
  s.st_t+=1
  if s.st_t==1:s.audio.play_bgm('overworld')
  if s.st_t>=60:s._cs(S_MODE)
 def _u_mode(s):
  s.st_t+=1
  if s.inp.pressed(1):s.mode_cur=(s.mode_cur-1)%6
  if s.inp.pressed(2):s.mode_cur=(s.mode_cur+1)%6
  if s.inp.pressed(0):
   s.audio.play_sfx('select')
   if s.mode_cur==0:
    s.audio.stop_bgm();return 'OLD'
   elif s.mode_cur==1:
    s.custom_mode=False;s._cs(S_DIFF)
   elif s.mode_cur==2:
    # カスタムモード: 利用可能なカスタムステージを読み込み、選択画面へ
    try:
     import custom_stages as cust
     s.custom_stages=cust.load_custom_stages(s.bank)
    except Exception as e:
     print('custom load error:',e);s.custom_stages=[]
    s.custom_idx=0;s._cs(S_CUSTOM_SEL)
   elif s.mode_cur==3:
    s.audio.stop_bgm();s.music_cur=0;s.music_playing=False;s._cs(S_MUSIC)
   elif s.mode_cur==4:
    s._cs(S_OPTION)
   elif s.mode_cur==5:
    # テストモード: AutoInputに差し替えて全ステージ自動走破
    s.test_mode=True;s.inp=AutoInput();s.custom_mode=False
    s.diff=C.DIFF_NORMAL
    s.lives=s.diff['lives'];s.score=0;s.sn=1;s.deaths=0;s.coins=0;s.coins_max=0
    s.fx.set_difficulty(s.diff['name'])
    s.audio.stop_bgm();s._cs(S_INTRO)
  return None

 def _u_custom_sel(s):
  s.st_t+=1
  if not s.custom_stages:
   # 戻るのみ
   if s.inp.pressed(0) or s.inp.pressed(1) or s.inp.pressed(2):
    s.audio.play_sfx('select');s._cs(S_MODE)
   return
  if s.inp.pressed(1):s.custom_idx=(s.custom_idx-1)%len(s.custom_stages);s.audio.play_sfx('select')
  if s.inp.pressed(2):s.custom_idx=(s.custom_idx+1)%len(s.custom_stages);s.audio.play_sfx('select')
  # SW1 + SW2 同時: 戻る
  if s.inp.held(1) and s.inp.pressed(2):
   s.audio.play_sfx('select');s._cs(S_MODE);return
  if s.inp.pressed(0):
   s.audio.play_sfx('select')
   s.custom_mode=True
   s.diff=C.DIFF_NORMAL;s.fx.set_difficulty(s.diff['name'])
   s.lives=s.diff['lives'];s.score=0;s.deaths=0;s.coins=0;s.coins_max=0
   s.sn=s.custom_idx+1
   s.audio.stop_bgm();s._cs(S_INTRO)

 def _load_vol(s):
  try:
   with open(C.SETTINGS_FILE,'r')as f:
    v=int(f.read().strip())
    s.vol_step=max(0,min(20,v))
  except Exception:
   s.vol_step=10
  s.audio.master_volume=(s.vol_step/20.0)**1.5

 def _save_vol(s):
  try:
   with open(C.SETTINGS_FILE,'w')as f:
    f.write(str(s.vol_step))
  except Exception:
   pass

 def _u_music(s):
  s.st_t+=1
  if s.inp.pressed(1):
   s.music_cur=(s.music_cur-1)%len(s.music_list)
   s.audio.stop_bgm(); s.music_playing=False
  if s.inp.pressed(2):
   s.music_cur=(s.music_cur+1)%len(s.music_list)
   s.audio.stop_bgm(); s.music_playing=False
  if s.inp.pressed(0):
   if s.music_playing:
    s.audio.stop_bgm();s.music_playing=False
   else:
    s.audio.play_bgm(s.music_list[s.music_cur]);s.music_playing=True
  if s.inp.held(1) and s.inp.pressed(2): # SW2+SW3 to exit
   s.audio.stop_bgm();s.audio.play_sfx('select');s._cs(S_MODE)

 def _u_option(s):
  s.st_t+=1
  if s.inp.pressed(1) and s.vol_step>0:
   s.vol_step-=1;s.audio.master_volume=(s.vol_step/20.0)**1.5;s.audio.play_sfx('coin')
  if s.inp.pressed(2) and s.vol_step<20:
   s.vol_step+=1;s.audio.master_volume=(s.vol_step/20.0)**1.5;s.audio.play_sfx('coin')
  if s.inp.pressed(0):
   s.audio.play_sfx('select');s._save_vol();s._cs(S_MODE)
 def _u_diff(s):
  s.st_t+=1
  if s.inp.pressed(1):s.diff_cur=(s.diff_cur-1)%3
  if s.inp.pressed(2):s.diff_cur=(s.diff_cur+1)%3
  if s.inp.pressed(0):
   s.audio.play_sfx('select');s.diff=C.DIFFICULTIES[s.diff_cur]
   s.lives=s.diff['lives'];s.score=0;s.sn=1;s.deaths=0;s.coins=0;s.coins_max=0
   s.fx.set_difficulty(s.diff['name'])
   s.audio.stop_bgm();s._cs(S_INTRO)
 def _u_intro(s):
  if s.st_t==0:s._start(s.sn);s.audio.pause_bgm()
  s.st_t+=1
  if s.st_t>=60:s.audio.resume_bgm();s._cs(S_PAN)
 def _u_pan(s):
  s.st_t+=1
  sd=s._gst()
  gcol=sd.get('goal_col',s.world.width-10)
  mx=max(0,gcol*C.TILE-C.SCREEN_W)
  if s.st_t<30:s.cam_x=int(mx*s.st_t/30)
  elif s.st_t<60:s.cam_x=int(mx*(60-s.st_t)/30)
  else:
   s.cam_x=0
   # ボスステージはイントロ演出へ
   if not s.custom_mode and s.sn==6:s._cs(S_BOSS_INTRO);s.audio.pause_bgm()
   else:s._cs(S_PLAY)
 def _u_boss_intro(s):
  s.st_t+=1
  # 0-20: カメラ右へパン(ボスを写す)
  if s.st_t<=20:
   s.cam_x=int(s.st_t*4)
  # 20: 咆哮再生
  if s.st_t==20:s.audio.play_sfx('boss_roar')
  # 30-70: "BOSS BATTLE!" 点滅 + ジリジリ揺れ
  if s.st_t==30:s.fx.set_damage()
  # 80: BGM再開
  if s.st_t==80:s.audio.resume_bgm();s.audio.play_bgm('boss')
  # 100: カメラを戻して開始
  if s.st_t>=100:s.cam_x=0;s._cs(S_PLAY)
 def _d_boss_intro(s):
  o=s.oled
  s.world.draw(o,s.bank,s.cam_x,s.cam_y,s.frame)
  for e in s.ents:
   if e.alive and hasattr(e,'draw'):e.draw(o,s.bank,s.cam_x,s.cam_y)
  s.player.draw(o,s.bank,s.cam_x,s.cam_y)
  # 暗幕 (画面上下から黒)
  o.fill_rect(0,0,128,8,0);o.fill_rect(0,56,128,8,0)
  # "BOSS BATTLE" 点滅
  if 30<=s.st_t<=80 and (s.st_t>>2)&1:
   o.fill_rect(20,22,88,18,0);o.rect(20,22,88,18,1)
   t1='BOSS BATTLE';t2='GET READY!'
   rd.draw_text(o,s.bank,t1,(128-len(t1)*5)//2,26)
   rd.draw_text(o,s.bank,t2,(128-len(t2)*5)//2,34)
 def _u_play(s):
  if s.inp.held(0)and s.inp.held(1)and s.inp.held(2):
   s._quit_hold+=1
   if s._quit_hold>=C.TARGET_FPS*3:
    s._quit_hold=0;s.audio.stop_bgm();s._cs(S_TITLE);return
  else:
   s._quit_hold=0
  # SW2 hold = しゃがみ/水中ダイブ。SW3 hold = ダッシュ(player.py側で処理)
  crouch=s.inp.held(1)
  if crouch and s.player.is_water:s.player.vy+=0.3
  if s.test_mode:
   s.inp.update_auto(s.player,s.world,s.ents)
   s._test_t+=1
   if s.sn==6 and s._test_t>=60:s._on_clear();return
  s.player.update(s.inp,s._fire)
  if getattr(s.player,'_just_jumped',False):
   s.audio.play_sfx('jump_big'if s.player.state!=pl.STATE_SMALL else'jump_small')
  if getattr(s.player,'_just_bounced',False):
   s.audio.play_sfx('bounce');s.fx.rainbow(15)
  if getattr(s.player,'_fire_request',False):s.audio.play_sfx('fireball')
  if s.player.head_hit_col>=0:s._hit_block(s.player.head_hit_col)
  s._coin_pick()
  # 落下死/致死タイル判定は player.update() 側で行う(full DYING_FR で一貫)
  # pipe check
  sd=s._gst()
  pc=sd.get('pipe_col',-1)
  if pc>0 and crouch and s.player.on_ground and not s.test_mode:
   px=int(s.player.x)//C.TILE
   if abs(px-pc)<=1:s._enter_pipe(sd);return
  for e in s.ents:
   if e.alive:e.update(s.world,s.player)
  for f in s.fbs:
   if f.alive:f.update(s.world,s.player)
  s._tick_slot()
  if s.player.state!=pl.STATE_DEAD:s._collide()
  s._fb_collide()
  s.ents=[e for e in s.ents if e.alive];s.fbs=[f for f in s.fbs if f.alive]
  # star
  if s.star_t>0:
   s.star_t-=1;s.fx.set_star(True)
   if s.star_t==0:s.fx.set_star(False);s.audio.play_bgm(sd['bgm'])
  # camera
  tx=int(s.player.x)-40
  ty=int(s.player.y)-C.SCREEN_H//2
  mx=max(0,s.world.width*C.TILE-C.SCREEN_W)
  my=max(0,s.world.map_h_px-C.SCREEN_H)
  s.cam_x=max(0,min(tx,mx));s.cam_y=max(0,min(ty,my))
  # time
  s.tsf+=1
  if s.tsf>=C.TARGET_FPS:
   s.tsf=0;s.tl-=1
   if s.tl<=0:s.tl=0;s.player.kill_by_fall()
  if s.player.state==pl.STATE_DEAD:
   s._cs(S_DIE);s.audio.stop_bgm();s.audio.play_sfx('damage');return
  gcol2=sd.get('goal_col',-1)
  if gcol2>0 and s.player.x>=gcol2*C.TILE-4:s._on_clear()
  if not s.custom_mode and s.sn==6:
   boss_dead=True;has_boss=False
   for e in s.ents:
    if isinstance(e,et.Boss):has_boss=True;boss_dead=e.hp<=0 if boss_dead else False
   if (has_boss and boss_dead) or not has_boss:s._on_clear()
  s.fx.set_player_state(s.player.state)
  if s.player.invincible>0:s.fx.set_invincible(2)
 def _fire(s,x,y,d):
  if len(s.fbs)<2:s.fbs.append(et.Fireball(x,y,d))
 def _hit_block(s,col):
  hr=int(s.player.y)//C.TILE-1
  if hr<0 or hr>=s.world.rows:return
  tid=s.world.tile_at(col,hr)
  if tid==wn.QBLOCK:
   s.world.set_tile(col,hr,wn.QUSED);s.audio.play_sfx('bump');s.score+=C.SCORE_BLOCK
   s._start_slot(col,hr)
  elif tid==wn.BRICK:
   if s.player.state!=pl.STATE_SMALL:
    s.world.set_tile(col,hr,wn.AIR);s.audio.play_sfx('brick_break');s.score+=C.SCORE_BLOCK
   else:s.audio.play_sfx('bump')
 def _start_slot(s,col,row):
  # マリオカート式アイテムボックス: 短時間スピン → 確定 → 即取得
  import urandom
  r=urandom.getrandbits(7)%100;p=C.QBLOCK_PROBS
  if r<p[0]:it=0
  elif r<p[1]:it=1
  elif r<p[2]:it=2
  elif r<p[3]:it=3
  else:it=4
  s._pending_item=(it,col*C.TILE,(row-1)*C.TILE)
  s.slot_f=30;s.slot_r=urandom.getrandbits(3)%5
  s.fx.set_slot_spin(True);s.fx.rainbow(30)
  s.audio.play_sfx('item_get')
 def _tick_slot(s):
  if s.slot_f<=0:return
  # frames 30→16: 高速スピン (4F毎にランダム切替)
  # frame 15: 結果確定、ファンファーレ
  # frames 14→1: 確定アイコン表示 (キラキラ)
  # frame 1: アイテム発動
  if s.slot_f==15:
   if s._pending_item:s.slot_r=s._pending_item[0]
   s.fx.set_slot_spin(False)
  elif s.slot_f>15 and s.slot_f%4==0:
   import urandom
   s.slot_r=urandom.getrandbits(3)%5
  if s.slot_f==1:s._apply_pending_item()
  s.slot_f-=1
 def _apply_pending_item(s):
  if s._pending_item is None:return
  it,sx,sy=s._pending_item;s._pending_item=None
  if it==0:
   if s.player.state==pl.STATE_SMALL:s.ents.append(et.Mushroom(sx,sy))
   else:s.score+=C.SCORE_COIN;s.coins+=1
   s.audio.play_sfx('powerup');s.fx.rainbow(20)
  elif it==1:
   s.ents.append(et.FireFlower(sx,sy));s.audio.play_sfx('powerup');s.fx.rainbow(20)
  elif it==2:
   s.ents.append(et.OneUp(sx,sy));s.audio.play_sfx('1up')
  elif it==3:
   s.score+=C.SCORE_COIN;s.coins+=1;s.audio.play_sfx('coin');s.fx.event_flash((40,35,0),6)
  else:
   s.ents.append(en.StarItem(sx,sy));s.audio.play_sfx('powerup');s.fx.rainbow(30)
 def _coin_pick(s):
  px,py,pw,ph=s.player.aabb()
  l=int(px)//C.TILE;r=int(px+pw-1)//C.TILE
  t=int(py)//C.TILE;b=int(py+ph-1)//C.TILE
  for c in range(l,r+1):
   for rr in range(t,b+1):
    if s.world.tile_at(c,rr)==wn.COIN:
     s.world.set_tile(c,rr,wn.AIR);s.score+=C.SCORE_COIN;s.coins+=1
     s.audio.play_sfx('coin');s.fx.event_flash((40,35,0),6)
 def _collide(s):
  px,py,pw,ph=s.player.aabb()
  for e in s.ents:
   if not e.alive:continue
   if isinstance(e,en.KillerSpawner):
    for k in e.get_killers():
     if not k.alive:continue
     kx,ky,kw,kh=k.aabb()
     if px<kx+kw and px+pw>kx and py<ky+kh and py+ph>ky:
      if s.player.vy>0 and py+ph-s.player.vy<=ky+5:
       k.on_stomp();s.player.vy=-2.6;s.audio.play_sfx('stomp');s.score+=C.SCORE_STOMP
      elif s.star_t>0:k.alive=False;s.score+=C.SCORE_STOMP
      else:s._dmg()
    continue
   if isinstance(e,en.BigMushroom):
    ex,ey,ew,eh=e.aabb()
    if px<ex+ew and px+pw>ex and py<ey+eh and py+ph>ey:
     if s.player.vy>0:s.player.vy=-5.5;e.on_bounce();s.audio.play_sfx('jump_big')
    continue
   if isinstance(e,en.StarItem):
    ex,ey,ew,eh=e.aabb()
    if px<ex+ew and px+pw>ex and py<ey+eh and py+ph>ey:
     s.star_t=C.STAR_DURATION;e.alive=False;s.audio.play_sfx('powerup')
     s.fx.set_star(True);s.fx.rainbow(60)
    continue
   # items (pickup on contact, no damage)
   if isinstance(e,(et.Mushroom,et.FireFlower,et.OneUp)):
    ex,ey,ew,eh=e.aabb()
    if px<ex+ew and px+pw>ex and py<ey+eh and py+ph>ey:
     if isinstance(e,et.Mushroom):
      s.player.powerup_mushroom();s.audio.play_sfx('powerup');s.fx.rainbow(30);s.score+=1000
     elif isinstance(e,et.FireFlower):
      s.player.powerup_fire();s.audio.play_sfx('powerup');s.fx.rainbow(30);s.score+=1000
     elif isinstance(e,et.OneUp):
      s.lives=min(C.MAX_LIVES,s.lives+1);s.audio.play_sfx('1up')
     e.alive=False
    continue
   if not e.solid_for_player:continue
   ex,ey,ew,eh=e.aabb()
   if not(px<ex+ew and px+pw>ex and py<ey+eh and py+ph>ey):continue
   stomp=s.player.vy>0 and py+ph-s.player.vy<=ey+5
   if s.star_t>0:e.alive=False;s.score+=C.SCORE_STOMP;s.audio.play_sfx('stomp');continue
   if stomp:
    if e.on_stomp():s.player.vy=-2.6;s.audio.play_sfx('stomp');s.score+=C.SCORE_STOMP
    else:s.player.vy=-2.0;s._dmg()
   else:
    if e.on_collide(s.player)=='damage':s._dmg()
  # ボス火球は本体AABBと無関係に当たり判定
  for e in s.ents:
   if isinstance(e,et.Boss) and e.alive:
    if e.fire_hits(px,py,pw,ph):s._dmg();break
 def _dmg(s):
  if s.player.invincible>0:return
  died=s.player.take_damage()
  if not died:
   s.audio.play_sfx('damage');s.fx.set_damage();s.fx.set_invincible(C.NEW_INVINCIBLE_FR)
 def _fb_collide(s):
  for f in s.fbs:
   if not f.alive:continue
   fx2,fy2,fw2,fh2=f.aabb()
   for e in s.ents:
    if not e.alive:continue
    ex,ey,ew,eh=e.aabb()
    if fx2<ex+ew and fx2+fw2>ex and fy2<ey+eh and fy2+fh2>ey:
     if e.on_fireball():f.alive=False;s.score+=C.SCORE_FIREKILL;s.audio.play_sfx('stomp')
     elif isinstance(e,et.Boss):f.alive=False;s.score+=200;s.audio.play_sfx('boss_hit')
     break
 def _on_clear(s):
  sd=s._gst()
  fc=sd.get('flag_col',-1) if sd else -1
  if fc>0 and s.st!=S_FLAG:
   s._cs(S_FLAG);s.fx.set_goal_flash(90)
  else:
   s.audio.stop_bgm();s.audio.play_sfx('stage_clear');s.fx.rainbow(60)
   s.score+=s.tl*C.TIME_BONUS
   if s.tl>=C.GOAL_BONUS_TIME_THRESH:s.lives=min(C.MAX_LIVES,s.lives+1)
   s._cs(S_CLEAR)
 def _enter_pipe(s,sd):
  s.audio.play_sfx('pipe');s.main_world=s.world;s.main_cam=s.cam_x
  s.main_ents=s.ents;s._cs(S_PIPE_IN);s.pipe_f=0
 def _u_pipein(s):
  s.st_t+=1
  if s.st_t>=45:
   ps=sn.PIPE_SUBSTAGE;s.world=wn.WorldNew(ps);s.player.world=s.world
   s.player.x=float(ps['start_col']*C.TILE);s.player.y=float(ps['start_row']*C.TILE)
   s.player.vy=0;s.ents=[];s.cam_x=0;s.cam_y=0;s._cs(S_PIPE_P)
 def _u_pipep(s):
  s.player.update(s.inp,s._fire)
  s._coin_pick()
  tx=int(s.player.x)-40;mx=max(0,s.world.width*C.TILE-C.SCREEN_W)
  s.cam_x=max(0,min(tx,mx))
  ps=sn.PIPE_SUBSTAGE;ec=ps.get('exit_col',30)
  near_exit=int(s.player.x)//C.TILE>=ec
  s._pipe_near_exit=near_exit
  if near_exit and s.inp.pressed(0):
   s.audio.play_sfx('pipe');s._cs(S_PIPE_OUT)
  if s.inp.held(0)and s.inp.held(1)and s.inp.held(2):
   s._quit_hold+=1
   if s._quit_hold>=C.TARGET_FPS*3:
    s._quit_hold=0;s.audio.stop_bgm();s.world=s.main_world if s.main_world else s.world;s._cs(S_TITLE);return
  else:
   s._quit_hold=0
  if s.player.y>s.world.map_h_px+8:s.player.kill_by_fall()
  if s.player.state==pl.STATE_DEAD:s._cs(S_DIE);s.audio.play_sfx('damage')
 def _u_pipeout(s):
  s.st_t+=1
  if s.st_t>=45:
   sd=s._gst();rc=sd.get('pipe_return_col',64)
   s.world=s.main_world;s.player.world=s.world;s.ents=s.main_ents
   s.player.x=float(rc*C.TILE);s.player.vy=0;s.cam_x=s.main_cam;s._cs(S_PLAY)
 def _u_die(s):
  s.st_t+=1;s.player.update(s.inp,lambda*a:None)
  if s.st_t>=C.DYING_FR:
   if s.test_mode:s._cs(S_INTRO);return
   s.lives-=1;s.deaths+=1
   if s.lives<=0:s._cs(S_OVER);s.audio.play_sfx('game_over')
   else:s._cs(S_INTRO)
 def _u_pause(s):
  s.st_t+=1
  if s.inp.pressed(0):s.audio.play_sfx('pause');s.audio.resume_bgm();s._cs(S_PLAY)
  if s.inp.held(0)and s.inp.held(1)and s.inp.held(2):
   s._quit_hold+=1
   if s._quit_hold>=C.TARGET_FPS*3:s._quit_hold=0;s.audio.stop_bgm();s._cs(S_TITLE)
  else:s._quit_hold=0
 def _u_clear(s):
  s.st_t+=1
  if s.st_t>=150:
   if s.score>s.hi:s.hi=s.score
   total=len(s.custom_stages) if s.custom_mode else len(sn.STAGES_NEW)
   if s.sn>=total:s._cs(S_END)
   else:s.sn+=1;s._cs(S_INTRO)
 def _u_over(s):
  s.st_t+=1
  if s.score>s.hi:s.hi=s.score
  if(s.st_t>60 and s.inp.any_pressed())or s.st_t>300:s._cs(S_TITLE)
 def _u_end(s):
  s.st_t+=1
  if s.st_t==1:
   s.crowns+=1;_save_cr(s.crowns);s.audio.play_bgm('ending')
   from ending import EndingScene
   stats={'score':s.score,'coins':s.coins,'coins_max':s.coins_max,'deaths':s.deaths}
   s._ending=EndingScene(s.oled,s.bank,s.inp,s.audio,s.fx,stats)
  if s._ending:
   if s._ending.update():s._ending=None;s._cs(S_TITLE)
 def _d_play(s):
  o=s.oled;s.world.draw(o,s.bank,s.cam_x,s.cam_y,s.frame)
  for e in s.ents:
   if e.alive and hasattr(e,'draw'):e.draw(o,s.bank,s.cam_x,s.cam_y)
  for f in s.fbs:
   if f.alive:f.draw(o,s.bank,s.cam_x,s.cam_y)
  s.player.draw(o,s.bank,s.cam_x,s.cam_y)
  ui.draw_header_new(o,s.bank,s.score,s.lives,s.tl,str(s.sn),s.coins)
  if s.st==S_PIPE_P and s._pipe_near_exit and (s.frame>>3)&1:
   rd.draw_text(o,s.bank,'SW1:EXIT',36,54)
  if s.slot_f>0:
   settled=s.slot_f<=30
   ui.draw_item_slot(o,s.bank,s.slot_f,s.slot_r,settled)
 def _u_flag(s):
  s.st_t+=1
  sd=s._gst()
  fc=sd.get('flag_col',s.world.width-10)
  if s.st_t==1:s.audio.play_sfx('flag_slide')
  if s.st_t==30:s.audio.play_bgm('fanfare')
  if s.st_t<=20:
   target=float(fc*C.TILE)
   if s.player.x<target:s.player.x=min(s.player.x+1.5,target)
  elif s.st_t<=70:
   s.player.vx=0;s.player.vy=0
  else:
   s.player.x+=1.5
  if s.st_t>=90:
   s.audio.stop_bgm();s.score+=s.tl*C.TIME_BONUS
   if s.tl>=C.GOAL_BONUS_TIME_THRESH:s.lives=min(C.MAX_LIVES,s.lives+1)
   s.audio.play_sfx('stage_clear');s._cs(S_CLEAR)
 def _d_flag(s):
  o=s.oled;sd=s._gst()
  fc=sd.get('flag_col',s.world.width-10)
  s.world.draw(o,s.bank,s.cam_x,s.cam_y,s.frame)
  for e in s.ents:
   if e.alive and hasattr(e,'draw'):e.draw(o,s.bank,s.cam_x,s.cam_y)
  ui.draw_flag_anim(o,s.bank,s.world,s.cam_x,s.cam_y,fc,s.st_t)
  if 50<=s.st_t<=70:
   sx=int(s.player.x)-s.cam_x-1;sy=int(s.player.y)-s.cam_y
   o.blit(s.bank.fb['mario_flag'],sx,sy)
  else:
   s.player.draw(o,s.bank,s.cam_x,s.cam_y)
  ui.draw_header_new(o,s.bank,s.score,s.lives,s.tl,str(s.sn),s.coins)
 def _d_clear(s):
  o=s.oled;o.fill(0);o.rect(4,6,120,52,1)
  rd.draw_text(o,s.bank,'STAGE CLEAR!',28,12)
  o.hline(4,22,120,1);rd.draw_text(o,s.bank,'SCORE',8,26)
  rd.draw_number(o,s.bank,s.score,58,26,width=6)
  rd.draw_text(o,s.bank,'BONUS',8,38)
  rd.draw_number(o,s.bank,s.tl*C.TIME_BONUS,58,38,width=6)
 def _d_over(s):
  o=s.oled;o.fill(0);o.rect(4,10,120,36,1)
  rd.draw_text(o,s.bank,'GAME OVER',41,18)
  rd.draw_text(o,s.bank,'SCORE',24,30);rd.draw_number(o,s.bank,s.score,54,30,width=5)
  if(s.st_t>>3)&1:rd.draw_text(o,s.bank,'PRESS SW1',41,52)
 def _d_end(s):
  if s._ending:
   s._ending.draw();return
  o=s.oled;o.fill(0)
  for sx,sy in[(10,6),(118,10),(64,2)]:
   if(s.st_t+sx)&8:o.pixel(sx,sy,1);o.pixel(sx+1,sy,1)
  o.rect(6,14,116,36,1);rd.draw_text(o,s.bank,'YOU WIN!',44,20)
  rd.draw_text(o,s.bank,'SCORE',14,32);rd.draw_number(o,s.bank,s.score,44,32,width=5)
  for i in range(min(s.crowns,4)):
   o.blit(s.bank.fb['crown'],96+i*8,6)
  if(s.st_t>>3)&1:rd.draw_text(o,s.bank,'PRESS SW1',41,54)

def _load_cr():
 try:
  with open(C.CROWN_FILE,'r')as f:return int(f.read().strip())
 except:return 0
def _save_cr(n):
 try:
  with open(C.CROWN_FILE,'w')as f:f.write(str(n))
 except:pass
