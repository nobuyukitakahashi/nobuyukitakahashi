---
name: creative-dept
description: >-
  制作・編集部門（02_Creative_Dept）を稼働させ、01_Research_Dept/reports/ の調査レポートをもとに
  ドラフト執筆（drafts/）とセルフ校正を経て完成原稿（final_outputs/）を出力した後、
  04_Delivery_Dept を通じて固定出力フォルダ 04_Delivery_Dept/outputs/ に最終成果物を納品するスキル。
  /creative-dept コマンド実行時に使用する。
---

# 制作・編集部門（`02_Creative_Dept`）実行スキル

1. [`02_Creative_Dept/AGENTS.md`](../../../02_Creative_Dept/AGENTS.md) および [`.agents/rules/global-policy.md`](../../rules/global-policy.md) を読み込む。
2. 対象となる `01_Research_Dept/reports/report_[テーマ名].md` が存在することを確認する。
3. `define_subagent` および `invoke_subagent` で `creative-dept` サブエージェントを起動し、以下を実行させる：
   - 初稿 `02_Creative_Dept/drafts/draft_[テーマ名].md` の作成とセルフ校正
   - 完成原稿（中間成果物） `02_Creative_Dept/final_outputs/content_[テーマ名].md` の保存
4. **固定出力ルールの適用**: 単体実行時であっても、続けて `delivery-dept` サブエージェントを起動し、ユーザーが指定した形式で固定フォルダ `04_Delivery_Dept/outputs/` に最終成果物を格納・`INDEX.md` を更新する。
