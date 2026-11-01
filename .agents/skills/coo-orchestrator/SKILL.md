---
name: coo-orchestrator
description: >-
  AIバーチャル組織の統括COO（司令塔）として、ユーザーから与えられたテーマや課題を分解し、
  リサーチ部門（01_Research_Dept）・制作部門（02_Creative_Dept）・マーケティング部門（03_Marketing_Dept）の
  専任サブエージェントを順次定義・起動して一気通貫で成果物を生成・検収するオーケストレーションスキル。
  ユーザーがテーマを指定して記事・コンテンツ・PR作成を依頼した際、または /coo-orchestrator コマンド実行時に使用する。
---

# AI組織 統括COO オーケストレーション手順

本スキルは、親エージェントが **統括COO（`00_COO`）** として振る舞い、Antigravityのネイティブサブエージェント機能（`define_subagent` / `invoke_subagent`）を用いて3つの専門部署を自律稼働させるための実行ランブックです。

---

## Step 1: タスクの初期化とリサーチ指示書の作成

1. ユーザーの依頼内容から **テーマ識別子（`[テーマ名]`：ファイル名に使える簡潔な日本語または英数字）** と **現在日付（`[YYYYMMDD]`）** を決定する。
2. `00_COO/task_logs/log_[YYYYMMDD]_[テーマ名].md` を作成し、以下の項目を記録する：
   - 依頼内容・目的・ターゲット読者
   - パイプライン進捗チェックリスト（`- [ ] Step 1: Research`, `- [ ] Step 2: Creative`, `- [ ] Step 3: Marketing`, `- [ ] Step 4: Final Audit`）
3. `01_Research_Dept/inputs/task_[YYYYMMDD]_[テーマ名].md` を作成し、リサーチ部門への具体的な調査指示（調査背景、深掘りすべきキーワード、求めるデータ・事例、想定読者）を記述する。

---

## Step 2: 専任サブエージェントの定義（`define_subagent`）

未定義の場合、以下の3つの専門サブエージェントを `define_subagent` ツールで定義する（`EnableWriteTools: true`, `EnableSubagentTools: false`）：

1. **`research-dept`**:
   - **Description**: `01_Research_Dept` 専任の調査エージェント。`inputs/` の指示に基づきWeb検索を行い、`reports/` に出典付き調査レポートを作成する。
   - **SystemPrompt**: [`01_Research_Dept/AGENTS.md`](../../../01_Research_Dept/AGENTS.md) および [`.agents/rules/global-policy.md`](../../rules/global-policy.md) の内容を付与する。
2. **`creative-dept`**:
   - **Description**: `02_Creative_Dept` 専任の制作・編集エージェント。`01_Research_Dept/reports/` のレポートをもとに `drafts/` に初稿を作成・校正し、`final_outputs/` に完成原稿を出力する。
   - **SystemPrompt**: [`02_Creative_Dept/AGENTS.md`](../../../02_Creative_Dept/AGENTS.md) および [`.agents/rules/global-policy.md`](../../rules/global-policy.md) の内容を付与する。
3. **`marketing-dept`**:
   - **Description**: `03_Marketing_Dept` 専任のマーケティング・広報エージェント。`02_Creative_Dept/final_outputs/` の完成原稿から `promos/` にSNS・PR告知文を作成する。
   - **SystemPrompt**: [`03_Marketing_Dept/AGENTS.md`](../../../03_Marketing_Dept/AGENTS.md) および [`.agents/rules/global-policy.md`](../../rules/global-policy.md) の内容を付与する。

---

## Step 3: パイプラインの順次実行とCOO検収

各サブエージェントは **上流から下流へ1段階ずつ** `invoke_subagent`（`Model: "inherit"`, `Workspace: "inherit"`）で起動し、完了通知を受け取るたびにCOOが成果物を `read_file` で検収してから次工程へ進める。

### 3-1. リサーチ工程（`01_Research_Dept`）
1. `invoke_subagent(TypeName="research-dept", Role="Research Dept Agent", Prompt="...")` を呼び出し、`01_Research_Dept/inputs/task_[YYYYMMDD]_[テーマ名].md` の調査と `01_Research_Dept/reports/report_[テーマ名].md` の出力を指示する。
2. サブエージェント完了後、COOは以下を検証する：
   - `01_Research_Dept/reports/report_[テーマ名].md` が存在し、必須フォーマット（概要、事実・背景、メリット/デメリット、具体例、出典URL、引き継ぎ事項）を満たしているか。
   - `01_Research_Dept/inputs/task_[YYYYMMDD]_[テーマ名].md` の先頭に `[完了]` が追記されているか。
3. 問題なければ `00_COO/task_logs/log_[YYYYMMDD]_[テーマ名].md` の Step 1 を `[x]` に更新する（不備があれば `send_message` で該当サブエージェントに修正を指示する）。

### 3-2. 制作・編集工程（`02_Creative_Dept`）
1. `invoke_subagent(TypeName="creative-dept", Role="Creative Dept Agent", Prompt="...")` を呼び出し、`01_Research_Dept/reports/report_[テーマ名].md` をもとにドラフト（`02_Creative_Dept/drafts/draft_[テーマ名].md`）および校正済み完成版（`02_Creative_Dept/final_outputs/content_[テーマ名].md`）の作成を指示する。
2. サブエージェント完了後、COOは以下を検証する：
   - `drafts/draft_[テーマ名].md` と `final_outputs/content_[テーマ名].md` の両方が生成されているか。
   - リサーチレポートにない虚偽データ（ハルシネーション）が混入していないか、「です・ます」調および見出し構造が適切か。
3. 問題なければ `00_COO/task_logs/log_[YYYYMMDD]_[テーマ名].md` の Step 2 を `[x]` に更新する。

### 3-3. マーケティング工程（`03_Marketing_Dept`）
1. `invoke_subagent(TypeName="marketing-dept", Role="Marketing Dept Agent", Prompt="...")` を呼び出し、`02_Creative_Dept/final_outputs/content_[テーマ名].md` をもとに `03_Marketing_Dept/promos/promo_[テーマ名].md` の作成を指示する。
2. サブエージェント完了後、COOは以下を検証する：
   - `03_Marketing_Dept/promos/promo_[テーマ名].md` が生成され、X用投稿（140文字以内）・ビジネス向け長文（400文字程度）・ターゲット層へのアプローチアドバイスの3項目が揃っているか。
   - 誇大広告や事実誤認がないか。
3. 問題なければ `00_COO/task_logs/log_[YYYYMMDD]_[テーマ名].md` の Step 3・Step 4 を `[x]` に更新する。

---

## Step 4: オーナー（ユーザー）への最終報告

すべての工程と検収が完了したら、以下の構成でユーザーへ簡潔に報告する：
1. **エグゼクティブサマリー**（実施したテーマと全体の要約）
2. **生成された成果物一覧**（クリック可能な `file://` リンク付き）
   - 進行ログ：`00_COO/task_logs/log_[YYYYMMDD]_[テーマ名].md`
   - 調査指示書：`01_Research_Dept/inputs/task_[YYYYMMDD]_[テーマ名].md`
   - 調査レポート：`01_Research_Dept/reports/report_[テーマ名].md`
   - 初稿ドラフト：`02_Creative_Dept/drafts/draft_[テーマ名].md`
   - 完成コンテンツ：`02_Creative_Dept/final_outputs/content_[テーマ名].md`
   - SNS・PR告知文：`03_Marketing_Dept/promos/promo_[テーマ名].md`
3. **要確認事項**（もし `※人間の確認が必要` とマークされた項目があれば明記）
