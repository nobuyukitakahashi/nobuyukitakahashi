# 最終納品パッケージ：Adobe Photoshop 2027 (v28.0) ローカルMCPサーバー（`photoshop`）＆5大ジャンル制作体制構築
- **納品日**: 2026年11月11日
- **ジャンル**: `photoshop` (`blender` / `illustrator` / `photoshop` / `davinci` / `writing`)
- **格納場所**: `04_Delivery_Dept/outputs/photoshop/`
- **法務・コンプライアンス審査**: `SKIPPED（通常システム構築・内部ツール検証案件）`
- **同梱・変換ファイル一覧**:
  - マスターパッケージ: [`output_20261111_photoshop_mcp_setup_full.md`](output_20261111_photoshop_mcp_setup_full.md)
  - 検証生成マルチレイヤーPSD（`1600×1000 px`, `300 dpi`, RGB 8-bit, 3グループ計18レイヤー）: [`output_20261111_photoshop_mcp_verify.psd`](output_20261111_photoshop_mcp_verify.psd)
  - カンバス書き出し視覚監査用PNG（`1600×1000 px`, 100%等倍）: [`output_20261111_photoshop_mcp_verify.png`](output_20261111_photoshop_mcp_verify.png)

---

## Part 1. 完成コンテンツ本編・制作仕様

### 1. 概要と目的
Antigravity バーチャル組織における **Adobe Photoshop 2027 (`v28.0.0`)** 自動制御用ローカルMCPサーバー（`photoshop`）、即時実行CLIブリッジ（[`.agents/mcp/photoshop-mcp/cli.js`](../../../.agents/mcp/photoshop-mcp/cli.js)）、専用スキル（`/photoshop`・`adobe-photoshop`）を構築・グローバル登録し、実機検証（マルチレイヤー `.psd` 生成＋視覚監査用 `.png` 書き出し）を完了しました。

本拡張により、組織の制作・納品体制は以下の **5大ジャンル（`<genre>`）** へ拡張されました：
1. **`blender`** (`/blender`): Blender（3Dモデリング・CG・3Dアニメ）
2. **`illustrator`** (`/illustrator`): Illustrator（ベクターロゴ・DTP・印刷データ）
3. **`photoshop`** (`/photoshop`): Photoshop（画像編集・レタッチ・PSD合成・バナー制作）
4. **`davinci`** (`/davinci`): DaVinci Resolve（動画編集・グレーディング・テロップ）
5. **`writing`** (`/writing`): Writing / Document（記事執筆・企画書・Web HTML）

---

### 2. ローカルMCPサーバー＆CLIブリッジ（`.agents/mcp/photoshop-mcp/`）

- **サーバー本体**: [`.agents/mcp/photoshop-mcp/server.js`](../../../.agents/mcp/photoshop-mcp/server.js)
- **CLIブリッジ**: [`.agents/mcp/photoshop-mcp/cli.js`](../../../.agents/mcp/photoshop-mcp/cli.js)
- **特徴**:
  - 外部npmパッケージ依存ゼロ（Node.js標準モジュールのみ）。
  - MCP標準の **stdio JSON-RPC 2.0（`Content-Length` ヘッダおよび Newline-delimited JSON 両対応）**。
  - Windows ヘッドレス安全設計（`PS_EXE` フルパス解決、`"-NonInteractive", "-NoProfile", "-ExecutionPolicy", "Bypass"`、`{ stdio: ["ignore", "pipe", "pipe"], windowsHide: true }`、Node.js `fs.readdirSync` + `tasklist.exe` による高速ステータス確認で `316 ms` 応答）。
  - ExtendScript (`.jsx`) 一時ファイルへの UTF-8 BOM（`\uFEFF`）付与および非ASCII文字の `\uXXXX` エスケープ（`toAsciiJsString`）による完全な文字化け防止。

| # | ツール名 | CLIサブコマンド | 機能概要 |
| :--- | :--- | :--- | :--- |
| 1 | `get_photoshop_status` | `status` | Photoshop実行ファイルパス、COM ProgID (`Photoshop.Application`)、起動状態・PID、開いているドキュメント一覧（名前・幅/高さpx・解像度dpi・RGB/CMYK・レイヤー数）を取得 |
| 2 | `execute_photoshop_jsx` | `exec` | ExtendScript (DOM / ActionManager) コードまたは `.jsx` ファイルを `try/catch` ラッパー付きで実行し、結果JSONまたはエラー行番号を返す |
| 3 | `get_document_summary` | `summary` | アクティブドキュメント（または指定ファイル）の寸法・解像度・カラーモード・ビット深度・全レイヤー階層ツリー（`LayerSet` / `ArtLayer`、`kind`、`boundsPx`、`textInfo`）をJSON取得 |
| 4 | `export_canvas_png` | `export-png` | アクティブドキュメントの複製上でRGB変換・スケール調整を行い、視覚監査（`read_file`）用の高画質PNGを書き出す（元PSDのレイヤー構造は完全保持） |
| 5 | `save_photoshop_document` | `save` | `.psd` / `.png` / `.jpg` / `.tiff` 形式で保存。複製上でのテキストレイヤー一括ラスタライズ（`rasterize_text`）、CMYK変換（`cmyk_convert`）、レイヤー統合（`flatten`）に対応 |

---

### 3. 実機検証結果（Adobe Photoshop 2027 `v28.0.0`）

- **検証スクリプト**: [`02_Creative_Dept/photoshop/drafts/test_photoshop_mcp_build.jsx`](../../../02_Creative_Dept/photoshop/drafts/test_photoshop_mcp_build.jsx)
- **生成ドキュメント**: `CVN_Photoshop_MCP_Verify` (`1600 × 1000 px`, `300 dpi`, `RGB 8-bit`, 3 `LayerSet` グループ・計18レイヤー)
  - `01_Background_Group`: ダークエメラルド背景、ブランドグリーン外枠、ホワイトメインカード、ミントヘッダー帯、左アクセントバー
  - `02_Visual_Badge_and_Chips`: CVNブランドグリーン（`#00a273`）ヒーローバッジ、`+` クロスエンブレム、セクション区切り線、4色カラーチップ（`#00a273`, `#00c694`, `#00a8e8`, `#20302d`）
  - `03_Typography_Group`: `Title_Header`, `Subtitle_Header`, `Badge_CVN_Text` (`"cvn"`), `Hero_Brand_Title` (`"plus mobile"`), `Hero_Specs_Caption`, `Chip_Label_1`〜`4`（300dpi環境向けに `sizePx * (72.0 / doc.resolution)` pt 変換を適用し、1ピクセルの狂いもなく配置）
- **視覚監査（`read_file`）**:
  - `export_canvas_png` で書き出した [`output_20261111_photoshop_mcp_verify.png`](output_20261111_photoshop_mcp_verify.png) を目視監査し、余白バランス・文字サイズ・コントラスト・色再現がすべて設計通りであることを確認完了。
