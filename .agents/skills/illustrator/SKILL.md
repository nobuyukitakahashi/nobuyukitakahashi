---
name: illustrator
description: >-
  Adobe Illustrator 2027（MCPサーバー illustrator および CLIブリッジ .agents/mcp/illustrator-mcp/cli.js）を用いた
  ベクターロゴデザイン、CMYK印刷入稿データ、テキストのアウトライン化（.ai / .pdf / .svg / .eps）、および
  DTPレイアウト制作を専任で実行し、中間成果物を 02_Creative_Dept/illustrator/ に、
  最終成果物を 04_Delivery_Dept/outputs/illustrator/ に格納するスキル。
  ユーザーが /illustrator を指定した際、またはジャンル選択で「Illustrator（ベクターロゴ・DTP・印刷データ）」を選択した際に使用する。
---

# ✒️ Adobe Illustrator ベクター・DTP・CMYK印刷データ専任スキル (`/illustrator`)

## 1. ジャンル別ディレクトリ規約（厳守）
- **試作・JSXスクリプト・検証用ファイル置き場**:
  - [`02_Creative_Dept/illustrator/drafts/`](../../../02_Creative_Dept/illustrator/drafts/)
- **制作部門の完成中間成果物置き場**:
  - [`02_Creative_Dept/illustrator/final_outputs/`](../../../02_Creative_Dept/illustrator/final_outputs/)
- **最終納品フォルダ（`04_Delivery_Dept` による格納先）**:
  - [`04_Delivery_Dept/outputs/illustrator/`](../../../04_Delivery_Dept/outputs/illustrator/)
  - ※納品台帳 [`04_Delivery_Dept/outputs/INDEX.md`](../../../04_Delivery_Dept/outputs/INDEX.md) の「`## ✒️ 2. Adobe Illustrator`」セクションにリンク（`illustrator/ファイル名`）を追記する。

---

## 2. 実行手順（MCP `illustrator` ＆ CLI ハイブリッド運用）

詳細なExtendScript（JSX）実装パターンは [`.agents/skills/adobe-illustrator/SKILL.md`](../adobe-illustrator/SKILL.md) を参照してください。

1. **Illustrator 2027 ステータス確認**:
   - MCPサーバー `illustrator` の `get_illustrator_status` または CLI `node .agents/mcp/illustrator-mcp/cli.js status` を実行する。
2. **ExtendScript (JSX) スクリプトによるベクター構築・CMYK管理**:
   - スクリプトを `02_Creative_Dept/illustrator/drafts/build_[テーマ名].jsx` に作成し、`execute_illustrator_jsx` または `node .agents/mcp/illustrator-mcp/cli.js exec --file "02_Creative_Dept/illustrator/drafts/build_[テーマ名].jsx"` で実行する。
   - **CMYKカラー厳守**: `DocumentColorSpace.CMYK` および `new CMYKColor()` で印刷指定色（例：CVNブランドグリーン `C:90 M:0 Y:70 K:0`）を正確に設定し、名前付きスウォッチ（`doc.swatches`）として登録する。
   - **座標系の注意**: アートボード矩形 `artboardRect = [left, top, right, bottom]` はY軸が上向き正（下に向かうほどYが減少）であり、`rectangle(top, left, width, height)` の引数順に注意する。
3. **アートボードPNG書き出し＋`read_file` 視覚監査ループ**:
   - `export_artboard_png`（または `node .agents/mcp/illustrator-mcp/cli.js export-png --out "02_Creative_Dept/illustrator/final_outputs/[テーマ名].png" --scale 200`）で200%高解像度PNGを書き出す。
   - `read_file` で書き出されたPNG画像を実際に目視確認し、余白バランス・文字配置・カーニング・重なり・CMYK発色を監査・修正する。
4. **フォント保持版・アウトライン化済み入稿版の保存と最終納品**:
   - `save_illustrator_document`（または `node .agents/mcp/illustrator-mcp/cli.js save --out "02_Creative_Dept/illustrator/final_outputs/[テーマ名].ai" --outline-text true`）で `.ai` / `.pdf` / `.svg` / `.eps` および制作仕様書 `content_[テーマ名].md` を `02_Creative_Dept/illustrator/final_outputs/` に保存する。
   - 続けて `04_Delivery_Dept` を通じて `04_Delivery_Dept/outputs/illustrator/` に最終成果物を格納し、`04_Delivery_Dept/outputs/INDEX.md` を更新する。
