---
name: research-dept
description: >-
  リサーチ部門（01_Research_Dept）を稼働し、NotebookLM / Gemini Notebook と 2026年Web調査でレポートを作成・納品するスキル。
  NotebookLM調査や /research-dept 実行時に使用。
---

# リサーチ部門（`01_Research_Dept`）実行スキル (`/research-dept`)

1. [`01_Research_Dept/AGENTS.md`](../../../01_Research_Dept/AGENTS.md) と [`.agents/rules/global-policy.md`](../../rules/global-policy.md) を読み込む。
2. `01_Research_Dept/inputs/task_[YYYYMMDD]_[テーマ名].md` を確認（未作成なら生成）。
3. `research-dept`（`EnableWriteTools: true, EnableMCPTools: true`）を起動し以下を実行：
   - **公式API MCP（`gemini-notebook`）**: ノート一覧・作成・リネーム・高速ソース投入（最大200MiB）を優先使用。
   - **ブラウザMCP（`notebooklm-research`）**: グラウンディング質問（`ask_question`）・引用抽出・音声解説生成（`generate_audio`）を担当。
   - **Web検索（`search_web`）**: 2026年最新情報・出典URL収集。
   - `01_Research_Dept/reports/report_[テーマ名].md` 保存 ＆ タスク先頭へ `[完了]` 追記。
4. 単体実行時も `delivery-dept` を起動し `04_Delivery_Dept/outputs/writing/<案件サブフォルダ>/` 格納・`INDEX.md` 更新まで完了する。
