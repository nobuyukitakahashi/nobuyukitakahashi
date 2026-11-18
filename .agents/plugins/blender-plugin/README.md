# Blender Creative Plugin (`02_Creative_Dept` 連携用)

本プラグインは、制作・編集部門（`02_Creative_Dept`）サブエージェントおよび統括COOが **Blender Lab 公式 MCP**（`projects.blender.org/lab/blender_mcp` / MCPサーバー名: `blender`）に直接アクセスし、3Dモデリング・マテリアル設定・レンダリング・スクリーンショット視覚監査・`.blend` / `.glb` 出力を自律実行するためのワークスペースプラグインです。

## 主な機能（公式 MCP `blender` ツール群）
1. **`get_objects_summary` / `get_object_detail_summary`**: シーン内のオブジェクト一覧、階層、座標、詳細属性を取得。
2. **`execute_blender_code` / `execute_blender_code_for_cli`**: 稼働中のBlender（またはCLIバックグラウンド）内でPython（`bpy`, `bmesh`, `mathutils`）を実行し、モデリング・マテリアル構築・ライティング・アニメーション・ファイル書き出しを制御（戻り値は `result = {...}` の dict 形式で返す）。
3. **`render_viewport_to_path` / `get_screenshot_of_window_as_image`**: ビューポートレンダリング画像やBlenderウィンドウのスクリーンショットを保存し、エージェント自身が視覚的に出来栄えを監査。
4. **`get_blendfile_summary_*`**: `.blend` ファイル内のデータブロック、不足ファイル、リンクライブラリ、パス情報を検査。
5. **`search_api_docs` / `search_manual_docs`**: Blender Python API や公式マニュアルを検索。

## セットアップ・有効化手順
1. **公式 MCP サーバーの導入（初回のみ）**:
   ```powershell
   uv tool install --python 3.12 --from "git+https://projects.blender.org/lab/blender_mcp.git#subdirectory=mcp" blender-mcp
   ```
2. **Blender 側の公式拡張機能（`MCP`）とオンラインアクセス有効化**:
   - `Edit > Preferences > System > Network` で **Allow Online Access（オンラインアクセスを許可）** を有効化。
   - `Edit > Preferences > Add-ons` で **MCP**（`bl_ext.user_default.mcp`）が有効化され、`Server is running`（`localhost:9876`）になっていることを確認してください。
3. **最終出力ルール**:
   制作されたレンダリング画像（`.png`）、3Dファイル（`.blend`, `.glb` 等）、および制作仕様書は、中間保存先（`02_Creative_Dept/blender/final_outputs/`）から `04_Delivery_Dept` を通じて固定フォルダ **`04_Delivery_Dept/outputs/blender/`** に納品されます。
