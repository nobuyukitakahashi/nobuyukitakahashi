---
name: illustrator
description: >-
  Adobe Illustrator 2027（MCP illustrator / CLI）によるベクターロゴ・CMYK印刷入稿データ・アウトライン化・DTP制作スキル。
  /illustrator 指定時、またはベクター/印刷データ制作依頼時に使用。
---

# ✒️ Adobe Illustrator ベクター・DTP・CMYK印刷データ専任スキル (`/illustrator`)

## 1. ディレクトリ規約
- 試作・JSX：`02_Creative_Dept/illustrator/drafts/<案件サブフォルダ>/`
- 中間成果物：`02_Creative_Dept/illustrator/final_outputs/<案件サブフォルダ>/`
- 最終納品先：`04_Delivery_Dept/outputs/illustrator/<案件サブフォルダ>/`（[`INDEX.md`](../../../04_Delivery_Dept/outputs/INDEX.md) の `2. Adobe Illustrator` を更新）

## 2. 実行手順（MCP `illustrator` ＆ CLI ハイブリッド）
詳細JSXパターンは [`references/extendscript-guide.md`](references/extendscript-guide.md) を参照。

1. **稼働確認**: MCP `get_illustrator_status` または `node .agents/mcp/illustrator-mcp/cli.js status`。
2. **JSX ベクター構築**: `drafts/<案件サブフォルダ>/build_[テーマ名].jsx` を作成し、`execute_illustrator_jsx` または `cli.js exec --file <jsx>` で実行。
   - **CMYK厳守**: `DocumentColorSpace.CMYK`・`new CMYKColor()`・名前付きスウォッチ（`doc.swatches`）を使用。
   - **座標系注意**: `artboardRect = [left, top, right, bottom]` は Y上向き正、`rectangle(top, left, width, height)` の引数順に注意。
3. **視覚監査ループ**: `export_artboard_png`（`cli.js export-png --out <png> --scale 200`）で200%高解像度PNGを出力し、`read_file` で余白・文字配置・カーニング・CMYK発色を監査・修正。
4. **保存・納品**: `save_illustrator_document`（入稿版は `--outline-text true`）で `.ai`/`.pdf`/`.svg`/`.eps` と `content_[テーマ名].md` を保存し、`qa-verifier` 合格後に `04_Delivery_Dept/outputs/illustrator/<案件サブフォルダ>/` へ納品・`INDEX.md` 更新。
