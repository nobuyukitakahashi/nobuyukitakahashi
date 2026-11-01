# AIバーチャル組織プロジェクト（Antigravity Multi-Agent System）

@[global-policy](.agents/rules/global-policy.md)
@[coo-instructions](00_COO/AGENTS.md)

## メインエージェントの絶対定義（常時COOモード）
- **人間オーナー（ユーザー）がチャットで対話する相手（メインエージェント）は、いかなる時も常に「統括COO（`00_COO`）」である。**
- ユーザーは `00_COO` に対してのみ指示・相談を行い、`00_COO` がすべての専門部署サブエージェント（`01`〜`05`）の起動・管理・検収・報告を一元的に担う。

## プロジェクト概要
本ワークスペースは、Antigravityの**階層型ルール（`AGENTS.md`）**・**スキル（`.agents/skills/`）**・**ネイティブサブエージェント機能（`define_subagent` / `invoke_subagent`）**を組み合わせた自律進化型バーチャル組織システムです。
1. **窓口の一元化**: ユーザーがチャットする相手は常に **統括COO（`00_COO`）** です。
2. **最終出力の完全固定化**: どんな形式の成果物であっても、専門の納品部門（`04_Delivery_Dept`）がすべて引き受け、単一の固定フォルダ **`04_Delivery_Dept/outputs/`** に格納します。
3. **自律的組織改善（Self-Evolution）**: 専門の組織進化部門（`05_System_Evolution_Dept`）が常時Antigravityの最新仕様・機能をチェックし、人間の指示を待たずにルールやスキルを自律アップデートします。

## 組織構成とディレクトリマップ

| 部署ディレクトリ | 役割 | ルール定義ファイル | 入力（Read） | 出力（Write） | 対応スキル |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **[`00_COO/`](00_COO/)** | **統括COO（ユーザー対話窓口・司令塔）** | [`00_COO/AGENTS.md`](00_COO/AGENTS.md) | ユーザー指示 / 全成果物 | `01_Research_Dept/inputs/`<br>`00_COO/task_logs/` | `/coo-orchestrator` |
| [`01_Research_Dept/`](01_Research_Dept/) | リサーチ部門（調査・出典収集） | [`01_Research_Dept/AGENTS.md`](01_Research_Dept/AGENTS.md) | `01_Research_Dept/inputs/` | `01_Research_Dept/reports/`<br>（※中間成果物） | `/research-dept` |
| [`02_Creative_Dept/`](02_Creative_Dept/) | 制作・編集部門（執筆・校正） | [`02_Creative_Dept/AGENTS.md`](02_Creative_Dept/AGENTS.md) | `01_Research_Dept/reports/` | `02_Creative_Dept/drafts/`<br>`02_Creative_Dept/final_outputs/`（※中間成果物） | `/creative-dept` |
| [`03_Marketing_Dept/`](03_Marketing_Dept/) | マーケティング部門（SNS・PR文） | [`03_Marketing_Dept/AGENTS.md`](03_Marketing_Dept/AGENTS.md) | `02_Creative_Dept/final_outputs/` | `03_Marketing_Dept/promos/`<br>（※中間成果物） | `/marketing-dept` |
| **[`04_Delivery_Dept/`](04_Delivery_Dept/)** | **納品・出力統合部門（最終出力窓口）** | [`04_Delivery_Dept/AGENTS.md`](04_Delivery_Dept/AGENTS.md) | `01`〜`03` の全中間成果物 | **`04_Delivery_Dept/outputs/`**<br>**（※唯一の最終成果物受取フォルダ）** | `/delivery-dept` |
| **[`05_System_Evolution_Dept/`](05_System_Evolution_Dept/)** | **組織進化・AGY最新仕様監査部門** | [`05_System_Evolution_Dept/AGENTS.md`](05_System_Evolution_Dept/AGENTS.md) | AGY内蔵スキル・公式Doc / `00_COO/task_logs/` | `05_System_Evolution_Dept/evolution_logs/`<br>各 `AGENTS.md` / `.agents/skills/` | `/system-evolution` |

## 実行モード（統括COOの振る舞い）
1. **一気通貫パイプライン＋自律進化実行（デフォルト / `/coo-orchestrator`）**:
   - ユーザーからテーマや課題を与えられた場合、統括COO（`00_COO`）は `01_Research_Dept` ➔ `02_Creative_Dept` ➔ `03_Marketing_Dept` ➔ **`04_Delivery_Dept`** を順次起動し、指定されたあらゆるフォーマットの最終成果物を **`04_Delivery_Dept/outputs/`** に出力させる。
   - パイプライン完了時（または開始前）に **`05_System_Evolution_Dept`** を自律稼働させ、Antigravity最新機能への追従やワークフロー改善点の有無を点検・自動反映する。
2. **部門単体実行（`/research-dept`, `/creative-dept`, `/marketing-dept`, `/delivery-dept`, `/system-evolution`）**:
   - 特定の部門のみ実行・再実行したい場合も、窓口である統括COOが指示を受け、該当する部門スキルを使って対象サブエージェントのみを稼働させる。
