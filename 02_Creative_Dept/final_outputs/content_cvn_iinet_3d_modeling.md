# 株式会社CVN 公式キャラクター「いい-NETくん（LILI-net）」3Dモデリング＆レンダリング制作仕様書（Rev.9 最終改修版：立体青枠版 ＆ 非立体フラット青枠版）

- **制作年月**: 2026年11月
- **制作担当**: Creative部門（`02_Creative_Dept`）
- **使用環境**: Blender 5.2.3 LTS（Python API `bpy` / `bmesh` による完全プロシージャル構築・Cycles GPU レンダリング）

---

## 1. 成果物ファイル一覧（全2バリエーション・計12ファイル同梱）

### (1) 最終成果物（`02_Creative_Dept/final_outputs/`）

#### 【A】顔の青枠＝立体ベゼル仕様（標準版）
| 種別 | ファイルパス | 仕様・解像度 |
| :--- | :--- | :--- |
| **Blenderマスターファイル** | `02_Creative_Dept/final_outputs/cvn_iinet_kun.blend` | Blender 5.2形式（立体青枠仕様：全11メッシュパーツ＋リグ＋Cycles 3Dマットマテリアル設定済） |
| **Web / AR用 3Dモデル** | `02_Creative_Dept/final_outputs/cvn_iinet_kun.glb` | glTF 2.0 Binary形式（立体青枠仕様：11パーツ＋アーマチュア同梱） |
| **単体正面レンダリング（Front View）** | `02_Creative_Dept/final_outputs/iinet_kun_front.png` | `800 × 960 px`（立体青枠仕様・正面図単体・地球儀中央に日本列島表示） |
| **斜め3/4 ヒーローレンダリング** | `02_Creative_Dept/final_outputs/iinet_kun_hero_3quarter.png` | `1400 × 1680 px`（立体青枠仕様・Cycles 3Dマット陰影・接地シャドウ付） |
| **正面・側面・斜め・背面 4面比較ボード** | `02_Creative_Dept/final_outputs/iinet_kun_front_and_side.png` | `3320 × 1008 px`（立体青枠仕様・4パネル並列高解像度ボード） |
| **全6アングル統合シート（5面図＋斜め）** | `02_Creative_Dept/final_outputs/iinet_kun_5views_sheet.png` | `2496 × 1992 px`（立体青枠仕様・正面/側面/背面/上面/底面/斜め3/4） |

#### 【B】顔の青枠＝非立体フラット曲面仕様（別バージョン）
| 種別 | ファイルパス | 仕様・解像度 |
| :--- | :--- | :--- |
| **Blenderマスターファイル（非立体枠版）** | `02_Creative_Dept/final_outputs/cvn_iinet_kun_flat_frame.blend` | Blender 5.2形式（非立体フラット青枠仕様：全11メッシュパーツ＋リグ＋Cycles 3Dマットマテリアル設定済） |
| **Web / AR用 3Dモデル（非立体枠版）** | `02_Creative_Dept/final_outputs/cvn_iinet_kun_flat_frame.glb` | glTF 2.0 Binary形式（非立体フラット青枠仕様：11パーツ＋アーマチュア同梱） |
| **単体正面レンダリング（非立体枠版・Front View）** | `02_Creative_Dept/final_outputs/iinet_kun_flat_frame_front.png` | `800 × 960 px`（非立体フラット青枠仕様・正面図単体・地球儀中央に日本列島表示） |
| **斜め3/4 ヒーローレンダリング（非立体枠版）** | `02_Creative_Dept/final_outputs/iinet_kun_flat_frame_hero_3quarter.png` | `1400 × 1680 px`（非立体フラット青枠仕様・Cycles 3Dマット陰影・接地シャドウ付） |
| **正面・側面・斜め・背面 4面比較ボード（非立体枠版）** | `02_Creative_Dept/final_outputs/iinet_kun_flat_frame_front_and_side.png` | `3320 × 1008 px`（非立体フラット青枠仕様・4パネル並列高解像度ボード） |
| **全6アングル統合シート（非立体枠版）** | `02_Creative_Dept/final_outputs/iinet_kun_flat_frame_5views_sheet.png` | `2496 × 1992 px`（非立体フラット青枠仕様・正面/側面/背面/上面/底面/斜め3/4） |

### (2) 構築スクリプト・中間アセット（`02_Creative_Dept/drafts/`）
| 種別 | ファイルパス | 内容 |
| :--- | :--- | :--- |
| **3D一括構築Pythonスクリプト** | `02_Creative_Dept/drafts/build_iinet_kun.py` | 立体青枠版および非立体フラット青枠版の両対応プロシージャル構築・Cyclesレンダリングスクリプト |
| **モデリング設計ドラフト** | `02_Creative_Dept/drafts/draft_cvn_iinet_3d_modeling.md` | 座標変換定義・改修設計メモ |
| **全周360度地球儀テクスチャ** | `02_Creative_Dept/drafts/globe_texture.png` | `2048 × 1024 px` 正距円筒図法（Equirectangular）全周360度世界大陸テクスチャ（正面中央に日本列島配置） |

---

## 2. 造形・レンダリング仕様詳細（Rev.2 〜 Rev.9 累積反映事項）

### ① 顔の青枠に合わせたボディ横幅のスリム化＆単一強凸曲面（Rev.4 / Rev.8）
- **ボディ横幅のスリム化（Rev.8）**: 顔の青枠（`0.905倍` スケール）に対しボディ左右のピンク色余白が膨らみすぎていた問題を解消するため、ボディ最大横幅 `W_max` を従来の `0.91625 m` から **`0.81546 m`（`0.890倍`、全幅 `1.8325 m` ➔ `1.6309 m`）** にスリム化し、左右の足先間隔 `x_foot` も `±0.22962 m` に連動縮小。
- **下半部側面プロファイルのスマート化と凹みゼロの両立**: 外側輪郭の強凸プロファイル関数 `_f_convex_profile(u_out, alpha=0.45, delta=0.25)` により、全区間 $u \in (0, 1)$ で二階微分 $f''(u) < 0$（変曲点・凹みゼロ）を厳密に保ったまま、脇腹〜腰回りの横膨らみを抑えて足先まで滑らかに繋がるシルエットを実現。
- **両腕（`Arm.L` / `Arm.R`）・胸元3Dロゴ（`Logo_LILI_net`）・リグの完全同期**: スリム化したボディ側面表面 $X_{\text{body}}(Z)$ を `surf_model._eval_lower_z` から直接逆引きして両腕の付け根・パドル外周を密着させ、胸元ロゴも横幅 `0.90倍` に調整してスリムなボディにバランスよく配置。

### ② 地球儀（`Globe`）：正面構図で日本列島（北海道・本州・四国・九州）がクッキリ見える配置（Rev.9）
- **正面中央への日本列島配置（Rev.9）**: 正面カメラ（`-Y` 方向・経度 $\text{lon} = 0^\circ$）から地球儀を見た際、地球儀の正面中央領域（$\text{lon} = -5^\circ \sim +24^\circ,\ \text{lat} = +5^\circ \sim +40^\circ$）に **日本列島4島（北海道・本州の弓なり形状・四国・九州）** がクッキリと視認できるよう世界地図の経度配置を設計。
- **日本海・東アジア大陸との立体的な位置関係**: 日本列島のすぐ左上（$\text{lon} = -40^\circ \sim -4^\circ$）にユーラシア大陸東岸・朝鮮半島・シベリア・カムチャツカ半島を配置し、大陸と日本列島の間に青い日本海、右側に太平洋が広がる構図を実現。さらに側面・背面・上面・底面の全周360度にオーストラリア・東南アジア・インド・アフリカ・ヨーロッパ・南北アメリカ大陸をバランスよく配置。

### ③ 頭のラインの完全美化：$C^\infty$ 解析的ドーム曲線（Rev.4）
- 上半球（$Z \ge Z_{\text{eq}}$）の前後断面を純粋な楕円断面（`p = 2.0`, `f_yz = 1.0`）とし、正面頭頂プロファイルにピクセルLUTを一切使わない **$C^\infty$ 解析的ドーム関数** $Z_{\text{top}}(|X|) = Z_{\text{eq}} + (Z_{\text{apex}} - Z_{\text{eq}})(1 - (|X|/W_{\max})^2)^{0.480}$ を採用。全角度で完璧に綺麗で丸い頭頂ラインを実現。

### ④ 顔の青枠（`Face_Frame`）＆画面（`Face_Screen`）の2バージョン展開（Rev.5）
- **【A】立体青枠版（`cvn_iinet_kun.*`）**: 外径スケール `0.905倍`・枠幅係数 `0.54` のスリムな青枠を、ボディ表面から法線方向へ $+0.038\text{ m}$ ぷっくりと立体ベゼル状に隆起させた仕様。
- **【B】非立体フラット青枠版（`cvn_iinet_kun_flat_frame.*`）**: 青枠と画面の隆起を廃止し、ボディ前面曲面から法線方向へ均一な $+0.0007\text{ m}$（$0.7\text{ mm}$）の極薄コンフォーマル・フラッシュシェルとして同一面上に配置（`visible_shadow = False`）。

### ⑤ 口（`Mouth`）の両端の半円カプセル化（Rev.6）＆尻尾（`Antenna`）のスリム化（Rev.7）
- 口（`Mouth`）の両端キャップに厳密な円弧式 $\text{ext} = \cos\alpha \cdot (1.15\,r_{\text{tube}}),\ r_{\text{sc}} = \sin\alpha$ を適用し、ぷっくり丸い半円カプセル端を実現。
- 地球儀につながる尻尾（`Antenna`）のパイプ半径 `r_pipe` を `15.5 / 400.0`（`0.03875 m`）にスリム化し、地球儀の真下（南極中心 $Z = 2.1925\text{ m}$）へ垂直に接続。
