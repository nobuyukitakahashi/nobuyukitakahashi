# Blender Creative Plugin (`02_Creative_Dept` 連携用)

本プラグインは、制作・編集部門（`02_Creative_Dept`）サブエージェントおよび統括COOが **Blender MCP**（`mcp-for-blender` / MCPサーバー名: `blender`）に直接アクセスし、3Dモデリング・アセット配置・マテリアル設定・レンダリング・`.blend` / `.glb` 出力を自律実行するためのワークスペースプラグインです。

## 主な機能（MCP `blender` ツール群）
1. **`get_addon_status`**: Blender本体の接続状態、バージョン、有効なアセットライブラリ（Poly Haven / Sketchfab / Poly Pizza）および3D生成AIプロバイダーを確認。
2. **`get_scene_info`**: シーン内のオブジェクト一覧、座標（`location`）、バウンディングボックスサイズ（`size`）、階層、メッシュトポロジ、レンダリング設定を取得。
3. **`execute_blender_code`**: 稼働中のBlender内でPython（`bpy`, `bmesh`, `mathutils`）を直接実行し、モデリング・マテリアル構築・ライティング・アニメーション・ファイル書き出し（`.blend`, `.glb`, `.fbx`, `.png`）を制御。
4. **`look`**: ビューポート、カメラ視点、4面アングル（`front`, `right`, `top`, `three_quarter`）、またはアニメーションフレームを画像としてキャプチャし、エージェント自身が視覚的に出来栄えを監査。
5. **`search_assets` / `import_asset`**: Poly Haven（HDRI・PBRテクスチャ・3Dモデル）、Sketchfab、Poly Pizza からアセットを検索・インポート。
6. **`generate_3d`**: テキストプロンプトまたは参照画像からテクスチャ付き3Dモデルを生成・インポート。

## セットアップ・有効化手順
1. **アドオンのインストール（初回のみ）**:
   ```powershell
   uvx mcp-for-blender setup --yes
   ```
2. **Blenderの起動**:
   Blenderを起動し、`Edit > Preferences > Add-ons` で **MCP for Blender** アドオンが有効になっていることを確認してください。
3. **最終出力ルール**:
   制作されたレンダリング画像（`.png`）、3Dファイル（`.blend`, `.glb` 等）、および制作仕様書は、中間保存先（`02_Creative_Dept/final_outputs/`）から `04_Delivery_Dept` を通じて固定フォルダ **`04_Delivery_Dept/outputs/`** に納品されます。
