---
name: adobe-premiere
description: >
  Adobe Premiere Pro 2027 をローカルMCPサーバー（premiere）およびCLIブリッジ
  （node .agents/mcp/premiere-mcp/cli.js）経由で自動制御し、タイムライン・シーケンス編集、
  クリップ操作、フレームPNG書き出し（視覚監査）、.prproj 保存、および exportAsMediaDirect による
  映像書き出しを実行するスキル。作業ディレクトリは 02_Creative_Dept/premiere/{drafts,final_outputs}/、
  最終納品先は 04_Delivery_Dept/outputs/premiere/。Premiere Pro での映像編集・プロジェクト操作時に使用する。
---

# Adobe Premiere Pro 自動制御スキル (`adobe-premiere` / `/premiere`)

## 1. 概要とディレクトリ規約
本スキルは、**Adobe Premiere Pro 2027**（CEP Bridge 拡張 `com.antigravity.premiere.mcp.panel` 経由）を以下の2経路で制御します：
1. **MCPサーバー `premiere`**（[`.agents/mcp/premiere-mcp/server.js`](../../mcp/premiere-mcp/server.js)）:
   - `call_mcp_tool` から `premiere` サーバーの5つのネイティブツールを呼び出す。
2. **即時実行CLIブリッジ**（[`.agents/mcp/premiere-mcp/cli.js`](../../mcp/premiere-mcp/cli.js)）:
   - MCP未接続時やバッチ処理時に、`run_command` から `node .agents/mcp/premiere-mcp/cli.js <subcommand>` を呼び出して同じ5つのツール機能を実行する。

### 前提条件（CEP Bridge の起動）
- `premiere-mcp` は `os.tmpdir()/antigravity-premiere-mcp-bridge` のファイルキューと `heartbeat.json`（有効判定 `8000ms` 以内）を介して Premiere Pro 内の CEP パネルと通信します。
- JSX 実行系ツールを使う際は、**Adobe Premiere Pro を起動し、`ウィンドウ > エクステンション > Antigravity MCP Bridge` パネルが開いてアクティブであること**が必要です（`status` コマンドで `cepBridge.active: true` を確認）。

### 格納ディレクトリ規約
- **試作・JSXスクリプト置き場**: `02_Creative_Dept/premiere/drafts/`
- **制作部門の完成中間成果物置き場**: `02_Creative_Dept/premiere/final_outputs/`
- **最終納品フォルダ**: `04_Delivery_Dept/outputs/premiere/`

---

## 2. MCPサーバー `premiere` の提供ツール（全5種）

| ツール名 | 用途 | 主な引数 |
| :--- | :--- | :--- |
| `get_premiere_status` | Premiere Pro インストール状況・プロセス稼働有無・CEP Bridge ハートビート状態・アクティブプロジェクト/シーケンス情報を取得 | なし |
| `execute_premiere_jsx` | ExtendScript（JSX）文字列または `.jsx` ファイルをUTF-8保護（BOM除去）＆`try/catch` ラッパー付きで実行し、戻り値（JSON/文字列）とエラー行番号を取得 | `script` (string) または `script_path` (string), `wrap_try_catch` (boolean, default: `true`), `timeout_ms` (number, default: `30000`) |
| `get_project_summary` | アクティブプロジェクトのルートアイテム一覧、全シーケンス、ビデオトラック／クリップ（開始・終了・尺秒）、オーディオトラック数を取得 | なし |
| `export_frame_png` | アクティブシーケンスの指定秒（省略時は現在の再生ヘッド位置）の1フレームを `seq.exportFramePNG` で PNG 書き出しする（視覚監査用） | `output_path` (required string), `time_seconds` (optional number) |
| `save_or_export_premiere` | アクティブプロジェクトの保存（`.prproj`）および／または `seq.exportAsMediaDirect` によるメディア書き出しを実行（`timeout_ms: 180000`） | `save_project` (boolean, default: `false`), `save_as_path` (string), `export_media_path` (string), `export_preset_path` (string: `.epr` 必須), `work_area_type` (number, default: `0`) |

---

## 3. CLIブリッジ（`cli.js`）コマンドリファレンス

```powershell
# 1. Premiere Pro のインストール・起動状態・CEP Bridge 接続状態を確認
node .agents/mcp/premiere-mcp/cli.js status

# 2. アクティブプロジェクト・シーケンス・トラック・クリップ一覧を取得
node .agents/mcp/premiere-mcp/cli.js summary

# 3. ExtendScript (JSX) のインライン実行または .jsx ファイル実行
node .agents/mcp/premiere-mcp/cli.js exec --code "return app.version;"
node .agents/mcp/premiere-mcp/cli.js exec --file "02_Creative_Dept/premiere/drafts/edit_timeline.jsx"

# 4. 視覚監査（read_file）用のフレームPNG書き出し
node .agents/mcp/premiere-mcp/cli.js export-png --out "02_Creative_Dept/premiere/final_outputs/frame_audit.png" --time 5.0

# 5. プロジェクト保存（.prproj）およびメディア書き出し（.epr プリセット必須）
node .agents/mcp/premiere-mcp/cli.js save --save-as "02_Creative_Dept/premiere/final_outputs/project.prproj"
node .agents/mcp/premiere-mcp/cli.js save --export-out "02_Creative_Dept/premiere/final_outputs/output.mp4" --preset "C:\path\to\preset.epr"
```

---

## 4. Premiere Pro ExtendScript (JSX) 実装の重要ポイント

### ① ES3 互換と戻り値の返却方法
- `execute_premiere_jsx`（`wrap_try_catch: true`）ではスクリプト全体が匿名関数でラップされるため、結果を返す際は必ず `return JSON.stringify({...});` の形式で返却します（サーバー側で ES3 用 `JSON.stringify` ポリフィルが付与されます）。
- 日本語ファイルパスはサーバー側で `toAsciiJsString`（`\uXXXX` エスケープ）または UTF-8 保護して渡されます。

### ② プロジェクト・シーケンス・時間（`Time`）の扱い
```javascript
var proj = app.project;
if (!proj || !proj.activeSequence) {
  throw new Error("No active sequence in Premiere Pro.");
}
var seq = proj.activeSequence;

// 再生ヘッド移動・Time生成（秒指定）
var t = new Time();
t.seconds = 12.5;
seq.setPlayerPosition(t.ticks);
```
- `seq.end` などの内部 tick 値は `1秒 = 254016000000 ticks` として秒換算できます。

### ③ `exportAsMediaDirect` 書き出し時のプリセット必須ルール
- `save_or_export_premiere` / `cli.js save --export-out` を使用して映像をレンダリング書き出しする場合、Premiere Pro API の仕様上 **`export_preset_path`（`.epr` プリセットファイルの絶対パス）が必須**です。
- 長尺動画のレンダリングは 180 秒（`timeout_ms: 180000`）を超える場合があるため、必要に応じて Adobe Media Encoder キュー投入や、専用 JSX での `timeout_ms` 延長を検討してください。

### ④ 視覚監査ループ（`export-png` ＋ `read_file`）
- テロップ・色味・レイアウト・カット位置を編集した後は、必ず代表フレームを `export_frame_png` / `export-png` で PNG 書き出しし、`read_file` で画像を目視確認してから最終書き出しに進みます。
