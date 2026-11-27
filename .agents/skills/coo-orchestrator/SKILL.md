---
name: coo-orchestrator
description: >-
  AIバーチャル組織の統括COO「ジン」として11大制作ジャンル判定・各部門サブエージェント起動・独立検証・固定フォルダ納品・自律進化を統括するスキル。
  テーマ指定の制作依頼や /coo-orchestrator 実行時に使用。
---

# AI組織 統括COO「ジン」 オーケストレーション手順 (`/coo-orchestrator`)

## Step 0: モデル判定 ＆ ジャンルルーティング
1. **モデル判定**: `global-master-rules` §1〜2（Blender詳細は `blender/SKILL.md`）に従い現行モデルと難易度を照合。不一致時は4択提案、自動委任時は `swarm` 起動＋エラー時上位昇格。
2. **11ジャンル判定**（`AGENTS.md` 定義）：
   - 未明示時は `ask_question` で主要5択（`blender` / `illustrator` / `photoshop` / `davinci` / `writing`）を提示。
   - 明示またはスラッシュコマンド（上記5種＋拡張6種：`premiere` / `aftereffects` / `moho` / `pano2vr` / `krpano` / `ptgui`）時は直行。

## Step 1: 初期化
- `<genre>`・`[テーマ名]`・`<案件サブフォルダ>`・法務要否（5大トリガー判定）・出力形式を決定。
- `00_COO/task_logs/log_[YYYYMMDD]_[テーマ名].md`（進捗チェックリスト付き）と `01_Research_Dept/inputs/task_[YYYYMMDD]_[テーマ名].md` を作成。

## Step 2: 専門サブエージェント定義（`define_subagent` ※未定義時）
各 `SystemPrompt` には対応部署 `AGENTS.md` ＋ `.agents/rules/global-policy.md` を付与する。

| TypeName | Write | MCP | Subagent | 役割・出力先 |
| :--- | :---: | :---: | :---: | :--- |
| `research-dept` | `true` | `true` | `false` | `01_Research_Dept`（NotebookLM × Web ➔ `reports/`） |
| `creative-dept` | `true` | `true` | `false` | `02_Creative_Dept`（11ジャンル MCP/CLI 制作 ➔ `<genre>/{drafts,final_outputs}/`） |
| `marketing-dept` | `true` | `false` | `false` | `03_Marketing_Dept`（SNS・PR文 ➔ `promos/`） |
| `legal-dept` | `true` | `false` | `false` | `06_Legal_Dept`（※5大トリガー該当・`/legal-dept` 時のみ ➔ `reviews/`） |
| `qa-verifier` | **`false`** | `false` | `false` | 独立検証（`global-master-rules` §5：要件・対象パス・合格基準のみで `PASS`/`FAIL`） |
| `delivery-dept` | `true` | `false` | `false` | `04_Delivery_Dept`（最終納品 ➔ `outputs/<genre>/<案件サブフォルダ>/`＋`INDEX.md`） |
| `system-evolution-dept` | `true` | `false` | `false` | `05_System_Evolution_Dept`（仕様・モデル・ログ監査 ➔ `evolution_logs/`） |

## Step 3: パイプライン順次実行
1. `research-dept` ➔ `01_Research_Dept/reports/report_[テーマ名].md`
2. `creative-dept` ➔ `02_Creative_Dept/<genre>/{drafts,final_outputs}/<案件サブフォルダ>/`
3. `marketing-dept` ➔ `03_Marketing_Dept/promos/promo_[テーマ名].md`
4. **[条件付き]** `legal-dept` ➔ `06_Legal_Dept/reviews/review_[テーマ名].md`
5. **[必須]** `qa-verifier` ➔ `FAIL` 時は上流へ差し戻し、`PASS` 確認後に次工程へ
6. **[必須]** `delivery-dept` ➔ `04_Delivery_Dept/outputs/<genre>/<案件サブフォルダ>/` 格納 ＆ `INDEX.md` 更新
7. **[必須]** `system-evolution-dept` ➔ `05_System_Evolution_Dept/evolution_logs/evolution_[YYYYMMDD].md`

## Step 4: オーナー完了報告
- 最終成果物リンク（`04_Delivery_Dept/outputs/<genre>/<案件サブフォルダ>/` および `INDEX.md`）を最優先で提示し、中間成果物・進行ログ・進化ログへのリンクを簡潔に添付する。
