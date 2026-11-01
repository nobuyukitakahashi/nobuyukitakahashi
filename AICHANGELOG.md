# AI変更履歴 (AICHANGELOG)

## 2026-11-01: Antigravity最新仕様に基づくマルチエージェント組織構造・ルール・スキルの導入

### 変更理由
ユーザーが構想した「フォルダ構造とMDファイルによる仮想サブエージェント分業モデル」を、最新Antigravityの公式カスタマイズ仕様（Hierarchical Rules `AGENTS.md`、On-Demand Skills `.agents/skills/*/SKILL.md`、ネイティブサブエージェント起動ツール `define_subagent` / `invoke_subagent`）に完全適合させ、自律的かつ確実に動作するマルチエージェントパイプラインへ昇華させるため。

### Before / After
- **Before**:
  - 各部署の指示書が `coo_instructions.md` や `jinni.md` という独自ファイル名で配置されており、Antigravityの自動ルール探索（`AGENTS.md` / `GEMINI.md`）の対象外だった。
  - 各ファイルの1行目にコピー元の見出しメモが残存していた。
  - `00_COO` と `02_Creative_Dept` の間で `drafts/` フォルダの役割・受け渡し手順に矛盾があった。
  - サブエージェントを実際に起動・連携させるためのワークスペーススキル（`.agents/skills/`）が未定義だった。
  - 空フォルダ（`inputs/`, `reports/`, `drafts/` 等）に `.gitkeep` がなく、Gitでディレクトリ構造を追跡できなかった。
- **After**:
  - **ルートおよび各部署への [`AGENTS.md`](AGENTS.md) 配置**:
    - ルート [`AGENTS.md`](AGENTS.md) を新設し、`@[global-policy](.agents/rules/global-policy.md)` で全体共通ポリシーをインクルード。
    - 各部署の指示書を公式仕様の [`00_COO/AGENTS.md`](00_COO/AGENTS.md)、[`01_Research_Dept/AGENTS.md`](01_Research_Dept/AGENTS.md)、[`02_Creative_Dept/AGENTS.md`](02_Creative_Dept/AGENTS.md)、[`03_Marketing_Dept/AGENTS.md`](03_Marketing_Dept/AGENTS.md) に統一・刷新（旧 `coo_instructions.md`, `jinni.md` を統合・置き換え）。
  - **ワークスペーススキル（`.agents/skills/`）の新設**:
    - [`.agents/skills/coo-orchestrator/SKILL.md`](.agents/skills/coo-orchestrator/SKILL.md): `/coo-orchestrator` で起動可能な統括パイプラインスキル。`define_subagent` と `invoke_subagent` で3部門のサブエージェントを順次起動・検収。
    - [`.agents/skills/research-dept/SKILL.md`](.agents/skills/research-dept/SKILL.md): `/research-dept` リサーチ部門単体実行スキル。
    - [`.agents/skills/creative-dept/SKILL.md`](.agents/skills/creative-dept/SKILL.md): `/creative-dept` 制作部門単体実行スキル。
    - [`.agents/skills/marketing-dept/SKILL.md`](.agents/skills/marketing-dept/SKILL.md): `/marketing-dept` マーケ部門単体実行スキル。
  - **業務フロー不整合の解消とハルシネーション防止強化**:
    - リサーチレポートに出典URL記載欄を追加し、Creative部門が `01_Research_Dept/reports/` を読み込んで `02_Creative_Dept/drafts/` に初稿作成 ➔ セルフ校正 ➔ `final_outputs/` 出力という一貫したフローに統一。
  - **Git追跡用の `.gitkeep` 配置**:
    - 全6箇所の入出力・ログ用空ディレクトリに `.gitkeep` を配置。

### 影響範囲
- ワークスペース全体のエージェントルール認識（`AGENTS.md`, `.agents/rules/global-policy.md`）
- チャットUIのスラッシュコマンドおよび自動スキル選択（`.agents/skills/*`）
- 各部署ディレクトリの入出力管理およびGitリポジトリ同期対象
