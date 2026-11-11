# Adobe Photoshop 2027 (v28.0) ローカルMCPサーバー＆5大ジャンル制作パイプライン仕様書

## 1. 概要と目的
本ドキュメントは、Antigravity バーチャル組織における **Adobe Photoshop 2027 (`v28.0.0`)** 自動制御用ローカルMCPサーバー（`photoshop`）、即時実行CLIブリッジ（[`.agents/mcp/photoshop-mcp/cli.js`](../../../.agents/mcp/photoshop-mcp/cli.js)）、専用スキル（`/photoshop`・`adobe-photoshop`）の実装仕様、および実機検証（マルチレイヤー `.psd` 生成＋視覚監査用 `.png` 書き出し）の結果をまとめた技術仕様書です。

本拡張により、組織の制作・納品体制は以下の **5大ジャンル（`<genre>`）** へ拡張されました：
1. **`blender`** (`/blender`): Blender 3Dモデリング・CG・3Dアニメーション
2. **`illustrator`** (`/illustrator`): Adobe Illustrator ベクターロゴ・DTP・印刷データ
3. **`photoshop`** (`/photoshop`): Adobe Photoshop 画像編集・フォトレタッチ・マルチレイヤーPSD合成・バナー制作
4. **`davinci`** (`/davinci`): DaVinci Resolve 動画編集・カラーグレーディング・テロップ合成
5. **`writing`** (`/writing`): Writing / Document 記事執筆・企画書・Web HTML

---

## 2. アーキテクチャとヘッドレス安全設計（`.agents/mcp/photoshop-mcp/`）

### 2.1 外部npmパッケージ依存ゼロの stdio JSON-RPC 2.0 サーバー
- **サーバー本体**: [`.agents/mcp/photoshop-mcp/server.js`](../../../.agents/mcp/photoshop-mcp/server.js)
- **CLIブリッジ**: [`.agents/mcp/photoshop-mcp/cli.js`](../../../.agents/mcp/photoshop-mcp/cli.js)
- **フレーミング両対応**: MCP標準の `Content-Length` ヘッダ方式および Newline-delimited JSON（1行1JSON）方式の双方を自動判別して応答。
- **Windows ヘッドレス安全設計**:
  - `PS_EXE` フルパス解決（`C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe`）
  - すべての `spawnSync` に `"-NonInteractive", "-NoProfile", "-ExecutionPolicy", "Bypass"` および `{ stdio: ["ignore", "pipe", "pipe"], windowsHide: true }` を徹底し、MCPデーモンの標準入力・コンソールハンドル競合によるハングを完全排除。
  - `get_photoshop_status` は Node.js ネイティブ `fs.readdirSync` と `tasklist.exe` で高速検出（未起動時 `316 ms` で即時応答）。
  - ExtendScript（`.jsx`）一時ファイル書き出し時に UTF-8 BOM（`\uFEFF`）および非ASCII文字の `\uXXXX` エスケープ（`toAsciiJsString`）を適用し、日本語レイヤー名やテキストの文字化けを完全防止。

### 2.2 提供ツール一覧（全5種）

| # | ツール名 | CLIサブコマンド | 機能概要 |
| :--- | :--- | :--- | :--- |
| 1 | `get_photoshop_status` | `status` | Photoshop実行ファイルパス、COM ProgID (`Photoshop.Application`)、起動状態・PID、開いているドキュメント一覧（名前・幅/高さpx・解像度dpi・RGB/CMYK・レイヤー数）を取得 |
| 2 | `execute_photoshop_jsx` | `exec` | ExtendScript (DOM / ActionManager) コードまたは `.jsx` ファイルを `try/catch` ラッパー付きで実行し、結果JSONまたはエラー行番号を返す |
| 3 | `get_document_summary` | `summary` | アクティブドキュメント（または指定ファイル）の寸法・解像度・カラーモード・ビット深度・全レイヤー階層ツリー（`LayerSet` / `ArtLayer`、`kind`、`boundsPx`、`textInfo`）をJSON取得 |
| 4 | `export_canvas_png` | `export-png` | アクティブドキュメントの複製上でRGB変換・スケール調整を行い、視覚監査（`read_file`）用の高画質PNGを書き出す（元PSDのレイヤー構造は完全保持） |
| 5 | `save_photoshop_document` | `save` | `.psd` / `.png` / `.jpg` / `.tiff` 形式で保存。複製上でのテキストレイヤー一括ラスタライズ（`rasterize_text`）、CMYK変換（`cmyk_convert`）、レイヤー統合（`flatten`）に対応 |

---

## 3. 実機検証結果（Adobe Photoshop 2027 `v28.0.0`）

### 3.1 検証スクリプトと生成仕様
- **検証用スクリプト**: [`02_Creative_Dept/photoshop/drafts/test_photoshop_mcp_build.jsx`](../drafts/test_photoshop_mcp_build.jsx)
- **ドキュメント仕様**:
  - ドキュメント名: `CVN_Photoshop_MCP_Verify`
  - カンバス寸法: `1600 × 1000 px`
  - 解像度: `300 dpi`（高解像度印刷・Web兼用スペック）
  - カラーモード / ビット深度: `RGB` / `8-bit`
  - レイヤー階層構造（3グループ＋背景＝計18レイヤー）:
    1. `01_Background_Group` (`LayerSet`):
       - `Dark_Emerald_Backdrop` (`#0e1d1a`)
       - `Brand_Green_Outer_Card` (`#00a273`)
       - `Main_White_Canvas_Card` (`#ffffff`)
       - `Top_Mint_Header_Band` (`#e8f7f2`)
       - `Header_Left_Accent_Bar` (`#00a273`)
    2. `02_Visual_Badge_and_Chips` (`LayerSet`):
       - `Badge_Soft_Accent_Backing`
       - `CVN_Green_Hero_Badge` (`#00a273`)
       - `Plus_Cross_Emblem` (`+` クロスシンボル)
       - `Section_Divider_Line`
       - `Chip_1_CVN_Green` (`#00a273`), `Chip_2_Bright_Teal` (`#00c694`), `Chip_3_Cyan_Accent` (`#00a8e8`), `Chip_4_Dark_Slate` (`#20302d`)
    3. `03_Typography_Group` (`LayerSet` / `LayerKind.TEXT` 計9レイヤー):
       - `Title_Header`: `"ADOBE PHOTOSHOP 2027 MCP VERIFIED"`
       - `Subtitle_Header`: `"Multi-Layer PSD Composition & Automated Retouching Pipeline (02_Creative_Dept)"`
       - `Badge_CVN_Text`: `"cvn"`
       - `Hero_Brand_Title`: `"plus mobile"`
       - `Hero_Specs_Caption`: `"1600x1000px @ 300dpi | RGB 8-bit | Layered PSD & PNG Visual Audit Ready"`
       - `Chip_Label_1`〜`4`: `"HEX #00A273"`, `"RGB(0,198,148)"`, `"CYAN ACCENT"`, `"PSD LAYERED"`

### 3.2 視覚監査（`read_file`）による300dpiフォントサイズ倍率の発見と解決
- 初回生成時、`300 dpi` ドキュメントに対して `ti.size = UnitValue(sizePx, "px")` を指定したところ、Photoshop DOMの仕様（`72 dpi` 基準のポイント換算＝`300 / 72 = 4.1667倍`）によりテキストが約4.17倍に拡大される現象を `get_document_summary` の `boundsPx` および `read_file` 視覚監査で検出。
- `var sizePt = sizePx * (72.0 / doc.resolution); ti.size = new UnitValue(sizePt, "pt");` によるDPI補正公式を導入し、全タイポグラフィが `1600 × 1000 px` カンバス内の設計座標へ1ピクセルの狂いもなく収まることを検証・スキル化（[`.agents/skills/adobe-photoshop/SKILL.md`](../../../.agents/skills/adobe-photoshop/SKILL.md) 鉄則④）しました。
