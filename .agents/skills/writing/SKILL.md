---
name: writing
description: >-
  リサーチ結果（NotebookLM × Web調査）に基づく記事執筆・コラム・企画書・会議資料・法務/システム仕様書・
  スタンドアロンWeb HTMLレポートの作成とセルフ校正を専任で実行し、
  中間成果物を 02_Creative_Dept/writing/ に、最終成果物を 04_Delivery_Dept/outputs/writing/ に格納するスキル。
  ユーザーが /writing を指定した際、またはジャンル選択で「Writing / Document（記事執筆・企画書・Web HTML）」を選択した際に使用する。
---

# 📝 Writing & Documents（記事執筆・企画書・会議資料・Web HTML）専任スキル (`/writing`)

## 1. ジャンル別ディレクトリ規約（厳守）
- **初稿ドラフト・構成案置き場**:
  - [`02_Creative_Dept/writing/drafts/`](../../../02_Creative_Dept/writing/drafts/)
  - ファイル名規則：`draft_[テーマ名].md`
- **制作部門の完成中間成果物置き場**:
  - [`02_Creative_Dept/writing/final_outputs/`](../../../02_Creative_Dept/writing/final_outputs/)
  - ファイル名規則：`content_[テーマ名].md`（および必要に応じた `.html` / 図表）
- **最終納品フォルダ（`04_Delivery_Dept` による格納先）**:
  - [`04_Delivery_Dept/outputs/writing/`](../../../04_Delivery_Dept/outputs/writing/)
  - ※納品台帳 [`04_Delivery_Dept/outputs/INDEX.md`](../../../04_Delivery_Dept/outputs/INDEX.md) の「`## 📝 4. Writing & Documents`」セクションにリンク（`writing/ファイル名`）を追記する。

---

## 2. 実行手順

1. **インプット確認**:
   - `01_Research_Dept/reports/report_[テーマ名].md`（またはユーザーからの直接の執筆・資料作成要件）を読み込み、ファクト・数値・出典を正確に把握する。
2. **ドラフト執筆（`02_Creative_Dept/writing/drafts/`）**:
   - [`02_Creative_Dept/AGENTS.md`](../../../02_Creative_Dept/AGENTS.md) の「A. テキストコンテンツ制作手順」および「執筆のトンマナ・構成ルール」に従い、初稿を `02_Creative_Dept/writing/drafts/draft_[テーマ名].md` に作成する。
3. **セルフ校正（品質・ファクトチェック）**:
   - 誤字脱字、表記ゆれ、ハルシネーション（リサーチにない事実や数値の創作）がないか厳密に点検する。
4. **完成原稿の出力と最終納品**:
   - 校正済みの完成原稿を `02_Creative_Dept/writing/final_outputs/content_[テーマ名].md` に保存する。
   - 後続の `03_Marketing_Dept`（および該当時は `06_Legal_Dept`）を経て、`04_Delivery_Dept` が `04_Delivery_Dept/outputs/writing/` に統合パッケージ `output_[YYYYMMDD]_[テーマ名]_full.md`（および指定フォーマット `.html`, `.csv`, `.json` 等）を格納し、`04_Delivery_Dept/outputs/INDEX.md` を更新する。
