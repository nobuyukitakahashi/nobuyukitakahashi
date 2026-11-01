---
name: research-dept
description: >-
  リサーチ部門（01_Research_Dept）を稼働させ、指定されたテーマについて2026年基準のWeb調査を実行して
  01_Research_Dept/reports/ に中間レポートを出力した後、04_Delivery_Dept を通じて
  固定出力フォルダ 04_Delivery_Dept/outputs/ にも最終成果物を納品するスキル。
  /research-dept コマンド実行時に使用する。
---

# リサーチ部門（`01_Research_Dept`）実行スキル

1. [`01_Research_Dept/AGENTS.md`](../../../01_Research_Dept/AGENTS.md) および [`.agents/rules/global-policy.md`](../../rules/global-policy.md) を読み込む。
2. `01_Research_Dept/inputs/` 内の未完了タスクファイルを確認する。未作成の場合は `01_Research_Dept/inputs/task_[YYYYMMDD]_[テーマ名].md` を作成する。
3. `define_subagent` および `invoke_subagent` で `research-dept` サブエージェントを起動し、以下を実行させる：
   - `search_web` による最新情報（2026年基準）と信頼できる出典URLの調査
   - `01_Research_Dept/reports/report_[テーマ名].md` の出力
   - `01_Research_Dept/inputs/task_[YYYYMMDD]_[テーマ名].md` 先頭への `[完了]` 追記
4. **固定出力ルールの適用**: 単体実行時であっても、最終成果物をユーザーが `04_Delivery_Dept/outputs/` で受け取れるよう、続けて `delivery-dept` サブエージェントを起動し、指定フォーマットで `04_Delivery_Dept/outputs/` に格納・`INDEX.md` を更新する。
