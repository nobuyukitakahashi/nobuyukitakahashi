---
name: system-evolution
description: >-
  基盤・組織進化部門（05_System_Evolution_Dept）を稼働し、Antigravity最新仕様・利用可能モデル・verify_org.py機械監査・MCP/Hooks/PC同期基盤を自律最適化するスキル。
  定期点検や /system-evolution 実行時に使用。
---

# 基盤・組織進化部門（`05_System_Evolution_Dept`）実行スキル (`/system-evolution`)

1. [`05_System_Evolution_Dept/AGENTS.md`](../../../05_System_Evolution_Dept/AGENTS.md) と [`.agents/rules/global-policy.md`](../../rules/global-policy.md) を読み込む。
2. `system-evolution-dept` を起動し以下を実行：
   - 内蔵スキル（`agy-customizations` / `antigravity-guide`）および必要に応じて公式ドキュメントで最新仕様を確認。
   - `swarm(action="models", all=true)` で新モデル・残クォータを確認。
   - `python 07_QA_Dept/scripts/verify_org.py` を実行し、ルール24KB上限・UTF-8(BOMなし)・Frontmatter・`INDEX.md` リンク/直置き・構文を機械監査。
   - 必要に応じルール・スキル・Hooks・MCP基盤を更新し、`global-master-rules` §4 に従いローカル同期・Git反映。
   - `05_System_Evolution_Dept/evolution_logs/evolution_[YYYYMMDD].md` および `AICHANGELOG.md` を記録。
3. 監査結果と改善内容をユーザーへ報告する。
