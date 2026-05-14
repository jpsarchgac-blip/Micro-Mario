# ui.py - 画面UI(ヘッダ・タイトル・GAME OVER等)
# draw_text / draw_number は sprites.py の TINY_DIGITS (4x8 MONO_VLSB) を使う。
# アルファベット A-Z を追加したので、英語テキストが正しく表示される。
import config as C
import render as rd


# ---- ユーティリティ ----
def _center_x(text, char_w=5):
    """テキストを中央揃えにする x 座標を返す。"""
    return (C.SCREEN_W - len(text) * char_w) // 2


def draw_header(oled, bank, score, lives, time_left, stage_label):
    """画面上端のヘッダ(高さ8)を描画。"""
    oled.fill_rect(0, 0, 128, 8, 0)
    # スコア(左)
    rd.draw_number(oled, bank, score, 0, 0, width=5)
    # ステージ番号(中央)
    rd.draw_text(oled, bank, stage_label, 62, 0)
    # 残時間(右寄り)
    rd.draw_text(oled, bank, 'T', 75, 0)
    rd.draw_number(oled, bank, time_left, 81, 0, width=3)
    # 残機ハート(右端)
    rd.draw_hearts(oled, bank, lives, 102, 0)
    # ヘッダ下区切り線
    oled.hline(0, 8, 128, 1)


def draw_title(oled, bank, blink_frame):
    """タイトル画面 - MICRO MARIO"""
    oled.fill(0)

    # ---- 外枠 ----
    oled.rect(2, 2, 124, 60, 1)

    # ---- タイトル "MICRO MARIO" (中央揃え) ----
    title = 'MICRO MARIO'
    rd.draw_text(oled, bank, title, _center_x(title), 6)

    # ---- 区切り線 ----
    oled.hline(2, 17, 124, 1)

    # ---- マリオスプライト(タイトル用) + ステージ名 ----
    fb = bank.fb
    if 'mario_s_jump' in fb:
        key = 'mario_s_jump' if (blink_frame >> 4) & 1 else 'mario_s_r'
        oled.blit(fb[key], 10, 22)

    # ---- "PRESS SW1" 点滅 ----
    press = 'PRESS SW1'
    if (blink_frame >> 3) & 1:
        rd.draw_text(oled, bank, press, _center_x(press), 22)

    # ---- 操作説明 ----
    oled.hline(2, 34, 124, 1)
    rd.draw_text(oled, bank, 'SW1 JUMP', _center_x('SW1 JUMP'), 38)
    rd.draw_text(oled, bank, 'SW2 FIRE', _center_x('SW2 FIRE'), 47)
    rd.draw_text(oled, bank, 'SW3 DASH', _center_x('SW3 DASH'), 56)


def draw_game_over(oled, bank, score, blink):
    """ゲームオーバー画面"""
    oled.fill(0)
    oled.rect(4, 10, 120, 36, 1)

    # "GAME OVER" = 9文字 x 5px = 45px → x=41
    rd.draw_text(oled, bank, 'GAME OVER', 41, 18)
    # スコア
    rd.draw_text(oled, bank, 'SCORE', 24, 30)
    rd.draw_number(oled, bank, score, 54, 30, width=5)

    # "PRESS SW1" 点滅
    if (blink >> 3) & 1:
        rd.draw_text(oled, bank, 'PRESS SW1', 41, 52)


def draw_stage_intro(oled, bank, stage_num, lives):
    """ステージ開始インタータイトル"""
    oled.fill(0)
    oled.rect(14, 14, 100, 36, 1)

    # "STAGE" = 5文字 x 5px → x=51
    rd.draw_text(oled, bank, 'STAGE', 51, 20)
    # ステージ番号(大きめに): x中央
    rd.draw_number(oled, bank, stage_num, 60, 30, width=1)

    # 残機ハート
    rd.draw_text(oled, bank, 'LIFE', 28, 40)
    rd.draw_hearts(oled, bank, lives, 54, 40)


def draw_stage_clear(oled, bank, score, time_bonus):
    """ステージクリア画面"""
    oled.fill(0)
    oled.rect(4, 6, 120, 52, 1)

    # "STAGE CLEAR!" = 12文字 → x=28
    rd.draw_text(oled, bank, 'STAGE CLEAR!', 28, 12)

    oled.hline(4, 22, 120, 1)

    # スコア
    rd.draw_text(oled, bank, 'SCORE', 8, 26)
    rd.draw_number(oled, bank, score, 58, 26, width=6)

    # タイムボーナス
    rd.draw_text(oled, bank, 'BONUS', 8, 38)
    rd.draw_number(oled, bank, time_bonus, 58, 38, width=6)

    # ---- お祝いの星装飾 ----
    stars = [(10, 50), (30, 50), (50, 50), (70, 50), (90, 50), (110, 50)]
    for sx, sy in stars:
        oled.pixel(sx, sy, 1)
        oled.pixel(sx + 1, sy, 1)


def draw_pause(oled, bank):
    """ポーズ画面オーバーレイ"""
    oled.fill_rect(38, 22, 52, 20, 0)
    oled.rect(38, 22, 52, 20, 1)
    # "PAUSE" = 5文字 x 5px → x=51
    rd.draw_text(oled, bank, 'PAUSE', 51, 29)


def draw_ending(oled, bank, score, blink):
    """全クリア(エンディング)画面"""
    oled.fill(0)

    # ---- 点滅する星 ----
    stars = [(10, 6), (118, 10), (20, 57), (110, 54), (64, 2), (50, 60), (80, 58)]
    for sx, sy in stars:
        if (blink + sx) & 8:
            oled.pixel(sx, sy, 1)
            oled.pixel(sx + 1, sy, 1)
            oled.pixel(sx, sy + 1, 1)

    oled.rect(6, 14, 116, 36, 1)

    # "YOU WIN!" = 8文字 x 5px = 40px → x=44
    rd.draw_text(oled, bank, 'YOU WIN!', 44, 20)

    # スコア
    rd.draw_text(oled, bank, 'SCORE', 14, 32)
    rd.draw_number(oled, bank, score, 44, 32, width=5)

    # "PRESS SW1" 点滅
    if (blink >> 3) & 1:
        rd.draw_text(oled, bank, 'PRESS SW1', 41, 54)
