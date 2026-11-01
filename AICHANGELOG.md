# AI変更履歴 (AICHANGELOG)

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
