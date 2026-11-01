# AIバーチャル組織プロジェクト（Antigravity Multi-Agent System）

@[global-policy](.agents/rules/global-policy.md)

## プロジェクト概要
本ワークスペースは、Antigravityの**階層型ルール（`AGENTS.md`）**・**スキル（`.agents/skills/`）**・**ネイティブサブエージェント機能（`define_subagent` / `invoke_subagent`）**を組み合わせ、フォルダ構造による明確な成果物管理と専門サブエージェントによる分業パイプラインを実現するバーチャル組織システムです。

## 組織構成とディレクトリマップ

| 部署ディレクトリ | 役割 | ルール定義ファイル | 入力（Read） | 出力（Write） | 対応スキル |
| :--- | :--- | :--- | :--- | :--- | :--- |
| [`00_COO/`](00_COO/) | 統括COO（司令塔・品質監査） | [`00_COO/AGENTS.md`](00_COO/AGENTS.md) | ユーザー指示 / 各部署成果物 | `01_Research_Dept/inputs/`<br>`00_COO/task_logs/` | `/coo-orchestrator` |
| [`01_Research_Dept/`](01_Research_Dept/) | リサーチ部門（調査・出典収集） | [`01_Research_Dept/AGENTS.md`](01_Research_Dept/AGENTS.md) | `01_Research_Dept/inputs/` | `01_Research_Dept/reports/` | `/research-dept` |
| [`02_Creative_Dept/`](02_Creative_Dept/) | 制作・編集部門（執筆・校正） | [`02_Creative_Dept/AGENTS.md`](02_Creative_Dept/AGENTS.md) | `01_Research_Dept/reports/` | `02_Creative_Dept/drafts/`<br>`02_Creative_Dept/final_outputs/` | `/creative-dept` |
| [`03_Marketing_Dept/`](03_Marketing_Dept/) | マーケティング部門（SNS・PR文） | [`03_Marketing_Dept/AGENTS.md`](03_Marketing_Dept/AGENTS.md) | `02_Creative_Dept/final_outputs/` | `03_Marketing_Dept/promos/` | `/marketing-dept` |

## 実行モード（メインエージェントの振る舞い）
1. **一気通貫パイプライン実行（デフォルト / `/coo-orchestrator`）**:
   - ユーザーからテーマや課題を与えられた場合、メインエージェントは **統括COO（`00_COO`）** として振る舞う。
   - [`00_COO/AGENTS.md`](00_COO/AGENTS.md) およびスキル [`.agents/skills/coo-orchestrator/SKILL.md`](.agents/skills/coo-orchestrator/SKILL.md) の手順に従い、`define_subagent` と `invoke_subagent` を用いて各部署のサブエージェントを順次起動し、リサーチ ➔ 記事制作 ➔ マーケ告知文作成までを自律的に完遂させる。
2. **部門単体実行（`/research-dept`, `/creative-dept`, `/marketing-dept`）**:
   - 特定の部門のみ実行・再実行したい場合は、該当する部門スキルを使用して対象フェーズのみを実行する。
