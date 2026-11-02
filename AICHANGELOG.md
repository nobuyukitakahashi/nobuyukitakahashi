# AI変更履歴 (AICHANGELOG)

## 2026-11-02 (v5): 制作・編集部門（02_Creative_Dept）への Blender MCP 統合プラグインの組み込みとマルチPC環境同期の拡張

### 変更理由
制作部門（`02_Creative_Dept`）がテキスト執筆・編集だけでなく、**Blender MCP（`mcp-for-blender` / MCPサーバー名: `blender`）** を用いたライブ3Dモデリング、アセット検索・インポート（Poly Haven / Sketchfab / Poly Pizza）、AI 3Dモデル生成、カメラ視点・マルチアングル視覚検証（`look`）、およびシーン・画像出力を自律実行できるよう、ワークスペースプラグイン・部門ルール・マルチPC同期スクリプトに組み込むため。

### Before / After
- **Before**:
  - `02_Creative_Dept`（`creative-dept` サブエージェント）は `EnableMCPTools: false` で定義されており、テキスト原稿の作成のみを対象としていた。
  - Windows 用環境同期スクリプト（`sync_pc_env.ps1`）およびワークスペースプラグイン（`.agents/plugins/`）に Blender MCP の定義がなかった。
- **After**:
  - **ワークスペースプラグイン [`.agents/plugins/blender-plugin/`](.agents/plugins/blender-plugin/) の新設**:
    - [`plugin.json`](.agents/plugins/blender-plugin/plugin.json)、[`mcp_config.json`](.agents/plugins/blender-plugin/mcp_config.json)、[`README.md`](.agents/plugins/blender-plugin/README.md) を作成し、`uvx mcp-for-blender`（MCPサーバー名: `blender`）をワークスペースプラグインとして登録。
  - **制作部門 [`02_Creative_Dept/AGENTS.md`](02_Creative_Dept/AGENTS.md) およびスキルの更新**:
    - `creative-dept` サブエージェント定義時に **`EnableMCPTools: true`** を付与（[`coo-orchestrator/SKILL.md`](.agents/skills/coo-orchestrator/SKILL.md) および [`creative-dept/SKILL.md`](.agents/skills/creative-dept/SKILL.md)）。
    - `get_addon_status` ➔ `get_scene_info` ➔ `search_assets` / `import_asset` / `generate_3d` / `execute_blender_code` ➔ `look` によるマルチアングル視覚監査 ➔ `04_Delivery_Dept/outputs/` への最終納品フローを標準化。
  - **Windows 環境同期スクリプト [`sync_pc_env.ps1`](.agents/skills/pc-env-sync/scripts/sync_pc_env.ps1) の拡張**:
    - macOS 版（`sync_mac_env.sh`）と同様に、Windows 版でも `uvx` パスを自動検出して `~/.gemini/config/mcp_config.json` および `~/.gemini/antigravity/mcp_config.json` に `blender`（および `obsidian`）を自動登録するよう更新。

### 影響範囲
- 新設: [`.agents/plugins/blender-plugin/plugin.json`](.agents/plugins/blender-plugin/plugin.json), [`.agents/plugins/blender-plugin/mcp_config.json`](.agents/plugins/blender-plugin/mcp_config.json), [`.agents/plugins/blender-plugin/README.md`](.agents/plugins/blender-plugin/README.md)
- 更新: [`AGENTS.md`](AGENTS.md), [`02_Creative_Dept/AGENTS.md`](02_Creative_Dept/AGENTS.md), [`.agents/skills/creative-dept/SKILL.md`](.agents/skills/creative-dept/SKILL.md), [`.agents/skills/coo-orchestrator/SKILL.md`](.agents/skills/coo-orchestrator/SKILL.md), [`.agents/skills/pc-env-sync/SKILL.md`](.agents/skills/pc-env-sync/SKILL.md), [`.agents/skills/pc-env-sync/scripts/sync_pc_env.ps1`](.agents/skills/pc-env-sync/scripts/sync_pc_env.ps1)

---

## 2026-11-01 (v4): 条件付き・オンデマンド稼働型「法務・コンプライアンス部門（06_Legal_Dept）」の新設

### 変更理由
通常案件におけるパイプラインの処理スピードを維持しつつ、法的リスク（薬機法・景品表示法・ステマ規制・著作権引用・個人情報保護・誹謗中傷リスク等）が含まれる案件や契約書・利用規約等の法務文書案件においてのみ専門的なリーガルスクリーニングと「安全な代替表現」の提示を行うため、条件付き審査ゲート（Conditional Gate）兼オンデマンド専門部署として `06_Legal_Dept` を新設。

### Before / After
- **Before**:
  - 法務・コンプライアンス専門の審査部門が存在せず、広告規制（薬機法・景表法・ステマ規制）や著作権引用要件、個人情報マスキング、契約・規約レビューを専門的に検証・代替案提示する仕組みがなかった。
- **After**:
  - **`06_Legal_Dept`（法務・コンプライアンス部門）と `/legal-dept` スキルの新設**:
    - [`06_Legal_Dept/AGENTS.md`](06_Legal_Dept/AGENTS.md) および [`.agents/skills/legal-dept/SKILL.md`](.agents/skills/legal-dept/SKILL.md) を作成。
    - 通常案件ではスキップし、統括COOが「5大法務リスクトリガー」に該当すると判定した案件（Step 3.5）、またはオーナーから `/legal-dept` で直接指名された案件のみ起動するハイブリッド稼働方式を採用。
    - 審査結果は3段階ステータス（`[APPROVED]` / `[CONDITIONAL_APPROVED]` / `[HOLD]`）で判定し、リスク箇所には「そのまま使える安全な代替表現（修正文案）」と弁護士法第72条配慮の免責注記を付与して `06_Legal_Dept/reviews/review_[テーマ名].md` に出力。
  - **最終出力固定ルール（`04_Delivery_Dept/outputs/`）との完全統合**:
    - `04_Delivery_Dept` が `06_Legal_Dept` の修正指示（安全な代替表現）を反映した上で統合納品パッケージ（Part 4）として `04_Delivery_Dept/outputs/` に格納するフローを確立。

### 影響範囲
- 新設: [`06_Legal_Dept/AGENTS.md`](06_Legal_Dept/AGENTS.md), [`06_Legal_Dept/reviews/.gitkeep`](06_Legal_Dept/reviews/.gitkeep), [`.agents/skills/legal-dept/SKILL.md`](.agents/skills/legal-dept/SKILL.md)
- 更新: [`AGENTS.md`](AGENTS.md), [`.agents/rules/global-policy.md`](.agents/rules/global-policy.md), [`00_COO/AGENTS.md`](00_COO/AGENTS.md), [`04_Delivery_Dept/AGENTS.md`](04_Delivery_Dept/AGENTS.md), [`.agents/skills/coo-orchestrator/SKILL.md`](.agents/skills/coo-orchestrator/SKILL.md)

---

## 2026-11-01 (v3): リサーチ部門（01_Research_Dept）への Google NotebookLM MCP 統合プラグインの組み込み

### 変更理由
リサーチ部門（`01_Research_Dept`）が Web 検索だけでなく、人間オーナーの Google NotebookLM 内のノートブック検索・質問・引用抽出・ソース追加（Ingest）を直接実行できるよう、ワークスペースプラグインとして `notebooklm-mcp` を組み込むため。

### Before / After
- **Before**:
  - `01_Research_Dept` の調査手段は `search_web` とローカルファイルのみだった。
- **After**:
  - **ワークスペースプラグイン [`.agents/plugins/notebooklm-plugin/`](.agents/plugins/notebooklm-plugin/) の新設**:
    - [`plugin.json`](.agents/plugins/notebooklm-plugin/plugin.json) および [`mcp_config.json`](.agents/plugins/notebooklm-plugin/mcp_config.json) を構成し、Windows 環境で確実に起動する `npx.cmd -y notebooklm-mcp@latest`（MCPサーバー名: `notebooklm-research`）を登録。
  - **リサーチ部門 [`01_Research_Dept/AGENTS.md`](01_Research_Dept/AGENTS.md) とスキルの更新**:
    - `research-dept` サブエージェントの定義時に `EnableMCPTools: true` を付与。
    - NotebookLM ナレッジ照会（`[NotebookLM]` タグ）と 2026年最新 Web 調査（`[Web]` タグ）を組み合わせるハイブリッド調査手順および出典記載フォーマットを実装。

---

## 2026-11-01 (v2): 最終出力引き受け専門部門（04_Delivery_Dept）と自律進化部門（05_System_Evolution_Dept）の実装

### 変更理由
1. ユーザーがどのような形式で成果物（Output）を受け取る場合でも、常に単一の固定フォルダ（`04_Delivery_Dept/outputs/`）で受け取れるよう、最終出力を一手に引き受ける専門サブエージェント（`04_Delivery_Dept`）を実装し、全サブエージェントにそのルールを徹底させるため。
2. 人間から都度指示しなくても、常時Antigravityの最新機能・仕様を確認して組織のルールやスキルを自律的にアップデートし続ける専門サブエージェント（`05_System_Evolution_Dept`）を組み込むため。

### Before / After
- **Before**:
  - `01_Research_Dept/reports/`、`02_Creative_Dept/final_outputs/`、`03_Marketing_Dept/promos/` に成果物が分散しており、ユーザーが複数フォルダを見に行く必要があった。またHTMLやCSVなど別形式での出力を一元管理する専門部署がなかった。
  - 組織のルール（`AGENTS.md`）やスキル（`SKILL.md`）の改善は人間からの明示的な指示がある時のみ行われる設計だった。
- **After**:
  - **`04_Delivery_Dept`（納品・出力統合部門）と固定出力フォルダ `04_Delivery_Dept/outputs/` の新設**:
    - `01`〜`03` の各部門フォルダは「中間成果物置き場」と再定義し、全サブエージェントの `AGENTS.md` および `global-policy.md` に「最終成果物はどんな形式であれ必ず `04_Delivery_Dept` が引き受け、`04_Delivery_Dept/outputs/` に格納する」ルールを徹底。
    - `04_Delivery_Dept/outputs/INDEX.md`（納品台帳）により、全成果物を1箇所で一覧・取得可能化。
  - **`05_System_Evolution_Dept`（組織進化・Antigravity最新仕様監査部門）の新設**:
    - パイプライン実行時（および `/system-evolution` 実行時）に、Antigravityの内蔵スキル（`agy-customizations`, `antigravity-guide`）や公式ドキュメント/Changelog、実行ログを自律監査し、人間の指示を待たずに各 `AGENTS.md` や `.agents/skills/` をアップデートする特権部門を実装。

### 影響範囲
- [`.agents/rules/global-policy.md`](.agents/rules/global-policy.md), [`AGENTS.md`](AGENTS.md)
- [`00_COO/AGENTS.md`](00_COO/AGENTS.md) 〜 [`05_System_Evolution_Dept/AGENTS.md`](05_System_Evolution_Dept/AGENTS.md)
- [`.agents/skills/`](.agents/skills/) 配下の全6スキル

---

## 2026-11-01 (v1): Antigravity最新仕様に基づくマルチエージェント組織構造・ルール・スキルの導入

### 変更理由
ユーザーが構想した「フォルダ構造とMDファイルによる仮想サブエージェント分業モデル」を、最新Antigravityの公式カスタマイズ仕様（Hierarchical Rules `AGENTS.md`、On-Demand Skills `.agents/skills/*/SKILL.md`、ネイティブサブエージェント起動ツール `define_subagent` / `invoke_subagent`）に完全適合させ、自律的かつ確実に動作するマルチエージェントパイプラインへ昇華させるため。
