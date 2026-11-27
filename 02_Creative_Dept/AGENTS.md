# 役割定義：Creative部門（`02_Creative_Dept`：11大ジャンル制作）

制作は11ジャンル（主要5：`blender` / `illustrator` / `photoshop` / `davinci` / `writing`、拡張6：`premiere` / `aftereffects` / `moho` / `pano2vr` / `krpano` / `ptgui`）へ分離し、必ず**案件別サブフォルダ（`<案件サブフォルダ>`）**で作業する。

## 1. ディレクトリ ＆ 専任スキル規約
- **作業先（中間成果物）**: `02_Creative_Dept/<genre>/{drafts,final_outputs}/<案件サブフォルダ>/`
- **最終納品先（`04_Delivery_Dept` 移管先）**: `04_Delivery_Dept/outputs/<genre>/<案件サブフォルダ>/`
- **着手前必須**: 対象 `<genre>` に対応する専任スキル `.agents/skills/<genre>/SKILL.md` を必ず読み込み、ツール接続・カラー/座標/解像度・視覚監査（`read_file` による実画像確認）規約を遵守する。
- モデル判定・`swarm` 昇格は `global-master-rules`（Blender詳細は `blender/SKILL.md`）に委任。

## 2. `writing` 執筆トンマナ・構成
- `01_Research_Dept/reports/report_[テーマ名].md` の事実・出典のみに基づき、`drafts/` へ初稿、`final_outputs/<案件サブフォルダ>/content_[テーマ名].md` へ校正済み原稿を出力する。
- 文体は「です・ます」調（別指定優先）、構成は「タイトル ➔ リード文 ➔ 本文（H2/H3）➔ まとめ ➔ 出典」。

## 3. 禁止事項
- リサーチにない架空データ・数値の捏造禁止。
- `02_Creative_Dept/<genre>/final_outputs/` は中間成果物置き場のため、`04_Delivery_Dept` が回収・パッケージング可能な構造で出力し、`04_Delivery_Dept/outputs/` へ直接書き込まない。
