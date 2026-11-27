---
name: photoshop
description: >-
  Adobe Photoshop 2027（MCP photoshop / CLI）による画像編集・フォトレタッチ・マルチレイヤーPSD合成・バナー/サムネイル制作スキル。
  /photoshop 指定時、または画像編集・PSD制作依頼時に使用。
---

# 🖼️ Adobe Photoshop 画像編集・レタッチ・PSD合成専任スキル (`/photoshop`)

## 1. ディレクトリ規約
- 試作・JSX・素材：`02_Creative_Dept/photoshop/drafts/<案件サブフォルダ>/`
- 中間成果物：`02_Creative_Dept/photoshop/final_outputs/<案件サブフォルダ>/`
- 最終納品先：`04_Delivery_Dept/outputs/photoshop/<案件サブフォルダ>/`（[`INDEX.md`](../../../04_Delivery_Dept/outputs/INDEX.md) の `3. Adobe Photoshop` を更新）

## 2. 実行手順（MCP `photoshop` ＆ CLI ハイブリッド）
詳細JSX（DOM + ActionManager）は [`references/extendscript-guide.md`](references/extendscript-guide.md) を参照。

1. **稼働確認**: MCP `get_photoshop_status` または `node .agents/mcp/photoshop-mcp/cli.js status`。
2. **JSX 構築**: `drafts/<案件サブフォルダ>/build_[テーマ名].jsx` を `execute_photoshop_jsx` または `cli.js exec --file <jsx>` で実行。
   - **単位・ダイアログ固定**: 冒頭で `app.displayDialogs = DialogModes.NO;`、`rulerUnits = Units.PIXELS;`、`typeUnits = TypeUnits.PIXELS;`（左上原点 `(0,0)`・X右正・Y下正）。
   - **高DPIフォント補正**: `300 dpi` 等では `new UnitValue(sizePx * (72.0 / doc.resolution), "pt")` で補正。
   - **非破壊階層**: 背景・ビジュアル・タイポグラフィを `LayerSet` で整理し編集可能 `.psd` を維持。
3. **視覚監査ループ**: `export_canvas_png`（`cli.js export-png --out <png> --scale 100`）出力後、`read_file` でレイアウト・文字・色味・境界を監査・修正。
4. **保存・納品**: `save_photoshop_document` で `.psd`（および `.png`/`.jpg`/`.tiff`）と `content_[テーマ名].md` を保存し、`qa-verifier` 合格後に `04_Delivery_Dept/outputs/photoshop/<案件サブフォルダ>/` へ納品・`INDEX.md` 更新。
