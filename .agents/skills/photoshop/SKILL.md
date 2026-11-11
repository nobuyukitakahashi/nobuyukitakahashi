---
name: photoshop
description: >-
  Adobe Photoshop 2027（MCPサーバー photoshop および CLIブリッジ .agents/mcp/photoshop-mcp/cli.js）を用いた
  画像編集、フォトレタッチ、マルチレイヤーPSD合成、バナー・サムネイル制作、カラーモード変換（RGB/CMYK）を専任で実行し、
  中間成果物を 02_Creative_Dept/photoshop/ に、最終成果物を 04_Delivery_Dept/outputs/photoshop/ に格納するスキル。
  ユーザーが /photoshop を指定した際、またはジャンル選択で「Photoshop（画像編集・レタッチ・PSD合成・バナー制作）」を選択した際に使用する。
---

# 🖼️ Adobe Photoshop 画像編集・レタッチ・PSD合成専任スキル (`/photoshop`)

## 1. ジャンル別ディレクトリ規約（厳守）
- **試作・JSXスクリプト・素材画像置き場**:
  - [`02_Creative_Dept/photoshop/drafts/`](../../../02_Creative_Dept/photoshop/drafts/)
- **制作部門の完成中間成果物置き場**:
  - [`02_Creative_Dept/photoshop/final_outputs/`](../../../02_Creative_Dept/photoshop/final_outputs/)
- **最終納品フォルダ（`04_Delivery_Dept` による格納先）**:
  - [`04_Delivery_Dept/outputs/photoshop/`](../../../04_Delivery_Dept/outputs/photoshop/)
  - ※納品台帳 [`04_Delivery_Dept/outputs/INDEX.md`](../../../04_Delivery_Dept/outputs/INDEX.md) の「`## 🖼️ 3. Adobe Photoshop`」セクションにリンク（`photoshop/ファイル名`）を追記する。

---

## 2. 実行手順（MCP `photoshop` ＆ CLI ハイブリッド運用）

詳細なExtendScript（DOM + ActionManager）実装パターンは [`.agents/skills/adobe-photoshop/SKILL.md`](../adobe-photoshop/SKILL.md) を参照してください。

1. **Photoshop 2027 ステータス確認**:
   - MCPサーバー `photoshop` の `get_photoshop_status` または CLI `node .agents/mcp/photoshop-mcp/cli.js status` を実行する。
2. **ExtendScript (JSX) スクリプトによるマルチレイヤーPSD構築・レタッチ**:
   - スクリプトを `02_Creative_Dept/photoshop/drafts/build_[テーマ名].jsx` に作成し、`execute_photoshop_jsx` または `node .agents/mcp/photoshop-mcp/cli.js exec --file "02_Creative_Dept/photoshop/drafts/build_[テーマ名].jsx"` で実行する。
   - **単位とダイアログの固定**: スクリプト冒頭で必ず `app.displayDialogs = DialogModes.NO;`、`app.preferences.rulerUnits = Units.PIXELS;`、`app.preferences.typeUnits = TypeUnits.PIXELS;` を設定する。
   - **非破壊レイヤー階層設計**: 背景グループ（`LayerSet`）、ビジュアル・シェイプグループ、タイポグラフィグループ等にレイヤーを整理し、後から再編集可能な `.psd` 構造を維持する。
3. **カンバスPNG書き出し＋`read_file` 視覚監査ループ**:
   - `export_canvas_png`（または `node .agents/mcp/photoshop-mcp/cli.js export-png --out "02_Creative_Dept/photoshop/final_outputs/[テーマ名].png" --scale 100`）で高画質PNGを書き出す。
   - `read_file` で書き出されたPNG画像を実際に目視確認し、レイアウトバランス・文字配置・色味・コントラスト・切り抜き境界を監査・修正する。
4. **ネイティブPSD保存と最終納品**:
   - `save_photoshop_document`（または `node .agents/mcp/photoshop-mcp/cli.js save --out "02_Creative_Dept/photoshop/final_outputs/[テーマ名].psd"`）でレイヤー保持版の `.psd`（および必要に応じた `.png` / `.jpg` / `.tiff`）と制作仕様書 `content_[テーマ名].md` を `02_Creative_Dept/photoshop/final_outputs/` に保存する。
   - 続けて `04_Delivery_Dept` を通じて `04_Delivery_Dept/outputs/photoshop/` に最終成果物を格納し、`04_Delivery_Dept/outputs/INDEX.md` を更新する。
