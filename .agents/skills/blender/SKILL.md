---
name: blender
description: >-
  Blender 5.2（MCPサーバー blender および Headless CLI）を用いた3Dモデリング、キャラクター造形、
  ロゴ3DベベルCG、マテリアル・ライティング、3Dアニメーション制作を専任で実行し、
  中間成果物を 02_Creative_Dept/blender/ に、最終成果物を 04_Delivery_Dept/outputs/blender/ に格納するスキル。
  ユーザーが /blender を指定した際、またはジャンル選択で「Blender（3Dモデリング・CG・3Dアニメ）」を選択した際に使用する。
---

# 🎨 Blender 3Dモデリング・CG・アニメーション専任スキル (`/blender`)

## 1. ジャンル別ディレクトリ規約（厳守）
- **試作・スクリプト・テクスチャ・参照画像置き場**:
  - [`02_Creative_Dept/blender/drafts/`](../../../02_Creative_Dept/blender/drafts/)
- **制作部門の完成中間成果物置き場**:
  - [`02_Creative_Dept/blender/final_outputs/`](../../../02_Creative_Dept/blender/final_outputs/)
- **最終納品フォルダ（`04_Delivery_Dept` による格納先）**:
  - [`04_Delivery_Dept/outputs/blender/`](../../../04_Delivery_Dept/outputs/blender/)
  - ※納品台帳 [`04_Delivery_Dept/outputs/INDEX.md`](../../../04_Delivery_Dept/outputs/INDEX.md) の「`## 🎨 1. Blender`」セクションにリンク（`blender/ファイル名`）を追記する。

---

## 2. 実行手順（MCP `blender` ＆ Headless CLI ハイブリッド運用）

1. **要件確認と接続チェック**:
   - [`02_Creative_Dept/AGENTS.md`](../../../02_Creative_Dept/AGENTS.md) の「B. Blender 3D / CG制作手順」に従う。
   - MCPサーバー `blender` の `get_addon_status` / `get_scene_info` を確認し、MCP未起動またはバッチ処理時は直ちにローカルの Blender 5.2 CLI（`"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" --background --python 02_Creative_Dept/blender/drafts/<script.py>`）へフォールバックする。
2. **`bpy` / `bmesh` 構築と鉄則の適用**:
   - シェーダーノードは名前ではなく `type`（`"BSDF_PRINCIPLED"` 等）で検索する。
   - 原画色彩の忠実再現時は `scene.view_settings.view_transform = 'Standard'` を設定する。
   - 複数面図（5面図等）からの造形時は正面・側面輪郭LUT抽出＋コンフォーマル曲面投影を用いる。
   - 同色パーツ（胴体と腕等）のソフビ一体成型時は `BOOLEAN (UNION)` ＋ 高解像度 `REMESH (VOXEL)` ＋ 正面2D外周シルエットロック付き2段階調和スムージング（`Smooth_Seam_3D` + `Smooth_Seam_Y`）で境界筋を完全除去する。
   - 空間曲線パーツ（アンテナ・尻尾等）と球体（地球儀等）は必ず3D球心へ直接貫入接続させる。
3. **視覚監査ループ（Visual Ground Truth）**:
   - 各ステップでレンダリングした `.png`（またはアニメーションのキーフレーム一覧ボード `.png`）を `read_file` で目視監査し、正面・側面・斜め3/4・背面すべての角度で破綻がないか検証・改修する。
4. **中間成果物出力と最終納品**:
   - 完成した `.blend` / `.glb` / `.png` / `.mp4` および制作仕様書 `content_[テーマ名].md` を `02_Creative_Dept/blender/final_outputs/` に保存する。
   - 続けて `04_Delivery_Dept` を通じて `04_Delivery_Dept/outputs/blender/` に最終成果物を格納し、`04_Delivery_Dept/outputs/INDEX.md` を更新する。
