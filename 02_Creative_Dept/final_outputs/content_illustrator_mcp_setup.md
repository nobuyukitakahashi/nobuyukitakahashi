# Adobe Illustrator 2027 自動制御用ローカルMCPサーバー（`illustrator`）＆専用スキル（`adobe-illustrator`）構築・実機検証仕様書

## 1. 概要
本仕様書は、`02_Creative_Dept`（制作・編集・3D・ベクターDTP部門）において **Adobe Illustrator 2027 (Version 31.0.0)** を自動制御し、コーポレートロゴ、DTP・印刷入稿用CMYKデータ（`.ai` / `.pdf` / `.svg` / `.eps`）、テキストのアウトライン化（`createOutline()`）、および視覚監査用高解像度PNG書き出しを一気通貫で実行するためのローカルMCPサーバー＆CLIブリッジの実装・検証記録です。

---

## 2. システムアーキテクチャと実装ファイル

### 2.1 ローカルMCPサーバー（`.agents/mcp/illustrator-mcp/server.js`）
- **外部パッケージ依存ゼロ**: Node.js 標準モジュール（`fs`, `path`, `os`, `child_process`）のみで動作。
- **デュアルフレーミング対応 stdio JSON-RPC 2.0**:
  - `Content-Length` ヘッダ方式および Newline-delimited JSON（改行区切りJSON）の両方を自動判別して双方向応答。
  - 対応メソッド：`initialize`, `notifications/initialized`, `ping`, `tools/list`, `tools/call`。
- **UTF-8完全保護とExtendScript `JSON` ポリフィル**:
  - ExtendScript（ES3準拠エンジン）に存在しない `JSON.stringify` をラッパー内で自動ポリフィル。
  - 一時 `.jsx` ファイルを UTF-8 BOM（`\uFEFF`）付きでASCII一時ディレクトリ（`os.tmpdir()`）に生成し、日本語パス（`マイドライブ` 等）もすべて `\uXXXX` エスケープおよび一時ファイル経由コピーで処理することで、文字化け・パスエンコーディングエラーを100%防止。
- **Windows COM (`Illustrator.Application`) 参照保持機構（`ensureWindowsComKeeper`）**:
  - 短命プロセスから COM 経由（`-Embedding`）で Illustrator を起動した際、プロセス終了時に COM クラスファクトリが解除される問題を防ぐため、WMI（`Win32_Process.Create`）経由のバックグラウンド参照保持プロセスを自動維持し、2回目以降の CLI / MCP 呼び出しに約 `245 ms` で高速アタッチ。

### 2.2 提供ツール一覧（5種）
1. **`get_illustrator_status`**:
   - Illustrator実行ファイル（`C:\Program Files\Adobe\Adobe Illustrator 2027\Support Files\Contents\Windows\Illustrator.exe`, `v31.0.0`）、COM ProgID（`Illustrator.Application`, CLSID `{8F60463D-0543-413C-80EA-69133B2F206D}`）、プロセス起動状態、および開いているドキュメント一覧（名前・CMYK/RGB・アートボード数・寸法）を返す。
2. **`execute_illustrator_jsx`**:
   - `script`（ExtendScript文字列）または `script_path`（`.jsx` ファイルパス）を `try/catch` ラッパー付きで実行し、戻り値またはエラー行番号・メッセージをJSON形式で返す。
3. **`get_document_summary`**:
   - アクティブドキュメント（または `file_path` で指定した `.ai`/`.svg`/`.pdf`/`.eps`）のアートボード座標、レイヤー一覧、テキストフレーム一覧（フォント・サイズ・座標）、パス数、スウォッチ一覧（CMYK/RGB値）を返す。
4. **`export_artboard_png`**:
   - 指定アートボードを `ExportType.PNG24`（デフォルト `scale: 200`＝200%高解像度）でPNG書き出しし、出力ファイルパス・ファイルサイズ・画像ピクセル寸法（`width`, `height`）を返す。
5. **`save_illustrator_document`**:
   - `.ai`（PDF互換・ICCプロファイル埋込）、`.pdf`、`.svg`、`.eps` 形式で保存・書き出しを行う。`outline_text: true` 指定時は保存前に全テキストフレームを `createOutline()` でベクターパス化し、`cmyk_convert: true` 指定時はドキュメントをCMYKカラースペースへ変換する。

### 2.3 即時実行CLIブリッジ（`.agents/mcp/illustrator-mcp/cli.js`）
```powershell
node .agents/mcp/illustrator-mcp/cli.js status
node .agents/mcp/illustrator-mcp/cli.js summary [--file <path>]
node .agents/mcp/illustrator-mcp/cli.js exec --code "<jsx>" | --file <script.jsx>
node .agents/mcp/illustrator-mcp/cli.js export-png --out <png_path> [--artboard 0] [--scale 200] [--transparent true]
node .agents/mcp/illustrator-mcp/cli.js save --out <ai_or_pdf_or_svg_path> [--outline-text true] [--cmyk true]
```

---

## 3. 実機動作検証（Ground Truth）結果

### 3.1 MCP JSON-RPC 2.0 プロトコル応答検証
`server.js` の標準入力に `initialize` ➔ `notifications/initialized` ➔ `tools/list` ➔ `tools/call` (`get_illustrator_status`) を流し込み、以下を確認：
- `serverInfo: { name: "illustrator", version: "1.0.0" }`
- 全5ツールの JSON Schema 定義が正常に返却されること。
- `get_illustrator_status` が `Adobe Illustrator 2027 (31.0.0)` および COM CLSID `{8F60463D-0543-413C-80EA-69133B2F206D}` を正確に検出すること。

### 3.2 Adobe Illustrator 2027 実機制御・CMYKベクター生成・視覚監査
検証スクリプト [`02_Creative_Dept/drafts/test_illustrator_mcp_build.jsx`](../drafts/test_illustrator_mcp_build.jsx) を実行し、以下の通り検証完了：
- **ドキュメント設定**: `CVN_Illustrator_MCP_Verify`（`DocumentColorSpace.CMYK`, `800 × 500 pt`, 3レイヤー構成：`Background_Layer`, `Vector_Badge_Layer`, `Typography_Layer`）
- **登録スウォッチ**:
  - `CVN_Brand_Green_C90M0Y70K0`: `CMYK(90, 0, 70, 0)`
  - `CVN_Dark_Charcoal`: `CMYK(85, 65, 55, 70)`
- **生成ファイル**:
  1. 視覚監査用高解像度PNG（200%スケール、`1600 × 1000 px`）: [`02_Creative_Dept/final_outputs/test_illustrator_mcp_verify.png`](test_illustrator_mcp_verify.png)
  2. 全テキストアウトライン化済みCMYK Illustratorマスター（`.ai`、`1.30 MB`、`remainingTextFrames: 0`）: [`02_Creative_Dept/final_outputs/test_illustrator_mcp_verify.ai`](test_illustrator_mcp_verify.ai)
- **`read_file` 視覚監査結果**:
  - 1回目の書き出し画像を `read_file` で目視確認し、下段CMYKチップのテキスト位置およびサブタイトル右端マージンを検出して `.jsx` の座標・フォントサイズを微調整し、再書き出しにより4つのCMYKカラーチップ（`Cyan: 90%`, `Magenta: 0%`, `Yellow: 70%`, `CMYK(90,0,70,0)`）とカプセルバッジ（`+ cvn | plus mobile`）が完全な整列バランスで描画されていることを確認。
