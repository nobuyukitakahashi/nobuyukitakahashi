---
name: marketing-dept
description: >-
  マーケティング部門（03_Marketing_Dept）を稼働し、完成原稿からSNS・PR告知文を作成・納品するスキル。
  /marketing-dept 実行時に使用。
---

# マーケティング部門（`03_Marketing_Dept`）実行スキル (`/marketing-dept`)

1. [`03_Marketing_Dept/AGENTS.md`](../../../03_Marketing_Dept/AGENTS.md) と [`.agents/rules/global-policy.md`](../../rules/global-policy.md) を読み込む。
2. 対象原稿 `02_Creative_Dept/<genre>/final_outputs/<案件サブフォルダ>/content_[テーマ名].md` の存在を確認。
3. `marketing-dept` を起動し `03_Marketing_Dept/promos/promo_[テーマ名].md` を作成。
4. 単体実行時も `delivery-dept` を起動し `04_Delivery_Dept/outputs/<genre>/<案件サブフォルダ>/` 格納・`INDEX.md` 更新まで完了する。
