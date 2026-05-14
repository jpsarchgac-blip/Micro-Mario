# ending.py - 大長編RPGエンディングと高精細ピクセルアート表示
import config as C
import render as rd
import framebuf

_SCRIPT={
 'intro':[
  ('bg','A1'),
  ('bowser','Gaha...! I cant believe\nI lost to you...'),
  ('mario','Hah, hah...\nGive up, Bowser!'),
  ('bg','A2'),
  ('peach','Mario! You are safe!'),
  ('bowser','Peach... Grr,\nMy loss again...'),
  ('mario','Your ambition ends here.\nYour castle is ruined.'),
  ('bowser','Hmph! I can rebuild!\nMy ambition will\nNEVER die!!'),
  ('peach','Bowser...\nYou are so stubborn...\nMario, what will you do?'),
 ],
 'peace':[
  ('bg','A1'),
  ('mario','Bowser. If you promise\nto be good, I forgive you.'),
  ('bowser','W-what!?\nYou pity me!?'),
  ('mario','No. We have fought\ntoo many times.\nLets stop hating each other.'),
  ('bg','A2'),
  ('bowser','...Hmph. You are\ntoo soft, Mario.'),
  ('peach','Hehe. Bowser, you are\nsurprisingly honest.'),
  ('mario','Lets rebuild the\nMushroom Kingdom together!'),
  ('bowser','Dont get me wrong!\nWe fix MY castle first!'),
  ('bg','A3'),
  ('narrator','Thus, the long battle\ncame to an end.'),
  ('narrator','Mario and Bowser joined\nhands to rebuild.'),
  ('narrator','Eternal peace came to\nthe Mushroom Kingdom.\n-- PEACE END --'),
 ],
 'fight':[
  ('bg','B1'),
  ('mario','If you wont give up,\nIll fight you forever!'),
  ('bowser','Gahaha!\nNow thats what I like!'),
  ('peach','Wait! You both are\nalready battered!'),
  ('bg','B2'),
  ('peach','No more fighting!\nSettle this with\nhealthy sports!'),
  ('mario','Sports? Like\nKart racing or Tennis?'),
  ('bowser','Hmph! Ill crush you\nin ANY game!'),
  ('bg','B3'),
  ('narrator','Their battle moved\nto the race tracks.'),
  ('narrator','As true rivals, their\nmatches never end!'),
  ('narrator','The eternal battle of\nsports heroes!\n-- RIVAL END --'),
 ],
 'friend':[
  ('bg','C1'),
  ('peach','Stop fighting!\nDont you two actually\nlike each other?'),
  ('mario','What!? No way...!'),
  ('bowser','N-nonsense!\nI only think of\ndefeating him!'),
  ('bg','C2'),
  ('peach','Hehe. You two are\nso similar.\nLets have some cake!'),
  ('mario','Princess Peachs cake!\nMamma mia, yes!'),
  ('bowser','Mmm... Cake...!?\nIt better have\nstrawberries!'),
  ('bg','C3'),
  ('narrator','The battlefield turned\ninto a tea party.'),
  ('narrator','They forgot their enmity\nand became best friends.'),
  ('narrator','Sweet cake brought\npeace to the world!\n-- FRIEND END --'),
 ],
 'coin_bonus':[
  ('bg','R1'),
  ('peach','Mario, you collected\nan amazing amount of\ncoins!'),
  ('mario','Oh! Yes, my backpack\nis super heavy.'),
  ('bowser','W-what is this amount!?\nMore than my treasury!'),
  ('bg','R2'),
  ('mario','I am super rich!\nWhat should I buy?'),
  ('peach','Lets throw a massive\nfestival in the kingdom!'),
  ('bowser','Gaoo... Let me join\nthe festival too...'),
  ('bg','R3'),
  ('narrator','With massive wealth,\nthe kingdom boomed.'),
  ('narrator','A golden statue of Mario\nshines in the city!'),
  ('narrator','Ultimate celebrity who\nsolved all with money!\n-- RICH END --'),
 ],
 'nodeath':[
  ('bg','L1'),
  ('peach','Mario...! You dont have\na single scratch!'),
  ('bowser','I-impossible...!\nYou dodged EVERYTHING!?'),
  ('mario','Hehe. Anything to save\nyou, Princess!'),
  ('bg','L2'),
  ('peach','You are truly the\ngreatest hero ever.'),
  ('bowser','Tch... I admit it.\nYou are a monster...'),
  ('bg','L3'),
  ('narrator','A flawless victory.\nHis name became legend.'),
  ('narrator','It will be told for\neternity...'),
  ('narrator','The strongest player\nloved by the gods!\n-- LEGEND END --'),
 ]
}

CHOICES=['FORGIVE','FIGHT AGAIN','BE FRIENDS']

class EndingScene:
 def __init__(s,oled,bank,inp,audio,fx,stats):
  s.oled=oled;s.bank=bank;s.inp=inp;s.audio=audio;s.fx=fx
  s.stats=stats
  s.page=0;s.choice=0;s.branch=None
  s.coin_bonus=stats['coins']>=stats['coins_max']*0.8 if stats['coins_max']>0 else False
  s.no_death=stats['deaths']==0
  s.done=False;s.script=[];s.si=0;s.phase='intro'
  s.bg_buf=bytearray(1024)
  s.bg_fb=framebuf.FrameBuffer(s.bg_buf,128,64,framebuf.MONO_VLSB)
  s._load_bg('A1')
  
 def _load_bg(s,name):
  try:
   with open('art/'+name+'.bin','rb')as f:
    f.readinto(s.bg_buf)
  except:
   # Fallback if art doesn't exist
   s.bg_fb.fill(0)
   s.bg_fb.text("NO ART", 40, 28, 1)

 def _step_script(s):
  scr=_SCRIPT.get(s.phase,[])
  while s.si<len(scr):
   who,txt=scr[s.si]
   if who=='bg':
    s._load_bg(txt)
    s.si+=1
   else:
    break

 def update(s):
  if s.done:return True
  s._step_script()
  scr=_SCRIPT.get(s.phase if s.phase!='coin' else 'coin_bonus',[])
  
  if s.phase in ('intro','peace','fight','friend','coin','nodeath'):
   key=s.phase if s.phase!='coin' else 'coin_bonus'
   scr=_SCRIPT.get(key,[])
   if s.si>=len(scr):
    # Phase transition
    if s.phase=='intro': s.phase='choice'; s.choice=0
    elif s.phase in ('peace','fight','friend'):
     if s.coin_bonus: s.phase='coin'; s.si=0
     elif s.no_death: s.phase='nodeath'; s.si=0
     else: s.phase='stats'
    elif s.phase=='coin':
     if s.no_death: s.phase='nodeath'; s.si=0
     else: s.phase='stats'
    elif s.phase=='nodeath':
     s.phase='stats'
    return False

   if s.inp.pressed(0):
    s.si+=1
    s.audio.play_sfx('stomp')

  elif s.phase=='choice':
   if s.inp.pressed(1):s.choice=(s.choice-1)%3
   if s.inp.pressed(2):s.choice=(s.choice+1)%3
   if s.inp.pressed(0):
    s.branch=['peace','fight','friend'][s.choice]
    s.phase=s.branch;s.si=0;s.audio.play_sfx('select')
    
  elif s.phase=='stats':
   if s.inp.pressed(0):s.done=True
   
  return False

 def draw(s):
  o=s.oled;o.fill(0)
  if s.phase in ('intro','peace','fight','friend','coin','nodeath'):
   key=s.phase if s.phase!='coin' else 'coin_bonus'
   scr=_SCRIPT.get(key,[])
   if s.si<len(scr):
    who,txt=scr[s.si]
    # 背景描画
    o.blit(s.bg_fb,0,0)
    
    # テキストウィンドウ描画
    o.fill_rect(0,38,128,26,0)
    o.hline(0,37,128,1)
    
    # 発言者
    if who=='mario': rd.draw_text(o,s.bank,'MARIO:',2,40)
    elif who=='bowser': rd.draw_text(o,s.bank,'BOWSER:',2,40)
    elif who=='peach': rd.draw_text(o,s.bank,'PEACH:',2,40)
    elif who=='narrator': pass # No name prefix
    
    # 複数行テキスト
    lines = txt.split('\n')
    for i, line in enumerate(lines):
     y = 40 + i*8 if who=='narrator' else 48 + i*8
     rd.draw_text(o,s.bank,line,4 if who=='narrator' else 10, y)

  elif s.phase=='choice':
   o.rect(4,2,120,60,1)
   rd.draw_text(o,s.bank,'WHAT WILL YOU DO?',14,6)
   o.hline(4,16,120,1)
   for i,ch in enumerate(CHOICES):
    y=22+i*14
    rd.draw_text(o,s.bank,ch,30,y)
    if i==s.choice:o.fill_rect(22,y,4,7,1)
    
  elif s.phase=='stats':
   o.rect(4,2,120,60,1)
   rd.draw_text(o,s.bank,'CLEAR RESULTS',28,6)
   o.hline(4,16,120,1)
   rd.draw_text(o,s.bank,'SCORE',10,24)
   rd.draw_number(o,s.bank,s.stats['score'],70,24,5)
   rd.draw_text(o,s.bank,'COINS',10,36)
   rd.draw_number(o,s.bank,s.stats['coins'],70,36,3)
   rd.draw_text(o,s.bank,'DEATHS',10,48)
   rd.draw_number(o,s.bank,s.stats['deaths'],70,48,3)
