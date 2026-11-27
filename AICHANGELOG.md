# AI変更履歴 (AICHANGELOG)

## 2026-11-28 (v34): Phase 1〜4 全面組織刷新（`GEMINI.md` 圧縮・3レーン制・`07_QA_Dept` 新設・Hooks ガードレール・約 4.0GB ストレージ整理・Git 軽量化）

### 変更理由
1. 外部グローバルルール `G:\マイドライブ\gemini\GEMINI.md`（`9.4 KB`）に旧ツール名・Avada 固有ルール・重複原則が残り、毎ターン常時注入を圧迫していたため。
2. 稼働実態に基づき形骸化していた直列6段フローを見直し、独立検証部門 `07_QA_Dept` の正式化・`03_Marketing_Dept` の条件付き化・顧客カルテ（`projects/`）の `01` 移管・12ジャンル SSOT 化を行うため。
3. LLM の記憶頼みだったルール遵守を Antigravity Lifecycle Hooks（`PreToolUse`）と機械監査スクリプト（`verify_org.py` / `verify_media.py`）でシステム強制するため。
4. `INDEX.md`（`43.4 KB`）の `Premiere Pro` 欠落・直置き129件・`02_Creative_Dept` の重複/一時キャッシュ（約 4.0 GB）・Git 追跡内の大容量重複バイナリを一掃するため。

### Before / After
- **Phase 1（ルール・台帳・残骸整備）**:
  - `G:\マイドライブ\gemini\GEMINI.md`: `9,445 B` ➔ 約 `1.5 KB`（`-84%`）。Avada 4大検証義務を [`wordpress-avada-maintenance/SKILL.md`](.agents/skills/wordpress-avada-maintenance/SKILL.md) §7 へ完全移管。
  - [`04_Delivery_Dept/outputs/INDEX.md`](04_Delivery_Dept/outputs/INDEX.md): `43,422 B` ➔ 約 `12 KB`。欠落していた `6. Adobe Premiere Pro` と `12. Web / WordPress・Avada` を追加し全12ジャンル順序統一・直置き129件をすべて案件サブフォルダへ分類移設。
  - `AICHANGELOG.md`: `124.5 KB` ➔ 約 `8 KB`（過去分は `05_System_Evolution_Dept/changelogs/AICHANGELOG_2026-11_v01-v31.md` へアーカイブ）、`welcome.txt` 削除。
  - [`global-master-rules/rules/AGENTS.md`](.agents/plugins/global-master-rules/rules/AGENTS.md) §1 へ `Orchestrator` 系・`Hydrogen (XHigh)`・`Claude 5.5` 使い分けを追記。
- **Phase 2（構造最適化）**:
  - ルート [`AGENTS.md`](AGENTS.md) を12大ジャンル SSOT・案件タイプ別3レーン制（Lane A/B/C）・全8部門マップへ刷新。
  - [`07_QA_Dept/AGENTS.md`](07_QA_Dept/AGENTS.md)・[`verify_org.py`](07_QA_Dept/scripts/verify_org.py)・[`verify_media.py`](07_QA_Dept/scripts/verify_media.py) を新設。
  - `03_Marketing_Dept` を条件付きゲート化、`00_COO/projects/` を `01_Research_Dept/projects/` へ移設統合、`02_Creative_Dept/web/` ＆ `04_Delivery_Dept/outputs/web/` 新設。
  - 薄い部門ラッパー4スキル（`research-dept` / `creative-dept` / `marketing-dept` / `delivery-dept`）を `coo-orchestrator` へ統合廃止し、`sync_pc_env.ps1` / `sync_mac_env.sh` の自動掃除対象へ追加。
- **Phase 3（Hooks ガードレール ＆ 汎用 `.gitignore`）**:
  - [`.agents/plugins/global-master-rules/hooks.json`](.agents/plugins/global-master-rules/hooks.json) ＆ [`scripts/org_guard.js`](.agents/plugins/global-master-rules/scripts/org_guard.js) を新設（`~/.gemini/config/` 直接編集 `deny`・納品直置き `deny`・24KB超過警告）。
  - [`.gitignore`](.gitignore) を拡張子＋一時フォルダベースの汎用ルールへ全面刷新。
- **Phase 4（ストレージ・Git 軽量化）**:
  - `02_Creative_Dept/` の納品済み重複バイナリ・一時監査フレーム等を安全削除し **`3,994.89 MB`（約 4.00 GB）削減**（再現スクリプト・参照素材・最終納品正本は100%保全）。
  - 汎用 `.gitignore` 該当の大容量バイナリを `git rm --cached` で追跡解除（実ファイル・Google Drive 同期は完全保全）。

---

## 2026-11-28 (v33): 全ルール・全スキルの徹底効率化最適化（毎ターン常時注入 `-51.8%`・`blender`/`davinci` の `references/` 分離・隠れバグ5件撲滅）

### 変更理由
1. 毎ターン全チャットに常時注入されるアカウント共通マスタールール（`14.3 KB`）、ワークスペース常時ルール（`9.2 KB`）、および全28スキルの YAML Frontmatter（`16.5 KB`）の合計が **`40.0 KB`** に達しており、トークン効率と保守性を圧迫していたため。
2. `blender/SKILL.md`（`12.7 KB`）と `davinci/SKILL.md`（`15.2 KB`）に特定案件向け長大ガイドが直書きされており、Progressive Disclosure 最適化（`references/` 分離）の余地が大きかったため。
3. 全数監査で発見されたデッド見出し参照・旧パス（`02_Creative_Dept/final_outputs/`）・`INDEX.md` 見出し番号ズレを完全解消するため。

### Before / After
- **毎ターン常時注入コンテキスト合計**: `40,021 B` ➔ **`19,281 B`（`-51.8%` / `-20.7 KB`）**
  - `global-master-rules/rules/AGENTS.md`: `14,327 B` ➔ `6,919 B`（全7原則を §1〜§6 へ高密度化、ロジック・4択ゲート完全保持）
  - `global-policy.md` ＋ `AGENTS.md`: `9,163 B` ➔ `4,616 B`
  - 全28スキル YAML Frontmatter: `16,531 B` ➔ `7,746 B`（`-53.1%`）
- **全10ルールファイル合計**: `64,209 B` ➔ **`28,693 B`（`-55.3%`）**
- **全28スキル `SKILL.md` 本文合計**: `156,820 B` ➔ **`87,812 B`（`-44.0%`）**
- **`references/` 分離（技術ノウハウ100%保全）**:
  - [`.agents/skills/blender/references/mascot-animation-v8.md`](.agents/skills/blender/references/mascot-animation-v8.md) 新設
  - [`.agents/skills/davinci/references/live-action-production-guide.md`](.agents/skills/davinci/references/live-action-production-guide.md) 新設
- **隠れバグ5件修正**: デッド見出し参照、旧 `<genre>` 欠落パス、`writing/SKILL.md` の `INDEX.md` 番号ズレ、旧5大ジャンル注記、マスタールール §参照番号整合。

### 影響範囲
- 新規: `blender/references/mascot-animation-v8.md`, `davinci/references/live-action-production-guide.md`, `05_System_Evolution_Dept/evolution_logs/evolution_20261128_context_and_skills_optimization.md`
- 更新: 全10ルールファイル、自作22スキル `SKILL.md`、`AICHANGELOG.md`、およびローカル `~/.gemini/config/` 同期先一式

---

## 2026-11-28 (v32): Moho Pro 14 完全制御MCP（`moho`）・専任スキル（`/moho`）の組織完全統合 ＆ 11大制作ジャンル整合化・`/system-evolution` 定期監査

### 変更理由
1. `g:\マイドライブ\git\antigravity\moho\moho-control` で構築した Moho Pro 14.5.1 外部依存ゼロ4層ハイブリッド制御環境（MCP 15ツール・CLIブリッジ・Live Lua 5.4 Bridge・Headless `.moho` Engine・CLIレンダラ）を `nobuyukitakahashi` 正本へ統合し、Windows / macOS のどのPCでも `/pc-env-sync` 一発で `moho` MCPサーバー・Lua Bridge・`/moho` スキルが自動展開・維持されるようにするため。
2. `/system-evolution` 定期監査の結果、部門スキル（`coo-orchestrator` / `creative-dept` / `delivery-dept`）に残っていた旧「5大ジャンル」表記のズレを解消し、全ルール・スキル・台帳を **11大制作ジャンル（主要5ジャンル＋映像・2Dアニメ・VR拡張6ジャンル）** へ統一するため。

### Before / After
- **Before (v31)**:
  - `moho-control` は別フォルダに独立配置されており、`sync_pc_env.ps1` / `sync_mac_env.sh` の対象外だったため、SessionStart 自動同期後に `mcp_config.json` へ `moho` が登録されず、別PCへも展開されなかった。
  - 制作ジャンルは10ジャンル（`moho` 未登録）であり、`creative-dept` / `delivery-dept` の `SKILL.md` が旧「5大ジャンル」表記のままだった。
- **After (v32)**:
  - **`.agents/mcp/moho-mcp/` 新設 ＆ ポータブル強化**: `moho-control` 一式を正本統合し、`install-bridge.js` へ `--if-installed` オプション（Moho 未導入PCでは安全スキップ）と `antigravity-obsidian/mcp_config.json` 対応を追加、`lib/env.js` のフォールバック探索を強化。
  - **専任スキル `/moho`（`.agents/skills/moho/SKILL.md`）＆ 専用フォルダ新設**: 100%ネイティブベクター・ボーンリグ・スイッチレイヤー・完全透過3形式（ProRes 4444 `.mov` / VP9 Alpha `.webm` / 白背景 `.mp4`）＆透過チェッカーボード視覚監査・`qa-verifier` 検収フローを標準化し、`02_Creative_Dept/moho/`・`04_Delivery_Dept/outputs/moho/`・`INDEX.md` セクションを新設。
  - **クロスプラットフォーム自動同期（`sync_pc_env.ps1` / `sync_mac_env.sh`）対応**: 全3 `mcp_config.json` への `moho` 登録と、`install-bridge.js --no-mcp --if-installed` による Live Lua 5.4 Bridge 自動配備を組み込み。
  - **11大制作ジャンル統一 ＆ `/system-evolution` 監査完了**: 全ルールファイルが 24KB 上限内（切り捨てゼロ）であることを確認し、`global-master-rules` 領域Aへ Moho 2Dアニメ/Lua 5.4 を追記、全関連 `AGENTS.md` / `SKILL.md` を11ジャンル構成へ整合化。

### 影響範囲
- 新規作成:
  - [`.agents/mcp/moho-mcp/`](.agents/mcp/moho-mcp/README.md)（全20ファイル）
  - [`.agents/skills/moho/SKILL.md`](.agents/skills/moho/SKILL.md)
  - `02_Creative_Dept/moho/{drafts,final_outputs}/.gitkeep`、`04_Delivery_Dept/outputs/moho/.gitkeep`
  - [`05_System_Evolution_Dept/evolution_logs/evolution_20261128_moho_integration_and_audit.md`](05_System_Evolution_Dept/evolution_logs/evolution_20261128_moho_integration_and_audit.md)
- 更新:
  - [`.agents/skills/pc-env-sync/scripts/sync_pc_env.ps1`](.agents/skills/pc-env-sync/scripts/sync_pc_env.ps1)
  - [`.agents/skills/pc-env-sync/scripts/sync_mac_env.sh`](.agents/skills/pc-env-sync/scripts/sync_mac_env.sh)
  - [`.agents/skills/pc-env-sync/SKILL.md`](.agents/skills/pc-env-sync/SKILL.md)
  - [`.agents/plugins/global-master-rules/rules/AGENTS.md`](.agents/plugins/global-master-rules/rules/AGENTS.md)
  - [`AGENTS.md`](AGENTS.md)、[`00_COO/AGENTS.md`](00_COO/AGENTS.md)、[`02_Creative_Dept/AGENTS.md`](02_Creative_Dept/AGENTS.md)、[`04_Delivery_Dept/AGENTS.md`](04_Delivery_Dept/AGENTS.md)
  - [`.agents/skills/coo-orchestrator/SKILL.md`](.agents/skills/coo-orchestrator/SKILL.md)、[`.agents/skills/creative-dept/SKILL.md`](.agents/skills/creative-dept/SKILL.md)、[`.agents/skills/delivery-dept/SKILL.md`](.agents/skills/delivery-dept/SKILL.md)
  - [`04_Delivery_Dept/outputs/INDEX.md`](04_Delivery_Dept/outputs/INDEX.md)
  - [`AICHANGELOG.md`](AICHANGELOG.md)

---

---

> 過去の変更履歴（v01〜v31）は [5_System_Evolution_Dept/changelogs/AICHANGELOG_2026-11_v01-v31.md](05_System_Evolution_Dept/changelogs/AICHANGELOG_2026-11_v01-v31.md) にアーカイブ済み。
