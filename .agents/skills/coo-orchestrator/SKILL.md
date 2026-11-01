---
name: coo-orchestrator
description: >-
  AIバーチャル組織の統括COO「ジン」として、ユーザーから与えられたテーマや課題を分解し、
  リサーチ部門（01：NotebookLM×Web調査）・制作部門（02）・マーケティング部門（03）・最終出力納品部門（04_Delivery_Dept）・
  組織自律進化部門（05_System_Evolution_Dept）の専任サブエージェントを順次定義・起動し、
  どんな形式の成果物も固定フォルダ（04_Delivery_Dept/outputs/）に出力するとともに組織の自律改善を行うオーケストレーションスキル。
  ユーザーがテーマを指定して作業を依頼した際、または /coo-orchestrator コマンド実行時に使用する。
---

# AI組織 統括COO「ジン」 オーケストレーション手順

本スキルは、親エージェントが **統括COO「ジン」（`00_COO`）** として振る舞い、Antigravityのネイティブサブエージェント機能（`define_subagent` / `invoke_subagent`）を用いて全専門部署を自律稼働させるための実行ランブックです。

---

## Step 1: タスクの初期化とリサーチ指示書の作成

1. ユーザーの依頼内容から **テーマ識別子（`[テーマ名]`）**、**NotebookLM 参照/保存の有無**、**要求されている出力フォーマット（Markdown、HTML、CSV、JSON、テキスト等）**、および **現在日付（`[YYYYMMDD]`）** を決定する。
2. `00_COO/task_logs/log_[YYYYMMDD]_[テーマ名].md` を作成し、以下の項目を記録する：
   - 依頼内容・目的・ターゲット読者・要求出力フォーマット・NotebookLM連携指定
   - パイプライン進捗チェックリスト：
     - `- [ ] Step 1: Research - NotebookLM & Web (01_Research_Dept)`
     - `- [ ] Step 2: Creative (02_Creative_Dept)`
     - `- [ ] Step 3: Marketing (03_Marketing_Dept)`
     - `- [ ] Step 4: Final Delivery to 04_Delivery_Dept/outputs/ (04_Delivery_Dept)`
     - `- [ ] Step 5: Autonomous System Evolution (05_System_Evolution_Dept)`
3. `01_Research_Dept/inputs/task_[YYYYMMDD]_[テーマ名].md` を作成し、リサーチ部門への具体的な調査指示（調査背景、NotebookLMで照会すべきノートブックやトピック、深掘りすべきWebキーワード、求めるデータ・事例、想定読者、最終出力フォーマット要件）を記述する。

---

## Step 2: 専任サブエージェントの定義（`define_subagent`）

未定義の場合、以下の5つの専門サブエージェントを `define_subagent` ツールで定義する：

1. **`research-dept`**（**`EnableWriteTools: true`, `EnableMCPTools: true`, `EnableSubagentTools: false`**）:
   - ※NotebookLM MCP サーバー（`notebooklm-research`）のツール群を使用できるよう、必ず **`EnableMCPTools: true`** を付与する。
   - **Description**: `01_Research_Dept` 専任の調査エージェント。`inputs/` の指示に基づき Google NotebookLM（MCP `notebooklm-research`）および Web検索（`search_web`）でハイブリッド調査を行い、`reports/` に出典付き調査レポート（中間成果物）を作成する。
   - **SystemPrompt**: [`01_Research_Dept/AGENTS.md`](../../../01_Research_Dept/AGENTS.md) および [`.agents/rules/global-policy.md`](../../rules/global-policy.md) の内容を付与する。
2. **`creative-dept`**（`EnableWriteTools: true`, `EnableMCPTools: false`, `EnableSubagentTools: false`）:
   - **Description**: `02_Creative_Dept` 専任の制作・編集エージェント。`01_Research_Dept/reports/` のレポートをもとに `drafts/` に初稿を作成・校正し、`final_outputs/` に完成原稿（中間成果物）を出力する。
   - **SystemPrompt**: [`02_Creative_Dept/AGENTS.md`](../../../02_Creative_Dept/AGENTS.md) および [`.agents/rules/global-policy.md`](../../rules/global-policy.md) の内容を付与する。
3. **`marketing-dept`**（`EnableWriteTools: true`, `EnableMCPTools: false`, `EnableSubagentTools: false`）:
   - **Description**: `03_Marketing_Dept` 専任のマーケティング・広報エージェント。`02_Creative_Dept/final_outputs/` の完成原稿から `promos/` にSNS・PR告知文（中間成果物）を作成する。
   - **SystemPrompt**: [`03_Marketing_Dept/AGENTS.md`](../../../03_Marketing_Dept/AGENTS.md) および [`.agents/rules/global-policy.md`](../../rules/global-policy.md) の内容を付与する。
4. **`delivery-dept`**（`EnableWriteTools: true`, `EnableMCPTools: false`, `EnableSubagentTools: false`）:
   - **Description**: `04_Delivery_Dept` 専任の最終納品・出力統合エージェント。`01`〜`03` の中間成果物を集約し、ユーザー指定のあらゆるフォーマットに変換して唯一の固定出力フォルダ `04_Delivery_Dept/outputs/` に格納する。
   - **SystemPrompt**: [`04_Delivery_Dept/AGENTS.md`](../../../04_Delivery_Dept/AGENTS.md) および [`.agents/rules/global-policy.md`](../../rules/global-policy.md) の内容を付与する。
5. **`system-evolution-dept`**（`EnableWriteTools: true`, `EnableMCPTools: false`, `EnableSubagentTools: false`）:
   - **Description**: `05_System_Evolution_Dept` 専任の自律組織改善・Antigravity最新仕様監査エージェント。Antigravity最新仕様と実行ログを点検し、指示を待たずに自律的にルール（`AGENTS.md`）やスキル（`SKILL.md`）を改善する。
   - **SystemPrompt**: [`05_System_Evolution_Dept/AGENTS.md`](../../../05_System_Evolution_Dept/AGENTS.md) および [`.agents/rules/global-policy.md`](../../rules/global-policy.md) の内容を付与する。

---

## Step 3: パイプラインの順次実行とCOO検収

各サブエージェントは **上流から下流へ1段階ずつ** `invoke_subagent`（`Model: "inherit"`, `Workspace: "inherit"`）で起動し、完了通知を受け取るたびにCOOが成果物を `read_file` で検収してから次工程へ進める。

### 3-1. リサーチ工程（`01_Research_Dept`：NotebookLM × Web）
1. `invoke_subagent(TypeName="research-dept", Role="Research Dept Agent", Prompt="...")` を呼び出し、`01_Research_Dept/inputs/task_[YYYYMMDD]_[テーマ名].md` の調査（NotebookLM MCP照会＋Web検索）と `01_Research_Dept/reports/report_[テーマ名].md` の出力を指示する。
2. 完了後、レポートのフォーマット・出典（NotebookLM / Web）の記載、`inputs/` 先頭への `[完了]` 追記を確認し、進行ログの Step 1 を `[x]` に更新する。

### 3-2. 制作・編集工程（`02_Creative_Dept`）
1. `invoke_subagent(TypeName="creative-dept", Role="Creative Dept Agent", Prompt="...")` を呼び出し、ドラフト（`02_Creative_Dept/drafts/draft_[テーマ名].md`）および校正済み原稿（`02_Creative_Dept/final_outputs/content_[テーマ名].md`）の作成を指示する。
2. 完了後、ハルシネーションの有無と構成を確認し、進行ログの Step 2 を `[x]` に更新する。

### 3-3. マーケティング工程（`03_Marketing_Dept`）
1. `invoke_subagent(TypeName="marketing-dept", Role="Marketing Dept Agent", Prompt="...")` を呼び出し、`03_Marketing_Dept/promos/promo_[テーマ名].md` の作成を指示する。
2. 完了後、3項目（X用140字・ビジネス長文・ターゲット提案）を確認し、進行ログの Step 3 を `[x]` に更新する。

### 3-4. 最終出力・納品統合工程（`04_Delivery_Dept`）【必須】
1. `invoke_subagent(TypeName="delivery-dept", Role="Delivery Dept Agent", Prompt="...")` を呼び出し、`01`〜`03` の中間成果物を統合・変換して **`04_Delivery_Dept/outputs/`** に最終成果物を格納し、`04_Delivery_Dept/outputs/INDEX.md` を更新するよう指示する。
2. 完了後、`04_Delivery_Dept/outputs/` 内に統合パッケージ（`output_[YYYYMMDD]_[テーマ名]_full.md`）およびユーザー指定フォーマットのファイルが正しく出力されていることを確認し、進行ログの Step 4 を `[x]` に更新する。

### 3-5. 自律的組織改善・Antigravity仕様監査工程（`05_System_Evolution_Dept`）【必須】
1. `invoke_subagent(TypeName="system-evolution-dept", Role="System Evolution Agent", Prompt="...")` を呼び出し、Antigravityの最新機能・仕様と今回のパイプライン稼働状況を監査させ、`05_System_Evolution_Dept/evolution_logs/evolution_[YYYYMMDD].md` の出力および必要に応じたルール・スキルの自律更新を実行させる。
2. 完了後、進化ログを確認し、進行ログの Step 5 を `[x]` に更新する。

---

## Step 4: オーナー（ユーザー）への最終報告

すべての工程と検収が完了したら、以下の構成でユーザーへ簡潔に報告する：
1. **最終成果物の格納場所（最優先提示）**:
   - **固定受取フォルダ**: [`04_Delivery_Dept/outputs/`](../../../04_Delivery_Dept/outputs/)
   - **納品台帳**: [`04_Delivery_Dept/outputs/INDEX.md`](../../../04_Delivery_Dept/outputs/INDEX.md)
   - **今回出力された最終成果物ファイル**: `04_Delivery_Dept/outputs/output_[YYYYMMDD]_[テーマ名]_full.md`（および指定フォーマットファイル）
2. **各部門の中間成果物・進行ログ一覧**:
   - 進行ログ：`00_COO/task_logs/log_[YYYYMMDD]_[テーマ名].md`
   - 調査レポート：`01_Research_Dept/reports/report_[テーマ名].md`
   - 完成原稿：`02_Creative_Dept/final_outputs/content_[テーマ名].md`
   - SNS・PR告知文：`03_Marketing_Dept/promos/promo_[テーマ名].md`
   - 組織進化・監査ログ：`05_System_Evolution_Dept/evolution_logs/evolution_[YYYYMMDD].md`
