---
name: moho
description: >-
  Lost Marble Moho Pro 14.5（ローカルMCPサーバー moho および CLIブリッジ .agents/mcp/moho-mcp/cli.js、
  Live Lua 5.4 Bridge、Headless .moho ZIP/JSON エンジン、Headless CLI レンダラ Moho.exe -r）を用いた
  2Dベクターキャラクターアニメーション、ボーンリギング、スイッチレイヤー表情制御、可変線幅手描きタッチ、
  および完全透過（32-bit RGBA PNG連番 / ProRes 4444 .mov / VP9 Alpha .webm / 確認用 .mp4）書き出しを専任で実行し、
  中間成果物を 02_Creative_Dept/moho/ に、最終成果物を 04_Delivery_Dept/outputs/moho/ に格納するスキル。
  ユーザーが /moho を指定した際、または Moho Pro での2Dアニメーション制作・リギング・書き出しを指示した際に使用する。
---

# 🎞️ Moho Pro 14 2Dベクターアニメーション・ボーンリギング専任スキル (`/moho`)

## 1. ディレクトリ規約（案件別サブフォルダ分離）

本スキルは既存の主要5ジャンル（`blender` / `illustrator` / `photoshop` / `davinci` / `writing`）および他拡張ジャンルとフォルダを完全に分離して運用する専任スキルです。

- **試作・検証用 `.moho`・スクリプト・プレビューPNG置き場**:
  - [`02_Creative_Dept/moho/drafts/`](../../../02_Creative_Dept/moho/drafts/)（案件単位で `<案件サブフォルダ>/` を切って分離）
- **制作部門の完成中間成果物置き場（完成版 `.moho`・構築スクリプト・QAボード・仕様書）**:
  - [`02_Creative_Dept/moho/final_outputs/`](../../../02_Creative_Dept/moho/final_outputs/)（`<案件サブフォルダ>/` で分離）
- **最終納品フォルダ（完成版 `.moho`・透過 ProRes 4444 `.mov`・透過 VP9 `.webm`・確認用 `.mp4`・32-bit RGBA PNG連番）**:
  - [`04_Delivery_Dept/outputs/moho/`](../../../04_Delivery_Dept/outputs/moho/)（`<案件サブフォルダ>/` で分離）
  - 納品時は必ず [`04_Delivery_Dept/outputs/INDEX.md`](../../../04_Delivery_Dept/outputs/INDEX.md) の `Moho Pro 14` セクションへ追記する。
  - ※一般プロジェクト（`04_Delivery_Dept/` が存在しない別ワークスペース）では `global-master-rules` §7 に従い `<対象プロジェクト>/outputs/<案件サブフォルダ>/` へ格納する。

---

## 2. 最適モデル選定 ＆ 4層ハイブリッド制御アーキテクチャ

- **推奨モデル（領域A）**: Lua 5.4 コード生成・`.moho` JSON 構造編集・ベクター座標計算・ボーンリギングを含むため **`Gemini 4 Neon (High)`**（難航時は **`XHigh`**）を推奨。単発のステータス確認や軽量レンダリング実行のみ **`Gemini 4 Hydrogen`** で可。
- **ローカルMCPサーバー**: [`server.js`](../../mcp/moho-mcp/server.js)（MCPサーバー名: `moho`・外部 npm 依存ゼロ）
- **即時実行CLIブリッジ**: [`cli.js`](../../mcp/moho-mcp/cli.js)（`node .agents/mcp/moho-mcp/cli.js <subcommand>`）
- **Lua Bridge インストーラ**: [`install-bridge.js`](../../mcp/moho-mcp/install-bridge.js)（`node .agents/mcp/moho-mcp/install-bridge.js --no-mcp` で Moho の `EditableFilesDir/Scripts/` へ自動配備）
- **Moho Pro 14 実行バイナリ**:
  - Windows: `C:\Program Files\Moho 14\Moho.exe`
  - macOS: `/Applications/Moho 14.app/Contents/MacOS/Moho`

### 4層アーキテクチャと提供ツール（全 15 ツール）

| 層 | モード | 主なツール（MCP / CLI 共通） | 用途 |
| :--- | :--- | :--- | :--- |
| **共通** | 環境検出 | `get_moho_status` (`cli.js status --ping`) | インストール状態・`EditableFilesDir`・プロセス・Lua Bridge ハートビート確認 |
| **Layer A** | Live Lua 5.4 Bridge | `execute_moho_lua`, `get_live_document_summary`, `live_manage_layers`, `live_draw_vector`, `live_rig_bones`, `live_animate`, `open_in_moho` | 起動中 Moho GUI でのリアルタイム任意 Lua 実行、レイヤー操作、ベクター作画、ボーンリギング、キーフレーム打刻、保存・単フレーム書き出し |
| **Layer B** | Headless `.moho` Engine | `inspect_moho_file`, `create_moho_file`, `patch_moho_file`, `unpack_moho_file`, `pack_moho_file` | Moho 未起動でも `.moho`（ZIP内 `Project.mohoproj` JSON）の解析・新規作成・一括編集・展開/再パックを高速実行 |
| **Layer C** | Headless CLI Renderer | `render_moho`, `render_preview_frame` | `Moho.exe -r` による全フラグ対応レンダリング（PNG / JPEG / MP4 / QT / SVG 等）および 1 フレーム PNG 視覚監査出力 |

---

## 3. 標準制作ワークフロー（設計 ➔ 構築 ➔ 視覚監査 ➔ 透過3形式書き出し ➔ 独立QA ➔ 納品）

### フェーズ1：環境確認 ＆ アセット解析
1. **稼働確認**:
   - MCP `get_moho_status` または `node .agents/mcp/moho-mcp/cli.js status --ping` で Moho 14 バイナリ・カスタムコンテンツフォルダ・Live Bridge 状態を確認する。
   - Live Bridge 未配備時は `node .agents/mcp/moho-mcp/install-bridge.js --no-mcp` を実行し、Moho 起動中なら `Ctrl+Shift+Alt+L` でスクリプト再読込する。
2. **元データ解析（`.ai` / `.svg` / リファレンス画像がある場合）**:
   - Illustrator `.ai` や SVG からパーツ構造・座標・カラーコード・重なり順を精密抽出し、キャラクターのパーツ別レイヤー構成（胴体・手足・顔・目スイッチ・アンテナ/小物等）を設計する。

### フェーズ2：100%ネイティブベクター ＆ ボーンリグ構築
1. **リグ＆レイヤー構成の標準**:
   - キャラクターは単一画像ではなく **パーツ別ネイティブベクターレイヤー ＋ ボーンリグ（親ボーン階層＋強度・角度制約）＋ スイッチレイヤー（例：目 `Open` / `Half` / `Blink` / `Happy`、口パク）** で構築し、編集可能性（`.moho` 再編集）を最大限確保する。
   - 手描きイラスト・漫画調が求められる場合は、可変線幅（筆圧抑揚・入り抜き）と非ボイル固定ゆらぎを適用し、線がフレームごとに不自然にチラつかないよう制御する。
2. **モーション設計（予備動作・フォロースルー・イージング）**:
   - スクワッシュ＆ストレッチ、腕脚の位相差スイング、アンテナや髪・小物の遅れ揺れ（フォロースルー）、自然なまばたき、終盤の静止余韻（テロップ・フェード用）を明示的に設計してキーフレームを打刻する。

### フェーズ3：代表フレーム視覚監査ループ【必須】
1. **単フレーム PNG プレビュー書き出し**:
   - `render_preview_frame`（`cli.js preview --file <project.moho> --frame <N> --out <preview.png>`）で要所フレーム（開始・アクション頂点・表情切替・お辞儀/手振り・静止終端等）を PNG 書き出しする。
2. **実画像目視監査**:
   - 書き出した PNG を必ず `read_file` で開いて目視確認し、パーツの隙間・重なり破綻・線幅不整合・透過抜け漏れ・フレーム見切れがゼロになるまで修正ループを回す。

### フェーズ4：本番レンダリング ＆ 透過動画3フォーマット生成
1. **32-bit RGBA 透過 PNG 連番マスター出力**:
   - `render_moho`（`cli.js render --file <project.moho> --format PNG --start <S> --end <E> --outfolder <frames_png> --aa true --extrasmooth true --multithread true`）で完全透過 PNG 連番をレンダリングする。
2. **用途別3フォーマット動画エンコード（FFmpeg 連携）**:
   - **① 編集合成用マスター（推奨・アルファ透過）**: Apple ProRes 4444（`prores_ks -profile:v 4 -pix_fmt yuva444p12le`）➔ `*_alpha.mov`（DaVinci Resolve / Premiere / After Effects へそのまま載せて背景透過合成可能）
   - **② Web・OBS 配信透過用**: VP9 Alpha（`libvpx-vp9 -pix_fmt yuva420p -auto-alt-ref 0`）➔ `*_alpha.webm`
   - **③ 汎用プレイヤー確認用（白背景合成）**: H.264 MP4（白背景上へ透過連番をオーバーレイ、`yuv420p`）➔ `*.mp4`（H.264 はアルファ非対応のため、黒主線と発色が見やすい白背景版を必ず同梱する）
3. **透過チェッカーボード検証**:
   - 生成した `_alpha.mov` および `_alpha.webm` から抽出したフレームをチェッカーボード背景へ合成し、`read_file` で実際にアルファ透過が有効であること（黒フチ・白フチ・背景不透過がないこと）を確認する。

### フェーズ5：独立検証（`qa-verifier`）＆ 最終納品
1. `global-master-rules` §6 に従い、編集権限を持たない `qa-verifier` サブエージェントへ要件・成果物パス・監査画像を渡して `PASS` 判定を得る。
2. `04_Delivery_Dept/outputs/moho/<案件サブフォルダ>/` へ完成 `.moho`・動画3形式・PNG連番・納品仕様書を格納し、[`04_Delivery_Dept/outputs/INDEX.md`](../../../04_Delivery_Dept/outputs/INDEX.md) の `Moho Pro 14` セクションを更新してユーザーへ報告する。
