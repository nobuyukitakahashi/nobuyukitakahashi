---
name: system-evolution
description: >-
  組織進化部門（05_System_Evolution_Dept）を稼働し、Antigravity最新仕様・利用可能モデル・ルール/スキル容量と実行ログを監査して自律改善するスキル。
  定期点検や /system-evolution 実行時に使用。
---

# 組織進化・Antigravity最新仕様監査部門（`05_System_Evolution_Dept`）実行スキル (`/system-evolution`)

1. [`05_System_Evolution_Dept/AGENTS.md`](../../../05_System_Evolution_Dept/AGENTS.md) と [`.agents/rules/global-policy.md`](../../rules/global-policy.md) を読み込む。
2. `system-evolution-dept` を起動し以下を実行：
   - 内蔵スキル（`agy-customizations` / `antigravity-guide`）および公式ドキュメント（`antigravity.google/docs/changelog.md` 等）で最新仕様を確認。
   - `swarm(action="models", all=true)` で新モデル・残クォータを確認。
   - `00_COO/task_logs/`・固定出力ルール遵守・ルール容量（24KB上限）・重複/リンク切れを監査し、必要に応じ `AGENTS.md` / `SKILL.md` を自律更新（`global-master-rules` §4 に従い同期・Git反映）。
   - `05_System_Evolution_Dept/evolution_logs/evolution_[YYYYMMDD].md` および `AICHANGELOG.md` を記録。
3. 監査結果と改善内容をユーザーへ報告する。
