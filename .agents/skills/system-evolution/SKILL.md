---
name: system-evolution
description: >-
  組織進化・Antigravity最新仕様監査部門（05_System_Evolution_Dept）を稼働させ、
  Antigravityの最新機能・仕様（内蔵スキル agy-customizations / antigravity-guide や公式Changelog）および
  ワークスペース内の実行ログを点検し、指示を待たずに自律的にルール（AGENTS.md）やスキル（SKILL.md）を
  改善・最新化するスキル。定期点検や /system-evolution 実行時に使用する。
---

# 組織進化・Antigravity最新仕様監査部門（`05_System_Evolution_Dept`）実行スキル

1. [`05_System_Evolution_Dept/AGENTS.md`](../../../05_System_Evolution_Dept/AGENTS.md) および [`.agents/rules/global-policy.md`](../../rules/global-policy.md) を読み込む。
2. `define_subagent`（未定義の場合）および `invoke_subagent` で `system-evolution-dept` サブエージェントを起動し、以下を実行させる：
   - Antigravity内蔵スキル（`agy-customizations`, `antigravity-guide`）および必要に応じた公式ドキュメント（`https://antigravity.google/docs`, `https://antigravity.google/changelog`）から最新機能・カスタマイズ仕様を確認
   - `00_COO/task_logs/` や各部署の入出力状況（特に固定出力フォルダ `04_Delivery_Dept/outputs/` ルールの遵守状況）を監査
   - 改善点や新機能の活用余地があれば、各部署の `AGENTS.md` や `.agents/skills/*/SKILL.md` を自律的にアップデートし、`AICHANGELOG.md` に記録
   - 監査・進化レポートを `05_System_Evolution_Dept/evolution_logs/evolution_[YYYYMMDD].md` に出力
3. 監査結果および自律アップデート内容をユーザーに報告する。
