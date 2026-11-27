# 役割定義：Creative部門（`02_Creative_Dept`：12大ジャンル制作）

ルート [`AGENTS.md`](../AGENTS.md) 定義の12ジャンル（主要5＋拡張7）へ分離し、必ず**案件別サブフォルダ（`<案件サブフォルダ>`）**で作業する。

## 1. ディレクトリ ＆ 専任スキル規約
- **作業領域（スクリプト・中間生成物）**: `02_Creative_Dept/<genre>/drafts/<案件サブフォルダ>/`
- **最終納品先（`04_Delivery_Dept` 単一正本）**: `04_Delivery_Dept/outputs/<genre>/<案件サブフォルダ>/`
- **着手前必須**: 対象 `<genre>` に対応する専任スキル `.agents/skills/<genre>/SKILL.md`（`web` は `wordpress-avada-maintenance`）を必ず読み込み、ツール接続・カラー/座標/解像度・視覚監査（`read_file` 実画像確認）規約を遵守する。
- モデル判定・`swarm` 昇格は `global-master-rules`（Blender詳細は `blender/SKILL.md`）に委任。

## 2. `writing` 執筆トンマナ・構成
- `01_Research_Dept/reports/report_[テーマ名].md` の事実・出典のみに基づき、`drafts/<案件サブフォルダ>/` へ初稿、`final_outputs/<案件サブフォルダ>/content_[テーマ名].md` へ校正済み原稿を出力する。
- 文体は「です・ます」調（別指定優先）、構成は「タイトル ➔ リード文 ➔ 本文（H2/H3）➔ まとめ ➔ 出典」。

## 3. 単一正本 ＆ 一時ファイルクリーンアップ原則
- `04_Delivery_Dept` への最終納品が完了し `07_QA_Dept` が `PASS` した後、**重複する大容量バイナリ（`.mp4`/`.wav`/`.blend`/`.glb`/`.psd`/`.aep`/`.drp` 等）や一時監査連番フレーム（`audit_frames/`、`frames_raw/`、試行TTS等）は `drafts/` / `final_outputs/` に残置せず削除**する。
- `drafts/<案件サブフォルダ>/` には **再現用スクリプト（`.py`/`.jsx`/`.ps1`）・軽量設定・代表コンタクトシート** のみ保全する。

## 4. 禁止事項
- リサーチや一次素材にない架空データ・数値の捏造禁止。
- `04_Delivery_Dept/outputs/` へ直接書き込まない（`04_Delivery_Dept` を通じて単一正本移管する）。
