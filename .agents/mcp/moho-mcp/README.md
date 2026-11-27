# Moho Pro 14.5.1 完全制御環境 (`moho-control`)

Lost Marble **Moho Pro 14.5.1** を **MCP サーバー** および **直接 CLI** の両方から完全制御するための、外部依存ゼロ（Node.js 組み込みモジュール＋純 Lua 5.4）ハイブリッド制御スイートです。

## 4層ハイブリッド構成

1. **Layer A — Live Lua 5.4 Bridge (`Moho Pro/Scripts/`)**
   - 起動中の Moho Pro 14.5.1 内で任意 Lua 5.4 コード実行、レイヤー構築、ベクター作画、ボーンリギング、キーフレームアニメーション、ドキュメント保存／単フレーム書き出しをリアルタイム実行。
   - アトミックファイル IPC（`%TEMP%\agy-moho-bridge\`）＋ フォーカスを奪わない Win32 再描画ナッジにより、アイドル状態でも自動応答。
2. **Layer B — Headless `.moho` Archive & `Project.mohoproj` JSON Engine (`lib/moho-file.js`, `lib/zip.js`)**
   - Moho 未起動でも `.moho`（ZIP内 JSON）の解析・新規作成・一括パッチ・Unpack/Pack（Git 管理対応）を高速実行。
3. **Layer C — Headless CLI Renderer (`lib/cli-render.js`)**
   - `Moho.exe -r` による全フラグ対応のヘッドレス書き出し（PNG / JPEG / MP4 / QT / SVG 等）および 1 フレーム PNG プレビュー生成。
4. **Layer D — MCP Server (`server.js`) & Direct CLI (`cli.js`)**
   - Antigravity の `mcp_config.json` に `"moho"` として登録済み。ターミナルやスクリプトからは `node .agents/mcp/moho-mcp/cli.js` で即座に利用可能。

---

## セットアップ（初回・再同期）

```powershell
node .agents/mcp/moho-mcp/install-bridge.js
```

以下を自動実行します：
- `Moho Pro/Scripts/Utility/agy_json.lua` の配備
- `Moho Pro/Scripts/Tool/agy_moho_bridge.lua` ＋ アイコン `agy_moho_bridge.png` の配備
- `Moho Pro/Scripts/Menu/Antigravity/agy_moho_bridge_panel.lua` の配備
- Antigravity の `mcp_config.json` への `"moho"` MCP サーバー登録

> **Live Lua Bridge を反映させるには**: 配備後に Moho Pro 14.5.1 を起動（または起動中の場合は `Ctrl+Shift+Alt+L` でスクリプト再読込／再起動）してください。`Scripts > Antigravity > Moho Control Bridge...` から状態パネルも開けます。

---

## CLI クイックリファレンス

```powershell
# 1. 環境・稼働状態の確認（--ping でライブLua接続テスト）
node .agents/mcp/moho-mcp/cli.js status --ping

# 2. .moho ファイルのヘッドレス解析
node .agents/mcp/moho-mcp/cli.js inspect --file "Moho Pro/Tutorials/1 - Basics/Tutorial 1.01.moho"

# 3. 新規 .moho プロジェクトのヘッドレス生成
node .agents/mcp/moho-mcp/cli.js create --out "outputs/my_scene.moho" --width 1920 --height 1080 --fps 24 --end 120 --layers "BG,Character,FX"

# 4. .moho プロジェクトのヘッドレス編集
node .agents/mcp/moho-mcp/cli.js patch --file "outputs/my_scene.moho" --fps 30 --set-paths '{"project_data.end_frame":180}'

# 5. .moho の展開（Git管理・詳細編集用）と再パック
node .agents/mcp/moho-mcp/cli.js unpack --file "outputs/my_scene.moho" --out "outputs/my_scene_src"
node .agents/mcp/moho-mcp/cli.js pack --dir "outputs/my_scene_src" --out "outputs/my_scene_rebuilt.moho"

# 6. ヘッドレス単フレーム PNG プレビュー書き出し
node .agents/mcp/moho-mcp/cli.js preview --file "outputs/my_scene.moho" --frame 1 --out "outputs/frame1.png"

# 7. ヘッドレス本番レンダリング（PNG連番 / MP4 / QT 等）
node .agents/mcp/moho-mcp/cli.js render --file "outputs/my_scene.moho" --format PNG --start 1 --end 24 --outfolder "outputs/frames"

# 8. 起動中 Moho で任意の Lua 5.4 コードを実行
node .agents/mcp/moho-mcp/cli.js lua --code "return { doc = moho.document:Name(), layers = moho.document:CountLayers() }"

# 9. 起動中 Moho の高レベル操作（MCP ツール名をそのまま実行可能）
node .agents/mcp/moho-mcp/cli.js live-summary
node .agents/mcp/moho-mcp/cli.js call live_draw_vector --json '{"layer_name":"StarLayer","shape_type":"star","spikes":5,"radius":0.5,"fill_color":{"r":255,"g":210,"b":40,"a":255}}'
node .agents/mcp/moho-mcp/cli.js call live_rig_bones --json '{"bone_layer":"HeroRig","bones":[{"name":"Root","x":0,"y":-0.4,"angle_deg":90,"length":0.35},{"name":"Upper","x":0,"y":-0.05,"angle_deg":90,"length":0.35,"parent":"Root"}]}'
node .agents/mcp/moho-mcp/cli.js call live_animate --json '{"operation":"keyframe","keyframes":[{"frame":1,"layer_name":"HeroRig","bone_name":"Upper","bone_angle_deg":70},{"frame":24,"layer_name":"HeroRig","bone_name":"Upper","bone_angle_deg":110,"interpolation":"ease_in_out"}]}'
```

## 提供 MCP ツール一覧（全 15 ツール）

| ツール名 | モード | 用途 |
| :--- | :--- | :--- |
| `get_moho_status` | 共通 | インストール環境・カスタムフォルダ・プロセス・Bridge 稼働状態確認 |
| `inspect_moho_file` | Headless | `.moho` の解像度・FPS・全レイヤー階層・ボーン・メッシュ解析 |
| `create_moho_file` | Headless | Moho 14.5.1 準拠の新規 `.moho` プロジェクト生成 |
| `patch_moho_file` | Headless | プロジェクト設定・レイヤー・任意 JSON パスの一括更新 |
| `unpack_moho_file` | Headless | `.moho` → 整形済み `Project.mohoproj` フォルダ展開 |
| `pack_moho_file` | Headless | フォルダ → `.moho` アーカイブ再構築 |
| `render_moho` | CLI Render | `Moho.exe -r` による連番画像／動画レンダリング |
| `render_preview_frame` | CLI Render | 指定 1 フレームの PNG プレビュー書き出し |
| `open_in_moho` | GUI Control | Moho 起動・ファイル展開・スクリプト再読込・再描画ナッジ |
| `execute_moho_lua` | Live Lua | 起動中 Moho 内での任意 Lua 5.4 コード実行（完全制御の核） |
| `get_live_document_summary` | Live Lua | 起動中 Moho のアクティブドキュメント構造取得 |
| `live_manage_layers` | Live Lua | レイヤー作成・選択・リネーム・削除・複製・グループ化・変形 |
| `live_draw_vector` | Live Lua | ベクター図形（矩形・楕円・多角形・星・カスタムパス）作画＋着色 |
| `live_rig_bones` | Live Lua | ボーン階層生成・角度制約・子レイヤーのボーンバインド |
| `live_animate` | Live Lua | レイヤー／ボーン／カメラ／スイッチのキーフレーム打刻・保存・書き出し |

## 自動 E2E テスト

```powershell
node .agents/mcp/moho-mcp/scripts/test-e2e.js
```
