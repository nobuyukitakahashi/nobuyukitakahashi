---
name: pc-env-sync
description: >
  複数PC間で nobuyukitakahashi プロジェクトのAntigravity実行環境（Git最新化、グローバルスキル、
  Obsidian MCPサーバー設定、Blender MCPサーバー設定、Adobe Illustrator MCPサーバー設定、
  Adobe Photoshop MCPサーバー設定、NotebookLM認証ディレクトリ準備）を一言で完全同期・再現するスキル。
  ユーザーが「このPCの環境セットアップをして」「環境同期して」「別PCの初期設定をして」と指示した際、
  または /pc-env-sync 実行時に使用する。
---

# マルチPC環境同期スキル (`/pc-env-sync`)

## 概要
複数のPCで同じ `nobuyukitakahashi` プロジェクトを継続利用する際、PCローカル（`C:\Users\<ユーザー名>\` または `~/.gemini/`）に依存する設定を一括で構築・同期します。

## 実行手順

1. **同期スクリプトの実行（OS別）**
   - **Windows 環境の場合**:
     以下のPowerShellスクリプトを実行し、Git最新化・グローバルスキル配置（`adobe-illustrator`, `adobe-photoshop`, 5大ジャンルスキル等を含む）・`@bitbonsai/mcpvault` 導入・Blender MCP & Adobe Illustrator MCP (`.agents/mcp/illustrator-mcp/server.js`) & Adobe Photoshop MCP (`.agents/mcp/photoshop-mcp/server.js`) 登録・`mcp_config.json` 更新・NotebookLM保存先フォルダ作成を一括で行う。
     ```powershell
     powershell -NoProfile -ExecutionPolicy Bypass -File "g:\マイドライブ\git\nobuyukitakahashi\.agents\skills\pc-env-sync\scripts\sync_pc_env.ps1"
     ```
   - **macOS 環境の場合**:
     以下のBashスクリプトを実行し、Mac側のGoogle Driveパス自動検出・Git最新化・グローバルスキル配置・`@bitbonsai/mcpvault` & `notebooklm-mcp` 導入・`mcp_config.json` 更新を一括で行う。
     ```bash
     bash .agents/skills/pc-env-sync/scripts/sync_mac_env.sh
     ```

2. **NotebookLM MCPの認証状態チェック**
   - `notebooklm-plugin_notebooklm-research` の `get_health` を呼び出す。
   - `authenticated: false` の場合のみ、ユーザーに「このPCでの初回Googleログインを行うため `setup_auth` を起動しますか？」と案内する。
   - ※もし `setup_auth` でログイン完了後に `https://notebook.google.com/` へリダイレクトされて待機ループが残った場合は、`chrome_profile` から `AuthManager.saveBrowserState()` で `state.json` を書き出して認証を完了させる。

3. **完了報告**
   - Git同期状態、Obsidian Vault接続状態、NotebookLM認証状態を簡潔に報告する。
