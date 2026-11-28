# 組織自律進化・Remote Agents サブ機構成構築レポート（20261128-v37）
- **監査・構築対象**: `agy` CLI (`1.5.18`)、Antigravity Remote Agents / Remote Control 公式仕様、`gemini-notebook-mcp` クラウド対応、`.agents/skills` / `.gitignore` / `pc-env-sync`
- **判定ステータス**: `[UPDATED: Remote Agents ＆ gemini-notebook-mcp 構成整備完了]`

### 1. ローカル環境・公式仕様調査結果
- **`agy` CLI**: `C:\Users\nobuy\AppData\Local\agy\bin\agy.exe`（`v1.5.18`、`1.4.12` 以上を満たし `--remote-agent` / `--remote-control` / `remote-control start` 対応済み）。個人 Google アカウント（`consumer`）で keyring 認証済み。
- **設定ファイル検証**:
  - `~/.gemini/antigravity-cli/settings.json`: 公式スキーマ上 Remote Control/Remote Agents の ON/OFF キーは非存在（`--remote-agent` 用設定は `/config` の Remote Agent タブで管理、`remote-control` は `--remote-control` / `/remote-control` / `agy remote-control start` で制御）。`$schema` を追加設定。
  - `~/.gemini/config/config.json`: `userSettings.remoteControlEnabled: true` および `userSettings.cliRemoteControlHostname: "msi-lunar-nova-cli"`（既存の App 用 `remoteControlHostname: "msi-lunar-nova"` と分離）を安全に設定。

### 2. 実施した改善アクション
1. **`gemini-notebook-mcp` Remote Agents 対応** ([`server.js`](../../.agents/mcp/gemini-notebook-mcp/server.js) / [`README.md`](../../.agents/mcp/gemini-notebook-mcp/README.md)):
   - Remote Agents の **Upload Files** 配置先 `/home/antigravity/upload/`（`gemini-notebook-config.json` / `config.json` および `gemini-notebook-tokens.json` / `tokens.json`）から `~/.config/gemini-notebook-mcp/` への自動シード（`0o600`）を実装。
   - 環境変数 OAuth リフレッシュ（`GEMINI_NOTEBOOK_CLIENT_ID` + `GEMINI_NOTEBOOK_REFRESH_TOKEN` 等）も追加対応し、Git へ秘密情報を含めないクラウド運用を確立。
2. **新規スキル追加**:
   - [`.agents/skills/gemini-notebook/SKILL.md`](../../.agents/skills/gemini-notebook/SKILL.md): ローカル MCP / Remote Agents `cli.js` フォールバック・認証受け渡し規約を定義。
   - [`.agents/skills/remote-agents/SKILL.md`](../../.agents/skills/remote-agents/SKILL.md): Remote Agents / Remote Control / SSH / `/pc-env-sync` の 4 モード使い分けと GitHub リソース併設ルールを整備。
3. **同期基盤・`.gitignore` 強化**:
   - [`.gitignore`](../../.gitignore) へ `client_secret*.json` / `tokens.json` / `gemini-notebook-*.json` / `application_default_credentials.json` / `.env` 保護を追加（`nobuyukitakahashi` は `public` リポのため必須防衛）。
   - [`sync_pc_env.ps1`](../../.agents/skills/pc-env-sync/scripts/sync_pc_env.ps1)・[`sync_mac_env.sh`](../../.agents/skills/pc-env-sync/scripts/sync_mac_env.sh)・[`pc-env-sync/SKILL.md`](../../.agents/skills/pc-env-sync/SKILL.md) へ `agy` バージョン・Remote Control 状態確認および `settings.json` `$schema` 保全を追加。
