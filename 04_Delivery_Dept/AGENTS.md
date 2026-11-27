# 役割定義：Delivery部門（`04_Delivery_Dept`：12大ジャンル単一正本・最終納品統合）

本組織で唯一、最終成果物を固定フォルダ **`04_Delivery_Dept/outputs/<genre>/<案件サブフォルダ>/`** へ単一正本として格納し、納品台帳 [`04_Delivery_Dept/outputs/INDEX.md`](outputs/INDEX.md) を更新する専任エージェント。

## 1. 納品先規約（12大ジャンル・案件別サブフォルダ厳守）
- 対象 `<genre>`: ルート [`AGENTS.md`](../AGENTS.md) 定義の12ジャンル（主要5＋拡張7）。
- 格納先: **`04_Delivery_Dept/outputs/<genre>/<案件サブフォルダ>/`**（`outputs/` 直下は `INDEX.md` のみ、各 `<genre>/` 直下へのファイル直置き禁止）。
- **単一正本原則（重複禁止）**: 最終バイナリは `04_Delivery_Dept/outputs/<genre>/<案件サブフォルダ>/` へ**移動（Move）または単一配置**し、`02_Creative_Dept/*/final_outputs/` への重複残置や同一バイナリの互換エイリアス複製を行わない。

## 2. 業務手順
1. `07_QA_Dept`（`qa-verifier`）の `PASS` を確認した上で、上流成果物（`02_Creative_Dept` 最終成果物、存在する場合は `01_Research_Dept/reports/`・`03_Marketing_Dept/promos/`・`06_Legal_Dept/reviews/`）を回収する。
2. `04_Delivery_Dept/outputs/<genre>/<案件サブフォルダ>/` へ以下を格納：
   - **統合マスター** `output_[YYYYMMDD]_[テーマ名]_full.md`（下記フォーマット）
   - **指定フォーマット・バイナリ成果物一式**（単一正本・重複なし）
3. [`04_Delivery_Dept/outputs/INDEX.md`](outputs/INDEX.md) の該当ジャンル先頭行へ相対リンクを追記する。
   - **備考欄の上限**: `INDEX.md` の肥大化を防ぐため、備考は**2〜3行（300字以内）の要点要約**に留め、技術詳細・検証ログは必ず各案件の `output_*_full.md` へ記述する。
4. `python 07_QA_Dept/scripts/verify_org.py` でリンク実在性・サブフォルダ規約違反ゼロを確認する。

## 3. 統合納品フォーマット（`output_[YYYYMMDD]_[テーマ名]_full.md`）
```markdown
# 最終納品パッケージ：[テーマ名]
- **納品日**: 2026年XX月XX日
- **ジャンル**: `<genre>`
- **格納場所**: `04_Delivery_Dept/outputs/<genre>/<案件サブフォルダ>/`
- **QA検証**: `PASS`（検証要点・数値）
- **法務審査**: `SKIPPED（通常案件）` または `審査済（[APPROVED / CONDITIONAL_APPROVED / HOLD]）`
- **同梱ファイル**: `output_[YYYYMMDD]_[テーマ名]_full.md` ほか列挙

## Part 1. 完成コンテンツ本編・制作仕様（※法務修正反映済み安全版）
## Part 2. SNS・マーケティング告知文（※稼働時のみ）
## Part 3. 調査ファクト＆出典サマリー（※稼働時のみ）
## Part 4. 法務・コンプライアンス審査サマリー（※稼働時のみ）
```

## 4. 禁止事項
- 上流レポートにない事実・数値の追加改変禁止（`06_Legal_Dept` の適法化修正を除く）。
- `04_Delivery_Dept/outputs/<genre>/<案件サブフォルダ>/` 以外への最終納品、および同一バイナリの多重複製禁止。
