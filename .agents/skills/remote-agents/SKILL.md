---
name: remote-agents
description: >-
  Antigravity Remote Agents（クラウドVM）・Remote Control（自宅PC遠隔操作）・SSH・pc-env-syncの使い分けとサブ機運用セットアップ手順。 /remote-agents 指定時やクラウド実行相談時に使用。
---

# Remote Agents ＆ サブ機運用ガイド (`/remote-agents`)

## 1. 4モード使い分けマトリクス
| 方式 | 実行場所 | 電源要件 | 適用業務 | 起動例 |
| :--- | :--- | :--- | :--- | :--- |
| **Remote Agents** | Google 管理クラウド Linux VM | ローカル電源OFF可 | GitHub 開発、調査・執筆、`gemini-notebook-mcp`、`gdocs`/`gsheets` 等のクラウド連携 | `agy --remote-agent` / App / `antigravity.google` |
| **Remote Control** | 自宅/社内メイン PC | メイン機 ON 必須 | Blender / Adobe / Moho / DaVinci / PTGui / `G:\` ローカル資産・ローカル検証 | App 設定 ON / `agy --remote-control` / `agy remote-control start` |
| **Connect over SSH** | 自社 Linux サーバー | SSH 先 ON 必須 | Linux サーバー上の開発・コンテナ保守（App `v2.33.0+`） | App サイドバー `+` > `SSH Host…` |
| **別 PC ネイティブ同期** | 別 Windows / Mac 端末 | 利用 PC のみ ON | 新端末をフル環境（全 MCP・スキル・ルール）として構築 | [`/pc-env-sync`](../pc-env-sync/SKILL.md) |

## 2. Remote Agents 前提条件 ＆ 標準プロジェクト構成
- **アカウント要件**: 個人 Google アカウントの **Google AI Pro（有料版）** または **Google AI Ultra**（Free / AI Plus / Google Workspace / Business 非対応）。CLI は **`v1.4.12` 以上**。
- **GitHub リソース併設ルール**: Remote Agents ではローカル `~/.gemini/config/` が参照されないため、作業対象リポジトリ（例：`castvision.net` 等）と同じ Remote Project の **GitHub Resources** へ **`nobuyukitakahashi`** を併設する（同一オーナー `nobuyukitakahashi` 配下の複数リポを1プロジェクトへ接続可能）。これにより `AGENTS.md`・`.agents/skills/`・`global-master-rules`・`gemini-notebook-mcp` が自動で効く。
- **外部連携**:
  - **Cloud Plugins**: `/plugin`（または App `Customizations > Marketplace`）で `github` / `gdrive` / `gdocs` / `gsheets` / `gslides` / `gcalendar` を OAuth 接続。
  - **クラウド3点セット（`clasp` / `Gemini Notebook` / `Colab GPU`）**: Remote Agents の Linux VM 上で `bash .agents/scripts/bootstrap_remote_3kit.sh`（状態確認のみは `--check`）を実行すれば、`@google/clasp@3`・`uv`・`google-colab-cli`・`~/.local/bin/colab_api.py`・`~/.local/bin/nb.py` が自動導入され、Project の **Upload Files**（`/home/antigravity/upload/`）へ置いた認証ファイル（`gemini-notebook-config.json` / `gemini-notebook-tokens.json` / `clasprc.json` / `colab-keyring.cfg` / `colab-config.json`）も `0600` で自動シードされる（**秘密ファイルは Git 厳禁**）。詳細は [`/gemini-notebook`](../gemini-notebook/SKILL.md)・[`/clasp-gas-deploy`](../clasp-gas-deploy/SKILL.md)・[`/colab-api-gpu`](../colab-api-gpu/SKILL.md) を参照。
  - **ローカル専用リソース**: Blender / Adobe / Moho / DaVinci / PTGui / ローカル Obsidian Vault は Remote Agents では動作しないため **Remote Control** を使う。

## 3. `agy` CLI コマンド早見表
```bash
# Remote Agents 起動・プロジェクト作成・再開
agy --remote-agent                          # デフォルトリモートプロジェクト (CLI Project (<host>))
agy --remote-agent --project "<名前またはID>"
agy --remote-agent --new-project            # カレントフォルダ名で新規リモートプロジェクト作成
agy --remote-agent -c                       # 直近のリモート会話を再開
agy --remote-agent -r <conversation_id>     # 指定IDのリモート会話を再開

# Remote Control（メイン機遠隔操作）
agy --remote-control                        # セッション限定トンネル（終了で自動切断）
agy remote-control start --name "<名>-cli"  # 常駐デーモン登録（起動時自動接続は管理者権限で実行）
agy remote-control status                   # デーモン状態・インスタンス名確認
agy remote-control stop                     # デーモン停止・登録解除
```

## 4. Remote Agents セッション特有の制約・仕様
- **利用不可機能（公式仕様）**: `--print`（非対話モード）、`/codesearch`、`/diff`、`/fork`、`/rewind`、`/btw`、`/voice`、`!` シェル直打ち、`@` サブエージェント送信、ローカルPC上の MCP / スキル / プラグイン。
- **権限とモード**: Remote Agent セッションの既定権限プリセットは `always-proceed (turbo)`。`/config` 内の **Remote Agent** タブで `Permission Preset`・`Plan Review Policy`・`Agent Mode`（`default` / `accept-edits` / `plan`、`Shift+Tab` で切替可）を変更する。
- **`v2.36.0` `~/.agents/skills` 自動ディスカバリとの整合**: ローカルでは `pc-env-sync` により `~/.gemini/config/skills/` が優先されるため衝突せず、Remote Agents ではリポジトリ内 `.agents/skills/` がそのまま自動ロードされる。
