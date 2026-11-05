# 株式会社CVN 公式キャラクター「いい-NETくん（LILI-net）」3Dモデリング＆レンダリング制作仕様書（Rev.4 立体青枠版 ＆ 非立体フラット青枠版）

- **制作年月**: 2026年11月
- **制作担当**: Creative部門（`02_Creative_Dept`）
- **使用環境**: Blender 5.2.3 LTS（Python API `bpy` / `bmesh` による完全プロシージャル構築・Cycles GPU レンダリング）

---

## 1. 成果物ファイル一覧（全2バリエーション同梱）

### (1) 最終成果物（`02_Creative_Dept/final_outputs/`）

#### 【A】顔の青枠＝立体ベゼル仕様（Rev.4 標準版）
| 種別 | ファイルパス | 仕様・解像度 |
| :--- | :--- | :--- |
| **Blenderマスターファイル** | `02_Creative_Dept/final_outputs/cvn_iinet_kun.blend` | Blender 5.2形式（立体青枠仕様：全11メッシュパーツ＋リグ＋Cycles 3Dマットマテリアル設定済） |
| **Web / AR用 3Dモデル** | `02_Creative_Dept/final_outputs/cvn_iinet_kun.glb` | glTF 2.0 Binary形式（立体青枠仕様：11パーツ＋アーマチュア同梱） |
| **斜め3/4 ヒーローレンダリング** | `02_Creative_Dept/final_outputs/iinet_kun_hero_3quarter.png` | `1400 × 1680 px`（立体青枠仕様・Cycles 3Dマット陰影・接地シャドウ付） |
| **正面・側面・斜め・背面 4面比較ボード** | `02_Creative_Dept/final_outputs/iinet_kun_front_and_side.png` | `3320 × 1008 px`（立体青枠仕様・4パネル並列高解像度ボード） |
| **全6アングル統合シート（5面図＋斜め）** | `02_Creative_Dept/final_outputs/iinet_kun_5views_sheet.png` | `2496 × 1992 px`（立体青枠仕様・正面/側面/背面/上面/底面/斜め3/4） |

#### 【B】顔の青枠＝非立体フラット曲面仕様（別バージョン）
| 種別 | ファイルパス | 仕様・解像度 |
| :--- | :--- | :--- |
| **Blenderマスターファイル（非立体枠版）** | `02_Creative_Dept/final_outputs/cvn_iinet_kun_flat_frame.blend` | Blender 5.2形式（非立体フラット青枠仕様：全11メッシュパーツ＋リグ＋Cycles 3Dマットマテリアル設定済） |
| **Web / AR用 3Dモデル（非立体枠版）** | `02_Creative_Dept/final_outputs/cvn_iinet_kun_flat_frame.glb` | glTF 2.0 Binary形式（非立体フラット青枠仕様：11パーツ＋アーマチュア同梱） |
| **斜め3/4 ヒーローレンダリング（非立体枠版）** | `02_Creative_Dept/final_outputs/iinet_kun_flat_frame_hero_3quarter.png` | `1400 × 1680 px`（非立体フラット青枠仕様・Cycles 3Dマット陰影・接地シャドウ付） |
| **正面・側面・斜め・背面 4面比較ボード（非立体枠版）** | `02_Creative_Dept/final_outputs/iinet_kun_flat_frame_front_and_side.png` | `3320 × 1008 px`（非立体フラット青枠仕様・4パネル並列高解像度ボード） |
| **全6アングル統合シート（非立体枠版）** | `02_Creative_Dept/final_outputs/iinet_kun_flat_frame_5views_sheet.png` | `2496 × 1992 px`（非立体フラット青枠仕様・正面/側面/背面/上面/底面/斜め3/4） |

### (2) 構築スクリプト・中間アセット（`02_Creative_Dept/drafts/`）
| 種別 | ファイルパス | 内容 |
| :--- | :--- | :--- |
| **3D一括構築Pythonスクリプト** | `02_Creative_Dept/drafts/build_iinet_kun.py` | 立体青枠版および非立体フラット青枠版の両対応プロシージャル構築・Cyclesレンダリングスクリプト |
| **モデリング設計ドラフト** | `02_Creative_Dept/drafts/draft_cvn_iinet_3d_modeling.md` | 座標変換定義・改修設計メモ |
| **全周360度地球儀テクスチャ** | `02_Creative_Dept/drafts/globe_texture.png` | `2048 × 1024 px` 正距円筒図法（Equirectangular）全周360度世界大陸テクスチャ |

---

## 2. 造形・レンダリング仕様詳細

### ① ボディと足の付け根のへこみ完全解消：胴体から足先まで変曲点ゼロで連続する単一強凸曲面（Rev.4）
- 水平断面 $(X, Y) = (W_{\max} n_x, D_{\max} n_y)$ は一切の局所的な絞りを持たない純粋な楕円断面を維持。
- 外側輪郭（$|X| \in [x_{\text{foot}}, W_{\max}]$）および前後方向（$|c_t| = |Y|/Y_{\max} \in [0, 1]$）の高さプロファイルに、円弧 $\sqrt{1 - u^2}$ と丸み付き双曲線 $1 - \frac{\sqrt{u^2 + \delta^2} - \delta}{\sqrt{1 + \delta^2} - \delta}$ の凸結合（全区間 $u \in (0, 1)$ で二階微分 $f''(u) < 0$ の強凸関数）を採用。
- 赤道（$Z = 1.155\text{ m}$）から脇腹・お腹・お尻を通って足先（$X = \pm 0.258\text{ m}, Y = 0.0\text{ m}, Z = -0.068\text{ m}$）に至るまで、いかなる角度から見てもへこみ・くびれ・折れ目が一切生じないツルンと滑らかな一体造形を実現し、さらに下半部メッシュに20反復の体積保存型 Taubin スムージングを適用。

### ② 頭のラインの完全美化：$C^\infty$ 解析的ドーム曲線（Rev.4）
- 上半球（$Z \ge Z_{\text{eq}}$）の前後断面を純粋な楕円断面（`p = 2.0`, `f_yz = 1.0`）とし、正面頭頂プロファイルにピクセルLUTを一切使わない **$C^\infty$ 解析的ドーム関数** $Z_{\text{top}}(|X|) = Z_{\text{eq}} + (Z_{\text{apex}} - Z_{\text{eq}})(1 - (|X|/W_{\max})^2)^{0.480}$ を採用。全角度で完璧に綺麗で丸い頭頂ラインを実現。

### ③ 顔の青枠（`Face_Frame`）＆画面（`Face_Screen`）の2バージョン展開
- **【A】立体青枠版（`cvn_iinet_kun.*`）**:
  - 外径スケール `0.905倍`・枠幅係数 `0.54` のスリムな青枠を、ボディ表面から法線方向へ $+0.038\text{ m}$ ぷっくりと立体ベゼル状に隆起させた仕様。
- **【B】非立体フラット青枠版（`cvn_iinet_kun_flat_frame.*`）**:
  - 青枠（`Face_Frame`, $r \in [r_{\text{in}}, r_{\text{out}}]$）と画面（`Face_Screen`, $r \in [0, r_{\text{in}}]$）の断面アーチ隆起を廃止し、両者をボディ前面曲面から法線方向へ均一な $+0.0007\text{ m}$（$0.7\text{ mm}$）の極薄コンフォーマル・フラッシュシェルとして同一面上に配置。
  - さらに両オブジェクトの Cycles `visible_shadow = False` を設定し、ボディ表面法線と完全に一致させることで、側面・上面・底面・斜め3/4のどこから見ても青枠がボディの丸い輪郭から一切出っ張らず、段差影もない滑らかなフラッシュ曲面仕様とした（目・口・胸元 `LILI-net` ロゴのぷっくりした3D立体感はそのまま維持）。

### ④ 尻尾先端の地球儀真下接続・全周360度地球儀テクスチャ・Cycles 3DCGマット質感
- 尻尾はお尻から解析的余弦S字カーブを描いて地球儀の真下（南極中心 $Z = 2.1925\text{ m}$）へ垂直に接続。
- 地球儀には全周360度に世界の大陸・半島・島列を配置した `2048 × 1024 px` テクスチャを適用。
- Freestyle黒輪郭線および自己発光（`Emission`）を完全ゼロとし、Cycles GPU＋4灯スタジオソフトボックス照明による上品な3DCGマット質感（`Roughness = 0.94, Specular = 0.08`）でレンダリング。
