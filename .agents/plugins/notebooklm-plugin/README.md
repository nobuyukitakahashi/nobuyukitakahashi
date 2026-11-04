# NotebookLM Research Plugin (`01_Research_Dept` 連携用)

本プラグインは、リサーチ部門（`01_Research_Dept`）サブエージェントが Google **NotebookLM**（`notebooklm-mcp`）に直接アクセスし、以下の操作を行えるようにするためのワークスペースプラグインです。

## 主な機能
1. **ノートブック検索・一覧取得**: ご自身の Google アカウント内の NotebookLM ノートブック一覧やソース一覧を参照。
2. **グラウンディング質問・引用抽出**: NotebookLM 内の信頼できる資料群に対して質問を投げ、ハルシネーションのない回答と正確な引用（Citations）を取得。
3. **ソースの自動追加（Ingest）**: Web 調査で得た知見やレポートを NotebookLM のノートブックへソースとして追加。
4. **Audio Overview（音声概要）等の生成トリガー**: 必要に応じて NotebookLM のスタジオ機能を呼び出し。

## 初回セットアップ・有効化手順
1. 新しくプラグインディレクトリ（`.agents/plugins/notebooklm-plugin/`）を追加したため、**一度 Antigravity を再起動**すると MCP サーバー（`notebooklm-research`）が認識されます。
2. 初回呼び出し時に Google アカウントのブラウザセッション認証（ログイン）が求められた場合は、表示されるブラウザウィンドウで Google アカウントにログインしてください（以降は永続プロファイルにより自動接続されます）。
