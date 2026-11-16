---
name: ptgui
description: >-
  PTGui Pro 13（ローカルMCPサーバー ptgui および CLIブリッジ .agents/mcp/ptgui-mcp/cli.js、
  本体 "C:/Program Files/PTGui/PTGui.exe"）を用いた 360°パノラマスティッチ、HDRパノラマ合成、
  .pts（JSON v55）プロジェクト自動生成・投影法/レンズ/ブレンディング設定制御、
  およびヘッドレス書き出し（-stitchnogui）＋視覚監査を実行し、
  中間成果物を 02_Creative_Dept/ptgui/ に、最終成果物を 04_Delivery_Dept/outputs/ptgui/ に格納するスキル。
  ユーザーが /ptgui を指定した際、または PTGui でのパノラマスティッチ・360°正距円筒図法（Equirectangular）生成を指示した際に使用する。
---

# 📸 PTGui Pro 13 パノラマスティッチ・HDR合成専任スキル (`/ptgui`)

## 1. ディレクトリ規約（案件別サブフォルダ分離）

本スキルは既存の5大ジャンル（`blender` / `illustrator` / `photoshop` / `davinci` / `writing`）および `/pano2vr`・`/krpano` とフォルダを完全に分離して運用する単体操作スキルです。

- **試作・検証用 `.pts`・軽量プレビューパノラマ置き場**:
  - [`02_Creative_Dept/ptgui/drafts/`](../../../02_Creative_Dept/ptgui/drafts/)（案件単位で `<案件サブフォルダ>/` を切って分離）
- **制作部門の完成中間成果物置き場（完成版 `.pts` プロジェクト / カスタムテンプレート `.pts` / 仕様メモ）**:
  - [`02_Creative_Dept/ptgui/final_outputs/`](../../../02_Creative_Dept/ptgui/final_outputs/)（`<案件サブフォルダ>/` で分離）
- **最終納品フォルダ（高解像度パノラマ Equirectangular JPEG / 16bit・32bit TIFF / レイヤー付き PSD / EXR / DNG）**:
  - [`04_Delivery_Dept/outputs/ptgui/`](../../../04_Delivery_Dept/outputs/ptgui/)（`<案件サブフォルダ>/` で分離）
  - 納品時は必ず [`04_Delivery_Dept/outputs/INDEX.md`](../../../04_Delivery_Dept/outputs/INDEX.md) の `PTGui Pro 13` セクションへ追記する。

---

## 2. 制御アーキテクチャ（MCPサーバー `ptgui` ＆ CLIブリッジ）

- **ローカルMCPサーバー**: [`server.js`](../../mcp/ptgui-mcp/server.js)（MCPサーバー名: `ptgui`）
- **即時実行CLIブリッジ**: [`cli.js`](../../mcp/ptgui-mcp/cli.js)（`node .agents/mcp/ptgui-mcp/cli.js <subcommand>`）
- **PTGui Pro 13 実行バイナリ**:
  - Windows: `C:\Program Files\PTGui\PTGui.exe`（ビューア: `C:\Program Files\PTGui\PTGuiViewer.exe`）
  - macOS: `/Applications/PTGui Pro.app/Contents/MacOS/PTGui Pro`
- **提供ツール一覧（MCP / CLI 共通）**:
  1. `get_ptgui_status` (`cli.js status`): インストール状態・バージョン・保存済みテンプレート（`%APPDATA%\PTGui\Templates\*.pts`）の確認
  2. `create_ptgui_project` (`cli.js create`): `-createproject` による `.pts`（JSON v55）ヘッドレス生成＋初期パラメータ適用
  3. `get_project_summary` (`cli.js summary`): `.pts` 内の画像枚数・レンズ・投影法・FOV・出力設定・コントロールポイント数・最適化状態の解析
  4. `update_project_settings` (`cli.js update`): `.pts` JSON の投影法（`equirectangular` / `rectilinear` / `cylindrical` / `stereographic`）、HFOV/VFOV、出力解像度（相対比率または固定ピクセル）、出力形式（`jpeg` / `tiff` / `psd` / `exr` / `dng`）、ブレンディング（`zerooverlap` / `multiband` / `fillholes`）、HDR設定、画像ごとの `yaw/pitch/roll` の安全な更新
  5. `stitch_project` (`cli.js stitch`): `-stitchnogui` による完全ヘッドレスのアライメント＆パノラマ書き出し（`scale_fraction` による高速プレビュー出力対応）
  6. `open_in_ptgui_gui` (`cli.js open`): 必要時に `.pts` または出力パノラマを `PTGui.exe` / `PTGuiViewer.exe` で起動

---

## 3. 標準実行手順（生成 ➔ 設定 ➔ プレビュー視覚監査 ➔ 本番スティッチ ➔ 納品）

### フェーズ1：環境確認とプロジェクト生成（`drafts/<案件サブフォルダ>/`）
1. **ステータス確認**:
   - MCP `get_ptgui_status` または `node .agents/mcp/ptgui-mcp/cli.js status` を実行し、PTGui Pro 13 と利用可能テンプレートを確認する。
2. **`.pts` プロジェクト生成**:
   - 入力画像（またはフォルダ）から `02_Creative_Dept/ptgui/drafts/<案件サブフォルダ>/project.pts` を生成する：
     ```powershell
     node .agents/mcp/ptgui-mcp/cli.js create `
       --dir "<入力画像フォルダ>" `
       --out "02_Creative_Dept/ptgui/drafts/<案件サブフォルダ>/project.pts" `
       --projection equirectangular --hfov 360 --vfov 180 `
       --blend zerooverlap --fill-holes true
     ```

### フェーズ2：軽量プレビュー書き出し ＆ `read_file` 視覚監査【必須】
1. **高速プレビュースティッチ（25%スケール）**:
   - いきなりフル解像度で長時間レンダリングせず、まず `scale_fraction: 0.25` で軽量プレビュー画像を書き出す：
     ```powershell
     node .agents/mcp/ptgui-mcp/cli.js stitch `
       --file "02_Creative_Dept/ptgui/drafts/<案件サブフォルダ>/project.pts" `
       --out "02_Creative_Dept/ptgui/drafts/<案件サブフォルダ>/preview_audit.jpg" `
       --scale 0.25
     ```
2. **視覚監査ループ**:
   - 生成された `preview_audit.jpg` を `read_file` で目視確認し、水平線の傾き、シーム（継ぎ目）のズレ、露出ムラ、天頂（Zenith）・天底（Nadir）の欠けがないか点検する。
   - 補正が必要な場合は `update_project_settings`（`cli.js update`）でレンズ投影法、初期 `yaw/pitch/roll`、`blend_engine`（`zerooverlap` ⇄ `multiband`）、`fill_holes`、または HDR/露出設定を調整して再検証する。

### フェーズ3：フル解像度本番スティッチ ＆ 最終納品（Pano2VR / krpano 連携）
1. **完成版 `.pts` の保存**:
   - 確定した `.pts` プロジェクトを `02_Creative_Dept/ptgui/final_outputs/<案件サブフォルダ>/` へ保存する。
2. **フル解像度パノラマの本番スティッチ**:
   - `scale_fraction: 1.0`（または指定の固定解像度 `width`×`height`、フォーマット `jpeg` / `tiff` / `psd` / `exr`）で `04_Delivery_Dept/outputs/ptgui/<案件サブフォルダ>/` へ最終パノラマを書き出す。
3. **下流VRツアー制作（`/pano2vr`・`/krpano`）への連携**:
   - 書き出した 360° Equirectangular パノラマ画像をそのまま `/pano2vr` または `/krpano` の入力として渡し、HTML5 バーチャルツアーまで一気通貫で構築できる。
4. **納品台帳更新**:
   - [`04_Delivery_Dept/outputs/INDEX.md`](../../../04_Delivery_Dept/outputs/INDEX.md) の `PTGui Pro 13` セクションへ納品情報を追記し、ユーザーへ最終成果物リンクを報告する。
