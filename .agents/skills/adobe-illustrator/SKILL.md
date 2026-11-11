---
name: adobe-illustrator
description: >
  Adobe Illustrator 2027 をローカルMCPサーバー（illustrator）およびCLIブリッジ
  （node .agents/mcp/illustrator-mcp/cli.js）経由で自動制御し、ベクターロゴ、DTP・印刷用CMYKデータ、
  パッケージ・キャラクター図面、アウトライン化済み入稿データ（.ai / .pdf / .svg / .eps）および
  視覚監査用高解像度PNGを生成・編集するスキル。
  Illustratorでのベクター制作、SVGからのCMYK .ai変換、テキストのアウトライン化、DTP入稿データ作成時に使用する。
---

# Adobe Illustrator 自動制御スキル (`adobe-illustrator`)

## 1. 概要とハイブリッド運用アーキテクチャ
本スキルは、**Adobe Illustrator 2027**（Windows COM `Illustrator.Application` / macOS `osascript`）を以下の2経路でシームレスに制御します：
1. **MCPサーバー `illustrator`**（[`.agents/mcp/illustrator-mcp/server.js`](../../mcp/illustrator-mcp/server.js)）:
   - `call_mcp_tool` から `illustrator` サーバーの5つのネイティブツールを呼び出す。
2. **即時実行CLIブリッジ**（[`.agents/mcp/illustrator-mcp/cli.js`](../../mcp/illustrator-mcp/cli.js)）:
   - MCP未接続時（Antigravity再起動前）やバッチ処理時に、`run_command` から `node .agents/mcp/illustrator-mcp/cli.js <subcommand>` を呼び出して全く同じ5つのツール機能を実行する。

---

## 2. MCPサーバー `illustrator` の提供ツール（全5種）

| ツール名 | 用途 | 主な引数 |
| :--- | :--- | :--- |
| `get_illustrator_status` | Illustrator実行ファイル・COM登録状態・プロセス起動有無・開いているドキュメント一覧（名前・CMYK/RGB・アートボード数）を取得 | なし |
| `execute_illustrator_jsx` | ExtendScript（JSX）文字列または `.jsx` ファイルをUTF-8保護＆`try/catch` ラッパー付きで実行し、戻り値（JSON/文字列）とエラー行番号を取得 | `script` (string) または `script_path` (string), `wrap_try_catch` (boolean, default: `true`) |
| `get_document_summary` | アクティブドキュメント（または指定ファイルを開いて）のカラースペース、アートボード座標、レイヤー構成、テキストフレーム、パス数、スウォッチ一覧を取得 | `file_path` (optional string: `.ai`/`.svg`/`.pdf`/`.eps`) |
| `export_artboard_png` | 指定アートボードを `ExportType.PNG24` で高解像度PNG書き出しし、出力パスとピクセル寸法（`width`, `height`）を返す | `output_path` (required), `artboard_index` (default: `0`), `scale` (default: `200`), `transparency` (default: `true`) |
| `save_illustrator_document` | アクティブドキュメントを `.ai` / `.pdf` / `.svg` / `.eps` で保存・書き出しする。保存前の全テキスト `createOutline()` やCMYK変換に対応 | `output_path` (required), `outline_text` (default: `false`), `cmyk_convert` (default: `false`) |

---

## 3. CLIブリッジ（`cli.js`）コマンドリファレンス

MCP未接続時やスクリプト連続実行時は、`run_command` で以下のコマンドを使用します：

```powershell
# 1. Illustratorのインストール・起動状態・開いているドキュメント一覧を確認
node .agents/mcp/illustrator-mcp/cli.js status

# 2. アクティブドキュメント（または指定ファイル）の構造サマリーを取得
node .agents/mcp/illustrator-mcp/cli.js summary
node .agents/mcp/illustrator-mcp/cli.js summary --file "02_Creative_Dept/final_outputs/logo.ai"

# 3. ExtendScript (JSX) のインライン実行または .jsx ファイル実行
node .agents/mcp/illustrator-mcp/cli.js exec --code "return app.version;"
node .agents/mcp/illustrator-mcp/cli.js exec --file "02_Creative_Dept/drafts/build_logo.jsx"

# 4. 視覚監査（read_file）用の高解像度アートボードPNG書き出し（200%スケール・透過あり）
node .agents/mcp/illustrator-mcp/cli.js export-png --out "02_Creative_Dept/final_outputs/preview.png" --scale 200 --transparent true

# 5. ドキュメントの保存（.ai / .pdf / .svg / .eps）＋テキストのアウトライン化
node .agents/mcp/illustrator-mcp/cli.js save --out "02_Creative_Dept/final_outputs/master_editable.ai" --outline-text false
node .agents/mcp/illustrator-mcp/cli.js save --out "02_Creative_Dept/final_outputs/print_outlined.ai" --outline-text true
node .agents/mcp/illustrator-mcp/cli.js save --out "02_Creative_Dept/final_outputs/print_outlined.pdf" --outline-text true
```

---

## 4. ExtendScript (JSX) 重要実装パターンと鉄則

### 鉄則①：Illustratorの座標系（Y軸は上がプラス・下がマイナス）
- SVGやHTML Canvasとは異なり、Illustratorの座標系は **Y軸が上向き正（下に向かうほどYが減る）** です。
- アートボード矩形 `var r = doc.artboards[0].artboardRect;` は `[left, top, right, bottom]` の配列を返します。
  - 幅 `W = r[2] - r[0]`
  - 高さ `H = r[1] - r[3]`（※`top > bottom` であるため `r[1] - r[3]` が正の高さ）
- アートボード左上から `(dx, dy)` 下がった位置に図形を置く場合：
  - `left = r[0] + dx`
  - `top = r[1] - dy`
- `pathItems.rectangle(top, left, width, height)` および `pathItems.roundedRectangle(top, left, width, height, rx, ry)` の第1引数は **`top`（Y座標）**、第2引数は **`left`（X座標）** の順であることに注意してください。

### 鉄則②：CMYKドキュメントの新規作成と厳密なCMYKカラー設定
印刷物・コーポレートロゴ制作時は、`DocumentPreset` で最初から `DocumentColorSpace.CMYK` を指定し、`new CMYKColor()` でプロセスカラーまたはグローバルスウォッチを設定します。

```javascript
var preset = new DocumentPreset();
preset.title = "Brand_Logo_CMYK";
preset.width = 800; // pt
preset.height = 500; // pt
preset.colorMode = DocumentColorSpace.CMYK;
preset.units = RulerUnits.Points;

var doc = app.documents.addDocument(DocumentColorSpace.CMYK, preset);

function makeCMYK(c, m, y, k) {
  var col = new CMYKColor();
  col.cyan = c;
  col.magenta = m;
  col.yellow = y;
  col.black = k;
  return col;
}

// 例：株式会社cvn プライマリーブランドグリーン (C:90 M:0 Y:70 K:0)
var cvnGreen = makeCMYK(90, 0, 70, 0);
```

### 鉄則③：ベジェ曲線パス（`pathItems` + `pathPoints`）の精密構築
直線ポリゴンは `path.setEntirePath([[x0, y0], [x1, y1], ...])` で一括設定でき、滑らかなベジェ曲線は `pathPoints` の `anchor`, `leftDirection`, `rightDirection`, `pointType` で精密に制御できます。

```javascript
var p = doc.pathItems.add();
p.filled = true;
p.fillColor = cvnGreen;
p.stroked = false;
p.closed = true;

// ベジェ制御点の追加例
var pt0 = p.pathPoints.add();
pt0.anchor = [100, -100];
pt0.leftDirection = [100, -130];
pt0.rightDirection = [100, -70];
pt0.pointType = PointType.SMOOTH;
```

### 鉄則④：テキスト生成と印刷入稿用アウトライン化（`createOutline()`）
- フォント依存による文字化け・フォント置換事故を防ぐため、最終納品時は「フォント保持版（編集用 `.ai`）」と「全テキストアウトライン化済み版（入稿用 `.ai` / `.pdf`）」を書き分けます。
- `save_illustrator_document` で `outline_text: true`（または CLI `--outline-text true`）を指定すると、ドキュメント内の全 `textFrames` を末尾から安全に `createOutline()` してから保存します。

### 鉄則⑤：既存SVGのインポート・CMYK色を当て直して `.ai` / `.pdf` 入稿データ化
SVGファイル（RGB）をIllustratorで開き、CMYKカラースペースへ変換した上で指定CMYK値を再適用し、純正 `.ai` / `.pdf` として保存するワークフロー：

```javascript
var svgFile = new File("G:/path/to/input.svg");
var doc = app.open(svgFile);
app.executeMenuCommand("doc-color-cmyk");

var brandCmyk = new CMYKColor();
brandCmyk.cyan = 90; brandCmyk.magenta = 0; brandCmyk.yellow = 70; brandCmyk.black = 0;

for (var i = 0; i < doc.pathItems.length; i++) {
  var item = doc.pathItems[i];
  if (item.filled) {
    item.fillColor = brandCmyk;
  }
}
```

### 鉄則⑥：アートボードPNG書き出し＋`read_file` による視覚監査ループ（Visual Ground Truth）
1. JSXスクリプトで図形・ロゴ・レイアウトを構築したら、必ず `export_artboard_png`（または `cli.js export-png`）で200%高解像度PNGを書き出す。
2. `read_file` で書き出したPNG画像を実際に目視確認し、以下を監査する：
   - アートボードの上下左右マージン・センタリングのズレがないか（特にY軸反転の計算ミスによる天地逆転やアートボード外へのはみ出し）。
   - 文字やベクターパーツ同士の重なり・潰れ・カーニング不良がないか。
   - 指定したCMYK配色・線幅・角丸半径がデザイン意図通りか。
3. 視覚監査に合格したら、`save_illustrator_document`（または `cli.js save`）で `.ai` / `.pdf` / `.svg` を保存する。
