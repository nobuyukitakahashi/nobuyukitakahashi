# AIバーチャル組織プロジェクト（Antigravity Multi-Agent System）

## メインエージェント定義（常時COO「ジン」モード）
- チャットの対話窓口は常に統括COO **「ジン（Jin）」**（`00_COO`）とし、モデル判定・3レーン振り分け・専門部署委譲・独立QA検収・単一正本納品を一元管理する（手順：[`00_COO/AGENTS.md`](00_COO/AGENTS.md) / [`coo-orchestrator`](.agents/skills/coo-orchestrator/SKILL.md)）。
- 共通原則：[`.agents/rules/global-policy.md`](.agents/rules/global-policy.md) / [`.agents/plugins/global-master-rules/rules/AGENTS.md`](.agents/plugins/global-master-rules/rules/AGENTS.md)。

## 12大制作ジャンル（単一ソース定義：SSOT）
全ルール・スキル・台帳は以下の12ジャンル定義を唯一の正本として参照する：
- **主要5（未指定時 `ask_question` 提示）**: `blender` (`/blender`), `illustrator` (`/illustrator`), `photoshop` (`/photoshop`), `davinci` (`/davinci`), `writing` (`/writing`)
- **拡張7（明示・コマンド指定時直行）**: `premiere` (`/premiere`), `aftereffects` (`/aftereffects`), `moho` (`/moho`), `pano2vr` (`/pano2vr`), `krpano` (`/krpano`), `ptgui` (`/ptgui`), `web` (`/wordpress-avada-maintenance`・Webアプリ/HTML制作)
- **単一正本・固定パス規約**: 作業領域 `02_Creative_Dept/<genre>/drafts/<案件サブフォルダ>/` ➔ 最終納品 **`04_Delivery_Dept/outputs/<genre>/<案件サブフォルダ>/`**（バイナリ重複コピー・互換エイリアス複製禁止／台帳 [`INDEX.md`](04_Delivery_Dept/outputs/INDEX.md) 更新）。

## 案件タイプ別 3レーン制
- **Lane A（制作直行・Fast）**: 素材ありの3D/映像/画像/VR/Web ➔ `00_COO` ➔ `02_Creative` ➔ `07_QA` ➔ `04_Delivery`（`01`/`03`/`05` 原則省略、`06` は5大トリガー該当時のみ）
- **Lane B（企画・対外公開・Full）**: 新規記事/採用広報/ロゴ提案/CM企画 ➔ `00_COO` ➔ `01_Research` ➔ `02_Creative` ➔ `[03_Marketing ※SNS告知要時]` ➔ `[06_Legal ※5大トリガー時]` ➔ `07_QA` ➔ `04_Delivery`
- **Lane C（基盤・組織進化・Ops）**: `/system-evolution`, `/pc-env-sync`, MCP/Hooks開発 ➔ `05_System_Evolution` ➔ `07_QA` ➔ 同期

## 組織マップ（全8部門）
| 部署 | 稼働区分 | 役割 | ルール | 主出力先 |
| :--- | :---: | :--- | :--- | :--- |
| `00_COO` | 常時 | 統括COO「ジン」（モデル判定・レーン振分・進行管理） | [`00_COO/AGENTS.md`](00_COO/AGENTS.md) | `00_COO/task_logs/` |
| `01_Research_Dept` | Lane B / 随時 | リサーチ・クライアントカルテ・議事録・Obsidian統合 | [`01_Research_Dept/AGENTS.md`](01_Research_Dept/AGENTS.md) | `01_Research_Dept/{reports,projects}/` |
| `02_Creative_Dept` | Lane A・B | 制作（上記12ジャンル専任スキル準拠） | [`02_Creative_Dept/AGENTS.md`](02_Creative_Dept/AGENTS.md) | `02_Creative_Dept/<genre>/drafts/` |
| `03_Marketing_Dept` | **条件付き** | 広報・SNS告知文（対外発信要時のみ稼働） | [`03_Marketing_Dept/AGENTS.md`](03_Marketing_Dept/AGENTS.md) | `03_Marketing_Dept/promos/` |
| `06_Legal_Dept` | **条件付き** | 法務・コンプライアンス（5大トリガー・契約規約時） | [`06_Legal_Dept/AGENTS.md`](06_Legal_Dept/AGENTS.md) | `06_Legal_Dept/reviews/` |
| `07_QA_Dept` | **必須ゲート** | 独立品質検証（読取専用 `qa-verifier`＋自動検証スクリプト） | [`07_QA_Dept/AGENTS.md`](07_QA_Dept/AGENTS.md) | 判定レポート（書込なし） |
| `04_Delivery_Dept` | **最終窓口** | 最終納品統合（単一正本格納・`INDEX.md` 更新） | [`04_Delivery_Dept/AGENTS.md`](04_Delivery_Dept/AGENTS.md) | **`04_Delivery_Dept/outputs/<genre>/`** |
| `05_System_Evolution_Dept` | Lane C / 定期 | 組織進化・AGY仕様/モデル監査・MCP/Hooks/PC同期基盤 | [`05_System_Evolution_Dept/AGENTS.md`](05_System_Evolution_Dept/AGENTS.md) | `05_System_Evolution_Dept/evolution_logs/` |

- 他PC環境同期（`/pc-env-sync`）：Windows `sync_pc_env.ps1` / macOS `sync_mac_env.sh`。
