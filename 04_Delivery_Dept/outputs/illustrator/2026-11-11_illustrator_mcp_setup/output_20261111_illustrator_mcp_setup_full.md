# 最終納品パッケージ：Adobe Illustrator 2027 自動制御用ローカルMCPサーバー（`illustrator`）＆専用スキル（`adobe-illustrator`）構築・AGY常設統合・実機検証パッケージ
- **納品日**: 2026年11月11日
- **格納場所**: `04_Delivery_Dept/outputs/`
- **法務・コンプライアンス審査**: `SKIPPED（通常案件・内部技術インフラ整備）`
- **同梱・変換ファイル一覧**:
  - マスターパッケージ: [`output_20261111_illustrator_mcp_setup_full.md`](output_20261111_illustrator_mcp_setup_full.md)
  - 実機検証済みAdobe Illustratorネイティブファイル（CMYK・全テキストアウトライン化済 `.ai`）: [`output_20261111_illustrator_mcp_verify.ai`](output_20261111_illustrator_mcp_verify.ai)（`1,314,313 bytes`）
  - 実機検証済み200%高解像度アートボードPNG（`1600 × 1000 px`）: [`output_20261111_illustrator_mcp_verify.png`](output_20261111_illustrator_mcp_verify.png)（`60,577 bytes`）
  - ローカルMCPサーバー本体: [`.agents/mcp/illustrator-mcp/server.js`](../../.agents/mcp/illustrator-mcp/server.js)
  - 即時実行CLIブリッジ: [`.agents/mcp/illustrator-mcp/cli.js`](../../.agents/mcp/illustrator-mcp/cli.js)
  - 専用スキル定義: [`.agents/skills/adobe-illustrator/SKILL.md`](../../.agents/skills/adobe-illustrator/SKILL.md)（およびグローバル同期先 `C:\Users\nobuy\.gemini\config\skills\adobe-illustrator\SKILL.md`）

---

## Part 1. 完成コンテンツ本編：Adobe Illustrator 2027 自動制御用ローカルMCPサーバー（`illustrator`）＆専用スキル（`adobe-illustrator`）構築・実機検証仕様書

### 1. 概要
本仕様書は、`02_Creative_Dept`（制作・編集・3D・ベクターDTP部門）において **Adobe Illustrator 2027 (Version 31.0.0)** を自動制御し、コーポレートロゴ、DTP・印刷入稿用CMYKデータ（`.ai` / `.pdf` / `.svg` / `.eps`）、テキストのアウトライン化（`createOutline()`）、および視覚監査用高解像度PNG書き出しを一気通貫で実行するためのローカルMCPサーバー＆CLIブリッジの実装・検証記録です。

---

### 2. システムアーキテクチャと実装ファイル

#### 2.1 ローカルMCPサーバー（[`.agents/mcp/illustrator-mcp/server.js`](../../.agents/mcp/illustrator-mcp/server.js)）
- **外部パッケージ依存ゼロ**: Node.js 標準モジュール（`fs`, `path`, `os`, `child_process`）のみで動作。
- **デュアルフレーミング対応 stdio JSON-RPC 2.0**:
  - `Content-Length` ヘッダ方式および Newline-delimited JSON（改行区切りJSON）の両方を自動判別して双方向応答。
  - 対応メソッド：`initialize`, `notifications/initialized`, `ping`, `tools/list`, `tools/call`。
- **UTF-8完全保護とExtendScript `JSON` ポリフィル**:
  - ExtendScript（ES3準拠エンジン）に存在しない `JSON.stringify` をラッパー内で自動ポリフィル。
  - 一時 `.jsx` ファイルを UTF-8 BOM（`\uFEFF`）付きでASCII一時ディレクトリ（`os.tmpdir()`）に生成し、日本語パス（`マイドライブ` 等）もすべて `\uXXXX` エスケープおよび一時ファイル経由コピーで処理することで、文字化け・パスエンコーディングエラーを100%防止。
- **Windows COM (`Illustrator.Application`) 参照保持機構（`ensureWindowsComKeeper`）**:
  - 短命プロセスから COM 経由（`-Embedding`）で Illustrator を起動した際、プロセス終了時に COM クラスファクトリが解除される問題を防ぐため、WMI（`Win32_Process.Create`）経由のバックグラウンド参照保持プロセスを自動維持し、2回目以降の CLI / MCP 呼び出しに約 `245 ms` で高速アタッチ。

#### 2.2 提供ツール一覧（5種）
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

#### 2.3 即時実行CLIブリッジ（[`.agents/mcp/illustrator-mcp/cli.js`](../../.agents/mcp/illustrator-mcp/cli.js)）
```powershell
node .agents/mcp/illustrator-mcp/cli.js status
node .agents/mcp/illustrator-mcp/cli.js summary [--file <path>]
node .agents/mcp/illustrator-mcp/cli.js exec --code "<jsx>" | --file <script.jsx>
node .agents/mcp/illustrator-mcp/cli.js export-png --out <png_path> [--artboard 0] [--scale 200] [--transparent true]
node .agents/mcp/illustrator-mcp/cli.js save --out <ai_or_pdf_or_svg_path> [--outline-text true] [--cmyk true]
```

#### 2.4 ExtendScript (`.jsx`) 実装時の鉄則（`adobe-illustrator` スキルより）
1. **ES3構文の厳守**: `let` / `const` / アロー関数 `()=>` / テンプレートリテラルは使用不可。必ず `var` と `function` を使用する。
2. **Illustrator座標系（Y軸上向き正）の考慮**:
   - アートボード左上を `(0, 0)` に揃えた場合、下方向への移動は **負のY座標（`-y`）** となる。
   - `pathItems.rectangle(top, left, width, height)` の第1引数は `top`（上端Y座標）、第2引数は `left`（左端X座標）。
3. **CMYKカラーの厳密指定**:
   ```javascript
   function makeCMYK(c, m, y, k) {
       var col = new CMYKColor();
       col.cyan = c; col.magenta = m; col.yellow = y; col.black = k;
       return col;
   }
   ```
4. **アウトライン化前の保存順序**:
   - `tf.createOutline()` を実行するとテキスト再編集が不可になるため、編集用マスターと入稿用アウトライン化データを分けるか、最終 `save_illustrator_document` 呼び出し時に `outline_text: true` を指定する。

---

### 3. 実機動作検証（Ground Truth）結果

#### 3.1 MCP JSON-RPC 2.0 プロトコル応答検証
`server.js` の標準入力に `initialize` ➔ `notifications/initialized` ➔ `tools/list` ➔ `tools/call` (`get_illustrator_status`) を流し込み、以下を確認：
- `serverInfo: { name: "illustrator", version: "1.0.0" }`
- 全5ツールの JSON Schema 定義が正常に返却されること。
- `get_illustrator_status` が `Adobe Illustrator 2027 (31.0.0)` および COM CLSID `{8F60463D-0543-413C-80EA-69133B2F206D}` を正確に検出すること。

#### 3.2 Adobe Illustrator 2027 実機制御・CMYKベクター生成・視覚監査
検証スクリプト [`02_Creative_Dept/drafts/test_illustrator_mcp_build.jsx`](../../02_Creative_Dept/drafts/test_illustrator_mcp_build.jsx) を実行し、以下の通り検証完了：
- **ドキュメント設定**: `CVN_Illustrator_MCP_Verify`（`DocumentColorSpace.CMYK`, `800 × 500 pt`, 3レイヤー構成：`Background_Layer`, `Vector_Badge_Layer`, `Typography_Layer`）
- **登録スウォッチ**:
  - `CVN_Brand_Green_C90M0Y70K0`: `CMYK(90, 0, 70, 0)`
  - `CVN_Dark_Charcoal`: `CMYK(85, 65, 55, 70)`
- **生成・納品ファイル**:
  1. 視覚監査用高解像度PNG（200%スケール、`1600 × 1000 px`）: [`output_20261111_illustrator_mcp_verify.png`](output_20261111_illustrator_mcp_verify.png)
  2. 全テキストアウトライン化済みCMYK Illustratorマスター（`.ai`、`1.31 MB`、`remainingTextFrames: 0`）: [`output_20261111_illustrator_mcp_verify.ai`](output_20261111_illustrator_mcp_verify.ai)
- **`read_file` 視覚監査結果**:
  - 1回目の書き出し画像を `read_file` で目視確認し、下段CMYKチップのテキスト位置およびサブタイトル右端マージンを検出して `.jsx` の座標・フォントサイズを微調整し、再書き出しにより4つのCMYKカラーチップ（`Cyan: 90%`, `Magenta: 0%`, `Yellow: 70%`, `CMYK(90,0,70,0)`）とカプセルバッジ（`+ cvn | plus mobile`）が完全な整列バランスで描画されていることを確認。

---

## Part 2. 組織自律進化・監査サマリー（`05_System_Evolution_Dept`）

- **監査対象**: Antigravity MCPサーバー拡張仕様 & `02_Creative_Dept` ベクター/DTP制作パイプライン
- **判定ステータス**: `[UPDATED: 改善実施]`
- **常設統合・同期済み設定一覧**:
  1. **MCPサーバー登録**:
     - `C:\Users\nobuy\.gemini\antigravity\mcp_config.json`
     - `C:\Users\nobuy\.gemini\config\mcp_config.json`
     - `C:\Users\nobuy\.gemini\antigravity-obsidian\mcp_config.json`
     - （※すべて既存の `blender-mcp.exe` カスタム設定を完全保持した上で `"illustrator"` を追加登録）
  2. **マルチPC環境同期スクリプト対応**:
     - [`.agents/skills/pc-env-sync/scripts/sync_pc_env.ps1`](../../.agents/skills/pc-env-sync/scripts/sync_pc_env.ps1)（Windows用）
     - [`.agents/skills/pc-env-sync/scripts/sync_mac_env.sh`](../../.agents/skills/pc-env-sync/scripts/sync_mac_env.sh)（macOS用）
     - [`.agents/skills/pc-env-sync/SKILL.md`](../../.agents/skills/pc-env-sync/SKILL.md)
  3. **部門ルール・スキル更新**:
     - [`AGENTS.md`](../../AGENTS.md)
     - [`02_Creative_Dept/AGENTS.md`](../../02_Creative_Dept/AGENTS.md)
     - [`.agents/skills/creative-dept/SKILL.md`](../../.agents/skills/creative-dept/SKILL.md)
     - [`.agents/skills/adobe-illustrator/SKILL.md`](../../.agents/skills/adobe-illustrator/SKILL.md)
