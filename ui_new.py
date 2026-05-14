# ui_new.py - NEWモード用UI描画
import config as C
import render as rd

def _cx(text,cw=5):
    return(C.SCREEN_W-len(text)*cw)//2

def draw_mode_select(oled,bank,cursor,blink):
    oled.fill(0)
    oled.rect(2,2,124,60,1)
    rd.draw_text(oled,bank,'MICRO MARIO',_cx('MICRO MARIO'),4)
    oled.hline(2,13,124,1)
    labels=['OLD MODE','NEW MODE','MUSIC MODE','OPTION MODE','TEST MODE']
    for i,lb in enumerate(labels):
        y=16+i*8
        if cursor==i and (blink>>2)&1:
            oled.fill_rect(24,y-1,80,9,1)
        rd.draw_text(oled,bank,lb,_cx(lb),y)
        if i==cursor:
            oled.fill_rect(18,y,4,7,1)

def draw_music_player(oled,bank,track_name,is_playing):
    oled.fill(0)
    oled.rect(2,2,124,60,1)
    rd.draw_text(oled,bank,'MUSIC PLAYER',_cx('MUSIC PLAYER'),6)
    oled.hline(2,16,124,1)
    
    rd.draw_text(oled,bank,'TRACK:',10,26)
    rd.draw_text(oled,bank,track_name,40,26)
    
    status='PLAYING' if is_playing else 'STOPPED'
    rd.draw_text(oled,bank,status,_cx(status),38)
    
    rd.draw_text(oled,bank,'SW1:PLAY/STOP',2,50)
    rd.draw_text(oled,bank,'SW2+3:EXIT',80,50)

def draw_option_menu(oled,bank,vol):
    oled.fill(0)
    oled.rect(2,2,124,60,1)
    rd.draw_text(oled,bank,'OPTION',_cx('OPTION'),6)
    oled.hline(2,16,124,1)
    
    rd.draw_text(oled,bank,'VOLUME',_cx('VOLUME'),24)
    
    # Vol meter 0..10
    bar_w=80; bar_x=24; bar_y=36
    oled.rect(bar_x,bar_y,bar_w,6,1)
    fill_w=int((vol/10)*bar_w)
    if fill_w>0:
        oled.fill_rect(bar_x,bar_y,fill_w,6,1)
        
    rd.draw_text(oled,bank,'SW1:SAVE & EXIT',_cx('SW1:SAVE & EXIT'),50)

def draw_difficulty_select(oled,bank,cursor,blink):
    oled.fill(0)
    oled.rect(4,4,120,56,1)
    rd.draw_text(oled,bank,'DIFFICULTY',_cx('DIFFICULTY'),8)
    oled.hline(4,18,120,1)
    labels=['EASY','NORMAL','HARD']
    for i,lb in enumerate(labels):
        y=24+i*12
        rd.draw_text(oled,bank,lb,_cx(lb),y)
        if i==cursor:
            oled.fill_rect(20,y,4,7,1)

def draw_header_new(oled,bank,score,lives,time_left,stage_label,coins):
    oled.fill_rect(0,0,128,8,0)
    rd.draw_number(oled,bank,score,0,0,width=5)
    rd.draw_text(oled,bank,stage_label,50,0)
    rd.draw_text(oled,bank,'T',75,0)
    rd.draw_number(oled,bank,time_left,81,0,width=3)
    # コイン数
    rd.draw_text(oled,bank,'C',105,0)
    rd.draw_number(oled,bank,coins,111,0,width=2)
    oled.hline(0,8,128,1)

def draw_item_slot(oled,bank,frame,result_idx,settled):
    """?ブロックのスロット演出。画面右上に表示。"""
    items=['mushroom','fire_flower','one_up','coin','star_1']
    x=100;y=12
    oled.rect(x-1,y-1,10,10,1)
    if settled:
        key=items[result_idx]
        oled.blit(bank.fb[key],x,y)
    else:
        # 回転アニメ
        idx=(frame>>1)%len(items)
        oled.blit(bank.fb[items[idx]],x,y)

def draw_panorama_bar(oled,progress):
    """ステージ見渡し中の進行バー"""
    oled.fill_rect(0,60,int(128*progress),3,1)

def draw_pipe_transition(oled,bank,frame,entering=True):
    """ドカンロード演出"""
    oled.fill(0)
    # 土管の断面(縦2本線)
    oled.vline(48,0,64,1);oled.vline(80,0,64,1)
    # レンガ模様
    for i in range(0,64,8):
        oled.hline(48,i,1,1);oled.hline(80,i,1,1)
    # マリオ落下/上昇
    if entering:
        my=frame*2-16
    else:
        my=64-frame*2
    if'mario_s_r'in bank.fb:
        oled.blit(bank.fb['mario_s_r'],60,my)
    # キラキラ
    for i in range(5):
        px=52+(frame*7+i*19)%24
        py=(frame*3+i*17)%64
        oled.pixel(px,py,1)
        if px+1<80:oled.pixel(px+1,py,1)
    # 進行バー
    bw=frame*128//45
    oled.fill_rect(0,61,min(bw,128),3,1)
    # テキスト
    if entering:
        rd.draw_text(oled,bank,'GOING DOWN!',_cx('GOING DOWN!'),2)
    else:
        rd.draw_text(oled,bank,'GOING UP!',_cx('GOING UP!'),2)

def draw_flag_anim(oled,bank,world,cam_x,cam_y,flag_col,frame):
    """旗降下アニメ。frame 20-49で旗マーカーがポール上から降りる。"""
    import config as C
    sx=flag_col*C.TILE-cam_x
    if sx<-8 or sx>=C.SCREEN_W+8:return
    pole_top=max(9,4*C.TILE-cam_y)
    pole_bot=min(C.SCREEN_H-4,(world.rows-4)*C.TILE-cam_y)
    if frame<20:return
    if frame<50:
        t=frame-20
        flag_y=pole_top+(pole_bot-pole_top)*t//30
    else:
        flag_y=pole_bot
    fx=sx+C.TILE;fy=int(flag_y)
    if 0<=fx<C.SCREEN_W-4 and 9<=fy<C.SCREEN_H-3:
        oled.fill_rect(fx,fy,5,4,1)

def draw_stage_intro_new(oled,bank,stage_num,lives,diff_name):
    oled.fill(0)
    oled.rect(10,10,108,44,1)
    rd.draw_text(oled,bank,'STAGE',_cx('STAGE'),16)
    rd.draw_number(oled,bank,stage_num,60,26,width=1)
    rd.draw_text(oled,bank,'LIFE',28,38)
    rd.draw_hearts(oled,bank,lives,54,38)
    rd.draw_text(oled,bank,diff_name,_cx(diff_name),48)
