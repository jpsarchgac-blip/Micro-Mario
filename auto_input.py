# auto_input.py - テスト自動プレイ用入力シミュレーター
# Input クラスと同じインターフェース。ハードウェアボタンの代わりに
# ゲーム状況(前方の壁/穴/敵)を見て自動でジャンプ+ダッシュを入力する。
import config as C

_JUMP_HOLD = 18  # ジャンプ長押しフレーム(高さ調整)
_LOOK_PX   = 14  # 前方障害検知距離 px
_LOOK_ROWS = 2   # 壁として検知する高さ(タイル数)
_MENU_FR   = 90  # メニュー/エンディング自動進行間隔(フレーム)


class AutoInput:
    """S_PLAY中は update_auto() でゲーム状況に応じてジャンプ判断。
    それ以外の状態は update() の定期SW0でメニュー/ダイアログを自動進行。
    """
    def __init__(self):
        self._jf = 0   # ジャンプ押下残フレーム
        self._pt = 0   # 定期タイマー

    def update(self):
        """毎フレーム: タイマー更新。非ゲーム中はここで定期ボタン押し。"""
        if self._jf > 0:
            self._jf -= 1
        self._pt += 1
        if self._pt >= _MENU_FR and self._jf == 0:
            self._jf = _JUMP_HOLD
            self._pt = 0

    def update_auto(self, player, world, ents):
        """S_PLAY用: player.update() より前に毎フレーム呼ぶ。
        前方の壁・穴・致死タイル・敵を検知してジャンプ判断。
        """
        if not player.on_ground or self._jf > 0:
            return

        look_col = int(player.x + player.w + _LOOK_PX) // C.TILE
        foot_row = int(player.y + player.h - 1) // C.TILE

        wall   = any(world.is_solid(look_col, foot_row - r)
                     for r in range(1, _LOOK_ROWS + 1))
        gap    = (not world.is_solid(look_col, foot_row) and
                  not world.is_solid(look_col, foot_row + 1))
        lethal = (world.is_lethal(look_col, foot_row) or
                  world.is_lethal(look_col, foot_row - 1))
        enemy  = any(getattr(e, 'alive', False) and hasattr(e, 'x')
                     and e.x > player.x and e.x - player.x < 28
                     for e in (ents or []))

        if wall or gap or lethal or enemy:
            self._jf = _JUMP_HOLD
            self._pt = 0  # 検知後は定期タイマーをリセット

    # ----- Input インターフェース -----
    def pressed(self, i):
        if i == 0: return self._jf == _JUMP_HOLD  # ジャンプ開始フレームのみ
        return False

    def held(self, i):
        if i == 0: return self._jf > 0  # ジャンプ長押し → フルジャンプ高さ
        return False  # SW3ダッシュ/しゃがみは使わない(クラウチ回避)

    def released(self, i): return False
    def any_pressed(self):  return self._jf == _JUMP_HOLD
