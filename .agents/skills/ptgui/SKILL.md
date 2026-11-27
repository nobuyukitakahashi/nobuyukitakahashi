---
name: ptgui
description: >-
  PTGui Pro 13（MCP ptgui / CLI / -stitchnogui）による360°パノラマスティッチ・HDR合成・.pts制御とヘッドレス書き出しスキル。
  /ptgui 指定時、またはパノラマスティッチ・Equirectangular生成依頼時に使用。
---

# 📸 PTGui Pro 13 パノラマスティッチ・HDR合成専任スキル (`/ptgui`)

## 1. ディレクトリ規約
- 試作・`.pts`・軽量プレビュー：`02_Creative_Dept/ptgui/drafts/<案件サブフォルダ>/`
- 中間成果物（完成版 `.pts` / テンプレート）：`02_Creative_Dept/ptgui/final_outputs/<案件サブフォルダ>/`
- 最終納品先（Equirectangular `.jpg`/`.tif`/`.psd`/`.exr`/`.dng`）：`04_Delivery_Dept/outputs/ptgui/<案件サブフォルダ>/`（[`INDEX.md`](../../../04_Delivery_Dept/outputs/INDEX.md) の `PTGui Pro 13` 更新）

## 2. 制御ツール（MCP `ptgui` / CLI `node .agents/mcp/ptgui-mcp/cli.js`）
- **バイナリ**: Win `C:\Program Files\PTGui\PTGui.exe` / Mac `/Applications/PTGui Pro.app/Contents/MacOS/PTGui Pro`
- **6ツール**: `get_ptgui_status` (`status`), `create_ptgui_project` (`create`), `get_project_summary` (`summary`), `update_project_settings` (`update`), `stitch_project` (`stitch`), `open_in_ptgui_gui` (`open`)

## 3. 標準実行手順
1. **確認・生成**: `cli.js status` で環境確認後、`cli.js create --dir "<入力>" --out "02_Creative_Dept/ptgui/drafts/<案件>/project.pts" --projection equirectangular --hfov 360 --vfov 180 --blend zerooverlap --fill-holes true` で `.pts`（JSON v55）生成。
2. **軽量プレビュー ＆ 視覚監査【必須】**:
   - `cli.js stitch --file "<project.pts>" --out "<preview_audit.jpg>" --scale 0.25` で25%プレビュー出力。
   - `read_file` で水平傾き・シーム・露出ムラ・天頂/天底欠けを監査し、必要時は `cli.js update` で投影法・`yaw/pitch/roll`・`blend_engine`（`zerooverlap` ⇄ `multiband`）・`fill_holes`・HDR設定を補正して再検証。
3. **本番スティッチ ＆ 納品**:
   - 確定 `.pts` を `final_outputs/` へ保存し、`scale_fraction: 1.0`（または指定解像度・形式）で `04_Delivery_Dept/outputs/ptgui/<案件サブフォルダ>/` へ本番書き出し。
   - 下流 `/pano2vr`・`/krpano` へそのまま連携可能。`qa-verifier` 合格後に `INDEX.md` 更新。
