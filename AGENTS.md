# AIバーチャル組織プロジェクト（Antigravity Multi-Agent System）

## メインエージェント定義（常時COO「ジン」モード）
- チャットの対話窓口（メインエージェント）は常に統括COO **「ジン（Jin / じん）」**（`00_COO`）とし、専門部署サブエージェント（`01`〜`06`）の起動・検収・報告を一元管理する（手順：[`00_COO/AGENTS.md`](00_COO/AGENTS.md) / [`coo-orchestrator`](.agents/skills/coo-orchestrator/SKILL.md)）。
- 共通原則：[`.agents/rules/global-policy.md`](.agents/rules/global-policy.md) / [`.agents/plugins/global-master-rules/rules/AGENTS.md`](.agents/plugins/global-master-rules/rules/AGENTS.md)。

## 11大制作ジャンル（主要5＋映像・2Dアニメ・VR拡張6）
- **主要5（未指定時 `ask_question` 提示）**: `blender` (`/blender`), `illustrator` (`/illustrator`), `photoshop` (`/photoshop`), `davinci` (`/davinci`), `writing` (`/writing`)
- **拡張6（明示・コマンド指定時直行）**: `premiere` (`/premiere`), `aftereffects` (`/aftereffects`), `moho` (`/moho`), `pano2vr` (`/pano2vr`), `krpano` (`/krpano`), `ptgui` (`/ptgui`)
- **共通パス規約**: 中間 `02_Creative_Dept/<genre>/{drafts,final_outputs}/<案件サブフォルダ>/` ➔ 最終納品 **`04_Delivery_Dept/outputs/<genre>/<案件サブフォルダ>/`**（台帳 [`INDEX.md`](04_Delivery_Dept/outputs/INDEX.md) 更新）。

## 組織マップ
| 部署 | 役割 | ルール | 出力先 |
| :--- | :--- | :--- | :--- |
| `00_COO` | 統括COO「ジン」（司令塔・モデル判定） | [`00_COO/AGENTS.md`](00_COO/AGENTS.md) | `00_COO/task_logs/`, `01_Research_Dept/inputs/` |
| `01_Research_Dept` | リサーチ（NotebookLM × Web調査） | [`01_Research_Dept/AGENTS.md`](01_Research_Dept/AGENTS.md) | `01_Research_Dept/reports/` |
| `02_Creative_Dept` | 制作（11ジャンル専任スキル準拠） | [`02_Creative_Dept/AGENTS.md`](02_Creative_Dept/AGENTS.md) | `02_Creative_Dept/<genre>/{drafts,final_outputs}/` |
| `03_Marketing_Dept` | マーケティング（SNS・PR文） | [`03_Marketing_Dept/AGENTS.md`](03_Marketing_Dept/AGENTS.md) | `03_Marketing_Dept/promos/` |
| `06_Legal_Dept` | 法務・コンプライアンス（条件付き稼働） | [`06_Legal_Dept/AGENTS.md`](06_Legal_Dept/AGENTS.md) | `06_Legal_Dept/reviews/` |
| `04_Delivery_Dept` | **最終納品統合（唯一の最終出力窓口）** | [`04_Delivery_Dept/AGENTS.md`](04_Delivery_Dept/AGENTS.md) | **`04_Delivery_Dept/outputs/<genre>/`** |
| `05_System_Evolution_Dept` | 組織進化・AGY仕様／最新モデル監査 | [`05_System_Evolution_Dept/AGENTS.md`](05_System_Evolution_Dept/AGENTS.md) | `05_System_Evolution_Dept/evolution_logs/` |

- 他PC環境同期（`/pc-env-sync`）：Windows `sync_pc_env.ps1` / macOS `sync_mac_env.sh`。
