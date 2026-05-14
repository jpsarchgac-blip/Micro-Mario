# config.py - チューニング定数を一箇所に集約
# 数字をいじるだけで触り心地が変わる。マジックナンバーをコードに撒かない。

# ----- ハードウェアピン -----
# I2C(0)のピンを明示指定する(GP4とSW3の競合回避)
PIN_I2C_SDA   = 8
PIN_I2C_SCL   = 9
PIN_SW1       = 2     # ジャンプ / 決定
PIN_SW2       = 3     # ファイア / キャンセル
PIN_SW3       = 4     # ダッシュ / ポーズ補助
PIN_NEOPIXEL  = 10
PIN_SPEAKER   = 21
I2C_FREQ      = 400_000   # 400kHz I2C(SSD1306の事実上の標準)

# ----- 画面 -----
SCREEN_W      = 128
SCREEN_H      = 64
TILE          = 8         # タイルサイズ
COLS_VISIBLE  = SCREEN_W // TILE   # 16
ROWS          = SCREEN_H // TILE   # 8
HEADER_H      = 8         # 画面上端のUI領域(高さ)
PLAY_TOP      = HEADER_H  # ゲーム領域のy開始
PLAY_BOT      = SCREEN_H  # ゲーム領域のy終端

# ----- フレームレート -----
TARGET_FPS    = 30
FRAME_MS      = 1000 // TARGET_FPS   # 33ms

# ----- プレイヤー物理 -----
WALK_SPEED    = 1.2
RUN_SPEED     = 2.4
RUN_ACCEL_FR  = 15        # ダッシュ最高速到達までのフレーム数
JUMP_VELOCITY = -3.4
GRAVITY_UP    = 0.18      # ジャンプ上昇中(SW1押下)
GRAVITY_DOWN  = 0.38      # 落下中
TERMINAL_VEL  = 4.5
COYOTE_FRAMES = 6         # 足場離脱後もジャンプ受付
JUMP_BUFFER   = 6         # 着地前ジャンプ入力先行受付
SHORT_JUMP_CUT= 0.45      # ボタン離した時の上昇速度カット率

# 水中ステージ用
WATER_GRAVITY = 0.10
WATER_JUMP    = -2.0
WATER_TERMVEL = 1.5

# ----- プレイヤー状態 -----
INVINCIBLE_FR = 90        # 被ダメ後の無敵時間
POWERUP_FR    = 60        # キノコ取得演出
DYING_FR      = 60        # 死亡演出時間

# ----- スコア -----
SCORE_COIN    = 100
SCORE_STOMP   = 200
SCORE_FIREKILL= 400
SCORE_BLOCK   = 50
SCORE_1UP     = 5000
TIME_BONUS    = 50

# ----- 残機 -----
START_LIVES   = 3
MAX_LIVES     = 9
GOAL_BONUS_TIME_THRESH = 30  # クリア時残時間>=これで1UP

# ----- LED -----
LED_MAX_BRIGHT = 40       # NeoPixel直視時のまぶしさ抑制

# ----- オーディオ -----
AUDIO_MAX_VOL  = 6000     # PWM duty(0..65535)、これ以上はうるさい
AUDIO_BGM_VOL  = 3000
AUDIO_SFX_VOL  = 5000

# ----- ステージ -----
STAGE_COUNT    = 6        # 1..5 + ボス
DEFAULT_TIME   = 100      # ステージ制限時間(秒)

# =============================================
# NEWモード専用定数
# =============================================
NEW_INVINCIBLE_FR = 60    # 被ダメ後の無敵(2秒@30fps)
CROUCH_SPEED_MUL  = 0.4   # しゃがみ時の移動速度倍率
STAR_DURATION      = 300   # スター無敵(10秒@30fps)

# ?ブロック アイテム確率(累積%: きのこ50, ファイア65, 1UP80, コイン90, スター100)
QBLOCK_PROBS = (50, 65, 80, 90, 100)

# 難易度テーブル
DIFF_EASY   = {'lives': 5, 'enemy_mul': 0.5, 'speed_mul': 0.8, 'name': 'EASY'}
DIFF_NORMAL = {'lives': 3, 'enemy_mul': 1.0, 'speed_mul': 1.0, 'name': 'NORMAL'}
DIFF_HARD   = {'lives': 2, 'enemy_mul': 1.5, 'speed_mul': 1.2, 'name': 'HARD'}
DIFFICULTIES = (DIFF_EASY, DIFF_NORMAL, DIFF_HARD)

# 王冠永続化
CROWN_FILE = 'crowns.dat'

# 旗ゴール得点(上から)
FLAG_SCORE_TOP = 5000
FLAG_SCORE_MID = 2000
FLAG_SCORE_BOT = 500

# 音量設定永続化
SETTINGS_FILE = 'settings.dat'
