# game.py - ゲーム状態機械の中核
#
# 状態:
#   TITLE → STAGE_INTRO → PLAYING → (DYING or STAGE_CLEAR) → ...
#   GAME_OVER → TITLE
#   ENDING (全クリア)
#
# 全ての状態は update_xxx() / draw_xxx() の対で実装。
import time
import gc
import config as C
import stages as st
import world as wd
import player as pl
import entity as et
import render as rd
import ui


STATE_TITLE       = 'title'
STATE_STAGE_INTRO = 'intro'
STATE_PLAYING     = 'playing'
STATE_DYING       = 'dying'
STATE_PAUSED      = 'paused'
STATE_STAGE_CLEAR = 'clear'
STATE_GAME_OVER   = 'gameover'
STATE_ENDING      = 'ending'


class Game:
    def __init__(self, oled, bank, inp, audio, fx):
        self.oled = oled
        self.bank = bank
        self.inp = inp
        self.audio = audio
        self.fx = fx

        self.state = STATE_TITLE
        self.state_timer = 0
        self.frame = 0

        self.score = 0
        self.lives = C.START_LIVES
        self.stage_num = 1
        self.high_score = 0

        # ゲームプレイデータ(ステージ毎にリセット)
        self.world = None
        self.player = None
        self.entities = []
        self.fireballs = []
        self.cam_x = 0
        self.time_left = C.DEFAULT_TIME
        self.time_subframe = 0   # 60フレームで1秒減らす

    # ================================================================
    # メイン update / draw
    # ================================================================
    def update(self):
        self.inp.update()
        self.frame += 1

        s = self.state
        if s == STATE_TITLE:           self._update_title()
        elif s == STATE_STAGE_INTRO:   self._update_intro()
        elif s == STATE_PLAYING:       self._update_playing()
        elif s == STATE_DYING:         self._update_dying()
        elif s == STATE_PAUSED:        self._update_paused()
        elif s == STATE_STAGE_CLEAR:   self._update_stage_clear()
        elif s == STATE_GAME_OVER:     self._update_game_over()
        elif s == STATE_ENDING:        self._update_ending()

        # オーディオ更新
        self.audio.update()
        # BGMがビート進行したらLEDに通知
        if self.audio.beat_pulse:
            self.fx.beat()
        # LED更新
        self.fx.update(self.frame)

    def draw(self):
        oled = self.oled
        oled.fill(0)
        s = self.state
        if s == STATE_TITLE:
            ui.draw_title(oled, self.bank, self.state_timer)
        elif s == STATE_STAGE_INTRO:
            ui.draw_stage_intro(oled, self.bank, self.stage_num, self.lives)
        elif s == STATE_PLAYING or s == STATE_DYING:
            self._draw_playing()
        elif s == STATE_PAUSED:
            self._draw_playing()
            ui.draw_pause(oled, self.bank)
        elif s == STATE_STAGE_CLEAR:
            ui.draw_stage_clear(oled, self.bank, self.score, self.time_left * C.TIME_BONUS)
        elif s == STATE_GAME_OVER:
            ui.draw_game_over(oled, self.bank, self.score, self.state_timer)
        elif s == STATE_ENDING:
            ui.draw_ending(oled, self.bank, self.score, self.state_timer)
        oled.show()

    # ================================================================
    # 状態切替
    # ================================================================
    def _change_state(self, new_state):
        self.state = new_state
        self.state_timer = 0

    def _start_stage(self, num):
        """ステージ初期化"""
        stage_data = st.STAGES[num - 1] if 1 <= num <= len(st.STAGES) else None
        if stage_data is None:
            self._change_state(STATE_ENDING)
            self.audio.play_bgm(None)
            return
        self.stage_num = num
        self.world = wd.World(stage_data)
        self.player = pl.Player(self.world)
        self.player.apply_stage(stage_data)
        # オブジェクト配置
        self.entities = []
        for obj in stage_data['objects']:
            col, row = obj[0], obj[1]
            type_str = obj[2]
            ent = et.make_entity(type_str, col, row)
            if ent is not None:
                self.entities.append(ent)
        self.fireballs = []
        self.cam_x = 0
        self.time_left = stage_data.get('time_limit', C.DEFAULT_TIME)
        self.time_subframe = 0
        # 演出
        self.fx.set_stage(num)
        self.fx.set_player_state(self.player.state)
        # BGM
        self.audio.play_bgm(stage_data['bgm'])
        # GC
        gc.collect()

    # ================================================================
    # TITLE
    # ================================================================
    def _update_title(self):
        self.state_timer += 1
        # 初回到達時BGM
        if self.state_timer == 1:
            self.audio.play_bgm('overworld')
        if self.inp.pressed(0):
            self.audio.play_sfx('select')
            self.score = 0
            self.lives = C.START_LIVES
            self.stage_num = 1
            self._change_state(STATE_STAGE_INTRO)
            self.audio.stop_bgm()

    # ================================================================
    # STAGE_INTRO
    # ================================================================
    def _update_intro(self):
        if self.state_timer == 0:
            self._start_stage(self.stage_num)
            # ステージ開始まで BGM 一旦停止
            self.audio.pause_bgm()
        self.state_timer += 1
        if self.state_timer >= 60:   # 2秒表示
            self.audio.resume_bgm()
            self._change_state(STATE_PLAYING)

    # ================================================================
    # PLAYING
    # ================================================================
    def _update_playing(self):
        # ポーズ判定(SW1+SW3同時押し)
        if self.inp.held(0) and self.inp.pressed(2):
            self.audio.play_sfx('pause')
            self.audio.pause_bgm()
            self._change_state(STATE_PAUSED)
            return

        # ---- プレイヤー更新 ----
        prev_on_ground = self.player.on_ground
        self.player.update(self.inp, self._spawn_fireball)

        # ジャンプ音
        if getattr(self.player, '_just_jumped', False):
            if self.player.state == pl.STATE_SMALL:
                self.audio.play_sfx('jump_small')
            else:
                self.audio.play_sfx('jump_big')

        # ファイア音
        if getattr(self.player, '_fire_request', False):
            self.audio.play_sfx('fireball')

        # ---- 頭ぶつけ判定(?ブロック・レンガ) ----
        if self.player.head_hit_col >= 0:
            self._hit_block_from_below(self.player.head_hit_col)

        # ---- コイン取得 ----
        self._check_coin_pickup()

        # ---- エンティティ更新 ----
        for e in self.entities:
            if e.alive:
                e.update(self.world, self.player)

        # ---- ファイアボール ----
        for f in self.fireballs:
            if f.alive:
                f.update(self.world, self.player)

        # ---- 当たり判定: プレイヤー vs エンティティ ----
        if self.player.state != pl.STATE_DEAD:
            self._collide_player_entities()

        # ---- 当たり判定: ファイアボール vs エンティティ ----
        self._collide_fireball_entities()

        # ---- 死亡したエンティティ・ファイアボールを掃除 ----
        self.entities = [e for e in self.entities if e.alive]
        self.fireballs = [f for f in self.fireballs if f.alive]

        # ---- カメラ追従 ----
        target_cam = int(self.player.x) - 40
        if target_cam < 0:
            target_cam = 0
        max_cam = self.world.width * C.TILE - C.SCREEN_W
        if target_cam > max_cam:
            target_cam = max_cam
        self.cam_x = target_cam

        # ---- 時間経過 ----
        self.time_subframe += 1
        if self.time_subframe >= C.TARGET_FPS:
            self.time_subframe = 0
            self.time_left -= 1
            if self.time_left <= 0:
                self.time_left = 0
                # 時間切れ死亡
                self.player.kill_by_fall()

        # ---- 死亡判定 ----
        if self.player.state == pl.STATE_DEAD:
            self._change_state(STATE_DYING)
            self.audio.stop_bgm()
            self.audio.play_sfx('damage')
            return

        # ---- ゴール判定 ----
        stage_data = st.STAGES[self.stage_num - 1]
        goal_col = stage_data.get('goal_col', -1)
        if goal_col > 0 and self.player.x >= goal_col * C.TILE - 4:
            self._on_stage_clear()

        # ---- ボス撃破判定 ----
        if self.stage_num == 6:
            boss_dead = True
            has_boss = False
            for e in self.entities:
                if isinstance(e, et.Boss):
                    has_boss = True
                    if e.hp > 0:
                        boss_dead = False
            if has_boss and boss_dead:
                # 既にdying中
                pass
            elif not has_boss:
                # ボスが完全に消えた
                self._on_stage_clear()

        # FX状態同期
        self.fx.set_player_state(self.player.state)
        if self.player.invincible > 0:
            self.fx.set_invincible(2)

    def _spawn_fireball(self, x, y, direction):
        if len(self.fireballs) < 2:
            self.fireballs.append(et.Fireball(x, y, direction))

    def _hit_block_from_below(self, col):
        """頭ぶつけ。col列のどの行が当たったか探して処理。"""
        # プレイヤーの頭が触れた行を探す
        head_row = int(self.player.y) // C.TILE
        if head_row < 0 or head_row >= 8:
            return
        tid = self.world.tile_at(col, head_row)
        if tid == st.QBLOCK:
            # ?ブロック→使用済みに変更、アイテム/コイン出現
            self.world.set_tile(col, head_row, st.QUSED)
            self.audio.play_sfx('bump')
            self.score += C.SCORE_BLOCK
            # objects定義から該当アイテムを探す
            stage_data = st.STAGES[self.stage_num - 1]
            for obj in stage_data['objects']:
                if obj[0] == col and obj[1] == head_row:
                    ot = obj[2]
                    spawn_x = col * C.TILE
                    spawn_y = (head_row - 1) * C.TILE
                    if ot == 'qblock_coin':
                        self.score += C.SCORE_COIN
                        self.audio.play_sfx('coin')
                        self.fx.event_flash((40, 35, 0), 8)
                    elif ot == 'qblock_mushroom':
                        if self.player.state == pl.STATE_SMALL:
                            self.entities.append(et.Mushroom(spawn_x, spawn_y))
                        else:
                            self.entities.append(et.FireFlower(spawn_x, spawn_y))
                        self.audio.play_sfx('powerup')
                        self.fx.rainbow(20)
                    elif ot == 'qblock_fire':
                        if self.player.state == pl.STATE_SMALL:
                            self.entities.append(et.Mushroom(spawn_x, spawn_y))
                        else:
                            self.entities.append(et.FireFlower(spawn_x, spawn_y))
                        self.audio.play_sfx('powerup')
                        self.fx.rainbow(20)
                    elif ot == 'qblock_1up':
                        self.entities.append(et.OneUp(spawn_x, spawn_y))
                        self.audio.play_sfx('1up')
                    break
        elif tid == st.BRICK:
            if self.player.state != pl.STATE_SMALL:
                # 破壊
                self.world.set_tile(col, head_row, st.AIR)
                self.audio.play_sfx('brick_break')
                self.score += C.SCORE_BLOCK
            else:
                self.audio.play_sfx('bump')

    def _check_coin_pickup(self):
        """プレイヤーAABBの占めるタイルにコインがあれば取得"""
        px, py, pw, ph = self.player.aabb()
        left = int(px) // C.TILE
        right = int(px + pw - 1) // C.TILE
        top = int(py) // C.TILE
        bot = int(py + ph - 1) // C.TILE
        for c in range(left, right + 1):
            for r in range(top, bot + 1):
                if self.world.tile_at(c, r) == st.COIN:
                    self.world.set_tile(c, r, st.AIR)
                    self.score += C.SCORE_COIN
                    self.audio.play_sfx('coin')
                    self.fx.event_flash((40, 35, 0), 6)

    def _collide_player_entities(self):
        px, py, pw, ph = self.player.aabb()
        for e in self.entities:
            if not e.alive or not e.solid_for_player:
                continue
            ex, ey, ew, eh = e.aabb()
            if (px < ex + ew and px + pw > ex and
                py < ey + eh and py + ph > ey):
                # 踏みつけ判定: プレイヤーが下方向で、かつ足元が敵の上側
                stomp = (self.player.vy > 0 and py + ph - self.player.vy <= ey + 5)
                if stomp:
                    if e.on_stomp():
                        # 踏み成功
                        self.player.vy = -2.6
                        self.audio.play_sfx('stomp')
                        if isinstance(e, et.Boss):
                            self.score += 500
                            self.audio.play_sfx('boss_hit')
                            self.fx.event_flash((40, 40, 40), 4)
                            if e.is_dying():
                                self.audio.play_sfx('boss_dead')
                                self.fx.rainbow(40)
                        else:
                            self.score += C.SCORE_STOMP
                            self.fx.event_flash((40, 0, 0), 6)
                    else:
                        # ボスは踏み弾かれる
                        self.player.vy = -2.0
                        self._damage_player()
                else:
                    # 横/上からの接触はダメージ
                    if e.on_collide(self.player) == 'damage':
                        self._damage_player()
            # アイテム接触(キノコ・花)
            if isinstance(e, et.Mushroom):
                if (px < ex + ew and px + pw > ex and
                    py < ey + eh and py + ph > ey):
                    self.player.powerup_mushroom()
                    self.audio.play_sfx('powerup')
                    self.fx.rainbow(30)
                    self.score += 1000
                    e.alive = False
            if isinstance(e, et.FireFlower):
                if (px < ex + ew and px + pw > ex and
                    py < ey + eh and py + ph > ey):
                    self.player.powerup_fire()
                    self.audio.play_sfx('powerup')
                    self.fx.rainbow(30)
                    self.score += 1000
                    e.alive = False
            if isinstance(e, et.OneUp):
                if (px < ex + ew and px + pw > ex and
                    py < ey + eh and py + ph > ey):
                    self.lives = min(C.MAX_LIVES, self.lives + 1)
                    self.audio.play_sfx('1up')
                    e.alive = False
            # ナイフ判定
            if isinstance(e, et.Ninja):
                if e.knife_hits(px, py, pw, ph):
                    self._damage_player()
            # ボスの火球判定
            if isinstance(e, et.Boss):
                if e.fire_hits(px, py, pw, ph):
                    self._damage_player()

    def _damage_player(self):
        if self.player.take_damage():
            # 死亡確定
            pass
        else:
            self.audio.play_sfx('damage')
            self.fx.set_damage()
            self.fx.set_invincible(C.INVINCIBLE_FR)

    def _collide_fireball_entities(self):
        for f in self.fireballs:
            if not f.alive:
                continue
            fx, fy, fw, fh = f.aabb()
            for e in self.entities:
                if not e.alive:
                    continue
                ex, ey, ew, eh = e.aabb()
                if (fx < ex + ew and fx + fw > ex and
                    fy < ey + eh and fy + fh > ey):
                    if e.on_fireball():
                        # 撃破
                        f.alive = False
                        self.score += C.SCORE_FIREKILL
                        self.audio.play_sfx('stomp')
                    else:
                        # ボスのように生き残る場合もある
                        if isinstance(e, et.Boss):
                            f.alive = False
                            self.score += 200
                            self.audio.play_sfx('boss_hit')
                            self.fx.event_flash((40, 40, 40), 4)
                            if e.is_dying():
                                self.audio.play_sfx('boss_dead')
                                self.fx.rainbow(40)
                    break

    def _on_stage_clear(self):
        self.audio.stop_bgm()
        self.audio.play_sfx('stage_clear')
        self.fx.rainbow(60)
        # 残時間ボーナス
        self.score += self.time_left * C.TIME_BONUS
        # 残時間多ければ1UP
        if self.time_left >= C.GOAL_BONUS_TIME_THRESH:
            self.lives = min(C.MAX_LIVES, self.lives + 1)
        self._change_state(STATE_STAGE_CLEAR)

    # ================================================================
    # DYING
    # ================================================================
    def _update_dying(self):
        self.state_timer += 1
        self.player.update(self.inp, lambda *a: None)   # 落下演出
        if self.state_timer >= C.DYING_FR:
            self.lives -= 1
            if self.lives <= 0:
                self._change_state(STATE_GAME_OVER)
                self.audio.play_sfx('game_over')
            else:
                self._change_state(STATE_STAGE_INTRO)

    # ================================================================
    # PAUSED
    # ================================================================
    def _update_paused(self):
        self.state_timer += 1
        if self.inp.pressed(0):
            self.audio.play_sfx('pause')
            self.audio.resume_bgm()
            self._change_state(STATE_PLAYING)
        # SW3でタイトルへ
        if self.state_timer > 20 and self.inp.held(0) and self.inp.pressed(2):
            self.audio.stop_bgm()
            self._change_state(STATE_TITLE)

    # ================================================================
    # STAGE_CLEAR
    # ================================================================
    def _update_stage_clear(self):
        self.state_timer += 1
        if self.state_timer >= 150:   # 5秒
            if self.score > self.high_score:
                self.high_score = self.score
            if self.stage_num >= len(st.STAGES):
                self._change_state(STATE_ENDING)
                self.audio.play_sfx('stage_clear')
            else:
                self.stage_num += 1
                self._change_state(STATE_STAGE_INTRO)

    # ================================================================
    # GAME_OVER
    # ================================================================
    def _update_game_over(self):
        self.state_timer += 1
        if self.score > self.high_score:
            self.high_score = self.score
        if (self.state_timer > 60 and self.inp.any_pressed()) or self.state_timer > 300:
            self._change_state(STATE_TITLE)

    # ================================================================
    # ENDING
    # ================================================================
    def _update_ending(self):
        self.state_timer += 1
        if self.state_timer == 1:
            self.audio.play_bgm('overworld')
        if self.state_timer > 60 and self.inp.any_pressed():
            self._change_state(STATE_TITLE)

    # ================================================================
    # PLAYING 描画
    # ================================================================
    def _draw_playing(self):
        oled = self.oled
        # 背景は単純な黒、必要なら星や雲を描いてもよい
        # タイルマップ
        # World.drawはy=0始まりで描くが、ゲーム領域はy=PLAY_TOPから
        # 簡略化のためWorldは既にy=0..63で描く設計だが、PLAY_TOPを考慮するため
        # World.drawをスクリーン全体描画とし、その後ヘッダで上書きする
        self.world.draw(oled, self.bank, self.cam_x)

        # エンティティ
        for e in self.entities:
            if e.alive:
                e.draw(oled, self.bank, self.cam_x)
        # ファイアボール
        for f in self.fireballs:
            if f.alive:
                f.draw(oled, self.bank, self.cam_x)
        # プレイヤー
        self.player.draw(oled, self.bank, self.cam_x)

        # ヘッダ(最後に上書き)
        stage_data = st.STAGES[self.stage_num - 1]
        label_num = self.stage_num
        ui.draw_header(oled, self.bank, self.score, self.lives,
                       self.time_left, str(label_num))
