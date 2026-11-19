---
name: adobe-photoshop
description: >
  Adobe Photoshop 2027 (v28.0) をローカルMCPサーバー（photoshop）およびCLIブリッジ
  （node .agents/mcp/photoshop-mcp/cli.js）経由で自動制御し、画像編集、フォトレタッチ、
  マルチレイヤーPSD合成、バナー・サムネイル生成、RGB/CMYK変換、および視覚監査用PNG書き出しを実行するスキル。
  作業ディレクトリは 02_Creative_Dept/photoshop/{drafts,final_outputs}/、最終納品先は 04_Delivery_Dept/outputs/photoshop/。
  PhotoshopでのPSD作成、バナーデザイン、画像合成、フォトレタッチ時に使用する。
---

# Adobe Photoshop 自動制御スキル (`adobe-photoshop` / `/photoshop`)

## 1. 概要とジャンル別ディレクトリ規約
本スキルは、**Adobe Photoshop 2027 (v28.0)**（Windows COM `Photoshop.Application` / macOS `osascript`）を以下の2経路でシームレスに制御します：
1. **MCPサーバー `photoshop`**（[`.agents/mcp/photoshop-mcp/server.js`](../../mcp/photoshop-mcp/server.js)）:
   - `call_mcp_tool` から `photoshop` サーバーの5つのネイティブツールを呼び出す。
2. **即時実行CLIブリッジ**（[`.agents/mcp/photoshop-mcp/cli.js`](../../mcp/photoshop-mcp/cli.js)）:
   - MCP未接続時やバッチ処理時に、`run_command` から `node .agents/mcp/photoshop-mcp/cli.js <subcommand>` を呼び出して全く同じ5つのツール機能を実行する。

### 格納ディレクトリ規約（厳守）
- **試作・JSXスクリプト置き場**: `02_Creative_Dept/photoshop/drafts/`
- **制作部門の完成中間成果物置き場**: `02_Creative_Dept/photoshop/final_outputs/`
- **最終納品フォルダ**: `04_Delivery_Dept/outputs/photoshop/`（`INDEX.md` の `## 🖼️ 3. Adobe Photoshop` セクションへ登録）

---

## 2. MCPサーバー `photoshop` の提供ツール（全5種）

| ツール名 | 用途 | 主な引数 |
| :--- | :--- | :--- |
| `get_photoshop_status` | Photoshop実行ファイル・COM登録状態・プロセス起動有無・開いているドキュメント一覧（名前・幅/高さpx・解像度dpi・RGB/CMYK・レイヤー数）を取得 | なし |
| `execute_photoshop_jsx` | ExtendScript（JSX / ActionManager）文字列または `.jsx` ファイルをUTF-8保護＆`try/catch` ラッパー付きで実行し、戻り値（JSON/文字列）とエラー行番号を取得 | `script` (string) または `script_path` (string), `wrap_try_catch` (boolean, default: `true`) |
| `get_document_summary` | アクティブドキュメント（または指定ファイルを開いて）の寸法、解像度、カラーモード、ビット深度、全レイヤー階層ツリー（名前・`kind`・不透明度・描画モード・`boundsPx`・テキスト内容/フォント/サイズ）を取得 | `file_path` (optional string: `.psd`/`.psb`/`.png`/`.jpg`/`.tiff`) |
| `export_canvas_png` | アクティブドキュメントのカンバスを複製上でRGB変換・スケール調整して高画質PNG書き出しし、出力パス・ファイルサイズ・ピクセル寸法を返す（元PSDのレイヤー構造は無傷で保持） | `output_path` (required), `scale` (default: `100`) |
| `save_photoshop_document` | アクティブドキュメントを `.psd` / `.png` / `.jpg` / `.tiff` で保存・書き出しする。複製上でのテキストレイヤーラスタライズ（`rasterize_text`）、CMYK変換（`cmyk_convert`）、統合（`flatten`）に対応 | `output_path` (required), `rasterize_text` (default: `false`), `cmyk_convert` (default: `false`), `flatten` (default: `false`) |

---

## 3. CLIブリッジ（`cli.js`）コマンドリファレンス

```powershell
# 1. Photoshopのインストール・起動状態・開いているドキュメント一覧を確認
node .agents/mcp/photoshop-mcp/cli.js status

# 2. アクティブドキュメント（または指定ファイル）のレイヤー階層・構造サマリーを取得
node .agents/mcp/photoshop-mcp/cli.js summary
node .agents/mcp/photoshop-mcp/cli.js summary --file "02_Creative_Dept/photoshop/final_outputs/banner.psd"

# 3. ExtendScript (JSX) のインライン実行または .jsx ファイル実行
node .agents/mcp/photoshop-mcp/cli.js exec --code "return app.version;"
node .agents/mcp/photoshop-mcp/cli.js exec --file "02_Creative_Dept/photoshop/drafts/build_banner.jsx"

# 4. 視覚監査（read_file）用のカンバスPNG書き出し（100%等倍）
node .agents/mcp/photoshop-mcp/cli.js export-png --out "02_Creative_Dept/photoshop/final_outputs/preview.png" --scale 100

# 5. ドキュメントの保存（.psd / .png / .jpg / .tiff）
node .agents/mcp/photoshop-mcp/cli.js save --out "02_Creative_Dept/photoshop/final_outputs/master_layered.psd"
node .agents/mcp/photoshop-mcp/cli.js save --out "02_Creative_Dept/photoshop/final_outputs/print_cmyk.psd" --cmyk true --rasterize-text true
```

---

## 4. Photoshop ExtendScript (DOM + ActionManager) 重要実装パターンと鉄則

### 鉄則①：Photoshopの座標系と単位設定（左上原点・X右向き正・Y下向き正）
- Illustratorとは異なり、Photoshopの座標系は **左上が原点 `(0, 0)`、X軸は右向き正、Y軸は下向き正** です。
- スクリプト冒頭で必ず以下を設定し、pt/mm混在によるサイズ計算ズレを防止します：
```javascript
app.displayDialogs = DialogModes.NO;
app.preferences.rulerUnits = Units.PIXELS;
app.preferences.typeUnits = TypeUnits.PIXELS;
```

### 鉄則②：新規PSDドキュメント作成とRGB/CMYKカラー設定
```javascript
var doc = app.documents.add(
  UnitValue(1600, "px"),
  UnitValue(1000, "px"),
  300, // resolution (dpi)
  "Banner_Master",
  NewDocumentMode.RGB,
  DocumentFill.WHITE,
  1.0,
  BitsPerChannelType.EIGHT
);

function makeRGB(r, g, b) {
  var c = new SolidColor();
  c.rgb.red = r;
  c.rgb.green = g;
  c.rgb.blue = b;
  return c;
}
```

### 鉄則③：矩形・領域塗りつぶしとレイヤーセット（グループ）整理
```javascript
function fillRectSelection(layer, left, top, right, bottom, solidCol) {
  doc.activeLayer = layer;
  var region = [[left, top], [right, top], [right, bottom], [left, bottom]];
  doc.selection.select(region);
  doc.selection.fill(solidCol);
  doc.selection.deselect();
}
```

### 鉄則④：テキストレイヤー（`LayerKind.TEXT`）の生成と解像度（DPI）補正の鉄則
- `ti.position = [UnitValue(xPx, "px"), UnitValue(yPx, "px")]` の `yPx` はテキストの**ベースラインY座標**です。
- **超重要（300dpi等の高解像度ドキュメントにおける文字サイズ拡大バグ防止）**:
  - PhotoshopのDOMでは `textItem.size` は常に `72 dpi` 基準のポイント換算で評価されるため、たとえば `300 dpi` のドキュメントで `UnitValue(46, "px")` をそのまま指定すると、`300 / 72 = 4.1667倍`（約 `191 px`）に巨大化してカンバスからはみ出します。
  - 必ず **`var sizePt = sizePx * (72.0 / doc.resolution); ti.size = new UnitValue(sizePt, "pt");`** でDPIスケーリング補正を行ってください。
```javascript
function addTextLayer(parentSet, layerName, contents, xPx, yPx, sizePx, rgbCol) {
  var tl = parentSet.artLayers.add();
  tl.kind = LayerKind.TEXT;
  tl.name = layerName;
  var ti = tl.textItem;
  ti.contents = contents;
  try { ti.font = "Arial-BoldMT"; } catch (e) {}
  var sizePt = sizePx * (72.0 / doc.resolution);
  ti.size = new UnitValue(sizePt, "pt");
  ti.color = rgbCol;
  ti.position = [new UnitValue(xPx, "px"), new UnitValue(yPx, "px")];
  return tl;
}
```

### 鉄則⑤：カンバスPNG書き出し＋`read_file` による視覚監査ループ（Visual Ground Truth）
1. JSXスクリプトでレイヤー構成・タイポグラフィ・画像合成を構築したら、必ず `export_canvas_png`（または `cli.js export-png`）でPNGを書き出す。
2. `read_file` で書き出したPNG画像を実際に目視確認し、テキストのベースライン位置、余白バランス、コントラスト、文字化けや重なりがないかを監査する。
3. 視覚監査に合格したら、`save_photoshop_document`（または `cli.js save`）でレイヤー構造を保持した `.psd` を保存する。
