# Gemini Notebook Official API Local MCP Server (`gemini-notebook`)

Google 公式 **Gemini Notebook REST API（`https://notebook.googleapis.com/v1` / `/upload/v1`）** へ接続する、ゼロ外部依存のローカル stdio MCP サーバーおよび CLI ブリッジです。

## 既存 `notebooklm-research` とのハイブリッド役割分担

公式 Gemini Notebook API（Public Preview）は高速・高安定である一方、現時点では **RAG 質問応答（Q&A）や音声解説（Audio Overview）生成には未対応** です。そのため、本環境では以下のハイブリッド運用を行います。

| MCP サーバー名 | 通信方式 | 担当機能 |
| :--- | :--- | :--- |
| **`gemini-notebook`（本サーバー）** | 公式 REST API (`notebook.googleapis.com/v1`) + OAuth 2.0 自動リフレッシュ | ノートブック一覧・取得・作成・リネーム、Web/YouTube/Text/Markdown ソース追加、ローカルファイルアップロード（最大 200 MiB）、ソース処理状態監視 |
| **`notebooklm-research`（既存）** | ブラウザセッション (`state.json`) | ノートブックへのグラウンディング質問（`ask_question`）、音声解説生成（`generate_audio`） |

## 認証仕様（1時間失効問題の解消）

公式リモート MCP（`https://notebook.googleapis.com/mcp`）にアクセストークンを直接記載すると約1時間で失効します。本ローカル MCP サーバーは **`refresh_token` による自動更新** を内蔵しており、初回ログイン後はトークン失効を自動回避します。

認証情報の保存先（Git 管理外のローカル OS 保護領域）：
- **Windows**: `%LOCALAPPDATA%\gemini-notebook-mcp\`
- **macOS**: `~/Library/Application Support/gemini-notebook-mcp/`

### 複数端末間での自動同期
`/pc-env-sync`（`sync_pc_env.ps1` / `sync_mac_env.sh`）を実行すると、上記ローカル領域の `config.json` と `tokens.json` が **Git 管理外の Google Drive プライベート領域（`<DriveRoot>/_private_backup/gemini-notebook-mcp/`）** と更新日時ベースで双方向自動同期されます。
これにより、1台のPCで初回ログインを完了すれば、他の Windows / Mac 端末では再ログインや `client_secret.json` の再設定なしで即座に利用できます。

## 初回セットアップ手順（個人 Google アカウント向け）

### 前提条件
- 個人用 Google アカウント（`@gmail.com` 等。Google Workspace アカウントは Public Preview 非対応）
- 対象アカウントで一度ブラウザから `https://notebook.google.com` にサインイン済みであること
- Google Cloud プロジェクトを 1 つ作成し、**Gemini Notebook API (`notebook.googleapis.com`)** を有効化済みであること

### 方式 A（推奨・`gcloud` CLI 不要）：OAuth 2.0 デスクトップクライアント方式

1. Google Cloud Console で対象プロジェクトを開き、`notebook.googleapis.com` を有効化します。
2. 「API とサービス」→「OAuth 同意画面」でユーザータイプを **外部**（テストユーザーに自分の個人 Google アカウントを追加）に設定し、スコープに `https://www.googleapis.com/auth/notebook` を許可します。
3. 「認証情報」→「認証情報を作成」→「OAuth クライアント ID」→ アプリケーションの種類 **デスクトップ アプリ** を作成し、JSON ファイル（`client_secret_*.json`）をダウンロードします。
4. ターミナルで以下 2 コマンドを実行します：

```powershell
# 1. クライアント設定をローカルOS領域へ保存（Gitリポジトリには保存されません）
node .agents/mcp/gemini-notebook-mcp/cli.js auth-setup --client-secret "C:\path\to\client_secret.json" --project "<YOUR_GCP_PROJECT_ID>"

# 2. ブラウザで初回ログイン（refresh_token を自動保存）
node .agents/mcp/gemini-notebook-mcp/cli.js login

# 3. 実API疎通確認
node .agents/mcp/gemini-notebook-mcp/cli.js status --live
```

### 方式 B：`gcloud` CLI（ADC）を利用する場合

```bash
gcloud services enable notebook.googleapis.com --project="<YOUR_GCP_PROJECT_ID>"
gcloud auth application-default login --scopes="https://www.googleapis.com/auth/cloud-platform,https://www.googleapis.com/auth/notebook"
gcloud auth application-default set-quota-project "<YOUR_GCP_PROJECT_ID>"
node .agents/mcp/gemini-notebook-mcp/cli.js status --live
```

## 提供 MCP ツール一覧

- `get_gemini_notebook_status`
- `list_notebooks`
- `get_notebook`
- `create_notebook`
- `rename_notebook`
- `list_sources`
- `get_source`
- `add_web_source`
- `add_text_source`
- `upload_file_source`
