---
name: pc-env-sync
description: >-
  Windows/macOS複数PC間で Git・SSH・グローバルスキル/ルール・全MCPサーバー（Obsidian/Blender/Adobe/PTGui/Moho/NotebookLM等）と認証情報を一括同期するスキル。
  「環境同期して」「別PC初期設定」や /pc-env-sync 実行時に使用。
---

# マルチPC環境同期スキル (`/pc-env-sync`)

## 概要
PCローカル依存設定（`~/.gitconfig`, `~/.ssh/config`, `~/.gemini/config/` グローバルスキル・単一ソースマスタールール、全MCPサーバー設定、Blender公式アドオン、Moho Lua 5.4 Bridge、Gemini Notebook 認証のGoogle Drive双方向同期、SessionStart自動同期フック＆起動ショートカット）を一括同期する。ワークスペース実パス・Google Drive・Obsidian Vault は自動探索される。

## 実行手順
1. **OS別同期スクリプト実行**:
   - **Windows**:
     ```powershell
     $s = @(".agents\skills\pc-env-sync\scripts\sync_pc_env.ps1", "$env:USERPROFILE\.gemini\config\skills\pc-env-sync\scripts\sync_pc_env.ps1") | Where-Object { Test-Path $_ } | Select-Object -First 1
     if (-not $s) { throw "sync_pc_env.ps1 が見つかりません。" }
     powershell -NoProfile -ExecutionPolicy Bypass -File $s
     ```
     （※明示時は `-WorkspaceRoot "<パス>"`）
   - **macOS**:
     ```bash
     for s in ".agents/skills/pc-env-sync/scripts/sync_mac_env.sh" "$HOME/.gemini/config/skills/pc-env-sync/scripts/sync_mac_env.sh"; do
       if [ -f "$s" ]; then bash "$s"; break; fi
     done
     ```
     （※明示時は `--workspace "<パス>"`）
2. **NotebookLM MCP 認証確認**: `notebooklm-research` の `get_health` を確認し、`authenticated: false` の場合のみ `setup_auth` 起動を案内する（リダイレクト待機が残った場合は `chrome_profile` から `AuthManager.saveBrowserState()` で `state.json` 保存）。
3. **完了報告**: 検出パス・Git同期・スキル/ルール同期・Blender/Moho/各MCP状態・SSH鍵有無・NotebookLM認証状態を簡潔に報告し、`mcp_config.json` 更新時は Antigravity リロードを案内。

## SSH秘密鍵の暗号化バックアップ／復元（`ssh_vault.js`）
秘密鍵・パスワードは GitHub・チャット・ワークスペースへ絶対保存せず、ユーザー端末で直接実行してもらう（保存先：`<DriveRoot>/_private_backup/ssh/ssh_keys_latest.agyvault` AES-256-GCM）：
- バックアップ：`node "$HOME/.gemini/config/skills/pc-env-sync/scripts/ssh_vault.js" backup`
- 復元（既存退避＋権限自動設定）：`node "$HOME/.gemini/config/skills/pc-env-sync/scripts/ssh_vault.js" restore`
- 検証（読取専用）：`node "$HOME/.gemini/config/skills/pc-env-sync/scripts/ssh_vault.js" verify`
