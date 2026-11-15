---
name: pano2vr
description: >-
  Pano2VR 8（公式MCPサーバー pano2vr および CLI "C:/Program Files/Pano2VR8/pano2vr.exe" --cli）を用いた
  360°パノラマ・バーチャルツアーの Skin Editor 制御（.ggsk 構築・Components Toolbox 活用・プレビューPNG視覚監査）、
  プロジェクト検証（project_validate）、およびバッチHTML5書き出しを実行し、
  中間成果物を 02_Creative_Dept/pano2vr/ に、最終成果物を 04_Delivery_Dept/outputs/pano2vr/ に格納するスキル。
  ユーザーが /pano2vr を指定した際、または Pano2VR でのスキン制作・ツアー構築・書き出しを指示した際に使用する。
---

# 🌐 Pano2VR 8 バーチャルツアー・スキン制作専任スキル (`/pano2vr`)

## 1. ディレクトリ規約
- **試作・スキン案・視覚監査用プレビューPNG置き場**:
  - [`02_Creative_Dept/pano2vr/drafts/`](../../../02_Creative_Dept/pano2vr/drafts/)
- **制作部門の完成中間成果物置き場（`.ggsk` / `.p2vr`）**:
  - [`02_Creative_Dept/pano2vr/final_outputs/`](../../../02_Creative_Dept/pano2vr/final_outputs/)
- **最終納品フォルダ（HTML5ツアー出力一式 / `.ggpkg` / `.ggsk`）**:
  - [`04_Delivery_Dept/outputs/pano2vr/`](../../../04_Delivery_Dept/outputs/pano2vr/)
  - 案件単位で管理する場合は各配下に `<案件サブフォルダ>/` を切って分離格納し、納品時は [`04_Delivery_Dept/outputs/INDEX.md`](../../../04_Delivery_Dept/outputs/INDEX.md) を更新する。
  - ※本スキルは既存の5大ジャンル（`blender` / `illustrator` / `photoshop` / `davinci` / `writing`）を変更せずに利用する単体操作スキルです。

---

## 2. 実行手順（MCP `pano2vr` ＆ CLI ハイブリッド運用）

### フェーズ1：接続・プロジェクト状態確認
1. **MCP ブリッジ稼働確認**:
   - MCP サーバー `pano2vr` の `mcp_health` および `mcp_status` を呼び出し、`status: "ok"`・`running: true` を確認する。
2. **アクティブプロジェクト確認（読み取り専用）**:
   - `project_get_overview` / `project_get_nodes` / `project_get_resources` で開いている `.p2vr` プロジェクトの構成を把握する。
   - 必要に応じて `project_validate` で構造・外部リソース欠損チェックを実行する。

### フェーズ2：Skin Editor（`.ggsk`）の設計・構築・編集（MCP 主体）
1. **設計ガイドラインとリファレンス確認**:
   - 複雑なスキンを新規構築・改修する前は必ず `skin_design_guidance`（`format: "full"` または `"summary"`）を参照する。
   - 既存パターン・アイコン・コンポーネントを流用する場合は `skin_reference_search` や `skin_toolbox_list` / `skin_toolbox_get_preview` を活用する。
2. **スキンファイルの読み込み／新規作成・要素編集**:
   - 既存スキンを開く場合は `skin_open_file`（`path` に絶対パス指定）を実行する。
   - 要素・レイアウト・アクション・モディファイア・ロジックブロック・変数の追加編集は `skin_create_element` / `skin_update_element` / `skin_create_action` / `skin_set_logic_block` / `skin_create_variable` / `skin_toolbox_insert_component` / `skin_batch_update` 等を用いる（すべて Undo スタック経由で安全に実行される）。
   - `skin_validate_element` で警告・プレースホルダ不備がないか検証する。

### フェーズ3：プレビュー生成＋PNG視覚監査ループ【必須】
1. **プレビュー生成**:
   - `skin_generate_preview`（必要に応じて `width`, `height`, `is_mobile` を指定）を実行し、`preview_id` を取得する。
2. **PNG スクリーンショット撮影＆目視確認**:
   - `skin_capture_preview`（`preview_id` 指定、`encoding: "file"` / 必要に応じて `include_image: true`）で PNG を書き出し、必要なら `02_Creative_Dept/pano2vr/drafts/` へ保存または `read_file` で直接視覚監査する。
   - 要素の重なり、余白、レスポンシブ崩れ、視認性不良があれば修正し、監査完了後に `skin_close_preview` で一時プレビューを片付ける。

### フェーズ4：保存・CLI 書き出し・最終納品
1. **`.ggsk` スキン保存**:
   - `skin_save_file` または `skin_save_file_as`（チェックポイント保存時は `sync_project_reference: false`、プロジェクト反映時は `true`）で `02_Creative_Dept/pano2vr/final_outputs/` へ保存する。
2. **HTML5 ツアー等の自動書き出し（CLI / XML 併用）**:
   - Pano2VR プロジェクト（`.p2vr`）のビルド・一括書き出しは、MCP 対象外のため以下の CLI を使用する：
     ```powershell
     & "C:\Program Files\Pano2VR8\pano2vr.exe" --cli "<project.p2vr>"
     ```
   - テンプレート適用や複数パノラマからのツアー自動生成には `-t <template.p2vr>`、`--createtour`、`--autolink`、`--outputlist` を組み合わせる（終了コード `0`: 成功 / `1`: 失敗 / `2`: キャンセル）。
3. **最終納品格納**:
   - 完成した HTML5 出力一式・`.ggpkg`・`.ggsk` 等を `04_Delivery_Dept/outputs/pano2vr/` に格納し、[`04_Delivery_Dept/outputs/INDEX.md`](../../../04_Delivery_Dept/outputs/INDEX.md) に記録する。
