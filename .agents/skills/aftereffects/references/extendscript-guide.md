---
name: adobe-aftereffects
description: >
  Adobe After Effects 2027 をローカルMCPサーバー（aftereffects）およびCLIブリッジ
  （node .agents/mcp/aftereffects-mcp/cli.js）経由で自動制御し、コンポジション構築、
  テキスト／シェイプ／AVレイヤーアニメーション、フレームPNG書き出し（視覚監査）、
  .aep 保存、および Render Queue による映像レンダリングを実行するスキル。
  作業ディレクトリは 02_Creative_Dept/aftereffects/{drafts,final_outputs}/、
  最終納品先は 04_Delivery_Dept/outputs/aftereffects/。After Effects でのモーション制作時に使用する。
---

# Adobe After Effects 自動制御スキル (`adobe-aftereffects` / `/aftereffects`)

## 1. 概要とディレクトリ規約
本スキルは、**Adobe After Effects 2027**（CEP Bridge `antigravity-ae-mcp-bridge` 優先、非アクティブ時は Windows `AfterFX.exe -r` / macOS `osascript` フォールバック）を以下の2経路で制御します：
1. **MCPサーバー `aftereffects`**（[`.agents/mcp/aftereffects-mcp/server.js`](../../mcp/aftereffects-mcp/server.js)）:
   - `call_mcp_tool` から `aftereffects` サーバーの5つのネイティブツールを呼び出す。
2. **即時実行CLIブリッジ**（[`.agents/mcp/aftereffects-mcp/cli.js`](../../mcp/aftereffects-mcp/cli.js)）:
   - MCP未接続時やバッチ処理時に、`run_command` から `node .agents/mcp/aftereffects-mcp/cli.js <subcommand>` を呼び出して同じ5つのツール機能を実行する。

### 実行方式の特徴（CEP Bridge ＆ 自動起動フォールバック）
- **CEP Bridge 稼働中**（`os.tmpdir()/antigravity-ae-mcp-bridge/heartbeat.json` が 8000ms 以内に更新されている場合）はファイルキュー経由で高速に JSX を実行します（After Effects 側の「スクリプトによるファイルへの書き込み」設定不要）。
- **未起動または CEP Bridge 非アクティブ時**でも、Windows では `AfterFX.exe -r <jsx>` が自動起動して実行します（ただしファイル出力等を伴う場合、フォールバック経路では After Effects 環境設定の「スクリプトによるファイルへの書き込みとネットワークへのアクセスを許可」が必要になる点に注意してください）。

### 格納ディレクトリ規約
- **試作・JSXスクリプト置き場**: `02_Creative_Dept/aftereffects/drafts/`
- **制作部門の完成中間成果物置き場**: `02_Creative_Dept/aftereffects/final_outputs/`
- **最終納品フォルダ**: `04_Delivery_Dept/outputs/aftereffects/`

---

## 2. MCPサーバー `aftereffects` の提供ツール（全5種）

| ツール名 | 用途 | 主な引数 |
| :--- | :--- | :--- |
| `get_aftereffects_status` | After Effects インストール状況・プロセス稼働有無・アクティブプロジェクト・全コンポジション一覧を取得 | なし |
| `execute_aftereffects_jsx` | ExtendScript（JSX）文字列または `.jsx` ファイルをUTF-8保護（BOM除去）・ダイアログ抑制（`app.beginSuppressDialogs()`）＆`try/catch` ラッパー付きで実行し、戻り値とエラー行番号を取得 | `script` (string) または `script_path` (string), `wrap_try_catch` (boolean, default: `true`), `timeout_ms` (number, default: `60000`) |
| `get_project_summary` | アクティブプロジェクト（または `file_path` 指定の `.aep` を開いた状態）のプロジェクトアイテム・全コンポジション・各レイヤー詳細（種別・テキスト内容・時間）を取得 | `file_path` (optional string) |
| `export_comp_frame_png` | 指定コンポジション（省略時はアクティブまたは先頭コンポ）の指定秒フレームを `comp.saveFrameToPng` で PNG 書き出しする（視覚監査用） | `output_path` (required string), `comp_name` (optional string), `time_seconds` (optional number) |
| `save_aftereffects_project` | `.aep` プロジェクトの保存および／または `proj.renderQueue` によるコンポジションのレンダリング書き出しを実行（`timeout_ms: 180000`） | `output_path` (optional string), `render_comp_name` (optional string), `render_output_path` (optional string) |

---

## 3. CLIブリッジ（`cli.js`）コマンドリファレンス

```powershell
# 1. After Effects のインストール・起動状態・コンポジション一覧を確認
node .agents/mcp/aftereffects-mcp/cli.js status

# 2. アクティブプロジェクト（または指定 .aep）の構造サマリーを取得
node .agents/mcp/aftereffects-mcp/cli.js summary
node .agents/mcp/aftereffects-mcp/cli.js summary --file "02_Creative_Dept/aftereffects/final_outputs/motion.aep"

# 3. ExtendScript (JSX) のインライン実行または .jsx ファイル実行
node .agents/mcp/aftereffects-mcp/cli.js exec --code "return app.version;"
node .agents/mcp/aftereffects-mcp/cli.js exec --file "02_Creative_Dept/aftereffects/drafts/build_motion.jsx"

# 4. 視覚監査（read_file）用のコンポジションフレームPNG書き出し
node .agents/mcp/aftereffects-mcp/cli.js export-png --out "02_Creative_Dept/aftereffects/drafts/frame_audit.png" --comp "MainComp" --time 2.5

# 5. プロジェクト保存（.aep）およびレンダーキュー書き出し
node .agents/mcp/aftereffects-mcp/cli.js save --out "02_Creative_Dept/aftereffects/final_outputs/motion.aep"
node .agents/mcp/aftereffects-mcp/cli.js save --out "02_Creative_Dept/aftereffects/final_outputs/motion.aep" --render-comp "MainComp" --render-out "02_Creative_Dept/aftereffects/final_outputs/motion.mov"
```

---

## 4. After Effects ExtendScript (JSX) 実装の重要ポイント

### ① 1始まりインデックス（1-based indexing）
- After Effects DOM のコレクション（`proj.item(i)`, `comp.layer(l)`, `rqItem.outputModule(1)`）は JavaScript 配列と異なり **1 始まり**です（`1 <= i <= proj.numItems`）。

### ② ES3 互換と Undo グループ
- `execute_aftereffects_jsx`（`wrap_try_catch: true`）ではスクリプト全体が匿名関数でラップされるため、結果を返す際は `return JSON.stringify({...});` を使用します（サーバー側で ES3 用 `JSON.stringify` ポリフィルと `app.beginSuppressDialogs()` が付与されます）。
- 複数操作を行うスクリプトでは `app.beginUndoGroup("...");` と `app.endUndoGroup();` で括ると安全です。

### ③ 視覚監査ループ（`export-png` ＋ `read_file`）
- コンポジションやモーションを組み立てた後は、複数タイムスタンプ（開始・中間・終盤など）を `export_comp_frame_png` / `export-png` で PNG 書き出しし、`read_file` で視覚確認してから最終レンダリングに進みます。
