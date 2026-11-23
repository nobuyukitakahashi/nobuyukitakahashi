---
name: research-dept
description: >-
  リサーチ部門（01_Research_Dept）を稼働させ、指定されたテーマについて Google NotebookLM（MCP: notebooklm-research）の
  蓄積ナレッジ照会および2026年基準のWeb調査を実行して 01_Research_Dept/reports/ に中間レポートを出力した後、
  04_Delivery_Dept を通じて固定出力フォルダ 04_Delivery_Dept/outputs/ にも最終成果物を納品するスキル。
  NotebookLMの操作・調査や /research-dept コマンド実行時に使用する。
---

# リサーチ部門（`01_Research_Dept`：NotebookLM × Web調査）実行スキル

1. [`01_Research_Dept/AGENTS.md`](../../../01_Research_Dept/AGENTS.md) および [`.agents/rules/global-policy.md`](../../rules/global-policy.md) を読み込む。
2. `01_Research_Dept/inputs/` 内の未完了タスクファイルを確認する。未作成の場合は `01_Research_Dept/inputs/task_[YYYYMMDD]_[テーマ名].md` を作成する。
3. `define_subagent`（**`EnableWriteTools: true`, `EnableMCPTools: true`**）および `invoke_subagent` で `research-dept` サブエージェントを起動し、以下を実行させる：
   - **NotebookLM / Gemini Notebook ハイブリッド連携**:
     - **公式API MCP（`gemini-notebook`）**: ノートブック一覧・作成・リネーム、Web/YouTube/テキスト/ローカルファイル（最大200MiB）の高速ソース投入・処理状態監視を優先使用する。
     - **既存ブラウザMCP（`notebooklm-research`）**: 公式API（Public Preview）で未実装のグラウンディング質問（`ask_question`）・引用抽出および音声解説生成（`generate_audio`）を担当する。
   - **Web検索（`search_web`）**: 2026年基準の最新情報と信頼できる出典URLの調査
   - `01_Research_Dept/reports/report_[テーマ名].md` の出力
   - `01_Research_Dept/inputs/task_[YYYYMMDD]_[テーマ名].md` 先頭への `[完了]` 追記
4. **固定出力ルールの適用**: 単体実行時であっても、最終成果物をユーザーが `04_Delivery_Dept/outputs/` で受け取れるよう、続けて `delivery-dept` サブエージェントを起動し、指定フォーマットで `04_Delivery_Dept/outputs/` に格納・`INDEX.md` を更新する。
