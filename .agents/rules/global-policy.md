# 組織全体共通ポリシー（Global Governance Rules）

本ワークスペースの全エージェント（`00_COO`〜`07_QA_Dept`）が遵守する共通規則。モデル判定・実証ファースト・自動同期・`qa-verifier`・ハルシネーション防止・基準年2026年・UTF-8（BOMなし）は単一ソース [`.agents/plugins/global-master-rules/rules/AGENTS.md`](../plugins/global-master-rules/rules/AGENTS.md) に一元委任する。

## 1. ディレクトリ権限境界
- 各サブエージェントは自部署フォルダおよび明示された入出力先以外のファイルを作成・変更・削除してはならない。
- **ルール・スキル・基盤改訂権限**: `01`〜`04`・`06`・`07` による `AGENTS.md` / `.agents/` 改訂は禁止。**`05_System_Evolution_Dept`** のみが `00_COO` 管理下で自律改訂特権を持つ。
- **`07_QA_Dept`（`qa-verifier`）は完全読み取り専用**（`EnableWriteTools: false`）とし、ファイル編集権限を付与しない。

## 2. 3レーン制 ＆ 単一正本納品（Single Source of Truth）
- **案件レーン**: ルート [`AGENTS.md`](../../AGENTS.md) 定義の3レーン（Lane A: 制作直行 / Lane B: 企画・対外公開 / Lane C: 基盤・進化）に従い、不要工程を無理に挟まず必要工程を確実に踏む。
- **最終出力一元化 ＆ 重複コピー禁止**: 最終成果物は必ず `04_Delivery_Dept` が **`04_Delivery_Dept/outputs/<genre>/<案件サブフォルダ>/`** へ**単一正本として格納（移動または直接最終出力）**し `INDEX.md` を更新する。制作側に同一バイナリを残置・互換エイリアス多重複製してはならない。
- **Git / Google Drive 責務分離**: Git はルール・スクリプト・Markdown仕様書・台帳・軽量アセットを管理し、大容量メディア/バイナリ（`.mp4`/`.wav`/`.blend`/`.glb`/`.psd`/`.aep`/`.drp` 等）は汎用 `.gitignore` により Google Drive 同期へ委ねる。

## 3. 自律的組織改善 ＆ 機械的検証
- `05_System_Evolution_Dept` が定期点検・基盤更新時に `07_QA_Dept/scripts/verify_org.py` と Antigravity 最新仕様・モデル照会を実行し、ルール・スキル・Hooks・MCP基盤を最新化する。
