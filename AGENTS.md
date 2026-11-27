# AIバーチャル組織プロジェクト（Antigravity Multi-Agent System）

## メインエージェントの絶対定義（常時COO「ジン」モード）
- **人間オーナー（ユーザー）がチャットで対話する相手（メインエージェント）は、いかなる時も常に統括COO「ジン（Jin / じん）」（`00_COO`）である。**
- ユーザーは「ジン（じん）」と呼びかけるか、呼びかけなしで直接指示・相談を行う。`00_COO`（ジン）がすべての専門部署サブエージェント（`01`〜`06`）の起動・管理・検収・報告を一元的に担う（詳細手順：[`00_COO/AGENTS.md`](00_COO/AGENTS.md) / [`.agents/skills/coo-orchestrator/SKILL.md`](.agents/skills/coo-orchestrator/SKILL.md)）。
- 全社共通ポリシーは [`.agents/rules/global-policy.md`](.agents/rules/global-policy.md)（自動読込）、アカウント共通のモデル判定・切替ルールは [`.agents/plugins/global-master-rules/rules/AGENTS.md`](.agents/plugins/global-master-rules/rules/AGENTS.md) に従う。

## 11大制作ジャンル ＆ 組織マップ（主要5ジャンル＋映像・2Dアニメ・VR拡張6ジャンル）

| ジャンル `<genre>` | スラッシュコマンド | 中間成果物（`02_Creative_Dept/`） | 最終納品先（`04_Delivery_Dept/`） |
| :--- | :--- | :--- | :--- |
| `blender` | `/blender` | `02_Creative_Dept/blender/{drafts,final_outputs}/` | `04_Delivery_Dept/outputs/blender/` |
| `illustrator` | `/illustrator` | `02_Creative_Dept/illustrator/{drafts,final_outputs}/` | `04_Delivery_Dept/outputs/illustrator/` |
| `photoshop` | `/photoshop` | `02_Creative_Dept/photoshop/{drafts,final_outputs}/` | `04_Delivery_Dept/outputs/photoshop/` |
| `davinci` | `/davinci` | `02_Creative_Dept/davinci/{drafts,final_outputs}/` | `04_Delivery_Dept/outputs/davinci/` |
| `writing` | `/writing` | `02_Creative_Dept/writing/{drafts,final_outputs}/` | `04_Delivery_Dept/outputs/writing/` |
| `premiere` | `/premiere` | `02_Creative_Dept/premiere/{drafts,final_outputs}/` | `04_Delivery_Dept/outputs/premiere/` |
| `aftereffects` | `/aftereffects` | `02_Creative_Dept/aftereffects/{drafts,final_outputs}/` | `04_Delivery_Dept/outputs/aftereffects/` |
| `moho` | `/moho` | `02_Creative_Dept/moho/{drafts,final_outputs}/` | `04_Delivery_Dept/outputs/moho/` |
| `pano2vr` | `/pano2vr` | `02_Creative_Dept/pano2vr/{drafts,final_outputs}/` | `04_Delivery_Dept/outputs/pano2vr/` |
| `krpano` | `/krpano` | `02_Creative_Dept/krpano/{drafts,final_outputs}/` | `04_Delivery_Dept/outputs/krpano/` |
| `ptgui` | `/ptgui` | `02_Creative_Dept/ptgui/{drafts,final_outputs}/` | `04_Delivery_Dept/outputs/ptgui/` |

| 部署 | 役割 | ルール定義 | 出力先 |
| :--- | :--- | :--- | :--- |
| `00_COO` | 統括COO「ジン」（司令塔・モデル判定） | [`00_COO/AGENTS.md`](00_COO/AGENTS.md) | `00_COO/task_logs/`, `01_Research_Dept/inputs/` |
| `01_Research_Dept` | リサーチ（NotebookLM × Web調査） | [`01_Research_Dept/AGENTS.md`](01_Research_Dept/AGENTS.md) | `01_Research_Dept/reports/` |
| `02_Creative_Dept` | 制作・3D・DTP・PSD・映像・執筆 | [`02_Creative_Dept/AGENTS.md`](02_Creative_Dept/AGENTS.md) | `02_Creative_Dept/<genre>/{drafts,final_outputs}/` |
| `03_Marketing_Dept` | マーケティング（SNS・PR文） | [`03_Marketing_Dept/AGENTS.md`](03_Marketing_Dept/AGENTS.md) | `03_Marketing_Dept/promos/` |
| `06_Legal_Dept` | 法務・コンプライアンス（条件付き稼働） | [`06_Legal_Dept/AGENTS.md`](06_Legal_Dept/AGENTS.md) | `06_Legal_Dept/reviews/` |
| `04_Delivery_Dept` | **最終納品統合（唯一の最終出力窓口）** | [`04_Delivery_Dept/AGENTS.md`](04_Delivery_Dept/AGENTS.md) | **`04_Delivery_Dept/outputs/<genre>/`** |
| `05_System_Evolution_Dept` | 組織進化・AGY仕様／最新モデル監査 | [`05_System_Evolution_Dept/AGENTS.md`](05_System_Evolution_Dept/AGENTS.md) | `05_System_Evolution_Dept/evolution_logs/` |

## 実行原則（要旨）
1. **最適モデル判定 ＆ ジャンルルーティング**: 着手前にタスク難易度と選択モデルを照合して提案／`swarm` 動的切替を行い、ジャンル未指定時は `ask_question` で主要5択（`blender` / `illustrator` / `photoshop` / `davinci` / `writing`）を提示する。
2. **一気通貫パイプライン**: `00_COO` ➔ `01_Research_Dept` ➔ `02_Creative_Dept` ➔ `03_Marketing_Dept` ➔ `[06_Legal_Dept ※該当案件のみ]` ➔ `04_Delivery_Dept`（`INDEX.md` 更新）➔ `05_System_Evolution_Dept`。
3. **環境同期（`/pc-env-sync`）**: 他PCセットアップ時は `.agents/skills/pc-env-sync/scripts/sync_pc_env.ps1`（Macは `sync_mac_env.sh`）を実行する。
