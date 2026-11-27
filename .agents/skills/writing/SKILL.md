---
name: writing
description: >-
  リサーチ結果に基づく記事・コラム・企画書・会議資料・仕様書・スタンドアロンWeb HTMLの作成と校正を行う執筆スキル。
  /writing 指定時、または文書・記事制作依頼時に使用。
---

# 📝 Writing & Documents 専任スキル (`/writing`)

## 1. ディレクトリ規約
- 初稿：`02_Creative_Dept/writing/drafts/<案件サブフォルダ>/draft_[テーマ名].md`
- 完成中間成果物：`02_Creative_Dept/writing/final_outputs/<案件サブフォルダ>/content_[テーマ名].md`（＋必要に応じ `.html` / 図表）
- 最終納品先：`04_Delivery_Dept/outputs/writing/<案件サブフォルダ>/`（[`INDEX.md`](../../../04_Delivery_Dept/outputs/INDEX.md) の `5. Writing & Documents` を更新）

## 2. 実行手順
1. **インプット把握**: `01_Research_Dept/reports/report_[テーマ名].md`（または直接要件）のファクト・数値・出典を確認。
2. **初稿執筆**: [`02_Creative_Dept/AGENTS.md`](../../../02_Creative_Dept/AGENTS.md) §2 のトンマナ・構成（タイトル ➔ リード ➔ 本文 H2/H3 ➔ まとめ ➔ 出典）に従い `drafts/` へ初稿を作成。
3. **セルフ校正**: 誤字・表記ゆれ・ハルシネーション（リサーチにない数値/事実の創作）を排除。HTML出力時は3デバイス（PC/Tablet/Mobile）実画面監査を実施。
4. **出力・納品**: 校正済み原稿を `final_outputs/` へ保存し、後続工程（`03` / 条件付き `06` / `qa-verifier`）を経て `04_Delivery_Dept` が `outputs/writing/<案件サブフォルダ>/` へ格納・`INDEX.md` 更新。
