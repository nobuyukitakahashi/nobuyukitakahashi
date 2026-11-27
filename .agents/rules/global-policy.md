# 組織全体共通ポリシー（Global Governance Rules）

本ワークスペースの全エージェント（`00_COO`〜`06_Legal_Dept`）が遵守する共通規則。モデル判定・実証ファースト・自動同期・`qa-verifier`・ハルシネーション防止・基準年2026年・UTF-8（BOMなし）は単一ソース [`.agents/plugins/global-master-rules/rules/AGENTS.md`](../plugins/global-master-rules/rules/AGENTS.md) に一元委任する。

## 1. ディレクトリ権限境界
- 各サブエージェントは自部署フォルダおよび明示された入出力先以外のファイルを作成・変更・削除してはならない。
- **ルール・スキル改訂権限**: `01`〜`04`・`06` による `AGENTS.md` / `.agents/` 改訂は禁止。**`05_System_Evolution_Dept`** のみが `00_COO` 管理下で自律改訂特権を持つ。

## 2. 単方向パイプライン ＆ 最終出力（Output）一元化
- **標準フロー**: `00_COO` ➔ `01_Research_Dept` ➔ `02_Creative_Dept` ➔ `03_Marketing_Dept` ➔ `[06_Legal_Dept ※該当案件のみ]` ➔ **`04_Delivery_Dept`** ➔ `05_System_Evolution_Dept`
- **固定出力の絶対原則**: `01`・`02`・`03`・`06` の出力物はすべて**中間成果物**であり、ユーザーへ引き渡す最終成果物は形式を問わず必ず **`04_Delivery_Dept`** が **`04_Delivery_Dept/outputs/<genre>/<案件サブフォルダ>/`** へ統合・変換格納し `INDEX.md` を更新する。

## 3. 自律的組織改善（Self-Evolution）
- `00_COO` はパイプライン完了時・定期点検時に `05_System_Evolution_Dept` を稼働させ、Antigravity最新仕様・利用可能モデル・実行ログを監査してルール・スキルを自律最新化する。
