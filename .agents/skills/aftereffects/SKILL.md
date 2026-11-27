---
name: aftereffects
description: >-
  Adobe After Effects 2027（MCP aftereffects / CLI）によるモーショングラフィックス・TVCM・コンポジション構築・.aep保存・映像書き出しスキル。
  /aftereffects 指定時、または After Effects 制作依頼時に使用。
---

# ✨ Adobe After Effects モーション・VFX制作専任スキル (`/aftereffects`)

## 1. ディレクトリ規約
- 試作・JSX・監査PNG：`02_Creative_Dept/aftereffects/drafts/<案件サブフォルダ>/`
- 中間成果物：`02_Creative_Dept/aftereffects/final_outputs/<案件サブフォルダ>/`
- 最終納品先：`04_Delivery_Dept/outputs/aftereffects/<案件サブフォルダ>/`（[`INDEX.md`](../../../04_Delivery_Dept/outputs/INDEX.md) の `Adobe After Effects 2027` を更新）

## 2. 実行手順（MCP `aftereffects` ＆ CLI ハイブリッド）
詳細JSX仕様は [`references/extendscript-guide.md`](references/extendscript-guide.md) を参照。

1. **稼働確認**: MCP `get_aftereffects_status`（`node .agents/mcp/aftereffects-mcp/cli.js status`）。既存 `.aep` は `get_project_summary`（`cli.js summary --file <.aep>`）で把握。
2. **JSX 構築**: `drafts/<案件サブフォルダ>/build_[テーマ名].jsx` を `execute_aftereffects_jsx`（`cli.js exec --file <jsx>`）で実行。
   - **1始まりインデックス厳守**: `proj.item(1)`, `comp.layer(1)` 等は1始まり、`app.beginUndoGroup()` / `endUndoGroup()` でラップ。
3. **視覚監査ループ**: `export_comp_frame_png`（`cli.js export-png --out <png> --comp <Comp名> --time <秒>`）で代表フレームを出力し、`read_file` でレイアウト・文字サイズ・アニメーション位置を監査・修正。
4. **保存・書き出し・納品**: `save_aftereffects_project`（`cli.js save --out <.aep>` / `--render-comp`＋`--render-out`）で保存・レンダリングし、`qa-verifier` 合格後に `04_Delivery_Dept/outputs/aftereffects/<案件サブフォルダ>/` へ納品・`INDEX.md` 更新。
