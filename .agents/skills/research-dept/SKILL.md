---
name: research-dept
description: >-
  リサーチ部門（01_Research_Dept）を単体稼働させ、指定されたテーマまたは 01_Research_Dept/inputs/ 内のタスクについて
  2026年基準のWeb調査を実行し、01_Research_Dept/reports/ に構造化レポートを出力するスキル。
  リサーチのみを実行・再実行したい場合や /research-dept コマンド実行時に使用する。
---

# リサーチ部門（`01_Research_Dept`）単体実行スキル

1. [`01_Research_Dept/AGENTS.md`](../../../01_Research_Dept/AGENTS.md) および [`.agents/rules/global-policy.md`](../../rules/global-policy.md) を読み込む。
2. `01_Research_Dept/inputs/` 内の未完了タスクファイルを確認する。もしユーザーが直接テーマを指定していて `inputs/` にタスクファイルがまだ存在しない場合は、`01_Research_Dept/inputs/task_[YYYYMMDD]_[テーマ名].md` を先に作成する。
3. `define_subagent`（未定義の場合）および `invoke_subagent` で `research-dept` サブエージェントを起動し、以下を実行させる：
   - `search_web` による最新情報（2026年基準）と信頼できる出典URLの調査
   - `01_Research_Dept/reports/report_[テーマ名].md` の指定フォーマットでの出力
   - `01_Research_Dept/inputs/task_[YYYYMMDD]_[テーマ名].md` 先頭への `[完了]` 追記
4. 出力されたレポートを検収し、ファイルリンク付きでユーザーに報告する。
