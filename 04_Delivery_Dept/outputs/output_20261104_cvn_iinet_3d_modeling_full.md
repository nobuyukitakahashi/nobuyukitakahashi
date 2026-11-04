# 最終納品パッケージ：株式会社CVN 公式キャラクター「いい-NETくん（LILI-net）」3Dモデリング＆レンダリング制作（Rev.2 改修完了版）

- **納品日**: 2026年11月04日（Rev.2 改修版）
- **格納場所**: `04_Delivery_Dept/outputs/`
- **法務・コンプライアンス審査**: `SKIPPED（通常案件・自社公式キャラクター3D制作）`
- **同梱・変換ファイル一覧**:
  - **マスターパッケージ（本書・Rev.2）**: [`output_20261104_cvn_iinet_3d_modeling_full.md`](output_20261104_cvn_iinet_3d_modeling_full.md)
  - **斜め3/4 ヒーローレンダリング（1400×1680 px・Rev.2）**: [`output_20261104_cvn_iinet_hero_3quarter.png`](output_20261104_cvn_iinet_hero_3quarter.png)（別名コピー: [`iinet_kun_hero_3quarter.png`](iinet_kun_hero_3quarter.png)）
  - **正面・側面・斜め・背面 4面比較ボード（3320×1008 px・Rev.2）**: [`output_20261104_cvn_iinet_front_and_side.png`](output_20261104_cvn_iinet_front_and_side.png)（別名コピー: [`iinet_kun_front_and_side.png`](iinet_kun_front_and_side.png)）
  - **全6アングル統合シート（5面図＋斜め / 2496×1992 px・Rev.2）**: [`output_20261104_cvn_iinet_5views_sheet.png`](output_20261104_cvn_iinet_5views_sheet.png)（別名コピー: [`iinet_kun_5views_sheet.png`](iinet_kun_5views_sheet.png)）
  - **Blender 5.2 マスターファイル（全11メッシュパーツ・リグ・完全無反射マットマテリアル設定済・Rev.2）**: [`output_20261104_cvn_iinet_kun.blend`](output_20261104_cvn_iinet_kun.blend)
  - **Web / AR / 汎用3Dエンジン用 glTF 2.0 Binary（11パーツ＋アーマチュア同梱・Rev.2）**: [`output_20261104_cvn_iinet_kun.glb`](output_20261104_cvn_iinet_kun.glb)

---

## エグゼクティブサマリー（Rev.2 全7項目改修・質感・ボーン構成・プレビュー）

### 1. レンダリング画像プレビュー一覧（Rev.2 改修完了版）

#### (1) 斜め3/4 ヒーローカット（広告チラシ・メインビジュアル用）
- ファイル: [`output_20261104_cvn_iinet_hero_3quarter.png`](output_20261104_cvn_iinet_hero_3quarter.png) / [`iinet_kun_hero_3quarter.png`](iinet_kun_hero_3quarter.png)
![斜め3/4 ヒーローカット（Rev.2）](output_20261104_cvn_iinet_hero_3quarter.png)

#### (2) 正面・左側面・斜め3/4・背面 4面比較ボード
- ファイル: [`output_20261104_cvn_iinet_front_and_side.png`](output_20261104_cvn_iinet_front_and_side.png) / [`iinet_kun_front_and_side.png`](iinet_kun_front_and_side.png)
![正面・側面・斜め・背面 4面比較ボード（Rev.2）](output_20261104_cvn_iinet_front_and_side.png)

#### (3) 全6アングル統合シート（正面・左側面・背面・上面・底面・斜め3/4）
- ファイル: [`output_20261104_cvn_iinet_5views_sheet.png`](output_20261104_cvn_iinet_5views_sheet.png) / [`iinet_kun_5views_sheet.png`](iinet_kun_5views_sheet.png)
![全6アングル統合シート（Rev.2）](output_20261104_cvn_iinet_5views_sheet.png)

---

### 2. Rev.2 ユーザー改修要件（全7項目）および5面図整合アプローチ一覧

| 項目 | Rev.2 改修要件・課題 | 3Dモデリング・マテリアルにおける実装仕様 |
| :--- | :--- | :--- |
| **① 足の延長・全方向から「足らしい」可愛い2本脚造形** | 従来モデルでは胴体下部が卵型のまま接地していたため、特に側面視で足の独立感が見えにくかった。 | 胴体下部（お腹・股下・お尻）を $Z \approx +0.185\text{ m}$ でぷっくり丸く収め、そこから左右2本の独立したマスコット脚（中心 $|X| \approx 0.278\text{ m}$）を接地底面 $Z = -0.275\text{ m}$ まで下方へしっかり延長（脚長約 $0.46\text{ m}$）。**太もも ➔ 足首のくびれ ➔ 前にぷっくり出た丸い足先（つま先・足の甲・かかと、前方 $-Y$ へ $+0.105\text{ m}$ 突出）** を付与し、正面・背面・側面・底面・斜めの全アングルで可愛い2本脚として自立する造形を実現。 |
| **② 完全無反射マット（つや消し）質感への統一** | 表面の光沢・テカリを抑え、落ち着いた完全マット（つや消し）質感にする。 | 全マテリアルの Principled BSDF において `Roughness = 1.0`, `Specular IOR Level = 0.0`, `Coat Weight = 0.0`, `Metallic = 0.0`, `Subsurface Weight = 0.0` を徹底設定。白い鏡面ハイライト・テカリを100%排除し、微量の自己発光（`Emission Strength = 0.16..0.28`）と柔らかなマット拡散陰影のみで上品なつや消し質感を構築。 |
| **③ TV画面モチーフの青枠（`Face_Frame`）＆画面（`Face_Screen`）のサイズ縮小と立体化** | TV画面の青枠をひと回り小さくし、さらに立体的なベゼルにする。 | 顔中心を $Z_c = 1.216\text{ m}$ へ微調整し、TV青枠および画面の外径サイズを従来の **`0.84倍`（84%）に縮小**（頭頂・左右頬・胸元にピンクのボディ余白がしっかり見えるバランス）。さらに青枠の法線方向張り出し厚みを従来の $+0.022\text{ m}$ から **`+0.056\text{ m}`（約2.5倍の立体ベゼル厚）** へ大幅強化。 |
| **④ 青枠（`Face_Frame`）の枠幅スリム化** | 青枠自体の太さを細めにする。 | 全体の `0.84倍` 縮小に加え、枠自体の太さ（$r_{\text{out}} - r_{\text{in}}$）をさらに **`0.74倍`（約26%細め）** にスリム化。青枠が重たくならず、内側のクリーム色のTV画面が広くスッキリと見えるデザインに改善。 |
| **⑤ 目（`Eye.L` / `Eye.R`）のサイズ拡大＆ぷっくり立体化** | 目をもう少し大きくし、かつ立体的にする。 | 目の半径を従来の $0.0625\text{ m}$ から **`0.080\text{ m}`（約1.28倍のパッチリ大きな丸目）** に拡大（左右間隔 $X = \pm 0.268\text{ m}, Z = 1.265\text{ m}$）。画面表面からの法線方向ドーム厚みを従来の $0.012\text{ m}$ から **`0.035\text{ m}`（約2.9倍のぷっくりドーム立体）** に増強し、口（`Mouth`）も $+0.022\text{ m}$ の立体チューブとして造形。 |
| **⑥ 尻尾（`Antenna`）とお尻（ボディ背面下部）の完全密着接続** | 尻尾がボディから浮いて見えないよう、ちゃんとお尻から生えているように繋げる。 | 尻尾（青いS字パイプ）の始点をボディ背面下部（$Z = 0.490\text{ m}$）のボディ内部深く（$Y = 0.350\text{ m}$）に設定し、お尻の表面（$Y \approx 0.70\text{ m}$）を貫通する20点の密な制御点列を追加した上でガウシアンスムージング後の始点を固定。全アングルで隙間が一切ない完全貫通接合を実現。 |
| **⑦ 胸元ロゴ「いい-net（`LILI-net`）」の3D立体メッシュ化（`Logo_LILI_net`）** | 胸元の「いい-net（`LILI-net`）」文字を平面テクスチャではなく立体（3Dメッシュ）にする。 | 平面UVテクスチャ貼付を廃止し、胸元の `LILI-net` ロゴを独立した高精細3D立体メッシュ（`Logo_LILI_net`）として新設。2Dガウシアンスムージング＋12反復Taubin境界スムージングで滑らかな文字輪郭へ変換し、ボディ前面曲面の法線方向へ **`+0.023\text{ m}` ぷっくりと立体押し出し**（前面：`Mat_Logo_Yellow`、側面ウォール：`Mat_Logo_Side`）。 |

---

### 3. アニメーション用アーマチュア（`IINet_Armature`）ボーン構成（全11メッシュパーツ対応）

広告ビジュアルのポーズ付けおよび3Dアニメーション制作にそのまま使用できる階層構造ボーン（計9本）を構築し、Rev.2で新設された立体ロゴ（`Logo_LILI_net`）および延長された2本脚を含む全11メッシュをスキニングバインド済み。

```text
IINet_Armature
└── Root (0, 0, -0.245) -> (0, 0, 0.18)
    └── Body (0, 0, 0.18) -> (0, 0, 1.90)
        │   [追従メッシュ: Body, Face_Screen, Face_Frame, Eye.L, Eye.R, Mouth, Logo_LILI_net]
        ├── Leg.L (+0.275, -0.02, 0.18) -> (+0.270, -0.05, -0.245)  [延長された左脚・足首・丸い足先制御]
        ├── Leg.R (-0.275, -0.02, 0.18) -> (-0.270, -0.05, -0.245)  [延長された右脚・足首・丸い足先制御]
        ├── Arm.L (+0.72, 0, 0.68)      -> (+0.96, 0, 0.32)         [左アーム パタパタ・曲げ制御]
        ├── Arm.R (-0.72, 0, 0.68)      -> (-0.96, 0, 0.32)         [右アーム パタパタ・曲げ制御]
        └── Antenna_1 -> Antenna_2 -> Antenna_3 -> Globe            [お尻貫通S字尻尾＆頭上地球儀の揺れ制御]
```

---

## Part 1. 完成コンテンツ本編（3Dモデリング＆レンダリング制作仕様書 Rev.2）

- **制作年月**: 2026年11月
- **制作担当**: Creative部門（`02_Creative_Dept`）
- **使用環境**: Blender 5.2.3 LTS（Python API `bpy` / `bmesh` による完全プロシージャル構築）

### 1. 成果物ファイル一覧

#### (1) 最終納品ファイル（`04_Delivery_Dept/outputs/` 格納済）
| 種別 | 納品ファイルパス | 仕様・解像度 |
| :--- | :--- | :--- |
| **Blenderマスターファイル** | [`04_Delivery_Dept/outputs/output_20261104_cvn_iinet_kun.blend`](output_20261104_cvn_iinet_kun.blend) | Blender 5.2形式（全11メッシュパーツ＋リグ＋完全無反射マットマテリアル設定済） |
| **Web / AR用 3Dモデル** | [`04_Delivery_Dept/outputs/output_20261104_cvn_iinet_kun.glb`](output_20261104_cvn_iinet_kun.glb) | glTF 2.0 Binary形式（11パーツ＋アーマチュア同梱） |
| **斜め3/4 ヒーローレンダリング** | [`04_Delivery_Dept/outputs/output_20261104_cvn_iinet_hero_3quarter.png`](output_20261104_cvn_iinet_hero_3quarter.png)<br>（同内容コピー: [`iinet_kun_hero_3quarter.png`](iinet_kun_hero_3quarter.png)） | `1400 × 1680 px`（透過合成スタジオカード背景・接地シャドウ付） |
| **正面・側面・斜め・背面 4面比較ボード** | [`04_Delivery_Dept/outputs/output_20261104_cvn_iinet_front_and_side.png`](output_20261104_cvn_iinet_front_and_side.png)<br>（同内容コピー: [`iinet_kun_front_and_side.png`](iinet_kun_front_and_side.png)） | `3320 × 1008 px`（4パネル並列高解像度ボード） |
| **全6アングル統合シート（5面図＋斜め）** | [`04_Delivery_Dept/outputs/output_20261104_cvn_iinet_5views_sheet.png`](output_20261104_cvn_iinet_5views_sheet.png)<br>（同内容コピー: [`iinet_kun_5views_sheet.png`](iinet_kun_5views_sheet.png)） | `2496 × 1992 px`（正面・側面・背面・上面・底面・斜め3/4） |

#### (2) 構築スクリプト・中間アセット（`02_Creative_Dept/drafts/`）
| 種別 | ファイルパス | 内容 |
| :--- | :--- | :--- |
| **3D一括構築Pythonスクリプト** | `02_Creative_Dept/drafts/build_iinet_kun.py` | 5面図輪郭LUT抽出・Rev.2全7項目3Dメッシュ生成・リギング・マット質感・レンダリング自動化 |
| **モデリング設計ドラフト** | `02_Creative_Dept/drafts/draft_cvn_iinet_3d_modeling.md` | 座標変換定義・Rev.2改修設計メモ |
| **地球儀球面テクスチャ** | `02_Creative_Dept/drafts/globe_texture.png` | `1024 × 512 px` 正距円筒図法（Equirectangular）地球儀テクスチャ |

### 2. Rev.2 ユーザー改修要件（全7項目）の実装仕様詳細

#### ① 足の延長・全方向から「足らしい」可愛い2本脚造形（`Body` 下部 `Leg.L` / `Leg.R`）
- 従来の5面図準拠モデルでは胴体下部が卵型のまま接地していたため、側面視で足の独立感が見えにくい構造であった。
- Rev.2では胴体下部（お腹・股下・お尻）を $Z \approx +0.185\text{ m}$ でぷっくり丸く収め、そこから左右2本の独立したマスコット脚（中心 $|X| \approx 0.278\text{ m}$）を接地底面 $Z = -0.275\text{ m}$ まで下方へしっかり延長（脚長約 $0.46\text{ m}$）。
- **太もも ➔ 足首のくびれ ➔ 前にぷっくり出た丸い足先（つま先・足の甲・かかと）** の断面・垂直プロファイルを付与し、前方（$-Y$ 方向）へつま先を $+0.105\text{ m}$ 張り出させることで、正面・背面・側面・底面・斜め3/4のどの角度から見ても「ちゃんとした可愛い2本の足」に見える造形を実現した。

#### ② 完全無反射マット（つや消し）質感への統一
- 全マテリアルの Principled BSDF において `Roughness = 1.0`, `Specular IOR Level = 0.0`, `Coat Weight = 0.0`, `Metallic = 0.0`, `Subsurface Weight = 0.0` を徹底設定。
- 白い鏡面ハイライト・テカリを100%排除し、アニメ調の発色を支える微量の自己発光（`Emission Strength = 0.16..0.28`）と柔らかなマット拡散陰影のみで落ち着いた上品なつや消し質感を構築した。

#### ③ TV画面モチーフの青枠（`Face_Frame`）＆画面（`Face_Screen`）のサイズ縮小と立体化
- 顔中心を $Z_c = 1.216\text{ m}$ へ微調整した上で、TV青枠および画面の外径サイズを従来の **`0.84倍`（84%）に縮小**。頭頂部・左右頬・胸元にピンク色のボディの丸い余白がしっかり見える愛らしいバランスに改善した。
- さらに青枠（`Face_Frame`）の法線方向への張り出し厚みを従来の $+0.022\text{ m}$ から **`+0.056\text{ m}`（約2.5倍の立体ベゼル厚）** へ大幅に強化し、斜め・側面・上面・底面からTVモニターフレームの立体感が際立つ造形とした。

#### ④ 青枠（`Face_Frame`）の枠幅スリム化
- 全体の `0.84倍` 縮小に加え、枠自体の太さ（$r_{\text{out}} - r_{\text{in}}$）をさらに **`0.74倍`（約26%細め）** にスリム化。青枠が重たくならず、内側のクリーム色のTV画面が広くスッキリと見えるデザインに仕上げた。

#### ⑤ 目（`Eye.L` / `Eye.R`）のサイズ拡大＆ぷっくり立体化（＋口 `Mouth` の立体化）
- 目の半径を従来の $0.0625\text{ m}$ から **`0.080\text{ m}`（約1.28倍のパッチリ大きな丸目）** に拡大し、左右間隔 $X = \pm 0.268\text{ m}, Z = 1.265\text{ m}$ に配置。
- 画面表面からの法線方向ドーム厚みを従来の $0.012\text{ m}$ から **`0.035\text{ m}`（約2.9倍のぷっくりしたボタン／ドーム状立体）** に増強し、口（`Mouth`）も $+0.022\text{ m}$ の立体チューブとして造形した。

#### ⑥ 尻尾（`Antenna`）とお尻（ボディ背面下部）の完全密着接続
- 尻尾（青いS字パイプ）の始点をボディ背面下部（$Z = 0.490\text{ m}$）のボディ内部深く（$Y = 0.350\text{ m}$）に設定し、お尻の表面（$Y \approx 0.70\text{ m}$）を貫通する20点の密な制御点列を追加した上でガウシアンスムージング後の始点を固定。
- 側面・背面・上面・底面・斜めの全アングルにおいて、隙間が一切なく「ちゃんとお尻から生えている」自然な接合を実現した。

#### ⑦ 胸元ロゴ「いい-net（`LILI-net`）」の3D立体メッシュ化（`Logo_LILI_net`）
- 従来の平面UVテクスチャ貼付を廃止し、ボディ本体（`Body`）は純粋なマットピンク単色とした上で、胸元の `LILI-net` ロゴを独立した高精細3D立体メッシュ（`Logo_LILI_net`）として造形。
- `05_front.png` の胸元ロゴ領域を2Dガウシアンスムージング＋12反復Taubin境界スムージングにより滑らかな文字輪郭へ変換し、ボディ前面曲面 $Y_{\text{body}}(X, Z)$ の法線方向へ **`+0.023\text{ m}` ぷっくりと立体的に押し出し**。前面には鮮やかなマットイエロー（`Mat_Logo_Yellow`）、立体側面ウォールには温かみのあるマットゴールド（`Mat_Logo_Side`）を割り当て、どの角度から見ても立体エンブレムとして視認できる造形とした。

### 3. 視覚監査（Visual Audit）結果

再生成された3種のレンダリング画像（`output_20261104_cvn_iinet_hero_3quarter.png`, `output_20261104_cvn_iinet_front_and_side.png`, `output_20261104_cvn_iinet_5views_sheet.png`）を目視監査し、Rev.2の全7項目が最高品質で達成されていることを確認した。

1. **足の造形（正面・側面・背面・底面・斜め3/4）**: 正面・背面では足首のくびれとぷっくり丸い足先を持つ可愛い2本脚として自立し、側面では丸いお腹・お尻の下から前方にぷっくり張り出した可愛い足先（つま先・足の甲）が接地シャドウ上にしっかり立つ造形となっている。
2. **完全無反射マット質感**: 全パーツから白いテカリ・鏡面反射が100%消去され、しっとりとした上品なつや消し質感と柔らかな立体陰影に統一されている。
3. **TV青枠・画面・目・口**: ひと回り小さくなったTV画面の周囲にピンクのボディ余白が可愛く見え、スリム化された青枠（`+0.056 m`）と大きくなった丸目（半径 `0.080 m`、厚み `+0.035 m`）が側面・斜めビューでもぷっくり立体的に浮かび上がっている。
4. **尻尾の接合部**: 側面・背面・上面・底面の全ビューでお尻の表面に隙間なく完全に繋がっている。
5. **胸元 `LILI-net` 3Dロゴ**: 胸元曲面に沿って1文字ずつ立体的に盛り上がり、正面・側面・底面・斜め3/4のすべてでエッジの滑らかな3D立体文字として表現されている。

---

## Part 2. 設計要件＆参照5面図仕様サマリー（`01_Research_Dept/inputs/task_20261104_cvn_iinet_3d_modeling.md` 準拠）

- **対象キャラクター**: 株式会社CVN キャラクター「いい-NETくん」（胸ロゴ：`LILI-net` ※「いい」を `LI` `LI` で表現したデザイン）
- **用途**: 広告チラシ用ビジュアル、およびアニメーション用3Dモデル
- **質感・トーン（Rev.2）**: アニメ調の発色を活かした完全無反射マット（つや消し）質感
- **参照5面図アセット**:
  - `02_Creative_Dept/drafts/ref_images/05_front.png`（正面図）
  - `02_Creative_Dept/drafts/ref_images/03_side.png`（左側面図）
  - `02_Creative_Dept/drafts/ref_images/01_back.png`（背面図）
  - `02_Creative_Dept/drafts/ref_images/04_top.png`（上面図）
  - `02_Creative_Dept/drafts/ref_images/02_bottom.png`（底面図）
