---
name: creative-dept
description: >-
  制作・編集部門（02_Creative_Dept）を稼働させ、01_Research_Dept/reports/ の調査レポートや制作指示をもとに
  テキスト原稿の執筆・セルフ校正、Blender MCP（MCP: blender）を用いた3Dモデリング・レンダリング、
  または Adobe Illustrator MCP（MCP: illustrator / CLI: .agents/mcp/illustrator-mcp/cli.js）を用いた
  ベクターロゴ・CMYK印刷入稿データ（.ai / .pdf / .svg / .eps）制作を実行して完成成果物（final_outputs/）を出力した後、
  04_Delivery_Dept を通じて固定出力フォルダ 04_Delivery_Dept/outputs/ に最終成果物を納品するスキル。
  記事執筆、Blender 3D制作、Illustratorベクター・DTP制作、/creative-dept コマンド実行時に使用する。
---

# 制作・編集・Blender 3D・Illustrator DTP部門（`02_Creative_Dept`）実行スキル

1. [`02_Creative_Dept/AGENTS.md`](../../../02_Creative_Dept/AGENTS.md) および [`.agents/rules/global-policy.md`](../../rules/global-policy.md) を読み込む。
2. 対象となる `01_Research_Dept/reports/report_[テーマ名].md`（またはユーザーからの直接の制作・3Dモデリング・ベクターDTP要件）を確認する。
3. `define_subagent`（**`EnableWriteTools: true`, `EnableMCPTools: true`, `EnableSubagentTools: false`**）および `invoke_subagent` で `creative-dept` サブエージェントを起動し、以下を実行させる：
   - **テキスト制作時**: 初稿 `02_Creative_Dept/drafts/draft_[テーマ名].md` の作成・セルフ校正、および完成原稿 `02_Creative_Dept/final_outputs/content_[テーマ名].md` の保存
   - **Blender 3D制作時**:
     - MCPサーバー `blender`（`get_addon_status`, `get_scene_info`, `execute_blender_code`, `look`, `search_assets`, `import_asset`, `generate_3d`）を用いた3Dシーン構築・視覚監査・レンダリング出力を実行する。
     - **Headless CLIフォールバック**: Blender MCPサーバーが未起動・タイムアウトの場合は、ローカルの `"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" --background --python <script.py>` によるヘッドレス `bpy` / `bmesh` 実行＋生成PNGの `view_file`（`read_file`）視覚監査ループに自動切り替えし、複数面図（5面図等）からの輪郭LUT抽出・コンフォーマル曲面投影モデリング・リギング・マルチアングルレンダリングを完遂させる。
     - 完成した `.blend` / `.glb` / `.png` および制作仕様書 `02_Creative_Dept/final_outputs/content_[テーマ名].md` を保存する。
   - **Adobe Illustrator ベクター・DTP・ロゴ制作時**:
     - 専用スキル [`.agents/skills/adobe-illustrator/SKILL.md`](../adobe-illustrator/SKILL.md) に従い、MCPサーバー `illustrator`（または `node .agents/mcp/illustrator-mcp/cli.js`）で **Adobe Illustrator 2027** を制御する。
     - CMYKカラー管理（`new CMYKColor()`）、ベジェパス生成、テキスト生成とアウトライン化（`createOutline()`）を行い、`export_artboard_png`（`cli.js export-png`）で書き出した高解像度PNGを `read_file` で目視監査した上で、完成した `.ai` / `.pdf` / `.svg` / `.png` および制作仕様書 `02_Creative_Dept/final_outputs/content_[テーマ名].md` を保存する。
4. **固定出力ルールの適用**: 単体実行時であっても、続けて `delivery-dept` サブエージェントを起動し、ユーザーが指定した形式（Markdown、HTML、レンダリング画像、3Dモデルファイル、Illustrator `.ai` / `.pdf` / `.svg` 等）で固定フォルダ `04_Delivery_Dept/outputs/` に最終成果物を格納・`INDEX.md` を更新する。
