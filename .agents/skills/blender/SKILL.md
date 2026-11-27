---
name: blender
description: >-
  Blender 5.3/5.2（公式MCP blender・Headless CLI）による3Dモデリング・CG・ロゴ立体化・3Dアニメーション制作スキル。
  /blender 指定時、または Blender 3D制作依頼時に使用。
---

# 🎨 Blender 3Dモデリング・CG・アニメーション専任スキル (`/blender`)

## 1. ディレクトリ規約
- 試作・スクリプト：`02_Creative_Dept/blender/drafts/<案件サブフォルダ>/`
- 中間成果物：`02_Creative_Dept/blender/final_outputs/<案件サブフォルダ>/`
- 最終納品先：`04_Delivery_Dept/outputs/blender/<案件サブフォルダ>/`（[`INDEX.md`](../../../04_Delivery_Dept/outputs/INDEX.md) の `1. Blender` を更新）

## 2. 最適モデル Tier ＆ 接続規約
- **モデル基準**（`global-master-rules` §1〜2 準拠）：
  - **Tier 1**（一覧確認・単体配置・単純移動/リネーム/単色変更）：`Gemini 4 Hydrogen (Low/Medium)`（`gemini-4-hydrogen-low`）
  - **Tier 2**（`bpy`/`bmesh` 造形・ノード・リギング・アニメ・空間計算・デバッグ）：**`Gemini 4 Neon (High)`**（`gemini-4-neon-high`）
  - **Tier 3**（極限幾何・連続エラー再試行時）：**`Gemini 4 Neon (XHigh)`**（`gemini-4-neon-xhigh`）
  - **Tier 4**（長尺映像参照・GUI視覚照合中心）：`Gemini 4 Argon (Medium/High)` / `Carbon`
- **接続チェック（Blender 5.3 優先・5.2 互換）**:
  - 公式 MCP `blender`（`bl_ext.user_default.mcp` `localhost:9876`）の `get_objects_summary` / `execute_blender_code`（戻り値は必ず `result = {...}` の dict）を確認。
  - GUI未接続時は `execute_blender_code_for_cli` または CLI（`C:\Program Files\Blender Foundation\Blender 5.3\blender.exe` 優先、未導入時は `5.2` へフォールバック：`--background --python <script.py>`）を使用。

## 3. `bpy` / `bmesh` 制作鉄則
- シェーダーノードは名前ではなく `type`（`"BSDF_PRINCIPLED"` 等）で検索する。
- 原画色彩忠実再現時は `scene.view_settings.view_transform = 'Standard'`。
- **Blender 5.2/5.3 MP4出力順序**: 必ず先に `scene.render.image_settings.media_type = 'VIDEO'` ➔ 次に `file_format = 'FFMPEG'`（逆順は `Enum 'FFMPEG' not found` エラー）。
- **4:3 → 16:9 縦切れ防止**: 焦点距離を `lens_16_9 = lens_4_3 * 0.75`（または `sensor_fit = 'VERTICAL'`）へ補正し、背景横幅も拡張。
- 複数面図からの造形は正面・側面輪郭LUT＋コンフォーマル曲面投影、空間曲線パーツ（アンテナ・尻尾等）と球体は3D球心へ貫入接続。
- **マスコット造形・3Dアニメ（v7/v8しわゼロ変形）・同期SE生成**: 着手前に必ず [`references/mascot-animation-v8.md`](references/mascot-animation-v8.md) を参照。

## 4. 視覚監査 ＆ 納品
1. レンダリングした `.png`（またはキーフレーム比較ボード）を `read_file` で正面・側面・斜め3/4・背面まで目視監査し、破綻ゼロまで改修。
2. `qa-verifier`（`global-master-rules` §5）で検収後、`.blend` / `.glb` / `.png` / `.mp4` / `content_[テーマ名].md` を `final_outputs/` ➔ `04_Delivery_Dept/outputs/blender/<案件サブフォルダ>/` へ納品し `INDEX.md` を更新。
