# 最終納品パッケージ：株式会社CVN 公式キャラクター「いい-NETくん（LILI-net）」3Dモデリング＆レンダリング制作（Rev.4 改修完了版）

- **納品日**: 2026年11月05日（Rev.4 改修版）
- **格納場所**: `04_Delivery_Dept/outputs/`
- **法務・コンプライアンス審査**: `SKIPPED（通常案件・自社公式キャラクター3D制作）`
- **同梱・変換ファイル一覧**:
  - **マスターパッケージ（本書・Rev.4）**: [`output_20261104_cvn_iinet_3d_modeling_full.md`](output_20261104_cvn_iinet_3d_modeling_full.md)
  - **斜め3/4 ヒーローレンダリング（1400×1680 px・Cycles 3DCGマット質感・Rev.4）**: [`output_20261104_cvn_iinet_hero_3quarter.png`](output_20261104_cvn_iinet_hero_3quarter.png)（別名コピー: [`iinet_kun_hero_3quarter.png`](iinet_kun_hero_3quarter.png)）
  - **正面・側面・斜め・背面 4面比較ボード（3320×1008 px・Rev.4）**: [`output_20261104_cvn_iinet_front_and_side.png`](output_20261104_cvn_iinet_front_and_side.png)（別名コピー: [`iinet_kun_front_and_side.png`](iinet_kun_front_and_side.png)）
  - **全6アングル統合シート（5面図＋斜め / 2496×1992 px・Rev.4）**: [`output_20261104_cvn_iinet_5views_sheet.png`](output_20261104_cvn_iinet_5views_sheet.png)（別名コピー: [`iinet_kun_5views_sheet.png`](iinet_kun_5views_sheet.png)）
  - **Blender 5.2 マスターファイル（全11メッシュパーツ・リグ・3DCGマットマテリアル・Cyclesスタジオライト設定済・Rev.4）**: [`output_20261104_cvn_iinet_kun.blend`](output_20261104_cvn_iinet_kun.blend)
  - **Web / AR / 汎用3Dエンジン用 glTF 2.0 Binary（11パーツ＋アーマチュア同梱・Rev.4）**: [`output_20261104_cvn_iinet_kun.glb`](output_20261104_cvn_iinet_kun.glb)

---

## エグゼクティブサマリー（Rev.4 曲面完全平滑化・Cycles 3DCGマット質感・ボーン構成・プレビュー）

### 1. レンダリング画像プレビュー一覧（Rev.4 改修完了版）

#### (1) 斜め3/4 ヒーローカット（広告チラシ・メインビジュアル用）
- ファイル: [`output_20261104_cvn_iinet_hero_3quarter.png`](output_20261104_cvn_iinet_hero_3quarter.png) / [`iinet_kun_hero_3quarter.png`](iinet_kun_hero_3quarter.png)
![斜め3/4 ヒーローカット（Rev.4）](output_20261104_cvn_iinet_hero_3quarter.png)

#### (2) 正面・左側面・斜め3/4・背面 4面比較ボード
- ファイル: [`output_20261104_cvn_iinet_front_and_side.png`](output_20261104_cvn_iinet_front_and_side.png) / [`iinet_kun_front_and_side.png`](iinet_kun_front_and_side.png)
![正面・側面・斜め・背面 4面比較ボード（Rev.4）](output_20261104_cvn_iinet_front_and_side.png)

#### (3) 全6アングル統合シート（正面・左側面・背面・上面・底面・斜め3/4）
- ファイル: [`output_20261104_cvn_iinet_5views_sheet.png`](output_20261104_cvn_iinet_5views_sheet.png) / [`iinet_kun_5views_sheet.png`](iinet_kun_5views_sheet.png)
![全6アングル統合シート（Rev.4）](output_20261104_cvn_iinet_5views_sheet.png)

---

### 2. Rev.4 最重要改修項目および累積仕様サマリー

| 項目 | Rev.4 / 累積改修要件・課題 | 3Dモデリング・マテリアル・レンダリングにおける実装仕様 |
| :--- | :--- | :--- |
| **① 【Rev.4】ボディと足の付け根のへこみ完全解消（単一強凸曲面＋Taubin平滑化）** | 胴体下部と足の付け根にあった不自然なへこみ・くびれ・溝状の陰影を完全に無くし、胴体から足先までツルンと滑らかに連続させる。 | 局所ディスクによる2段階脚突出および水平絞り（`rad_mult`）を完全廃止し、全区間 $u \in (0, 1)$ で二階微分 $f''(u) < 0$（変曲点ゼロ）を満たす**単一強凸プロファイル関数 `_f_convex_profile(u, alpha, delta)`**（円弧と丸み付き双曲線の凸結合）を導入。赤道（$Z=1.155\text{ m}$）から脇腹・お腹・お尻を通って丸く尖った足先（$X=\pm 0.258\text{ m}, Y=0.0\text{ m}, Z=-0.068\text{ m}$）まで1ミリの凹みもない一体造形を実現。さらに股下アーチ（$Z_{\text{crotch}}=+0.152\text{ m}$）は $C^2$ エルミート接続とし、お腹前面（$|c_t| \ge 0.44$）では股下溝重みを完全ゼロ化して `LILI-net` ロゴ領域も100%凸曲面化。仕上げに下半部へ20反復の体積保存型Taubinスムージング（$\lambda=+0.45, \mu=-0.47$）を適用。 |
| **② 【Rev.4】頭のラインの完全美化（$C^\infty$ 解析的ドーム曲線＋純粋楕円断面）** | 頭頂からこめかみ・側面にかけての微細なピクセル階段ノイズや斜め上の角張りを無くし、どの角度から見ても完璧に綺麗な丸い頭頂ラインにする。 | 2D画像の整数ピクセルLUT補間およびスーパー楕円体指数（`p=2.12`）を廃止。上半球（$Z \ge Z_{\text{eq}}$）の水平・前後断面を純粋な楕円断面（`p=2.0`, `f_yz=1.0`）に統一し、正面頭頂プロファイルに **$C^\infty$ 解析的ドーム関数** $Z_{\text{top}}(|X|) = Z_{\text{eq}} + (Z_{\text{apex}} - Z_{\text{eq}})(1 - (|X|/W_{\max})^2)^{0.480}$ を採用。全アングルで歪みのない完璧なドーム曲線を実現。 |
| **③ 尻尾先端と地球儀の接続位置（地球儀の真下へ垂直接続）** | お尻から生えた尻尾（`Antenna`）の先端が、地球儀の横／後ろではなく**地球儀の真下（南極点）**に繋がるようにする。 | お尻内部 $(Y=0.350\text{ m}, Z=0.490\text{ m})$ から表面を貫通し、背中下部ピーク $(Z=1.060\text{ m})$ ➔ 背中上部の谷部 $(Z=1.640\text{ m})$ ➔ 地球儀真下の直前 $(Z=2.155\text{ m}, Y=1.190\text{ m})$ を2段階の解析的余弦曲線（$C^1/C^2$ 連続）で滑らかに繋ぎ、そこから **$+Z$ 方向（真上）へ垂直に立ち上がって地球儀の真下（南極中心 $Z=2.1925\text{ m}$）へ接続**。 |
| **④ 顔のTV青枠のスリム化＆微拡大＋立体目・口＋胸元 `LILI-net` 3D立体文字** | TV青枠を細くシャープにしつつ画面サイズを微拡大し、目・口・胸元の `LILI-net` 文字をすべて3D立体メッシュとして造形する。 | TV青枠・画面の外径スケールを `0.905倍`（顔中心 $Z_c = 1.2645\text{ m}$）、枠幅係数を `0.54` の細枠とし、法線方向へ $+0.038\text{ m}$ 立体隆起。パッチリ丸目（半径 $0.080\text{ m}$、厚み $+0.035\text{ m}$）、立体口（$+0.022\text{ m}$）、および滑らかなお腹の凸曲面に沿って $+0.024\text{ m}$ 張り出す独立3Dメッシュの `LILI-net` ロゴ（`Logo_LILI_net`）を配置。 |
| **⑤ 本格3DCGマット質感（Cycles GPU）＆全周360度地球儀テクスチャ** | アニメ調（黒フチ線・自己発光塗り）を排して3DCGマット陰影でレンダリングし、地球儀は全方向から海と大陸が見える全周360度仕様にする。 | Freestyle輪郭線と自己発光（`Emission`）を完全ゼロ化し、Cycles GPU パストレーシング＋4灯スタジオソフトボックス照明により `Roughness=0.94, Specular=0.08` の上品な3DCGマット質感でレンダリング。地球儀には経度 $-180^\circ \sim +180^\circ$・緯度 $-90^\circ \sim +90^\circ$ の全周360度に世界の大陸・島列を配置した `2048×1024 px` Equirectangularテクスチャを適用。 |

---

### 3. アニメーション用アーマチュア（`IINet_Armature`）ボーン構成（全11メッシュパーツ対応）

```text
IINet_Armature
└── Root (0, 0, -0.068) -> (0, 0, 0.18)
    └── Body (0, 0, 0.18) -> (0, 0, 1.90)
        │   [追従メッシュ: Body, Face_Screen, Face_Frame, Eye.L, Eye.R, Mouth, Logo_LILI_net]
        ├── Leg.L (+0.258, 0.0, 0.18) -> (+0.258, 0.0, -0.068)  [単一凸曲面で連続する丸く尖った左足スイング制御]
        ├── Leg.R (-0.258, 0.0, 0.18) -> (-0.258, 0.0, -0.068)  [単一凸曲面で連続する丸く尖った右足スイング制御]
        ├── Arm.L (+0.72, 0.0, 0.68)  -> (+0.96, 0.0, 0.32)     [左アーム パタパタ・曲げ制御]
        ├── Arm.R (-0.72, 0.0, 0.68)  -> (-0.96, 0.0, 0.32)     [右アーム パタパタ・曲げ制御]
        └── Antenna_1 -> Antenna_2 -> Antenna_3 -> Globe        [お尻貫通〜地球儀真下接続S字尻尾＆地球儀制御]
```

---

## Part 1. 完成コンテンツ本編（3Dモデリング＆レンダリング制作仕様書 Rev.4）

- **制作年月**: 2026年11月
- **制作担当**: Creative部門（`02_Creative_Dept`）
- **使用環境**: Blender 5.2.3 LTS（Python API `bpy` / `bmesh` による完全プロシージャル構築・Cycles GPU レンダリング）

### 1. 成果物ファイル一覧

#### (1) 最終納品ファイル（`04_Delivery_Dept/outputs/` 格納済）
| 種別 | 納品ファイルパス | 仕様・解像度 |
| :--- | :--- | :--- |
| **Blenderマスターファイル** | [`04_Delivery_Dept/outputs/output_20261104_cvn_iinet_kun.blend`](output_20261104_cvn_iinet_kun.blend) | Blender 5.2形式（全11メッシュパーツ＋リグ＋3Dマットマテリアル＋Cyclesスタジオライト設定済） |
| **Web / AR用 3Dモデル** | [`04_Delivery_Dept/outputs/output_20261104_cvn_iinet_kun.glb`](output_20261104_cvn_iinet_kun.glb) | glTF 2.0 Binary形式（11パーツ＋アーマチュア同梱） |
| **斜め3/4 ヒーローレンダリング** | [`04_Delivery_Dept/outputs/output_20261104_cvn_iinet_hero_3quarter.png`](output_20261104_cvn_iinet_hero_3quarter.png)<br>（同内容コピー: [`iinet_kun_hero_3quarter.png`](iinet_kun_hero_3quarter.png)） | `1400 × 1680 px`（Cycles 3Dマット陰影・透過合成スタジオカード背景・接地シャドウ付） |
| **正面・側面・斜め・背面 4面比較ボード** | [`04_Delivery_Dept/outputs/output_20261104_cvn_iinet_front_and_side.png`](output_20261104_cvn_iinet_front_and_side.png)<br>（同内容コピー: [`iinet_kun_front_and_side.png`](iinet_kun_front_and_side.png)） | `3320 × 1008 px`（4パネル並列高解像度ボード） |
| **全6アングル統合シート（5面図＋斜め）** | [`04_Delivery_Dept/outputs/output_20261104_cvn_iinet_5views_sheet.png`](output_20261104_cvn_iinet_5views_sheet.png)<br>（同内容コピー: [`iinet_kun_5views_sheet.png`](iinet_kun_5views_sheet.png)） | `2496 × 1992 px`（正面・側面・背面・上面・底面・斜め3/4） |

#### (2) 構築スクリプト・中間アセット（`02_Creative_Dept/drafts/`）
| 種別 | ファイルパス | 内容 |
| :--- | :--- | :--- |
| **3D一括構築Pythonスクリプト** | `02_Creative_Dept/drafts/build_iinet_kun.py` | 輪郭抽出・Rev.4単一凸曲面ボディ＆解析ドーム頭頂・3Dメッシュ生成・リギング・Cyclesマットレンダリング自動化 |
| **モデリング設計ドラフト** | `02_Creative_Dept/drafts/draft_cvn_iinet_3d_modeling.md` | 座標変換定義・Rev.4改修設計メモ |
| **全周360度地球儀テクスチャ** | `02_Creative_Dept/drafts/globe_texture.png` | `2048 × 1024 px` 正距円筒図法（Equirectangular）全周360度世界大陸テクスチャ |

### 2. Rev.4 ＆ Rev.3 ユーザー改修要件の実装仕様詳細

#### ① ボディと足の付け根のへこみ完全解消：胴体から足先まで変曲点ゼロで連続する単一強凸曲面（Rev.4 最重要改修）
- **原因の解消**: 従来の「胴体底面を一旦平らに閉じてから局所ディスク（`r_u < 1`）で足を突き出し、水平半径を `rad_mult` で絞る」2段階方式では、付け根の境界に数学的な変曲点（凹み・くびれ・溝状の陰影）が発生していたため、これを**完全廃止**。
- **単一強凸プロファイル関数 `_f_convex_profile(u, alpha, delta)` の導入**:
  - 水平座標 $(X, Y) = (W_{\max} n_x, D_{\max} n_y)$ は一切の局所的な絞り・引っ張りを持たない純粋な楕円断面を維持。
  - 外側輪郭（$|X| \in [x_{\text{foot}}, W_{\max}]$）および前後方向（$|c_t| = |Y|/Y_{\max} \in [0, 1]$）の高さプロファイルに、円弧 $\sqrt{1 - u^2}$ と丸み付き双曲線 $1 - \frac{\sqrt{u^2 + \delta^2} - \delta}{\sqrt{1 + \delta^2} - \delta}$ の凸結合を採用。
  - この関数は全区間 $u \in (0, 1)$ で二階微分 $f''(u) < 0$（曲率符号が一定で変曲点が数学的に存在しない）を満たすため、**赤道（$Z = 1.155\text{ m}$）から脇腹・お腹・お尻を通って足先（$X = \pm 0.258\text{ m}, Y = 0.0\text{ m}, Z = -0.068\text{ m}$）に至るまで、いかなる角度から見ても1ミリのへこみ・くびれ・折れ目も生じないツルンと滑らかな一体造形**を実現。
  - 股下の中央アーチ（$|X| < 0.258\text{ m}, Z_{\text{crotch}} = +0.152\text{ m}$）は足先と $C^2$ 連続（曲率連続）のエルミート多項式で接続し、さらにお腹の `LILI-net` ロゴ領域（$|c_t| \ge 0.44$）では股下の溝重みを完全ゼロ（`0.0`）に減衰させることで、ロゴが乗るお腹前面も100%丸く滑らかな凸曲面に仕上げた。
  - メッシュ生成後に下半部（$Z < 0.48\text{ m}$）へ20反復の体積保存型 Taubin スムージング（$\lambda = +0.45, \mu = -0.47$）を適用し、局所曲率の連続性を極限まで高めた。

#### ② 頭のラインの完全美化：ピクセル階段ノイズを排した $C^\infty$ 解析的ドーム曲線（Rev.4 最重要改修）
- 2D画像（`05_front.png`）の整数ピクセル境界から抽出した `Z_top_lut` の線形補間およびスーパー楕円体指数（`p = 2.12`）を廃止。
- 上半球（$Z \ge Z_{\text{eq}}$）の前後断面を純粋な楕円断面（`p = 2.0`, `f_yz = 1.0`）とした上で、正面頭頂プロファイルに **$C^\infty$ 解析的ドーム関数**：
  $$Z_{\text{top}}(|X|) = Z_{\text{eq}} + (Z_{\text{apex}} - Z_{\text{eq}}) \left(1 - \left(\frac{|X|}{W_{\max}}\right)^2\right)^{0.480} \quad (Z_{\text{eq}} = 1.155\text{ m}, Z_{\text{apex}} = 2.010\text{ m})$$
  を採用。正面・側面・背面・上面・斜め3/4のどの角度から見ても、ピクセル由来のガタつきや斜め上の角張りが一切ない完璧に綺麗で丸い頭頂ラインを実現した。

#### ③ 尻尾（`Antenna`）の先端と地球儀（`Globe`）の接続位置を「地球儀の真下（南極点）」へ配置
- お尻の内部 $(Y=0.350\text{ m}, Z=0.490\text{ m})$ から背中下部ピーク $(Z=1.060\text{ m})$ ➔ 背中上部の谷部 $(Z=1.640\text{ m})$ ➔ 地球儀真下の直前 $(Z=2.155\text{ m}, Y=1.190\text{ m})$ を2段階の解析的余弦曲線（$C^1/C^2$ 連続）で滑らかに繋ぎ、そこから **$+Z$ 方向（真上）へ垂直に立ち上がって地球儀の真下（南極中心 $Z = 2.1925\text{ m}$）へ接続**。

#### ④ 顔の青枠（`Face_Frame`）の枠幅スリム化＆全体サイズの微拡大＋胸元 `LILI-net` 3D立体文字ロゴ
- TV画面モチーフの青枠および画面（`Face_Screen`）の外径スケールを `0.905倍`（顔中心 $Z_c = 1.2645\text{ m}$）、枠幅係数を `0.54` の細枠とし、法線方向へ $+0.038\text{ m}$ 立体的に隆起。
- 大きめの丸目（半径 $0.080\text{ m}$、厚み $+0.035\text{ m}$）、立体口（$+0.022\text{ m}$）、および滑らかなお腹の凸曲面に沿って $+0.024\text{ m}$ 張り出す独立3Dメッシュの `LILI-net` ロゴ（`Logo_LILI_net`）を配置。

#### ⑤ 本格3DCGマット質感（Cycles GPU）レンダリング＆全周360度地球儀テクスチャ
- Freestyle輪郭線および自己発光（`Emission`）を完全ゼロ（`0.0`）とし、Cycles GPU パストレーシング＋4灯スタジオソフトボックス照明により、`Roughness = 0.94, Specular = 0.08` の上品な3DCGマット質感と柔らかい立体陰影でレンダリング。
- 地球儀には経度 $-180^\circ \sim +180^\circ$・緯度 $-90^\circ \sim +90^\circ$ の全周360度に世界の大陸・半島・島列を配置した `2048 × 1024 px` Equirectangularテクスチャを適用し、全方位どの角度から見ても美しい水色の海と緑の大陸が見える仕上げとした。

### 3. 視覚監査（Visual Audit）結果

再生成された3種のレンダリング画像（`output_20261104_cvn_iinet_hero_3quarter.png`, `output_20261104_cvn_iinet_front_and_side.png`, `output_20261104_cvn_iinet_5views_sheet.png`）を目視監査し、Rev.4の全要件が完全に達成されていることを確認した。

1. **ボディと足の付け根の滑らかさ（正面・側面・背面・底面・斜め3/4）**: 脇腹・お腹・お尻から足先にかけての不自然なへこみ・くびれ・陰影のスジが100%消滅し、原画通りの丸く尖った2本の足へツルンと滑らかな単一凸曲面で繋がっている。お腹の `LILI-net` 3Dロゴも中央の凹みなく美しい円弧を描いて密着している。
2. **頭のラインの美しさ**: 正面・側面・背面・斜め3/4のすべてのビューにおいて、頭頂からこめかみ・側面赤道へ至るラインが1ミリの歪みもない完璧に滑らかなドーム曲線となっている。
3. **尻尾・地球儀・顔パーツ・マット質感**: 尻尾はお尻から滑らかなS字を描いて地球儀の真下へ垂直に接続し、地球儀は全6アングルすべてで鮮やかな大陸と海が見え、全体が上品な3DCGマット陰影で統一されている。

---

## Part 2. 設計要件＆参照5面図仕様サマリー（`01_Research_Dept/inputs/task_20261104_cvn_iinet_3d_modeling.md` 準拠）

- **対象キャラクター**: 株式会社CVN キャラクター「いい-NETくん」（胸ロゴ：`LILI-net` ※「いい」を `LI` `LI` で表現したデザイン）
- **用途**: 広告チラシ用ビジュアル、およびアニメーション用3Dモデル
- **質感・トーン（Rev.4）**: アニメ調を排した本格3DCGマット（つや消しラバー／クレイフィギュア）質感（Cycles GPU パストレーシング）
- **参照5面図アセット**:
  - `02_Creative_Dept/drafts/ref_images/05_front.png`（正面図）
  - `02_Creative_Dept/drafts/ref_images/03_side.png`（左側面図）
  - `02_Creative_Dept/drafts/ref_images/01_back.png`（背面図）
  - `02_Creative_Dept/drafts/ref_images/04_top.png`（上面図）
  - `02_Creative_Dept/drafts/ref_images/02_bottom.png`（底面図）
