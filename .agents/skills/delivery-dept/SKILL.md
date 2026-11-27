---
name: delivery-dept
description: >-
  納品統合部門（04_Delivery_Dept）を稼働し、上流中間成果物を変換・統合して 04_Delivery_Dept/outputs/<genre>/ へ格納・INDEX更新するスキル。
  出力形式変換・再パッケージングや /delivery-dept 実行時に使用。
---

# 納品統合部門（`04_Delivery_Dept`）実行スキル (`/delivery-dept`)

1. [`04_Delivery_Dept/AGENTS.md`](../../../04_Delivery_Dept/AGENTS.md) と [`.agents/rules/global-policy.md`](../../rules/global-policy.md) を読み込む。
2. 対象 `<genre>`（11ジャンルのいずれか）と `<案件サブフォルダ>` を確認。
3. `delivery-dept` を起動し、上流中間成果物を統合して `04_Delivery_Dept/outputs/<genre>/<案件サブフォルダ>/` へマスター `output_[YYYYMMDD]_[テーマ名]_full.md` および指定形式バイナリ一式を格納、`INDEX.md` を更新。
4. 出力ファイル実在性と `INDEX.md` 相対リンクを検収し、ファイルリンク付きで報告する。
