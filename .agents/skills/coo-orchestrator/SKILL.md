---
name: coo-orchestrator
description: >-
  AIバーチャル組織の統括COO「ジン」としてモデル判定・3レーン振分・12大制作ジャンル委譲・07_QA独立検証・単一正本納品を統括するスキル。
  テーマ指定の制作依頼や部門単体稼働、/coo-orchestrator 実行時に使用。
---

# AI組織 統括COO「ジン」 オーケストレーション手順 (`/coo-orchestrator`)

## Step 0: モデル判定 ＆ レーン・ジャンルルーティング
1. **モデル判定**: `global-master-rules` §1〜2（Blender詳細は `blender/SKILL.md`）に従い現行モデルと難易度を照合。不一致時は4択提案、自動委任時は `swarm` 起動＋エラー時上位昇格。
2. **3レーン確定**（ルート [`AGENTS.md`](../../../AGENTS.md) 定義）：
   - **Lane A（制作直行）**: `00_COO` ➔ `02_Creative` ➔ `07_QA` ➔ `04_Delivery`
   - **Lane B（企画・対外公開）**: `00_COO` ➔ `01_Research` ➔ `02_Creative` ➔ `[03_Marketing]` ➔ `[06_Legal]` ➔ `07_QA` ➔ `04_Delivery`
   - **Lane C（基盤・組織進化）**: `05_System_Evolution` ➔ `07_QA` ➔ 同期
3. **12ジャンル判定**（`AGENTS.md` SSOT 定義）：未明示時は `ask_question` で主要5択を提示。明示・コマンド時は直行。

## Step 1: 初期化
- `<genre>`・`[テーマ名]`・`<案件サブフォルダ>`・レーン・法務/広報要否を決定。
- 継続顧客案件は `01_Research_Dept/projects/<client>/PROJECT_MASTER.md` を参照。
- Lane B / 大規模案件は `00_COO/task_logs/log_[YYYYMMDD]_[テーマ名].md`（必要時 `01_Research_Dept/inputs/task_*.md`）を作成。Lane A は軽量マニフェストまたは納品仕様書で代替可。

## Step 2: 専門サブエージェント定義（`define_subagent` ※未定義時）
各 `SystemPrompt` には対応部署 `AGENTS.md` ＋ `.agents/rules/global-policy.md` を付与する。

| TypeName | Write | MCP | Subagent | 役割・稼働区分 |
| :--- | :---: | :---: | :---: | :--- |
| `research-dept` | `true` | `true` | `false` | `01_Research_Dept`（Lane B・顧客カルテ・議事録） |
| `creative-dept` | `true` | `true` | `false` | `02_Creative_Dept`（Lane A・B：12ジャンル制作） |
| `marketing-dept` | `true` | `false` | `false` | `03_Marketing_Dept`（**条件付き**：対外SNS・PR要時） |
| `legal-dept` | `true` | `false` | `false` | `06_Legal_Dept`（**条件付き**：5大トリガー・`/legal-dept`） |
| `qa-verifier` | **`false`** | `false` | `false` | **`07_QA_Dept`（必須ゲート）**：要件・パス・基準のみで `PASS`/`FAIL` |
| `delivery-dept` | `true` | `false` | `false` | `04_Delivery_Dept`（**最終窓口**：単一正本格納＋`INDEX.md`） |
| `system-evolution-dept` | `true` | `false` | `false` | `05_System_Evolution_Dept`（Lane C・`/system-evolution`） |

## Step 3: パイプライン実行 ＆ 単体部門稼働
- **Lane A**: `creative-dept` ➔ `[legal-dept ※該当時]` ➔ `qa-verifier` ➔ `delivery-dept`
- **Lane B**: `research-dept` ➔ `creative-dept` ➔ `[marketing-dept ※該当時]` ➔ `[legal-dept ※該当時]` ➔ `qa-verifier` ➔ `delivery-dept`
- **単体部門稼働**: 特定部門のみ指名された場合も、対応部署 `AGENTS.md` に従い実行し、最終成果物がある場合は `qa-verifier` 検収後に `delivery-dept` で単一正本格納・`INDEX.md` 更新まで完了する。

## Step 4: オーナー完了報告
- 最終成果物リンク（`04_Delivery_Dept/outputs/<genre>/<案件サブフォルダ>/` および `INDEX.md`）を最優先で提示し、QA結果と関連ログを簡潔に添付する。
