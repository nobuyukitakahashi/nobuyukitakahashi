# 組織自律進化・監査レポート（20261114：アカウント共通・最優先マスタールール「最適モデル逆提案ゲート」の全環境・全プロジェクト統合）
- **監査対象**: Antigravity グローバルルール機構（`user_global` / `~/.gemini/config/rules/` / `~/.gemini/config/plugins/`）＆ マルチPC同期パイプライン（`/pc-env-sync`）
- **判定ステータス**: `[UPDATED: 改善実施]`

### 1. Antigravity最新機能・仕様のチェック結果
- Antigravity の `<user_rules>` 読み込み仕様において、以下の3階層がすべてのワークスペース・すべてのエージェント（親エージェントおよびサブエージェント）のシステムプロンプトへ無条件かつ最優先で注入されることを確認：
  1. `RULE[user_global]`（`~/.gemini/config/AGENTS.md`）
  2. `RULE[~/.gemini/config/rules/AGENTS.md]`
  3. `RULE[~/.gemini/config/plugins/<plugin-name>/rules/AGENTS.md]`
- これにより、特定のプロジェクト（統括COO「ジン」）を開いていない場合でも、別プロジェクトや新規ワークスペースを含むアカウント全体の全エージェントに最優先ルールを強制適用できることを確認。

### 2. オーナー指示に基づく改善内容（最適モデル逆提案ゲートの全社・全環境標準化）
- **課題**: タスク難易度に対して現在のモデルがアンダースペック（例：`Hydrogen` で長尺動画・音声解析や複雑3D造形を実行）またはオーバースペック（例：`Argon` で定型コマンドや軽微作業を実行）である場合に、作業着手前にエージェント側から最適モデルへの切り替えを逆提案する仕組みを、本プロジェクトだけでなくアカウント全体の全プロジェクト・別PC環境でも恒久的に機能させる必要がある。
- **実装内容**:
  1. **アカウント共通プラグイン＆グローバルルールのリポジトリ永続化**:
     - [`.agents/plugins/global-master-rules/plugin.json`](../../.agents/plugins/global-master-rules/plugin.json) および [`.agents/plugins/global-master-rules/rules/AGENTS.md`](../../.agents/plugins/global-master-rules/rules/AGENTS.md) を新設。
  2. **マルチPC同期スクリプト（`/pc-env-sync`）への組み込み**:
     - [`.agents/skills/pc-env-sync/scripts/sync_pc_env.ps1`](../../.agents/skills/pc-env-sync/scripts/sync_pc_env.ps1) および [`.agents/skills/pc-env-sync/scripts/sync_mac_env.sh`](../../.agents/skills/pc-env-sync/scripts/sync_mac_env.sh) を更新し、別PCで `/pc-env-sync` を実行した際にも自動的に `~/.gemini/config/plugins/global-master-rules`、`~/.gemini/config/AGENTS.md`、`~/.gemini/config/rules/AGENTS.md` の3箇所へ最優先マスタールールが同期されるよう構成。
  3. **本ワークスペース内ルールへの統合**:
     - [`.agents/rules/global-policy.md`](../../.agents/rules/global-policy.md)（セクション0）、[`00_COO/AGENTS.md`](../../00_COO/AGENTS.md)（Step 0-A）、[`AGENTS.md`](../../AGENTS.md) に「最適モデル逆提案ゲート（Model Adequacy & Counter-Proposal Gate）」を明記。

### 3. 自律実施した改善アクション（変更ファイル一覧）
- [`.agents/plugins/global-master-rules/plugin.json`](../../.agents/plugins/global-master-rules/plugin.json)（新規作成）
- [`.agents/plugins/global-master-rules/rules/AGENTS.md`](../../.agents/plugins/global-master-rules/rules/AGENTS.md)（新規作成）
- [`.agents/skills/pc-env-sync/scripts/sync_pc_env.ps1`](../../.agents/skills/pc-env-sync/scripts/sync_pc_env.ps1)（更新）
- [`.agents/skills/pc-env-sync/scripts/sync_mac_env.sh`](../../.agents/skills/pc-env-sync/scripts/sync_mac_env.sh)（更新）
- [`.agents/rules/global-policy.md`](../../.agents/rules/global-policy.md)（更新）
- [`00_COO/AGENTS.md`](../../00_COO/AGENTS.md)（更新）
- [`AGENTS.md`](../../AGENTS.md)（更新）
- [`AICHANGELOG.md`](../../AICHANGELOG.md)（v26 追記）
