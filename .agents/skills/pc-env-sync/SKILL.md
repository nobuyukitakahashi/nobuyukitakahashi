---
name: pc-env-sync
description: >
  複数PC間で nobuyukitakahashi プロジェクトのAntigravity実行環境（Git最新化、~/.gitconfig初期設定、全14ホスト統合 ~/.ssh/config 構築、グローバルスキル、
  Obsidian MCPサーバー設定、Blender MCPサーバー設定、Adobe Illustrator MCPサーバー設定、
  Adobe Photoshop MCPサーバー設定、Adobe Premiere Pro MCPサーバー設定、Adobe After Effects MCPサーバー設定、
  PTGui Pro 13 MCPサーバー設定、NotebookLM認証ディレクトリ準備）を一言で完全同期・再現するスキル。
  ユーザーが「このPCの環境セットアップをして」「環境同期して」「別PCの初期設定をして」と指示した際、
  または /pc-env-sync 実行時に使用する。
---

# マルチPC環境同期スキル (`/pc-env-sync`)

## 概要
複数のPC（Windows / macOS、別ドライブレターや別ワークスペース含む）で同じ `nobuyukitakahashi` プロジェクトを継続利用する際、PCローカル（`C:\Users\<ユーザー名>\` や `~/`、`~/.gemini/`）に依存する設定を一括で構築・同期します。

スクリプト内部で **`nobuyukitakahashi` ワークスペースの実パス・Google Drive ルート・Obsidian Vault パスを自動探索**するため、PCごとにドライブレター（`G:\`, `H:\`, `D:\` 等）や配置先が異なっても、また別ワークスペースからグローバルスキルとして呼び出された場合でも安全に動作します。
（※ 部門オーケストレーション系7スキル `coo-orchestrator` / `research-dept` / `creative-dept` / `marketing-dept` / `delivery-dept` / `system-evolution` / `legal-dept` は `nobuyukitakahashi` プロジェクト固有のため、意図的にグローバル同期対象外としています）

## 実行手順

1. **同期スクリプトの実行（OS自動判定・ポータブル実行）**
   - **Windows 環境の場合**:
     カレントディレクトリ内の `.agents\skills\pc-env-sync\scripts\sync_pc_env.ps1`、またはグローバル配置先 `$env:USERPROFILE\.gemini\config\skills\pc-env-sync\scripts\sync_pc_env.ps1` のいずれか存在する方を実行する（見つからない場合は別ドライブ上の `nobuyukitakahashi` を探索して実行する）。
     ```powershell
     $s = @(
       ".agents\skills\pc-env-sync\scripts\sync_pc_env.ps1",
       "$env:USERPROFILE\.gemini\config\skills\pc-env-sync\scripts\sync_pc_env.ps1"
     ) | Where-Object { Test-Path $_ } | Select-Object -First 1
     if (-not $s) { throw "sync_pc_env.ps1 が見つかりません。nobuyukitakahashi ワークスペースを開いて実行してください。" }
     powershell -NoProfile -ExecutionPolicy Bypass -File $s
     ```
     ※ 特定パスを明示したい場合は `-WorkspaceRoot "<パス>"` を付与可能。
   - **macOS 環境の場合**:
     カレントディレクトリ内の `.agents/skills/pc-env-sync/scripts/sync_mac_env.sh`、またはグローバル配置先 `~/.gemini/config/skills/pc-env-sync/scripts/sync_mac_env.sh` のいずれか存在する方を実行する。
     ```bash
     for s in ".agents/skills/pc-env-sync/scripts/sync_mac_env.sh" "$HOME/.gemini/config/skills/pc-env-sync/scripts/sync_mac_env.sh"; do
       if [ -f "$s" ]; then bash "$s"; break; fi
     done
     ```
     ※ 特定パスを明示したい場合は `--workspace "<パス>"` を付与可能。

2. **NotebookLM MCPの認証状態チェック**
   - `notebooklm-research` MCP の `get_health` を呼び出す。
   - `authenticated: false` の場合のみ、ユーザーに「このPCでの初回Googleログインを行うため `setup_auth` を起動しますか？」と案内する。
   - ※もし `setup_auth` でログイン完了後に `https://notebook.google.com/` へリダイレクトされて待機ループが残った場合は、`chrome_profile` から `AuthManager.saveBrowserState()` で `state.json` を書き出して認証を完了させる。

3. **完了報告・引き継ぎ確認**
   - 検出された `Workspace` / `VaultPath`、Git同期状態、グローバルスキル／ルール同期状態、公式 Blender Lab MCP（`blender-mcp` クライアント設定・`BLENDER_PATH`・Blenderアドオン `bl_ext.user_default.mcp` ＆ Online Access 有効化状態）、SSH鍵の有無（未配置時は案内）、NotebookLM認証状態を簡潔に報告する。
   - `mcp_config.json` が新規作成・更新された場合は、Antigravity のリロード（または再起動）で新しい MCP サーバーが反映される旨を案内する。

4. **SSH秘密鍵の暗号化バックアップ／復元（`ssh_vault.js`）**
   - 秘密鍵やパスワードは **GitHub・チャットログ・ワークスペース内へ絶対に保存しない**。
   - ユーザーが「SSH鍵をバックアップしたい」「別PCにSSH鍵を復元したい」と指示した場合は、同梱の `ssh_vault.js` をユーザー自身のターミナルで実行するよう案内する（パスワードは端末上で非表示入力）：
     - **暗号化バックアップ作成**（Google Drive 上の Git 管理外 `<DriveRoot>/_private_backup/ssh/ssh_keys_latest.agyvault` およびタイムスタンプ付き世代スナップショットを AES-256-GCM で作成）:
       ```powershell
       # Windows / macOS 共通（パスはグローバル配置先またはワークスペース内）
       node "$HOME/.gemini/config/skills/pc-env-sync/scripts/ssh_vault.js" backup
       ```
     - **復元**（既存ファイルは `~/.ssh_pre_restore_<timestamp>/` へ退避した上で復元し、macOS は `chmod 700/600`、Windows は `icacls` で本人限定 ACL を自動設定）:
       ```powershell
       node "$HOME/.gemini/config/skills/pc-env-sync/scripts/ssh_vault.js" restore
       ```
     - **中身を確認（書き換えなし）**:
       ```powershell
       node "$HOME/.gemini/config/skills/pc-env-sync/scripts/ssh_vault.js" verify
       ```
