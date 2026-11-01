---
name: marketing-dept
description: >-
  マーケティング部門（03_Marketing_Dept）を稼働させ、02_Creative_Dept/final_outputs/ の完成原稿から
  SNS・PR告知文を作成して 03_Marketing_Dept/promos/ に出力した後、
  04_Delivery_Dept を通じて固定出力フォルダ 04_Delivery_Dept/outputs/ に最終成果物を納品するスキル。
  /marketing-dept 実行時に使用する。
---

# マーケティング部門（`03_Marketing_Dept`）実行スキル

1. [`03_Marketing_Dept/AGENTS.md`](../../../03_Marketing_Dept/AGENTS.md) および [`.agents/rules/global-policy.md`](../../rules/global-policy.md) を読み込む。
2. 対象となる `02_Creative_Dept/final_outputs/content_[テーマ名].md` が存在することを確認する。
3. `define_subagent` および `invoke_subagent` で `marketing-dept` サブエージェントを起動し、`03_Marketing_Dept/promos/promo_[テーマ名].md` を作成させる。
4. **固定出力ルールの適用**: 続けて `delivery-dept` サブエージェントを起動し、固定フォルダ `04_Delivery_Dept/outputs/` に最終成果物を格納・`INDEX.md` を更新する。
