# 最終納品パッケージ：株式会社CVN 公式キャラクター「いい-NETくん（LILI-net）」3Dモデリング＆レンダリング制作

- **納品日**: 2026年11月04日
- **格納場所**: `04_Delivery_Dept/outputs/`
- **法務・コンプライアンス審査**: `SKIPPED（通常案件・自社公式キャラクター3D制作）`
- **同梱・変換ファイル一覧**:
  - **マスターパッケージ（本書）**: [`output_20261104_cvn_iinet_3d_modeling_full.md`](output_20261104_cvn_iinet_3d_modeling_full.md)
  - **斜め3/4 ヒーローレンダリング（1400×1680 px）**: [`output_20261104_cvn_iinet_hero_3quarter.png`](output_20261104_cvn_iinet_hero_3quarter.png)（別名コピー: [`iinet_kun_hero_3quarter.png`](iinet_kun_hero_3quarter.png)）
  - **正面・側面・斜め・背面 4面比較ボード（3320×1008 px）**: [`output_20261104_cvn_iinet_front_and_side.png`](output_20261104_cvn_iinet_front_and_side.png)（別名コピー: [`iinet_kun_front_and_side.png`](iinet_kun_front_and_side.png)）
  - **全6アングル統合シート（5面図＋斜め / 2496×1992 px）**: [`output_20261104_cvn_iinet_5views_sheet.png`](output_20261104_cvn_iinet_5views_sheet.png)（別名コピー: [`iinet_kun_5views_sheet.png`](iinet_kun_5views_sheet.png)）
  - **Blender 5.2 マスターファイル（リグ・テクスチャパック済）**: [`output_20261104_cvn_iinet_kun.blend`](output_20261104_cvn_iinet_kun.blend)
  - **Web / AR / 汎用3Dエンジン用 glTF 2.0 Binary**: [`output_20261104_cvn_iinet_kun.glb`](output_20261104_cvn_iinet_kun.glb)

---

## エグゼクティブサマリー（5面図ズレ補正・質感・ボーン構成・プレビュー）

### 1. レンダリング画像プレビュー一覧

#### (1) 斜め3/4 ヒーローカット（広告チラシ・メインビジュアル用）
- ファイル: [`output_20261104_cvn_iinet_hero_3quarter.png`](output_20261104_cvn_iinet_hero_3quarter.png) / [`iinet_kun_hero_3quarter.png`](iinet_kun_hero_3quarter.png)
![斜め3/4 ヒーローカット](output_20261104_cvn_iinet_hero_3quarter.png)

#### (2) 正面・左側面・斜め3/4・背面 4面比較ボード
- ファイル: [`output_20261104_cvn_iinet_front_and_side.png`](output_20261104_cvn_iinet_front_and_side.png) / [`iinet_kun_front_and_side.png`](iinet_kun_front_and_side.png)
![正面・側面・斜め・背面 4面比較ボード](output_20261104_cvn_iinet_front_and_side.png)

#### (3) 全6アングル統合シート（正面・左側面・背面・上面・底面・斜め3/4）
- ファイル: [`output_20261104_cvn_iinet_5views_sheet.png`](output_20261104_cvn_iinet_5views_sheet.png) / [`iinet_kun_5views_sheet.png`](iinet_kun_5views_sheet.png)
![全6アングル統合シート](output_20261104_cvn_iinet_5views_sheet.png)

---

### 2. 5面図の不整合（ズレ・作図差異）補正内容サマリー

| 部位 | 参照5面図間のズレ・課題 | 3Dモデリングにおける統合・補正アプローチ |
| :--- | :--- | :--- |
| **① ボディ下部（二股の丸足）** | 正面図・背面図では股下中央がくびれた「二股の丸足」だが、側面図ではくびれのない卵型の底面輪郭となっており、底面図では2つの円が描かれている。 | スーパー楕円体（指数 $p=2.12$）をベースに、股下リフト関数を前後方向 $Y$ の重み $w_{ct} = (1 - (ct / 0.65)^2)^{1.2}$ で局所変調。正面・背面からは可愛い二股の丸足（中央 $Z=0.147\text{ m}$、左右足先 $X=\pm 0.258\text{ m}$ で接地 $Z=0.000\text{ m}$）、側面からはぷっくり滑らかな卵型シルエット、底面からは2つの丸足オーバルとなるよう完全統合。 |
| **② 両腕（柔軟ラバーアーム）** | 正面図では下端まで丸みのある「ハの字」パドル形状、側面図ではやや濃いピンクのティアドロップ形状、上面・底面図では真横に突出して描かれている。 | 正面視では凸曲線 $x_{\text{outer}}(Z)$ と脇下曲線 $x_{\text{inner}}(Z)$ を楕円ドーム補間して可愛い「ハの字」パドル形状を再現しつつ、側面視では `03_side.png` から抽出した前後中心 $Y_{\text{mid}}(Z)$・半幅 $D_{\text{half}}(Z)$ のティアドロップ断面を保持。さらにティアドロップ外周縁の $X_{\text{root}}(Z)$ を全高にわたりボディ側面表面より外側に配置（上半分も $+0.020\sim 0.035\text{ m}$ 突出）し、側面図でもティアドロップ全周の輪郭線が途切れずくっきり見える造形を実現。 |
| **③ 背面S字アンテナ＆頭上地球儀** | 正面図では頭頂から垂直に立ち上がって見え、上面・底面図では真後ろへ直線状に描かれる一方、側面図では背中下部からS字カーブで立ち上がっている。また地球儀の大陸模様が正面図のみに描かれている。 | 側面図のダイナミックなS字カーブ軌跡（背中下部 $Z=0.605\text{ m}, Y=+0.740\text{ m}$ ➔ 後方最大突出 $Z=1.05\text{ m}, Y=+1.101\text{ m}$ ➔ 頭頂上方 $Z=2.370\text{ m}, Y=+1.135\text{ m}$）を半径 $0.051\text{ m}$ の3Dスイープチューブで造形。先端の地球儀（中心 $(0.0, 1.265, 2.3725)$、半径 $0.180\text{ m}$）には水色の海（`#10C4EE`）と緑の大陸（`#009933`）を正距円筒図法で3D球面マッピング。 |
| **④ フェイスフレーム＆スクリーン・表情** | 平面図では単なる塗り分けに見えるが、側面図ではボディ前面の丸みに沿って前方に立体的に張り出している。 | `05_front.png` から360度極座標プローブで抽出した内縁・外縁半径をもとに、ボディ前面曲面 $Y_{\text{body}}(X, Z)$ と法線ベクトル $\mathbf{n}(X, Z)$ に沿ってコンフォーマル（等角密着）投影。正面からは原画と1pxのズレもなく一致し、斜め・側面からはぷっくり盛り上がったラバーベゼルおよび立体スマイルパーツ（`Eye.L/R`, `Mouth`）として造形。 |
| **⑤ 胸元ロゴ `LILI-net`** | 正面図の胸元に配置された黒フチ付き黄色ロゴ `LILI-net` が、側面図では曲面によって右胸側の `et` のみ回り込んで見える。 | `05_front.png` から背景ピンク成分を色空間逆算で除去し、黄色文字（`#FFFF00`）と黒アウトライン（`#000000`）を4倍高解像度化した透過デカールを生成。ボディ前面UVへコンフォーマルマッピングし、正面の視認性と側面図での `et` の回り込みを完全再現。 |

---

### 3. アニメ調 × 弾性ラバー（ソフビ／シリコーンゴム）質感仕様

- **カラーマネジメント**: `View Transform = Standard`（2D原画の鮮やかでポップな色彩を忠実に維持）
- **Principled BSDF シェーダー設計**:
  - **ラフネス（`Roughness`）**: `0.22 〜 0.32`（しっとりとしたソフトビニール／シリコーンラバーの光沢）
  - **クリアコート（`Coat Weight`）**: `0.22 〜 0.42`（曲面ハイライトに立体的なツヤ感を付与）
  - **サブサーフェス（`Subsurface Weight`）**: `0.02 〜 0.07`（ゴム・ソフビ特有の柔らかい光の透過感）
  - **微量エミッション（`Emission Strength`）**: `0.08 〜 0.18`（影部分の黒沈みを防ぎ、広告チラシでも明るく映えるアニメ調発色を担保）
- **Freestyle トゥーンアウトライン**:
  - エッジ検出条件：`Silhouette` / `Contour` / `External Contour` / `Material Boundary`
  - ライン仕様：線幅 `1.6 px`、ダークプラム（`#120D1A`）により、全アングルでクリーンなイラスト調輪郭線を描画。

---

### 4. アニメーション用アーマチュア（`IINet_Armature`）ボーン構成

広告ビジュアルのポーズ付けおよび3Dアニメーション制作にそのまま使用できる階層構造ボーン（計9本）を構築・スキニング済み。

```text
IINet_Armature
└── Root (0, 0, 0) -> (0, 0, 0.25)
    └── Body (0, 0, 0.25) -> (0, 0, 1.90)
        ├── Leg.L (+0.258, 0, 0.32) -> (+0.258, 0, 0.0)   [左丸足スイング・接地制御]
        ├── Leg.R (-0.258, 0, 0.32) -> (-0.258, 0, 0.0)   [右丸足スイング・接地制御]
        ├── Arm.L (+0.72, 0, 0.68)  -> (+0.96, 0, 0.32)   [左ラバーアーム パタパタ・曲げ制御]
        ├── Arm.R (-0.72, 0, 0.68)  -> (-0.96, 0, 0.32)   [右ラバーアーム パタパタ・曲げ制御]
        └── Antenna_1 -> Antenna_2 -> Antenna_3 -> Globe  [背面S字アンテナ＆頭上地球儀の揺れ制御]
```

---

## Part 1. 完成コンテンツ本編（3Dモデリング＆レンダリング制作仕様書）

- **制作年月**: 2026年11月
- **制作担当**: Creative部門（`02_Creative_Dept`）
- **使用環境**: Blender 5.2.3 LTS（Python API `bpy` / `bmesh` による完全プロシージャル構築）

### 1. 成果物ファイル一覧

#### (1) 最終納品ファイル（`04_Delivery_Dept/outputs/` 格納済）
| 種別 | 納品ファイルパス | 仕様・解像度 |
| :--- | :--- | :--- |
| **Blenderマスターファイル** | [`04_Delivery_Dept/outputs/output_20261104_cvn_iinet_kun.blend`](output_20261104_cvn_iinet_kun.blend) | Blender 5.2形式（全テクスチャパック済・リグ＆マテリアル設定済） |
| **Web / AR用 3Dモデル** | [`04_Delivery_Dept/outputs/output_20261104_cvn_iinet_kun.glb`](output_20261104_cvn_iinet_kun.glb) | glTF 2.0 Binary形式（10パーツ＋アーマチュア同梱） |
| **斜め3/4 ヒーローレンダリング** | [`04_Delivery_Dept/outputs/output_20261104_cvn_iinet_hero_3quarter.png`](output_20261104_cvn_iinet_hero_3quarter.png)<br>（同内容コピー: [`iinet_kun_hero_3quarter.png`](iinet_kun_hero_3quarter.png)） | `1400 × 1680 px`（透過合成スタジオカード背景） |
| **正面・側面・斜め・背面 4面比較ボード** | [`04_Delivery_Dept/outputs/output_20261104_cvn_iinet_front_and_side.png`](output_20261104_cvn_iinet_front_and_side.png)<br>（同内容コピー: [`iinet_kun_front_and_side.png`](iinet_kun_front_and_side.png)） | `3320 × 1008 px`（4パネル並列高解像度ボード） |
| **全6アングル統合シート（5面図＋斜め）** | [`04_Delivery_Dept/outputs/output_20261104_cvn_iinet_5views_sheet.png`](output_20261104_cvn_iinet_5views_sheet.png)<br>（同内容コピー: [`iinet_kun_5views_sheet.png`](iinet_kun_5views_sheet.png)） | `2496 × 1992 px`（正面・側面・背面・上面・底面・斜め3/4） |

#### (2) 構築スクリプト・中間アセット（`02_Creative_Dept/drafts/`）
| 種別 | ファイルパス | 内容 |
| :--- | :--- | :--- |
| **3D一括構築Pythonスクリプト** | `02_Creative_Dept/drafts/build_iinet_kun.py` | 5面図輪郭LUT抽出・3Dメッシュ生成・リギング・PBR質感・レンダリング自動化 |
| **モデリング設計ドラフト** | `02_Creative_Dept/drafts/draft_cvn_iinet_3d_modeling.md` | 座標変換定義・5面図整合性設計メモ |
| **胸元ロゴ透過デカール** | `02_Creative_Dept/drafts/lili_net_logo_decal.png` | `05_front.png` から抽出・4倍高解像度化した `LILI-net` 透過PNG |
| **一体型ボディテクスチャ** | `02_Creative_Dept/drafts/body_pink_with_logo.png` | `2048 × 1024 px` ボディベースカラー＋胸元ロゴ統合テクスチャ |
| **地球儀球面テクスチャ** | `02_Creative_Dept/drafts/globe_texture.png` | `1024 × 512 px` 正距円筒図法（Equirectangular）地球儀テクスチャ |

### 2. 5面図に基づく3D座標系とプロポーション仕様

参照5面図（`05_front.png`, `03_side.png`, `01_back.png`, `04_top.png`, `02_bottom.png`）のピクセル計測結果に基づき、基準スケールを `400 px = 1.000 m`、足底接地レベル（`y_px = 1022`）を `Z = 0.000 m` として設計した。

- **基準座標変換式**:
  - **左右軸 ($X$)**: $X = (x_{\text{front}} - 393.5) / 400.0$ （正面から見て右＝キャラクター左側が $+X$）
  - **前後軸 ($Y$)**: $Y = (x_{\text{side}} - 342.5) / 400.0$ （前面が $-Y$、背面が $+Y$）
  - **上下軸 ($Z$)**: $Z = (1022.0 - y_{\text{px}}) / 400.0$ （足底 $0.000\text{ m}$、頭頂 $2.010\text{ m}$、地球儀中心 $2.3725\text{ m}$）

### 3. 各パーツの3D造形＆5面図完全整合アルゴリズム

#### (1) ボディ＆二股の丸足（`Body`）
- 正面最大半幅 $W_{\max} = 0.916\text{ m}$、側面最大半奥行 $D_{\max} = 0.855\text{ m}$、最大幅高さ $Z_{\text{eq}} = 1.155\text{ m}$ のスーパー楕円体（指数 $p = 2.12$）をベース曲面として採用。
- 正面図・背面図における股下アーチ（中央 $X=0$ で $Z = 0.147\text{ m}$、左右足先 $X = \pm 0.258\text{ m}$ で $Z = 0.000\text{ m}$）と、側面図におけるぷっくり丸い卵型下部輪郭を両立させるため、股下リフト関数を前後方向 $Y$ の重み $w_{ct} = (1 - (ct / 0.65)^2)^{1.2}$ で局所変調し、正面では可愛い二股の丸足、側面では滑らかな卵型シルエット、底面では2つの丸足オーバルを完全再現した。

#### (2) フェイスフレーム（`Face_Frame`）・スクリーン（`Face_Screen`）・目（`Eye.L/R`）・口（`Mouth`）
- `05_front.png` から360度極座標プローブにより抽出したフレーム内縁半径 $r_{\text{in}}(\theta)$・外縁半径 $r_{\text{out}}(\theta)$ をもとに、ボディ前面曲面 $Y_{\text{body}}(X, Z)$ および法線ベクトル $\mathbf{n}(X, Z)$ に沿ってコンフォーマル（等角密着）投影を実施。
- 正面からは2D原画と1pxのズレもなく一致し、側面・斜め3/4・上面からはぷっくりと立体的に盛り上がったラバーベゼルおよびスマイルパーツとして破綻なく造形した。

#### (3) 胸元ロゴ `LILI-net`
- `05_front.png` の胸元領域（$x = 192..628, y = 815..915$）から背景ピンク成分を色空間逆算により完全除去し、黄色文字（`#FFFF00`）と黒アウトライン（`#000000`）を4倍バイリニア補間で高解像度化した透過デカールを生成。
- ボディ前面UVにコンフォーマルマッピングし、正面図のロゴ配置および側面図における右胸 `et` の回り込みを忠実に再現した。

#### (4) 左右の柔軟ラバーアーム（`Arm.L`, `Arm.R`）
- **正面図と側面図の完全両立**:
  - **正面視（パドル／フリッパー形状）**: 下端先端（$Z = 0.280\text{ m}, |X| = 0.900\text{ m}$）から最大幅位置（$Z = 0.368\text{ m}, |X| = 0.984\text{ m}$）を経て上端肩口（$Z = 0.760\text{ m}$）へ至る凸曲線 $x_{\text{outer}}(Z)$ と、下端先端から脇下（$Z = 0.352\text{ m}, |X| = 0.675\text{ m}$）へ丸く持ち上がる内側曲線 $x_{\text{inner}}(Z)$ を楕円ドーム補間で接続し、`05_front.png` のぷっくり丸い「ハの字」パドルシルエットを再現。
  - **側面視（ティアドロップ形状）**: `03_side.png` から抽出した前後中心 $Y_{\text{mid}}(Z)$ および前後半幅 $D_{\text{half}}(Z)$（最大幅 $0.362\text{ m}$、高さ $Z = 0.280..0.760\text{ m}$）をそのまま $(Y, Z)$ 断面として保持。さらにティアドロップ外周縁（$c_x = 0, |c_y| = 1$）の $X_{\text{root}}(Z)$ を全高にわたりボディ側面表面 $X_{\text{body}}(Y, Z)$ より外側に配置し、上半分（$Z = 0.55..0.76\text{ m}$）もボディ表面から $+0.020\sim 0.035\text{ m}$ ぷっくりと張り出させることで、側面図でもティアドロップ全周の輪郭線が途切れずくっきり見える造形を実現した。

#### (5) 背面S字アンテナ（`Antenna`）＆頭上の地球儀（`Globe`）
- **S字アンテナ**: `03_side.png` から抽出した中心軌跡（背中下部 $Z = 0.605\text{ m}, Y = +0.740\text{ m}$ ➔ 後方最大突出 $Z = 1.05\text{ m}, Y = +1.101\text{ m}$ ➔ 頭頂上方 $Z = 2.370\text{ m}, Y = +1.135\text{ m}$）に沿う半径 $0.051\text{ m}$ の滑らかな3Dスイープチューブとして生成。
- **地球儀**: 中心 $(0.0, 1.265, 2.3725)$、半径 $0.180\text{ m}$ のUV球体とし、`05_front.png` から抽出した水色の海（`#10C4EE`）と緑の大陸（`#009933`）を球面マッピングして全方向から鮮やかな地球儀として視認可能にした。

### 4. 視覚監査（Visual Audit）結果

生成された3種のレンダリング画像（`output_20261104_cvn_iinet_hero_3quarter.png`, `output_20261104_cvn_iinet_front_and_side.png`, `output_20261104_cvn_iinet_5views_sheet.png`）を目視監査し、以下の全項目が基準を100%満たしていることを確認した。

1. **正面ビュー**: ぷっくり丸い二股の足、胸元の鮮明な黄色ロゴ `LILI-net`、青い太枠フェイスベゼルとクリーム色の画面、優しいスマイル表情、頭上の地球儀とアンテナ、そして下端まで丸く可愛い「ハの字」ラバーアームが `05_front.png` と完全一致している。
2. **側面ビュー**: 卵型のボディシルエット、背面の滑らかなS字アンテナと地球儀、右胸 `et` の回り込みに加え、ティアドロップ型のラバーアームが上端から下端までボディ側面にくっきりと浮かび上がり、`03_side.png` と完全一致している。
3. **背面・上面・底面・斜め3/4ヒーロービュー**: すべての角度でパーツの浮き・めり込み・不自然な折れ目が一切なく、マスコットキャラクターとしての愛らしさと立体的なソフビ・ラバー質感が最高水準で表現されている。

---

## Part 2. 設計要件＆参照5面図仕様サマリー（`01_Research_Dept/inputs/task_20261104_cvn_iinet_3d_modeling.md` 準拠）

- **対象キャラクター**: 株式会社CVN キャラクター「いい-NETくん」（胸ロゴ：`LILI-net` ※「いい」を `LI` `LI` で表現したデザイン）
- **用途**: 広告チラシ用ビジュアル、およびアニメーション用3Dモデル
- **質感・トーン**: アニメ調 × 柔軟に曲げられる弾性ラバー（ソフトビニール／シリコーンゴム）のような艶と弾力感のある質感
- **参照5面図アセット**:
  - `02_Creative_Dept/drafts/ref_images/05_front.png`（正面図）
  - `02_Creative_Dept/drafts/ref_images/03_side.png`（左側面図）
  - `02_Creative_Dept/drafts/ref_images/01_back.png`（背面図）
  - `02_Creative_Dept/drafts/ref_images/04_top.png`（上面図）
  - `02_Creative_Dept/drafts/ref_images/02_bottom.png`（底面図）
