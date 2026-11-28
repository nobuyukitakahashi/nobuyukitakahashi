# AI変更履歴 (AICHANGELOG)

## 2026-11-28 (v37): Antigravity Remote Agents サブ機構成・`gemini-notebook-mcp` クラウド対応・Remote Control 設定整備

### 変更理由
1. ローカルPC非依存で稼働する **Remote Agents（`agy --remote-agent` / `antigravity.google`）** 上でも、`nobuyukitakahashi` 組織スキル・ルールおよび **`gemini-notebook-mcp`**（Google Cloud `gemini-notebook-mcp-515611` OAuth）を Git へ秘密情報を含めず安全に運用可能とするため。
2. ローカル `agy` CLI（`v1.5.18`）・Remote Control（`msi-lunar-nova` / `msi-lunar-nova-cli`）設定と `pc-env-sync` 同期基盤を最新仕様（`v2.36.0` `~/.agents/skills` 自動ディスカバリ対応含む）に整合させるため。

### Before / After
- **`gemini-notebook-mcp` クラウドVM対応**: [`.agents/mcp/gemini-notebook-mcp/server.js`](.agents/mcp/gemini-notebook-mcp/server.js) へ Remote Agents `/home/antigravity/upload/` 自動シードおよび環境変数 OAuth リフレッシュ対応を追加。
- **スキル新設**: [`.agents/skills/remote-agents/SKILL.md`](.agents/skills/remote-agents/SKILL.md)（4モード使い分け・GitHub併設運用）、[`.agents/skills/gemini-notebook/SKILL.md`](.agents/skills/gemini-notebook/SKILL.md)（ローカルMCP/リモートCLI統合）。
- **秘密情報防衛 ＆ 同期強化**: [`.gitignore`](.gitignore) へ OAuth JSON・`.env` 除外を追加し、[`pc-env-sync`](.agents/skills/pc-env-sync/SKILL.md)（`sync_pc_env.ps1` / `sync_mac_env.sh`）へ `agy` CLI バージョン・Remote Control 状態確認・`settings.json` `$schema` 保全を追加。
- **監査ログ**: [`05_System_Evolution_Dept/evolution_logs/evolution_20261128_remote_agents_setup.md`](05_System_Evolution_Dept/evolution_logs/evolution_20261128_remote_agents_setup.md)

---

## 2026-11-28 (v36): マスタールール双方向モデル停止ゲート強化・参考原本忠実性厳格化 ＆ `/system-evolution` 定期監査（Antigravity v2.36.0 対応確認）

### 変更理由
1. 派生デザイン（PC版→スマホ版等）制作・監査時に、参考原本と異なる人物トリミング・早期フェードを「境界が滑らか」等の好意的解釈で許容してしまう見逃しを恒久防止するため。
2. アンダースペック時だけでなく、上位モデルで軽量・定型作業（領域D）を実行するオーバースペック時も実作業前に一時停止して警告・4択提示を行い、クォータ消費を最適化するため。
3. `/system-evolution` 定期点検として Antigravity v2.36.0 最新仕様・全27モデル残クォータ・`verify_org.py` 機械監査・`org_guard.js` Hooks 実機ドライランを検証・記録するため。

### Before / After
- **参考原本・派生デザイン忠実性 ＆ 好意的許容禁止（コミット `f4f8de9`）**:
  - [`.agents/plugins/global-master-rules/rules/AGENTS.md`](.agents/plugins/global-master-rules/rules/AGENTS.md) §5 および [`07_QA_Dept/AGENTS.md`](07_QA_Dept/AGENTS.md) §1・§2 へ、原本・参考案と異なる処置の禁止および差異検知時の必須 `FAIL` 差し戻し規定を追加。
- **パターンB オーバースペック実行前一時停止ゲート統一（コミット `985ffae`）**:
  - [`.agents/plugins/global-master-rules/rules/AGENTS.md`](.agents/plugins/global-master-rules/rules/AGENTS.md) §1 パターンBをパターンAと同一の「実行前一時停止＋4択提示（画面切替 / `swarm`軽量 / `flash`委譲 / 続行）」へ強化（ツール不要の挨拶・1手即答の単純質問のみ例外）。
- **`/system-evolution` 監査結果**:
  - Antigravity v2.36.0（別ドライブプラグイン検出修正・`~/.agents/skills` 対応等）および全27モデル（Claude 5.5: 100%, Gemini 4 / Orchestrator: 75%、未記載主力モデルなし）を確認。
  - `verify_org.py`: **PASS**（ルール11件 38,364B・スキル24件・`INDEX.md` 21,928B・違反0件）、`org_guard.js` 3ケース実機検証 **PASS**。
  - 監査ログ: [`05_System_Evolution_Dept/evolution_logs/evolution_20261128.md`](05_System_Evolution_Dept/evolution_logs/evolution_20261128.md)

---

## 2026-11-28 (v35): 全30プロジェクト＋Obsidian 横断改善（Phase A〜D 完了：緊急Git復旧・全19サイト `AGENTS.md` 統一・SQL 1.25GB圧縮・一時資産 6.06GB整理・迷子納品物回収）

### 変更理由
1. `nobuyukitakahashi` 以外の全30プロジェクトおよび Obsidian Vault を横断監査した結果、Git インデックス破損・916件誤削除ステージング・WordPress 11サイトへの偽 `Framework: Streamlit` 混入・18プロジェクトの旧3スキル複製・非圧縮SQL 1.4GB蓄積・Obsidian直下の迷子納品物が判明したため。
2. 全 WordPress 保守サイトの共通規約を [`wordpress-avada-maintenance/SKILL.md`](.agents/skills/wordpress-avada-maintenance/SKILL.md) §8 へ単一ソース集約し、全プロジェクト横断監査ツール [`07_QA_Dept/scripts/verify_all_projects.py`](07_QA_Dept/scripts/verify_all_projects.py) を常設するため。

### Before / After
- **Phase A（緊急復旧・迷子回収）**:
  - `antigravity/httpsrecruit.kumashiro.co.jp`: 破損 `.git/index` を再構築し `.gitignore` 新設。
  - `antigravity/wn-sekizenkai.or.jp`: 放置 `.git/index.lock` 解除＋`git reset` で 916件の誤削除ステージングを無損失復旧。
  - `G:\マイドライブ\obsidian`: 直下に誤作成されていた `02_Creative_Dept` / `04_Delivery_Dept` から「cvn プラスモバイル ハガキ」納品物一式を `nobuyukitakahashi/04_Delivery_Dept/outputs/illustrator/2026-11-11_cvn_plus_mobile_postcard/` へ正式回収・[`INDEX.md`](04_Delivery_Dept/outputs/INDEX.md) 登録。
  - `antigravity/kumashiro.co.jp`: 追跡済み `.bak` ファイルを `git rm --cached` で追跡解除。
- **Phase B（ルール統一・脱コピペ・横断監査常設）**:
  - [`wordpress-avada-maintenance/SKILL.md`](.agents/skills/wordpress-avada-maintenance/SKILL.md) §8 へ全WPサイト共通の5部門分離・デュアル保守・再開時原則・バックアップ圧縮規約を集約。
  - 全16サイトの `AGENTS.md` を外科手術的にクリーン化（偽 `Streamlit` 11件一掃、`iidajob.com` 本番WP接続情報補完、`castvision.net` v34参照ズレ修正、`go.castvision.net` 旧 `view_file` 修正、`iida-hs.ed.jp` BOM除去、`kumashiro.co.jp` 重複段落除去）。
  - 18プロジェクトから旧複製3スキル（`loop-step` / `plan` / `review`）を一括撤去、`your-project-template/AGENTS.md` を v34 標準へ刷新、[`07_QA_Dept/scripts/verify_all_projects.py`](07_QA_Dept/scripts/verify_all_projects.py) を新設。
- **Phase C & D（Git保護・計 7.31 GB 容量削減）**:
  - 未管理2サイト（`iidajob.com`, `kumashiro-planning.co.jp`）へ `.gitignore`＋ローカル Git 保護を導入。
  - 全12サイトの非圧縮 `backups/*.sql` 73件（`1,399.0 MB`）を `.sql.gz`（`148.6 MB`）へ整合検証付き圧縮置換（**`-1,250.4 MB` / `-89.4%`**）。
  - `antigravity/blender` の連番フレーム `frames_v3/v5/v6`・`.blend1`（`5.84 GB`）、移行済 `antigravity/moho/moho-control`、展開済 `krpano-1.24.zip`（`222.8 MB`）を安全削除（**`-6,062.1 MB`**）し、`blender` の大容量52ファイルを `git rm --cached` で追跡解除。

---

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
