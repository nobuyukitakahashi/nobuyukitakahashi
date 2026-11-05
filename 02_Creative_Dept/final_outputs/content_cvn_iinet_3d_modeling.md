# 株式会社CVN 公式キャラクター「いい-NETくん（LILI-net）」3Dモデリング＆レンダリング制作仕様書（Rev.13 最終完成版：原画05_front完全一致・非立体平面顔・立体グラデーションライティング仕様）

- **制作年月**: 2026年11月
- **制作担当**: Creative部門（`02_Creative_Dept`）
- **使用環境**: Blender 5.2.3 LTS（Python API `bpy` / `bmesh` による完全プロシージャル構築・Cycles GPU レンダリング）

---

## 1. 成果物ファイル一覧（計12ファイル同梱）

### (1) 最終成果物（`02_Creative_Dept/final_outputs/`）

#### 【A】メイン出力ファイル（原画05_front完全一致・非立体平面顔・立体グラデーションライティング仕様）
| 種別 | ファイルパス | 仕様・解像度 |
| :--- | :--- | :--- |
| **Blenderマスターファイル** | `02_Creative_Dept/final_outputs/cvn_iinet_kun.blend` | Blender 5.2形式（原画05_front完全一致・非立体平面顔・立体グラデーションライティング仕様：全11メッシュパーツ＋リグ＋Cycles 3Dマットマテリアル設定済） |
| **Web / AR用 3Dモデル** | `02_Creative_Dept/final_outputs/cvn_iinet_kun.glb` | glTF 2.0 Binary形式（11パーツ＋アーマチュア同梱） |
| **単体正面レンダリング（Front View）** | `02_Creative_Dept/final_outputs/iinet_kun_front.png` | `800 × 960 px`（原画05_front完全一致：顔枠・目・口・LILI-net位置・立体グラデーション・地球儀中央に日本列島表示） |
| **斜め3/4 ヒーローレンダリング** | `02_Creative_Dept/final_outputs/iinet_kun_hero_3quarter.png` | `1400 × 1680 px`（斜め3/4でも歪みのない滑らかなタマゴ型シルエット・立体グラデーション・接地シャドウ付） |
| **正面・側面・斜め・背面 4面比較ボード** | `02_Creative_Dept/final_outputs/iinet_kun_front_and_side.png` | `3320 × 1008 px`（4パネル並列高解像度ボード） |
| **全6アングル統合シート（5面図＋斜め）** | `02_Creative_Dept/final_outputs/iinet_kun_5views_sheet.png` | `2496 × 1992 px`（正面/側面/背面/上面/底面/斜め3/4） |

#### 【B】`flat_frame` 互換パス出力ファイル（上記同一仕様）
| 種別 | ファイルパス | 仕様・解像度 |
| :--- | :--- | :--- |
| **Blenderマスターファイル（非立体枠版）** | `02_Creative_Dept/final_outputs/cvn_iinet_kun_flat_frame.blend` | Blender 5.2形式（上記同一仕様） |
| **Web / AR用 3Dモデル（非立体枠版）** | `02_Creative_Dept/final_outputs/cvn_iinet_kun_flat_frame.glb` | glTF 2.0 Binary形式（上記同一仕様） |
| **単体正面レンダリング（非立体枠版・Front View）** | `02_Creative_Dept/final_outputs/iinet_kun_flat_frame_front.png` | `800 × 960 px`（上記同一仕様） |
| **斜め3/4 ヒーローレンダリング（非立体枠版）** | `02_Creative_Dept/final_outputs/iinet_kun_flat_frame_hero_3quarter.png` | `1400 × 1680 px`（上記同一仕様） |
| **正面・側面・斜め・背面 4面比較ボード（非立体枠版）** | `02_Creative_Dept/final_outputs/iinet_kun_flat_frame_front_and_side.png` | `3320 × 1008 px`（上記同一仕様） |
| **全6アングル統合シート（非立体枠版）** | `02_Creative_Dept/final_outputs/iinet_kun_flat_frame_5views_sheet.png` | `2496 × 1992 px`（上記同一仕様） |

### (2) 構築スクリプト・中間アセット（`02_Creative_Dept/drafts/`）
| 種別 | ファイルパス | 内容 |
| :--- | :--- | :--- |
| **3D一括構築Pythonスクリプト** | `02_Creative_Dept/drafts/build_iinet_kun.py` | プロシージャル構築・Cyclesレンダリングスクリプト（Rev.13最終完成版） |
| **モデリング設計ドラフト** | `02_Creative_Dept/drafts/draft_cvn_iinet_3d_modeling.md` | 座標変換定義・改修設計メモ |
| **全周360度地球儀テクスチャ** | `02_Creative_Dept/drafts/globe_texture.png` | `2048 × 1024 px` 正距円筒図法（Equirectangular）全周360度世界大陸テクスチャ（正面中央に日本列島配置） |

---

## 2. 造形・レンダリング仕様詳細（最終完成版：Rev.13 原点アライメント）

### ① 原画（`05_front.png` / `03_side.png` / `04_top.png` / `02_bottom.png`）のピクセル計測値（Ground Truth）に完全一致したボディ＆顔枠バランス
- **ボディ輪郭と頭部超楕円ドーム曲線（`IINetSurfaceModel`）**:
  `body_x_scale = 0.992`（`W_max = 0.909 m`、原画 `364px = 0.910m` に一致）、`D_front = 0.640 m`、`D_back = 0.740 m`（原画 `03_side.png` 胴体奥行 `550px = 1.375m` に一致）、`Z_apex = 2.008 m`、`x_foot = 0.256 m`、`z_tip = -0.055 m`、および頭頂〜赤道（`y=219..560`）の肩の張りを誤差 `< 8.4mm` で再現する超楕円ドーム関数 $(1 - u^{2.35})^{0.420}$ を採用。
- **顔枠（`Face_Frame`）と画面（`Face_Screen`）の原画比率への完全復元**:
  `_compute_scaled_face_radii` にて `r_out_smooth = 0.90 * r_out_orig + 0.10 * r_ell`、`frame_scale = 0.975`、`thickness_slim = 0.92`、`zc = data["face_center_Z"]` とし、原画 `05_front.png` の顔枠とボディ外周のピンク余白バランス・枠太さを忠実に復元しました。

### ② 胸ロゴ `LILI-net` と顔枠の位置関係、および目・口のプロポーションの原画完全一致
- **胸ロゴ `LILI-net` と青枠下端の間隔（約 `20px = 0.050m`）の厳密再現**:
  原画 `05_front.png` における青枠下端（`y=795px`）と `LILI-net` 上端（`y=815px`）の隙間（`20px = 0.050m`）にピタリと一致するよう、`x_logo = ((x_px - 393.5) / 400.0) * 0.985`、`z_logo = ((1022.0 - y_px) / 400.0) + 0.022`、`h_off = 0.018` に設定。
- **目と目の間隔・サイズおよび口の両端の丸キャップ形状の原画一致**:
  - 左右の目（`Eye.L` / `Eye.R`）：原画の実測値（中心間隔 `248px = ±0.310m`、高さ `y=520.5px`、半径 `25px = 0.0625m`）に合わせ `cx_eye = ±0.3055 m, cz_eye = 1.2535 m, radius = 0.0630 m` に設定。
  - 口（`Mouth`）：原画の実測値に合わせ `z_arc_center = 1.2710 m, r_arc = 0.3780 m, r_tube = 0.0332 m, max_ang = 49.5°` とし、さらに両端キャップの引き伸ばしを撤廃して **真円の半円キャップ（`ext = cos(alpha) * r_tube`）** とすることで、口の両端が先細りせず目の中心よりわずかに外側までぷっくり丸く回り込む原画通りの可愛いスマイルを完全再現しました。
  - 顔パーツ全体（枠・画面・目・口）はボディ前面曲面にピタッと沿う非立体フラット仕様（落ち影ゼロ）を維持。

### ③ 地球儀（`Globe`）：正面構図で日本列島（北海道・本州・四国・九州）がクッキリ見える配置
- 正面カメラ（`-Y` 方向）から地球儀を見た際、地球儀のど真ん中に **日本列島4島（北海道・本州の弓なり形状・四国・九州）** が大陸と重ならず独立してクッキリ見えるよう配置し、全周360度に世界の大陸をバランスよく配置。

### ④ 立体感と光のグラデーションが美しく出るスタジオライティング＆3Dソフトビニール・マット質感（Rev.12）
- **Key-to-Fill比を強調した4灯スタジオライティング**:
  全方位の環境光（`World Background = 0.20`）と下からのバウンス光（`Bounce_Cam = 18W`）および右フィルライト（`Fill_Cam = 44W`）を適切に抑え、左上45度方向からのメイン指向性ソフトボックス（`Key_Cam = 335W`）と右上奥からのリムライト（`Rim_Cam = 88W`）によって、ボディおよび画面の左上（ハイライト領域）から右下・下部（シェード領域）へ向かって滑らかで立体感のある光のグラデーションが美しく浮かび上がるよう刷新しました。
- **ソフトビニール・マット質感の微調整**:
  Principled BSDFの `Roughness = 0.84`、`Specular IOR Level = 0.14` に設定し、強いテカリ（白飛び）を抑えつつも曲面の丸みに沿って柔らかい光のロールオフ（明暗グラデーション）が自然に表現される質感に仕上げました。

---

## 3. ペアキャラクター「いい-ch（胸ロゴ：`LILI-ch`）」3Dモデリング＆レンダリング制作仕様（`build_iich_kun.py`）

### (1) 「いい-ch」最終成果物一覧（`02_Creative_Dept/final_outputs/` 計7ファイル）
| 種別 | ファイルパス | 仕様・解像度 |
| :--- | :--- | :--- |
| **Blenderマスターファイル** | `02_Creative_Dept/final_outputs/cvn_iich_kun.blend` | Blender 5.2形式（全11メッシュパーツ＋リグ＋Cycles 3Dソフトビニール・マットマテリアル設定済） |
| **Web / AR用 3Dモデル** | `02_Creative_Dept/final_outputs/cvn_iich_kun.glb` | glTF 2.0 Binary形式（11パーツ＋アーマチュア同梱） |
| **単体正面レンダリング（Front View）** | `02_Creative_Dept/final_outputs/iich_kun_front.png` | `800 × 960 px`（原画Front完全一致：縦長オーバル目・優しいスマイル・LILI-ch立体ロゴ・地球儀中央に日本列島表示） |
| **単体左側面レンダリング（Side View）** | `02_Creative_Dept/final_outputs/iich_kun_side.png` | `800 × 960 px`（原画Side完全一致：単一C字カーブ尻尾・楕円パドル腕・滑らかなタマゴ底） |
| **斜め3/4 ヒーローレンダリング** | `02_Creative_Dept/final_outputs/iich_kun_hero_3quarter.png` | `1400 × 1680 px`（立体グラデーションライティング・接地シャドウ付） |
| **正面・側面・斜め・背面 4面比較ボード** | `02_Creative_Dept/final_outputs/iich_kun_front_and_side.png` | `3320 × 1008 px`（4パネル並列高解像度ボード） |
| **全6アングル統合シート（5面図＋斜め）** | `02_Creative_Dept/final_outputs/iich_kun_5views_sheet.png` | `2496 × 1992 px`（正面/左側面/背面/上面/底面/斜め3/4） |

### (2) 「いい-ch」Ground Truth 造形仕様（Rev.2：高解像度正面原画 `iich_05_front.png` 完全準拠）
- **「いい-NETくん」と完全同一のワールドスケール（`400.0 px = 1.000 m`, `y_foot = 1022.0 px`, 頭頂 `Z_apex = 2.005 m`）**:
  `W_max = 0.980 m`、`D_back = 0.760 m`、`D_front = 0.630 m`、`Z_eq = 1.0675 m`、`x_foot = 0.2625 m`、`z_tip = -0.005 m`、`z_crotch = 0.0975 m`。底面ビューでの波打ちをなくすため `t_cy = np.clip(abs_ct / 0.82, 0.0, 1.0)` による完全単調凸曲面を採用。
- **縦長オーバル（楕円）の目（`Eye.L` / `Eye.R`）とぷっくり丸いスマイルの口（`Mouth`）**:
  目は `cx_eye = ±0.3145 m, cz_eye = 1.1075 m, rx_eye = 0.0890 m, rz_eye = 0.1182 m`（原画と IoU 99.28% 一致）の縦長楕円フラットシェル、口は `z_arc_center = 1.0793 m, r_arc = 0.4180 m, r_tube = 0.0390 m, max_ang = 21.4°`＋真円半円キャップのフラットシェルとして造形。
- **胸元高精細3Dロゴメッシュ `LILI-ch`（`Logo_LILI_ch`）**:
  高解像度原画 `iich_05_front.png` の `im_f[886:966, 272:588]`（`80×316 px`）から `build_iinet_kun.py` と同一の2Dガウシアン平滑化＋12反復Taubin境界スムージング＋上面ベベルにより、ジャギー・歪みゼロの高精細立体3Dメッシュとして青枠下端のすぐ下（隙間約 `0.050 m`）に配置。
- **背面単一C字カーブ尻尾（`Antenna`）の付け根高さ統一 ＆ 地球儀（`Globe`）**:
  「いい-NETくん」と同じく下部お尻内部（`Z = 0.490 m, Y = 0.350 m`、表面 `Z ≈ 0.55 m` から出現）を始点とし、最大後方突出（`Y = +0.912 m, Z = 1.180 m`）を経て地球儀（中心 `Y = +0.720 m, Z = 2.356 m, r = 0.200 m`）の南極真下へ垂直接続する単一C字カーブとして造形。
