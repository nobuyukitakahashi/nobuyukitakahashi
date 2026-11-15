---
name: aftereffects
description: >-
  Adobe After Effects 2027（MCPサーバー aftereffects および CLIブリッジ .agents/mcp/aftereffects-mcp/cli.js）を用いた
  モーショングラフィックス制作、コンポジション・レイヤー構築、フレームPNG書き出し監査、.aep 保存、
  およびレンダーキュー映像書き出しを実行し、中間成果物を 02_Creative_Dept/aftereffects/ に、
  最終成果物を 04_Delivery_Dept/outputs/aftereffects/ に格納するスキル。
  ユーザーが /aftereffects を指定した際、または After Effects での映像・モーショングラフィックス作業を指示した際に使用する。
---

# ✨ Adobe After Effects モーション・VFX制作専任スキル (`/aftereffects`)

## 1. ディレクトリ規約
- **試作・JSXスクリプト・監査用一時ファイル置き場**:
  - [`02_Creative_Dept/aftereffects/drafts/`](../../../02_Creative_Dept/aftereffects/drafts/)
- **制作部門の完成中間成果物置き場**:
  - [`02_Creative_Dept/aftereffects/final_outputs/`](../../../02_Creative_Dept/aftereffects/final_outputs/)
- **最終納品フォルダ**:
  - [`04_Delivery_Dept/outputs/aftereffects/`](../../../04_Delivery_Dept/outputs/aftereffects/)
  - ※本スキルは既存の5大ジャンル（`blender` / `illustrator` / `photoshop` / `davinci` / `writing`）を変更せずに利用する単体操作スキルです。

---

## 2. 実行手順（MCP `aftereffects` ＆ CLI ハイブリッド運用）

詳細な ExtendScript（JSX）実装仕様は [`.agents/skills/adobe-aftereffects/SKILL.md`](../adobe-aftereffects/SKILL.md) を参照してください。

1. **After Effects 2027 ステータス確認**:
   - MCPサーバー `aftereffects` の `get_aftereffects_status` または CLI `node .agents/mcp/aftereffects-mcp/cli.js status` を実行する。
   - 既存 `.aep` を扱う場合は `get_project_summary` または `node .agents/mcp/aftereffects-mcp/cli.js summary --file "<aep_path>"` で構成を確認する。
2. **ExtendScript (JSX) スクリプトによるコンポジション・アニメーション構築**:
   - スクリプトを `02_Creative_Dept/aftereffects/drafts/build_[テーマ名].jsx` に作成し、`execute_aftereffects_jsx` または `node .agents/mcp/aftereffects-mcp/cli.js exec --file "02_Creative_Dept/aftereffects/drafts/build_[テーマ名].jsx"` で実行する。
   - **1始まりインデックス厳守**: `proj.item(1)`, `comp.layer(1)` 等は1始まりで参照し、`app.beginUndoGroup(...)` / `app.endUndoGroup()` でまとめる。
3. **フレームPNG書き出し＋`read_file` 視覚監査ループ**:
   - `export_comp_frame_png` または `node .agents/mcp/aftereffects-mcp/cli.js export-png --out "02_Creative_Dept/aftereffects/drafts/audit_[テーマ名].png" --comp "<Comp名>" --time <秒>` で代表フレームを書き出す。
   - `read_file` で書き出されたPNG画像を目視確認し、レイアウト・文字サイズ・アニメーション位置・エフェクト適用結果を監査・修正する。
4. **`.aep` 保存・レンダーキュー書き出しと最終納品**:
   - `save_aftereffects_project` または `node .agents/mcp/aftereffects-mcp/cli.js save --out "02_Creative_Dept/aftereffects/final_outputs/[テーマ名].aep"`（映像書き出し時は `--render-comp` と `--render-out` を指定）で保存・レンダリングする。
   - 最終成果物を `04_Delivery_Dept/outputs/aftereffects/` に格納する。
