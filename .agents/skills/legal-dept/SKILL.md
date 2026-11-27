---
name: legal-dept
description: >-
  法務・コンプライアンス部門（06_Legal_Dept）を稼働し、薬機法・景表法・ステマ・知財・PII・契約書等の審査と安全な代替文案提示を行うスキル。
  法的リスク審査、契約・規約作成/確認、または /legal-dept 実行時に使用。
---

# 法務・コンプライアンス部門（`06_Legal_Dept`）実行スキル (`/legal-dept`)

1. [`06_Legal_Dept/AGENTS.md`](../../../06_Legal_Dept/AGENTS.md) と [`.agents/rules/global-policy.md`](../../rules/global-policy.md) を読み込む。
2. 審査対象の中間成果物（`01_Research_Dept/reports/`、`02_Creative_Dept/<genre>/final_outputs/<案件サブフォルダ>/`、`03_Marketing_Dept/promos/`）または法務依頼指示書を確認。
3. `legal-dept`（`EnableWriteTools: true, EnableMCPTools: false`）を起動し、`06_Legal_Dept/reviews/review_[テーマ名].md`（3段階判定・安全な代替文案・免責注記付き）を作成。
4. 続けて `delivery-dept` を起動し、審査結果および修正反映済み成果物を `04_Delivery_Dept/outputs/<genre>/<案件サブフォルダ>/` へ格納・`INDEX.md` 更新を行う。
