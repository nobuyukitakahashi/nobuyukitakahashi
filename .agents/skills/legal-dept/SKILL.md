---
name: legal-dept
description: >-
  法務・コンプライアンス部門（06_Legal_Dept）を条件付きまたはオンデマンドで稼働させ、
  制作原稿（02_Creative_Dept）・SNS告知文（03_Marketing_Dept）・議事録・契約書/利用規約案等に対する
  リーガルチェック（薬機法・景表法・ステマ規制・著作権・個人情報・契約リスク審査）と安全な代替表現の提示を行い、
  06_Legal_Dept/reviews/ に審査レポートを出力した後、04_Delivery_Dept を通じて
  固定出力フォルダ 04_Delivery_Dept/outputs/ に最終成果物を納品するスキル。
  法的リスクのある案件の審査時、契約書・規約の作成/確認時、または /legal-dept 実行時に使用する。
---

# 法務・コンプライアンス部門（`06_Legal_Dept`）実行スキル

1. [`06_Legal_Dept/AGENTS.md`](../../../06_Legal_Dept/AGENTS.md) および [`.agents/rules/global-policy.md`](../../rules/global-policy.md) を読み込む。
2. 審査対象となる中間成果物（`02_Creative_Dept/final_outputs/content_[テーマ名].md`、`03_Marketing_Dept/promos/promo_[テーマ名].md`、`01_Research_Dept/reports/report_[テーマ名].md`）、または `01_Research_Dept/inputs/task_[YYYYMMDD]_[テーマ名].md` の法務依頼指示書を確認する。
3. 未定義の場合は `define_subagent` で `legal-dept` サブエージェント（`EnableWriteTools: true`, `EnableMCPTools: false`, `EnableSubagentTools: false`）を定義し、`invoke_subagent` で起動して `06_Legal_Dept/reviews/review_[テーマ名].md` を作成させる。
   - 審査レポートには必ず3段階判定ステータス（`[APPROVED]` / `[CONDITIONAL_APPROVED]` / `[HOLD]`）と、リスク箇所に対する「そのまま使える安全な代替表現（修正文案）」および免責注記を含めさせる。
4. **固定出力ルールの適用**: 続けて `delivery-dept` サブエージェントを起動し、法務審査結果（および修正指示を反映した最終コンテンツ）を固定フォルダ `04_Delivery_Dept/outputs/` に格納・`INDEX.md` を更新する。
