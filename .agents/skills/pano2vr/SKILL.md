---
name: pano2vr
description: >-
  Pano2VR 8（公式MCP pano2vr / CLI）による360°バーチャルツアーの Skin Editor (.ggsk) 制御・プレビュー監査・HTML5書き出しスキル。
  /pano2vr 指定時、または Pano2VR 制作依頼時に使用。
---

# 🌐 Pano2VR 8 バーチャルツアー・スキン制作専任スキル (`/pano2vr`)

## 1. ディレクトリ規約
- 試作・監査PNG：`02_Creative_Dept/pano2vr/drafts/<案件サブフォルダ>/`
- 中間成果物（`.ggsk` / `.p2vr`）：`02_Creative_Dept/pano2vr/final_outputs/<案件サブフォルダ>/`
- 最終納品先（HTML5出力 / `.ggpkg` / `.ggsk`）：`04_Delivery_Dept/outputs/pano2vr/<案件サブフォルダ>/`（[`INDEX.md`](../../../04_Delivery_Dept/outputs/INDEX.md) の `Pano2VR 8` 更新）

## 2. 実行手順（MCP `pano2vr` ＆ CLI ハイブリッド）
1. **接続・構成確認**: `mcp_health` / `mcp_status` で稼働確認後、`project_get_overview` / `project_get_nodes` / `project_get_resources` / `project_validate` でプロジェクト構造と欠損を検査。
2. **Skin Editor（`.ggsk`）構築**:
   - 着手前に `skin_design_guidance`、既存資産活用時は `skin_reference_search` / `skin_toolbox_list` を参照。
   - `skin_open_file`（絶対パス）後、`skin_create_element` / `skin_update_element` / `skin_create_action` / `skin_set_logic_block` / `skin_create_variable` / `skin_toolbox_insert_component` / `skin_batch_update` で編集し、`skin_validate_element` で検証。
3. **プレビュー視覚監査ループ【必須】**:
   - `skin_generate_preview`（`width`/`height`/`is_mobile`）➔ `skin_capture_preview` で PNG を取得し `read_file` で重なり・余白・レスポンシブ崩れを監査・修正。終了時は `skin_close_preview` で片付け。
4. **保存・CLI書き出し・納品**:
   - `skin_save_file` / `skin_save_file_as` で `final_outputs/` へ保存。
   - HTML5 ビルドは CLI を実行：`& "C:\Program Files\Pano2VR8\pano2vr.exe" --cli "<project.p2vr>"`（必要に応じ `-t <template.p2vr>`, `--createtour`, `--autolink`, `--outputlist` 併用）。
   - `qa-verifier` 合格後、`04_Delivery_Dept/outputs/pano2vr/<案件サブフォルダ>/` へ格納・`INDEX.md` 更新。
