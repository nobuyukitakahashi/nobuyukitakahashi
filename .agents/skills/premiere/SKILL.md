---
name: premiere
description: >-
  Adobe Premiere Pro 2027（MCP premiere / CLI）によるシーケンス編集・フレームPNG監査・.prproj保存・メディア書き出しスキル。
  /premiere 指定時、または Premiere Pro 映像編集依頼時に使用。
---

# 🎞️ Adobe Premiere Pro 映像編集・タイムライン制御専任スキル (`/premiere`)

## 1. ディレクトリ規約
- 試作・JSX・監査PNG：`02_Creative_Dept/premiere/drafts/<案件サブフォルダ>/`
- 中間成果物：`02_Creative_Dept/premiere/final_outputs/<案件サブフォルダ>/`
- 最終納品先：`04_Delivery_Dept/outputs/premiere/<案件サブフォルダ>/`（[`INDEX.md`](../../../04_Delivery_Dept/outputs/INDEX.md) を更新）

## 2. 実行手順（MCP `premiere` ＆ CLI ハイブリッド）
詳細JSX仕様は [`references/extendscript-guide.md`](references/extendscript-guide.md) を参照。

1. **稼働確認**: MCP `get_premiere_status` または `node .agents/mcp/premiere-mcp/cli.js status`。`cepBridge.active: false` 時は Premiere Pro で `ウィンドウ > エクステンション > Antigravity MCP Bridge` を開くよう案内。
2. **構成把握**: `get_project_summary`（`cli.js summary`）でシーケンス・トラック・クリップ情報を取得。
3. **JSX 編集**: `drafts/<案件サブフォルダ>/edit_[テーマ名].jsx` を `execute_premiere_jsx`（`cli.js exec --file <jsx>`）で実行。
4. **視覚監査ループ**: `export_frame_png`（`cli.js export-png --out <png> --time <秒>`）出力後、`read_file` で映像・テロップ・崩れを確認・修正。
5. **保存・書き出し・納品**: `save_or_export_premiere`（`cli.js save --save-as <.prproj>` / `--export-out`＋`--preset <.epr>`）で保存・書き出し、`qa-verifier` 合格後に `04_Delivery_Dept/outputs/premiere/<案件サブフォルダ>/` へ納品。
