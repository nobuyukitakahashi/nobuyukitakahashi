# 株式会社CVN 公式キャラクター「いい-NETくん（LILI-net）」3Dモデリング＆レンダリング制作仕様書（Rev.10 最終完成版：完全平面顔・小型角丸TV画面枠・楕円タマゴ底仕様）

- **制作年月**: 2026年11月
- **制作担当**: Creative部門（`02_Creative_Dept`）
- **使用環境**: Blender 5.2.3 LTS（Python API `bpy` / `bmesh` による完全プロシージャル構築・Cycles GPU レンダリング）

---

## 1. 成果物ファイル一覧（計12ファイル同梱）

### (1) 最終成果物（`02_Creative_Dept/final_outputs/`）

#### 【A】メイン出力ファイル（完全平面顔・小型角丸TV画面枠・楕円タマゴ底仕様）
| 種別 | ファイルパス | 仕様・解像度 |
| :--- | :--- | :--- |
| **Blenderマスターファイル** | `02_Creative_Dept/final_outputs/cvn_iinet_kun.blend` | Blender 5.2形式（完全平面顔・小型角丸TV枠・楕円タマゴ底仕様：全11メッシュパーツ＋リグ＋Cycles 3Dマットマテリアル設定済） |
| **Web / AR用 3Dモデル** | `02_Creative_Dept/final_outputs/cvn_iinet_kun.glb` | glTF 2.0 Binary形式（11パーツ＋アーマチュア同梱） |
| **単体正面レンダリング（Front View）** | `02_Creative_Dept/final_outputs/iinet_kun_front.png` | `800 × 960 px`（完全平面顔・小型角丸TV青枠・地球儀中央に日本列島表示） |
| **斜め3/4 ヒーローレンダリング** | `02_Creative_Dept/final_outputs/iinet_kun_hero_3quarter.png` | `1400 × 1680 px`（斜め3/4でも歪みのない滑らかなタマゴ型シルエット・接地シャドウ付） |
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
| **3D一括構築Pythonスクリプト** | `02_Creative_Dept/drafts/build_iinet_kun.py` | プロシージャル構築・Cyclesレンダリングスクリプト（Rev.10最終完成版） |
| **モデリング設計ドラフト** | `02_Creative_Dept/drafts/draft_cvn_iinet_3d_modeling.md` | 座標変換定義・改修設計メモ |
| **全周360度地球儀テクスチャ** | `02_Creative_Dept/drafts/globe_texture.png` | `2048 × 1024 px` 正距円筒図法（Equirectangular）全周360度世界大陸テクスチャ（正面中央に日本列島配置） |

---

## 2. 造形・レンダリング仕様詳細（最終完成版）

### ① 原図（`05_front.png` / `03_side.png` / `04_top.png` / `02_bottom.png`）に完全準拠したふっくら丸いタマゴ底＆斜め3/4曲線
- **前後断面（Y-Z断面）の楕円弧化による側面タマゴ底・斜め3/4曲線の完全美化**:
  `_eval_lower_z` の前後方向プロファイル `f_y` に `alpha = 0.06, delta = 0.45`（ほぼ純粋な円弧 $\sqrt{1 - \text{abs\_ct}^2}$）を採用し、さらに外側輪郭 `f_x` に `alpha = 0.28, delta = 0.30`、股下溝の減衰幅を `0.58` とすることで、側面図（`03_side.png`）の下部がV字に尖らず原図通りの**ふっくら丸いタマゴ底**になり、底面図（`02_bottom.png`）のくぼみもゼロ、斜め3/4ビュー（`hero_3quarter.png`）のお腹から足先へのシルエットも100%自然で滑らかなタマゴ曲線を実現しました。
- **ボディ横幅・奥行きの最適バランス**:
  `body_x_scale = 0.940`（`W_max = 0.861 m`, `x_foot = 0.242 m`, `D_front = 0.700 m`, `D_back = 0.740 m`）により、正面から見たときの可愛らしいタマゴ型プロポーションと、斜め3/4から見たときに黄色い画面がピンク輪郭からはみ出さない自然な立体感を両立しました。

### ② 顔全体（枠・画面・目・口）の完全フラット化＆角丸TV画面枠の小型化（`frame_scale = 0.835`）
- **顔パーツ全体の非立体フラット化**: 青枠（`Face_Frame`）と画面（`Face_Screen`）をボディ表面から $+0.0007\text{ m}$、左右の目（`Eye.L` / `Eye.R`, `cx = ±0.218 m, radius = 0.072 m`）と口（`Mouth`, `r_arc = 0.355 m, r_tube = 0.027 m`）を $+0.0014\text{ m}$（ドーム・チューブ隆起ゼロ、`visible_shadow = False`）のコンフォーマル平面シェルとして造形。
- **原図の角丸TVモニター形状の維持と小型化**: `_compute_scaled_face_radii` にて原図の角丸四角形形状を `82%` 維持しつつ `18%` の楕円平滑化を加え、`frame_scale = 0.835` に縮小することで、原図 `05_front.png` の可愛い角丸TVモニターらしさを100%保ったまま、周囲にバランスの良いピンク色の余白を確保しました。

### ③ 地球儀（`Globe`）：正面構図で日本列島（北海道・本州・四国・九州）がクッキリ見える配置
- 正面カメラ（`-Y` 方向）から地球儀を見た際、地球儀のど真ん中に **日本列島4島（北海道・本州の弓なり形状・四国・九州）** が大陸と重ならず独立してクッキリ見えるよう配置し、全周360度に世界の大陸をバランスよく配置。
