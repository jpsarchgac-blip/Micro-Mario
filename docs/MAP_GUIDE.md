# Micro-Mario マップ作成手引き

このドキュメントは **NEWモード/CUSTOMモード用のステージ作成** に関する完全リファレンスです。
人間が読んでマップを設計するためにも、AI が自然言語の指示からマップを生成するための仕様書としても使えます。

---

## 1. ステージデータの構造

各ステージは Python の dict で、以下のキーを持ちます。

| キー | 型 | 必須 | 説明 |
|---|---|---|---|
| `name` | str | yes | ステージ名 (画面表示用、18文字目安) |
| `bgm` | str | yes | BGM名: `overworld` / `underground` / `water` / `castle` / `sky` / `boss` |
| `width` | int | yes | 列数 (タイル数)。32〜128 推奨。最大256まで |
| `rows` | int | yes | 行数 (タイル数)。**8 / 12 / 16 のいずれか** |
| `time_limit` | int | yes | 制限時間 (秒)。標準100、ボス系200〜250 |
| `terrain` | list[bytes] | yes | 各列のタイル列。詳細は §3 |
| `water` | bool | yes | 水中ステージならTrue。重力と挙動が変わる |
| `gravity_scale` | float | yes | 重力倍率。標準1.0、水中0.2、低重力ステージなど用 |
| `start_col` | int | yes | プレイヤー開始列 |
| `start_row` | int | yes | プレイヤー開始行 (足の位置。BIGなら `rows-3〜rows-4` 程度) |
| `goal_col` | int | yes | ゴール判定列。プレイヤーが `x >= goal_col*8-4` でクリア |
| `flag_col` | int | no | 旗ゴール演出を出す列 (省略時は単純クリア) |
| `pipe_col` | int | no | 土管入口の列 (-1で無効)。SW2 hold + 接近で入る |
| `pipe_return_col` | int | no | 土管から帰還する列 |
| `objects` | list[tuple] | yes | エンティティ配置リスト。詳細は §5 |
| `enemy_sets` | dict | yes | 難易度別敵リスト。詳細は §6 |

---

## 2. 物理パラメータと制約 (チートシート)

| パラメータ | 値 | 意味 |
|---|---|---|
| `TILE` | 8 px | タイル1辺 |
| `SCREEN_W` | 128 px | 画面幅 (16タイル) |
| `SCREEN_H` | 64 px | 画面高 (8タイル) |
| `TARGET_FPS` | 30 | 1秒=30フレーム |
| `WALK_SPEED` | 1.2 px/F | 歩行速度 |
| `RUN_SPEED` | 2.4 px/F | ダッシュ最高速 |
| `RUN_ACCEL_FR` | 15 | ダッシュチャージにかかるフレーム数 |
| `JUMP_VELOCITY` | -3.4 px/F | ジャンプ初速 |
| `GRAVITY_UP` | 0.18 px/F² | 上昇中の重力 (SW1押下中) |
| `GRAVITY_DOWN` | 0.38 px/F² | 落下時の重力 |
| `TERMINAL_VEL` | 4.5 px/F | 最大落下速度 |
| `WATER_GRAVITY` | 0.10 | 水中重力 |
| `WATER_JUMP` | -2.0 | 水中ジャンプ初速 |

### 2.1 プレイヤー判定サイズ

- SMALL: AABB `8x8` (描画は `mario_s_*` 1枚スプライト)
- BIG / FIRE: AABB `8x16` (描画は2枚タイル)
- BIG/FIREしゃがみ中: AABB `8x8` (頭上1タイルで強制継続)

実際の幅は `w=6` で左右1pxずつ細い(タイル角で引っかからないように)。

### 2.2 最大ジャンプ性能

- **垂直**: 最大ジャンプ長押しで約 **4タイル分上昇**(`(JUMP_VELOCITY)² / 2GRAVITY_UP ≈ 32px`)
- **水平**: 一回のジャンプで通常歩行時 **〜10タイル**、ダッシュ込みで **〜11タイル** 進める

**直接届く浮島の高さ早見表** (足元基準):

| ステージ行数 R | 地面の行 | 易しい (足元 r) | 標準 (r) | やや難 (r) | 限界 (r) |
|---|---|---|---|---|---|
| 8 | 6-7 | 5 | 4 | 3 | 2 |
| 12 | 10-11 | 9 | 8 | 7 | 6 |
| 16 | 14-15 | 13 | 12 | 11 | 10 (限界) |

> **R=16 で `row 8 以上` の高さは段階的に登らないと届かない。**

### 2.3 最大水平ジャンプ距離

地面→同じ高さの地面: 横ギャップ最大 **約9タイル**(ダッシュ込み)。
通常設計は **2〜4タイル幅の穴** に留めると親切。

---

## 3. タイルID一覧

`world_new.py` で定義されている全タイル。`stages_new.py` の冒頭で別名(短縮)に再エイリアスされる:

```python
A=AIR;G=GROUND;B=BRICK;Q=QBLOCK;C=COIN;S=SPIKE
PT=PIPE_TL;PR=PIPE_TR;PB=PIPE_BL;PD=PIPE_BR
CL=CLOUD_PLAT;GO=GOAL;MA=MAGMA;GR=GRASS;FL=FLAG
```

| ID | 名前 | 短縮 | 種別 | 説明 |
|---|---|---|---|---|
| 0 | AIR | A | 空気 | 何もない。プレイヤーが通れる |
| 1 | GROUND | G | 固体 | 普通の地面ブロック |
| 2 | BRICK | B | 固体 | BIGなら頭突きで破壊可。SMALLは破壊不可 |
| 3 | QBLOCK | Q | 固体 | ?ブロック。頭突きで `objects` 配列にある `qblock_*` を発動 |
| 4-7 | PIPE_TL/TR/BL/BR | PT/PR/PB/PD | 固体 | 土管の4タイル(左上・右上・左下・右下) |
| 8 | COIN | C | 通過 | 接触でコイン1枚+100点 |
| 9 | SPIKE | S | 致死 | 触ると死亡 |
| 10 | GOAL | GO | 通過 | (現状はゴール演出用、`goal_col` でクリア判定) |
| 11 | CLOUD_PLAT | CL | 半固体 | 上からのみ着地できる雲足場 |
| 12 | QUSED | (自動) | 固体 | 使い切った?ブロック (描画は色違い) |
| 13 | MAGMA | MA | 致死 | 溶岩。波打ちアニメ。触ると死亡 |
| 14 | GRASS | GR | 固体 | 草原表面。挙動はGROUNDと同じ |
| 15 | FLAG | FL | 通過 | ゴール旗のポール部分。`flag_col` 演出と組み合わせる |

### 3.1 terrain の表現

`terrain` は `list[bytes]` で、**列ごと** にタイルIDを格納します。
1列の長さ = `rows`。インデックス0が画面上端、`rows-1` が画面下端。

```python
# R=12 (12行), col 0 のデータ例
# 上空6行AIR, 下4行GROUND(地面+その下)
col0 = bytes([A,A,A,A,A,A,A,A,G,G,G,G])  # ❌ ダメ: 12要素必要だが順序意識
# 推奨: ヘルパー _c() を使う (詳細§4)
col0 = _c(12, A,A,A,A,A,A,A,A,G,G,G,G)
```

---

## 4. ヘルパー関数

`stages_new.py` の冒頭で定義されている、列を作る便利関数。

### 4.1 `_c(rows, *ids)` — 1列を作る

下から順にIDを並べる。指定が `rows` 未満なら**先頭(上)をAIRでパディング**。

```python
_c(12, G, G)              # 下2行のみGROUND、上10行AIR (= 平地)
_c(12, A,A,A,A,A,A,A,Q,A,A,G,G)  # row7に?ブロック、row10-11に地面
```

### 4.2 `_flat(rows, n, top_id=A, bot_id=G, bot_n=2)` — 平地のリスト

`n` 列分の「上は`top_id`、下`bot_n`行は`bot_id`」な平地列を返す。

```python
t += _flat(12, 5)         # 5列分の平地 (上10行AIR、下2行GROUND)
t += _flat(12, 3, bot_n=3)  # 下3行GROUND (高めの地面)
```

### 4.3 `_hole(rows, n=1)` — 完全な空列

落下死ピットを作る (底まで何もない列)。

```python
t += _hole(12, 2)         # 2列幅の穴
```

---

## 5. objects (固定配置エンティティ)

`objects` リストは各要素 `(col, row, type_str)` のタプル。

### 5.1 利用可能な type_str

| type_str | 種別 | 解説 |
|---|---|---|
| `goomba` | 敵 | クリボー。歩き反転、踏みつけ可 |
| `bat` | 敵 | コウモリ。プレイヤー追跡、踏みつけ可 |
| `fish` | 敵 | 魚(水中)、軌道揺れ、踏みつけ可 |
| `pata_new` | 敵 | パタパタ(NEW)。横移動、踏むとバネジャンプ |
| `killer_spawn` | 召喚 | キラー砲台。一定間隔で横一直線弾を出す |
| `big_mushroom` | ギミック | 大キノコトランポリン。触れると高ジャンプ |
| `boss` | 敵 | キングクッパ(ボス)。ステージ6で使用 |
| `qblock_random` | スロット | ?ブロックの場所に対応。スロット演出付き |

**注意**: 通常`enemy_sets`で難易度別に管理するが、**ギミック系**(`big_mushroom`, `qblock_random`)は **`objects` 直下に書く** のが慣例。

### 5.2 配置例

```python
'objects':[
    (6, 6, 'qblock_random'),       # col 6 row 6 に?ブロック
    (28, 5, 'qblock_random'),
    (15, 9, 'big_mushroom'),       # トランポリン
],
```

---

## 6. enemy_sets (難易度別敵配置)

```python
'enemy_sets':{
    'easy':   [(col,row,type_str), ...],   # 少なめ
    'normal': [...],                        # 標準
    'hard':   [...],                        # 多め、強敵を追加
},
```

選ばれた難易度のリストが **`objects` の代わりに使われる**(差分ではなく差し替え)。
`qblock_random` などは `enemy_sets` 側にも書ける(自動でスキップされる)が、**慣例として `objects` 直下** に。

例 (S1の場合):

```python
'enemy_sets':{
    'easy':   [(22,R-3,'goomba'),(66,R-3,'goomba')],
    'normal': [(12,R-3,'goomba'),(22,R-3,'goomba'),(45,R-3,'goomba'),
               (78,R-3,'goomba'),(97,R-3,'goomba')],
    'hard':   [(12,R-3,'goomba'),(22,R-3,'goomba'),(45,R-3,'goomba'),
               (66,R-3,'goomba'),(78,R-3,'goomba'),(97,R-3,'goomba')],
},
```

`R-3` は「地面の上=row 9 (R=12 の場合)」を表す慣用表現。

---

## 7. よくあるパターン集

### 7.1 平地スタート + 穴 + 平地

```python
R=12;t=[]
t += _flat(R, 5)          # 0-4: 平地
t += _hole(R, 2)          # 5-6: 2幅の穴
t += _flat(R, 10)         # 7-16: 平地
```

### 7.2 階段クライム (4段)

```python
t.append(_c(R, A,A,A,A,A,A,A,A,A,G,G,G))   # row9: 1段
t.append(_c(R, A,A,A,A,A,A,A,A,G,G,G,G))   # row8: 2段
t.append(_c(R, A,A,A,A,A,A,A,G,G,G,G,G))   # row7: 3段
t.append(_c(R, A,A,A,A,A,A,G,G,G,G,G,G))   # row6: 4段(最高)
```

### 7.3 浮島 + コイン

```python
t.append(_c(R, A,A,A,A,A,A,A,A,G,A,A,A))   # 浮島row8
t.append(_c(R, A,A,A,A,A,A,C,A,G,A,A,A))   # 浮島+上にコインrow6
t.append(_c(R, A,A,A,A,A,A,A,A,G,A,A,A))   # 浮島row8
```

### 7.4 ?ブロック + objects 紐付け

```python
# terrain 側に Q タイルを置く
t.append(_c(R, A,A,A,A,A,A,Q,A,A,A,G,G))   # col X、row 6 に Q
# objects 側に同じ座標で qblock_random を登録
'objects':[(X, 6, 'qblock_random')],
```

→ プレイヤーが頭突きで叩くと、スロット演出 → キノコ/ファイアフラワー/1UP/コイン/スターのどれかが出る。

### 7.5 土管 (地下サブステージへの入口)

```python
t.append(_c(R, A,A,A,A,A,A,A, PT, PB, A, G, G))   # col X: 土管左半分
t.append(_c(R, A,A,A,A,A,A,A, PR, PD, A, G, G))   # col X+1: 土管右半分
# ステージdictに:
'pipe_col': X,
'pipe_return_col': X+10,   # 出てくる列
```

### 7.6 スパイク・ダクト(BIG/FIRE強制しゃがみ通路)

```python
# 天井1タイルすき間の通路: BIG/FIRE は SW2-hold で潜る必要がある
t.append(_c(R, A,A,A,A,A,A,A,A,A,S,G,G))   # row 9 にスパイク
t.append(_c(R, A,A,A,A,A,A,A,A,A,S,G,G))
```

### 7.7 ゴール旗

```python
t.append(_c(R, A,A,A,A, FL,FL,FL,FL,FL,FL, G, G))   # col X: 旗ポール
# ステージdictに:
'goal_col': X,
'flag_col': X,    # 旗滑り降り演出を出す
```

### 7.8 マグマ間欠ジャンプ (S5系)

```python
# 1コル幅マグマと1コル幅地面を交互
for i in range(N):
    if i % 2 == 0:
        t.append(_c(R, A,A,A,A,A,A,A,A,A,A, MA, MA))   # マグマ
    else:
        t.append(_c(R, A,A,A,A,A,A,A,A,A,A, G, G))     # 地面
```

---

## 8. ステージ末尾の処理

`terrain` の長さは `width` と一致させる必要がある。
慣例として最後にパディング:

```python
while len(t) < 128: t += _flat(R, 1)   # widthに揃える
t = t[:128]
```

---

## 9. 完全なステージ定義の最小例

```python
def _stage_simple():
    R = 12
    t = []
    # 平地 → 穴 → 浮島 → 旗
    t += _flat(R, 8)
    t += _hole(R, 2)
    t += _flat(R, 4)
    t.append(_c(R, A,A,A,A,A,A,A,A,G,A,A,A))   # 浮島row8
    t.append(_c(R, A,A,A,A,A,A,C,A,G,A,A,A))
    t.append(_c(R, A,A,A,A,A,A,A,A,G,A,A,A))
    t += _flat(R, 5)
    t.append(_c(R, A,A,A,A, FL,FL,FL,FL,FL,FL, G, G))
    while len(t) < 48: t += _flat(R, 1)
    t = t[:48]
    return {
        'name': 'SIMPLE 1', 'bgm': 'overworld',
        'width': 48, 'rows': R, 'time_limit': 60,
        'terrain': t, 'water': False, 'gravity_scale': 1.0,
        'start_col': 2, 'start_row': R-4,
        'goal_col': 41, 'flag_col': 41,
        'objects': [(12, R-3, 'goomba'), (20, R-3, 'goomba')],
        'enemy_sets': {},
    }
```

---

## 10. カスタムモードへのステージ追加

### 方法A: Python直接編集

`custom_stages.py` の `_stage_example()` の下に新しい関数 `_stage_my_1()` を追加し、
`load_custom_stages()` の `stages=[_stage_example()]` を `stages=[_stage_example(), _stage_my_1()]` に変える。

### 方法B: JSON (custom.dat) を配置

Pico のルートディレクトリに `custom.dat` を置く。Next.js エディタで生成可能。

#### custom.dat フォーマット

```json
{
  "stages": [
    {
      "name": "MY STAGE 1",
      "bgm": "overworld",
      "rows": 12,
      "width": 64,
      "time_limit": 100,
      "terrain": [
        "00000000000BB",
        "0000000000BB",
        ...
      ],
      "water": false,
      "gravity_scale": 1.0,
      "start_col": 2,
      "start_row": 8,
      "goal_col": 60,
      "flag_col": 60,
      "pipe_col": -1,
      "pipe_return_col": 0,
      "objects": [[6, 6, "qblock_random"], [15, 9, "goomba"]],
      "enemy_sets": {}
    }
  ]
}
```

#### terrain 列の文字列表現

各文字列が **1列のタイル列**。1文字 = 1タイルID (16進0-F):

```
'0' = AIR        '4' = PIPE_TL    '8' = COIN       'C' = QUSED
'1' = GROUND     '5' = PIPE_TR    '9' = SPIKE      'D' = MAGMA
'2' = BRICK      '6' = PIPE_BL    'A' = GOAL       'E' = GRASS
'3' = QBLOCK     '7' = PIPE_BR    'B' = CLOUD_PLAT 'F' = FLAG
```

文字列が `rows` より短いと、不足分は**先頭にAIR**が補われる(`_c()`と同じ規約)。

例(R=12の地面のみの列):
```
"0000000000011"  →  ❌ 13文字すぎる
"00000000000011" →  ❌ 14文字すぎる
"000000000011"   →  ✅ 12文字、上10行AIR + 下2行GROUND
"11"             →  ✅ 短縮: 上10行AIR(自動補完) + 下2行GROUND
```

---

## 11. AI への指示例 (ユーザー → Claude)

このドキュメントを参照して、自然言語で発注可能:

> 「64列のステージ作って。最初平地10列、穴3つ(各2幅)あり、中盤に高所row5の浮島3つ、各浮島の上にコイン1枚、終盤に階段3段→旗ゴール。難易度ノーマルで途中にクリボー4体、易しいでは2体にしてください。BGMはoverworld」

Claude は本ドキュメントに従って `custom_stages.py` 内に関数を追加し、テストモードで動作確認後にコミット。

---

## 12. デバッグ・検証 Tips

| 症状 | 原因 | 対処 |
|---|---|---|
| プレイヤーが地面にめり込む | `start_row` 設定ミス | 地面の行から `-3` (SMALL) or `-4` (BIG) 引いた値 |
| 「届くはず」のジャンプが届かない | 速度不足 / ギャップ過大 | §2.3 参照、SW3ダッシュ前提なら4タイル超は要注意 |
| ?ブロックを叩いても何も出ない | `objects` に `qblock_random` 未登録 | `terrain` のQの座標と一致させる |
| ステージが画面下に伸びすぎる | `rows` 増やすと縦スクロールが必要 | R=12→16 にすると camera_y 連動 |
| `IndexError` で起動失敗 | `terrain` の長さ ≠ `width` | パディング行を確認 |

---

## 13. 既存ステージの参考

`stages_new.py` の `_build_s1()` 〜 `_build_s6()` を読むと、本ガイドのパターンが実際にどう組み合わされているか分かる。
各セクション(A/B/C/...)単位でコメントが付いているので、似たステージを作りたい時のテンプレートとして使える。

---

## 14. カスタムブロックの追加

カスタムモードでは **タイルID 16〜255** に独自ブロックを定義できる。
組み込み例は `custom_stages.py` の `BUILTIN_BLOCKS` を参照。

### 14.1 ブロック定義の構造

```python
{
    'id':       16,            # 16-255 (16-31 は組み込みが予約)
    'name':     'tile_ice',    # SpriteBank への登録キー (一意)
    'behavior': 'solid',       # 'solid'|'platform'|'lethal'|'passable'
    'sprite':   bytes([0xFF, 0x81, 0xBD, 0xA5, 0xA5, 0xBD, 0x81, 0xFF]),
}
```

#### behavior の意味

| 値 | 動作 |
|---|---|
| `solid` | 4方向すべて衝突。プレイヤー/敵に対して床・壁・天井になる |
| `platform` | 上方からのみ着地可。下から通過可能 (CLOUD_PLAT 同等) |
| `lethal` | 接触するとプレイヤー死亡 (SPIKE/MAGMA 同等) |
| `bounce` | platform 兼バネ。上に着地すると `vy=-5.2` で大ジャンプ自動発動 + bounce SFX |
| `ice` | solid 兼氷上判定。しゃがみ中も減速せずフル速度でスライド |
| `passable` | 当たり判定なし。装飾のみ (BG 飾り用) |

#### sprite (ビットマップ)

`8バイト = 8x8 1ビットスプライト`。**MONO_VLSB** 形式:
- 1バイト = 縦8ピクセル
- LSB(最下位ビット) = 一番上のピクセル
- 8バイト並ぶ = 左→右の8列

##### 描き方の例: 「□」型の枠線ブロック

```
列0(左) ─ 0xFF (8px全部点灯)
列1    ─ 0x81 (上下端のみ点灯)
列2-5  ─ 0x81 〜 模様
列6    ─ 0x81
列7(右) ─ 0xFF
```

便利な変換: 1列の点灯パターンを2進数で下から上に並べて hex 化:
```
上 0
   1     0b01000000 = 0x40   → ... こうやって計算する
   0
   0
   0
   0
   0
下 0
```

→ 横8列分のhex列をbytes()に渡す。

### 14.2 組み込みカスタムブロックの一覧

`custom_stages.py` に定義済み (CUSTOM モード入場時に自動登録):

| ID | 定数 | name | behavior | 用途 |
|---|---|---|---|---|
| 16 | `ICE` | `tile_ice` | solid | 氷のブロック |
| 17 | `SAND` | `tile_sand` | solid | 砂ブロック |
| 18 | `BOUNCE` | `tile_bounce` | platform | 跳ねる雲足場 |
| 19 | `THORN` | `tile_thorn` | lethal | 横向きトゲ |
| 20 | `DARK_GR` | `tile_dark_gr` | solid | 暗い地面 (夜面用) |

カスタムステージから参照する例:

```python
from custom_stages import ICE, SAND  # 定数として import
t.append(_c(R, A,A,A,A,A,A,A,A,A,A, ICE, ICE))   # 氷の地面
```

### 14.3 JSON (custom.dat) でブロックを定義

```json
{
  "blocks": [
    {
      "id": 32,
      "name": "tile_lava_brick",
      "behavior": "lethal",
      "sprite": "DEADBEEFCAFE1234"
    }
  ],
  ...
}
```

`sprite` は **16文字の16進文字列** (= 8バイト)。bytes.fromhex() でデコードされる。

---

## 15. カスタム BGM の追加

カスタムモードでは独自BGMを定義し、`bgm: 'my_track'` でステージに割り当てられる。

### 15.1 トラック定義

各音符は `[音名 or 周波数, 長さms]` の2要素タプル/リスト。音名は `music.NOTES` 参照:

```
C3-G6 範囲。シャープは末尾 's': 'C4s', 'F5s' など。
'-' は休符。
```

```python
BUILTIN_BGM = {
    'my_track': [
        ['C5', 200], ['E5', 200], ['G5', 400],
        ['-',  100],
        ['F5', 200], ['D5', 200], ['B4', 400],
        [880,  150],   # 数値指定 = 直接Hz
        ['-',  300],
    ],
}
```

### 15.2 組み込みカスタムBGM

| 名前 | 雰囲気 |
|---|---|
| `ice_field` | 高音中心の煌めいたキラキラ曲 |
| `desert` | 砂漠風の不思議スケール |

### 15.3 JSON で BGM を定義

```json
{
  "bgm": {
    "midnight": [
      ["C4", 300], ["E4", 300], ["G4", 600],
      ["-", 200],
      ["B3", 300], ["D4", 300], ["F4", 600]
    ]
  },
  "stages": [
    { "name": "NIGHT 1", "bgm": "midnight", ... }
  ]
}
```

### 15.4 設計のコツ

- **テンポ**: 1拍200ms ≒ BPM 75 が標準。アクション速め=120ms、ホラー=300ms。
- **音域**: PWM 1ch 制約のため和音不可。**メロディラインを高低交互** にすると厚みを擬似的に出せる。
- **ループ**: 末尾に `['-', 200]` を入れて区切りを作る。
- **構造**: A 部 → B 部 → A 部の3部構成を意識すると単調にならない。

---

## 16. AI 発注の応用例

ブロック・BGMも含めた発注例:

> 「**雪原ステージ**を作って。タイルは ICE と DARK_GR を使う。最初に氷の平地8列、中央に跳ねる足場 (BOUNCE) を3つ並べて高所のコインを取らせる、終盤に DARK_GR で暗いゾーン。BGMは ice_field、難易度ノーマルでクリボー3体、ハードでパタパタ追加。」

> 「**夜の墓場** ステージ用に、新ブロック ID 32 を `behavior: lethal` の墓石として定義(スプライトは上が三角、下が四角の typical 墓石)。BGMは新規 `night_grave` で C3 中心の低音ドローン20秒分。地下風に12列の墓石地帯を作って、最後に旗ゴール」

これらは MAP_GUIDE.md に沿った仕様なら Claude が `custom_stages.py` に忠実実装可能。
