---
name: moho
description: >-
  Moho Pro 14（MCP moho / CLI / Live Lua 5.4 Bridge / Headless Engine）による2Dベクターキャラアニメ・ボーンリギング・透過動画書き出しスキル。
  /moho 指定時、または Moho 2Dアニメ制作依頼時に使用。
---

# 🎞️ Moho Pro 14 2Dベクターアニメーション専任スキル (`/moho`)

## 1. ディレクトリ規約 ＆ 推奨モデル
- **試作**: `02_Creative_Dept/moho/drafts/<案件サブフォルダ>/`
- **中間成果物**: `02_Creative_Dept/moho/final_outputs/<案件サブフォルダ>/`
- **最終納品先**: `04_Delivery_Dept/outputs/moho/<案件サブフォルダ>/`（[`INDEX.md`](../../../04_Delivery_Dept/outputs/INDEX.md) の `Moho Pro 14` 更新。一般プロジェクトは `global-master-rules` §6 に従い `<プロジェクト>/outputs/`）
- **推奨モデル（領域A）**: Lua 5.4・`.moho` JSON・座標/ボーン計算を伴うため **`Gemini 4 Neon (High)`**（難航時は **`XHigh`**）。単発ステータス確認・軽量書き出しのみ `Hydrogen` 可。

## 2. 4層ハイブリッド制御（全15ツール・外部依存ゼロ）
- **MCP**: [`.agents/mcp/moho-mcp/server.js`](../../mcp/moho-mcp/server.js)（`moho`） / **CLI**: `node .agents/mcp/moho-mcp/cli.js <subcmd>`
- **Bridge 配備**: `node .agents/mcp/moho-mcp/install-bridge.js --no-mcp`（Moho起動中なら `Ctrl+Shift+Alt+L` で再読込）
- **ツール群**:
  - **共通**: `get_moho_status` (`cli.js status --ping`)
  - **Layer A (Live Lua 5.4)**: `execute_moho_lua`, `get_live_document_summary`, `live_manage_layers`, `live_draw_vector`, `live_rig_bones`, `live_animate`, `open_in_moho`
  - **Layer B (Headless `.moho` ZIP/JSON)**: `inspect_moho_file`, `create_moho_file`, `patch_moho_file`, `unpack_moho_file`, `pack_moho_file`
  - **Layer C (Headless CLI `Moho.exe -r`)**: `render_moho`, `render_preview_frame`

## 3. 標準制作フロー
1. **環境確認 ＆ アセット解析**: `cli.js status --ping` で稼働確認。`.ai`/`.svg` 原画がある場合はパーツ構造・座標・色を精密抽出し、パーツ別レイヤーを設計。
2. **100%ネイティブベクター ＆ ボーンリグ構築**:
   - 単一画像ではなく **パーツ別ベクターレイヤー ＋ ボーン階層（強度・角度制約）＋ スイッチレイヤー（目 `Open/Half/Blink/Happy`・口パク）** で再編集可能に構築。
   - 手描き調は可変線幅（筆圧抑揚）＋非ボイル固定ゆらぎでチラつき防止。予備動作・スクワッシュ＆ストレッチ・フォロースルー・静止余韻を組み込む。
3. **視覚監査ループ【必須】**: `render_preview_frame`（`cli.js preview --file <.moho> --frame <N> --out <png>`）で要所フレームを出力し、`read_file` で隙間・重なり・線幅・見切れゼロまで修正。
4. **本番透過レンダリング ＆ 3フォーマット動画化**:
   - `render_moho`（`--format PNG --aa true --extrasmooth true --multithread true`）で 32-bit RGBA 透過PNG連番を出力。
   - FFmpeg で用途別3形式を生成：
     1. **編集用透過マスター**: ProRes 4444（`prores_ks -profile:v 4 -pix_fmt yuva444p12le`）➔ `*_alpha.mov`
     2. **Web/OBS透過用**: VP9 Alpha（`libvpx-vp9 -pix_fmt yuva420p -auto-alt-ref 0`）➔ `*_alpha.webm`
     3. **汎用確認用（白背景）**: H.264 MP4（白背景合成・`yuv420p`）➔ `*.mp4`
   - `_alpha.mov` / `_alpha.webm` から抽出したフレームをチェッカーボード背景へ合成し、`read_file` でアルファ透過（フチ汚れなし）を実証。
5. **独立QA ＆ 納品**: `qa-verifier`（`global-master-rules` §5）合格後、`.moho`・動画3形式・PNG連番・仕様書を `04_Delivery_Dept/outputs/moho/<案件サブフォルダ>/` へ格納・`INDEX.md` 更新。
