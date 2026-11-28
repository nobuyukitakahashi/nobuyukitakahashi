---
name: gemini-notebook
description: >-
  公式 Gemini Notebook REST API（notebook.googleapis.com/v1）連携スキル。ローカルMCPまたはRemote Agents環境からcli.js経由でノートブックCRUD・Web/YouTube/テキスト/ファイル投入を実行する際に使用。
---

# Gemini Notebook API 連携スキル (`/gemini-notebook`)

## 1. 実行経路の自動判定（ローカル vs Remote Agents）
- **ローカル環境（Windows / macOS）**: `~/.gemini/config/mcp_config.json` 登録済みの `gemini-notebook` MCP ツール（`get_gemini_notebook_status`, `list_notebooks`, `get_notebook`, `create_notebook`, `rename_notebook`, `list_sources`, `get_source`, `add_web_source`, `add_text_source`, `upload_file_source`）を優先利用する。
- **Remote Agents（クラウド Linux VM）/ MCP未接続環境**: 外部npm依存ゼロの Node.js CLI ブリッジ [`cli.js`](../../mcp/gemini-notebook-mcp/cli.js) を優先実行する。Python のみ環境やヘッドレス PKCE ログイン（`login-start` → `login-finish`）が必要な場合は [`nb.py`](../../scripts/nb.py)（同期先 `~/.local/bin/nb.py`）も利用可能。
- **役割分担**: Q&A（`ask_question`）と音声解説（`generate_audio`）はローカル専用 `notebooklm-research` MCP が担当し、公式 API による高速・自動リフレッシュ型の登録・投入・管理を本スキルが担当する。

## 2. 安全ルール（厳守）
- **削除 API が無いため作成・投入は明示時のみ**: 公式 API にノートブック/ソース削除機能が無いため、`create` / `add-web` / `add-text` / `upload` はユーザーが明示した時のみ実行する（`status` / `list` / `sources` は読み取り専用として安全）。
- **個人 Google アカウント専用**: 会社・学校のアカウントでは API が拒否する場合がある。`client_secret.json` はログインするアカウントと同一の Google アカウントで作成したものを使う（異なると `403 client_user_mismatch`）。
- **ヘッドレスログイン（`nb.py` 利用時）**:
  - 初回の認可 URL 発行はメールアドレス（`login_hint`）を付けずに `python3 ~/.local/bin/nb.py login-start` を実行し、承認 URL は Markdown リンクにせず ` ```text ` コードブロックで1行提示する。
  - テスト公開設定の GCP アプリは約7日でトークンが切れる場合があるため、`invalid_grant` 発生時は再認証を案内する。

## 2. CLI ブリッジ主要コマンド（Remote Agents 標準）
```bash
# 認証・疎通確認（/home/antigravity/upload からの自動シード対応）
node .agents/mcp/gemini-notebook-mcp/cli.js status --live

# ノートブック一覧・作成・リネーム
node .agents/mcp/gemini-notebook-mcp/cli.js notebooks-list --all
node .agents/mcp/gemini-notebook-mcp/cli.js notebook-create --name "調査テーマ"
node .agents/mcp/gemini-notebook-mcp/cli.js notebook-rename --notebook "notebooks/<id>" --name "新タイトル"

# ソース確認・Web/YouTube・テキスト・ファイル投入（最大200MiB）
node .agents/mcp/gemini-notebook-mcp/cli.js sources-list --notebook "notebooks/<id>" --all
node .agents/mcp/gemini-notebook-mcp/cli.js add-web --notebook "notebooks/<id>" --url "https://..." --wait
node .agents/mcp/gemini-notebook-mcp/cli.js add-text --notebook "notebooks/<id>" --title "議事録" --file "./notes.md" --wait
node .agents/mcp/gemini-notebook-mcp/cli.js upload-file --notebook "notebooks/<id>" --file "./doc.pdf" --wait
```

## 3. Remote Agents 認証受け渡し規約（秘密情報 Git 厳禁）
- `config.json` / `tokens.json` / `client_secret_*.json` は **絶対に Git へコミット・出力しない**。
- Remote Agents では Remote Project の **Upload Files** 機能で `gemini-notebook-config.json` と `gemini-notebook-tokens.json`（または `config.json` / `tokens.json`）を `/home/antigravity/upload/` へ一度アップロードすれば、`server.js` / `cli.js` が `~/.config/gemini-notebook-mcp/` へ自動シードし、`refresh_token` で自動更新する。
- 環境変数での注入も可：`GEMINI_NOTEBOOK_PROJECT_ID`, `GEMINI_NOTEBOOK_CLIENT_ID`, `GEMINI_NOTEBOOK_CLIENT_SECRET`, `GEMINI_NOTEBOOK_REFRESH_TOKEN`（または `GEMINI_NOTEBOOK_ACCESS_TOKEN`）。
