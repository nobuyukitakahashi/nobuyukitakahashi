---
name: premiere
description: >-
  Adobe Premiere Pro 2027（MCPサーバー premiere および CLIブリッジ .agents/mcp/premiere-mcp/cli.js）を用いた
  映像編集、シーケンス・タイムライン操作、フレームPNG書き出し監査、.prproj 保存、およびメディア書き出しを実行し、
  中間成果物を 02_Creative_Dept/premiere/ に、最終成果物を 04_Delivery_Dept/outputs/premiere/ に格納するスキル。
  ユーザーが /premiere を指定した際、または Premiere Pro での映像編集作業を指示した際に使用する。
---

# 🎞️ Adobe Premiere Pro 映像編集・タイムライン制御専任スキル (`/premiere`)

## 1. ディレクトリ規約
- **試作・JSXスクリプト・監査用一時ファイル置き場**:
  - [`02_Creative_Dept/premiere/drafts/`](../../../02_Creative_Dept/premiere/drafts/)
- **制作部門の完成中間成果物置き場**:
  - [`02_Creative_Dept/premiere/final_outputs/`](../../../02_Creative_Dept/premiere/final_outputs/)
- **最終納品フォルダ**:
  - [`04_Delivery_Dept/outputs/premiere/`](../../../04_Delivery_Dept/outputs/premiere/)
  - ※本スキルは既存の5大ジャンル（`blender` / `illustrator` / `photoshop` / `davinci` / `writing`）を変更せずに利用する単体操作スキルです。

---

## 2. 実行手順（MCP `premiere` ＆ CLI ハイブリッド運用）

詳細な ExtendScript（JSX）実装仕様は [`references/extendscript-guide.md`](references/extendscript-guide.md) を参照してください。

1. **Premiere Pro 2027 ＆ CEP Bridge ステータス確認**:
   - MCPサーバー `premiere` の `get_premiere_status` または CLI `node .agents/mcp/premiere-mcp/cli.js status` を実行する。
   - `running: false` または `cepBridge.active: false` の場合は、Premiere Pro を起動し `ウィンドウ > エクステンション > Antigravity MCP Bridge` パネルを開くようユーザーへ案内する（または状態を確認する）。
2. **プロジェクト・シーケンス構成の把握**:
   - `get_project_summary` または `node .agents/mcp/premiere-mcp/cli.js summary` で開いているプロジェクト・シーケンス・トラック・クリップ情報を取得する。
3. **ExtendScript (JSX) スクリプトによるタイムライン編集**:
   - スクリプトを `02_Creative_Dept/premiere/drafts/edit_[テーマ名].jsx` に作成し、`execute_premiere_jsx` または `node .agents/mcp/premiere-mcp/cli.js exec --file "02_Creative_Dept/premiere/drafts/edit_[テーマ名].jsx"` で実行する。
4. **フレームPNG書き出し＋`read_file` 視覚監査ループ**:
   - `export_frame_png` または `node .agents/mcp/premiere-mcp/cli.js export-png --out "02_Creative_Dept/premiere/drafts/audit_[テーマ名].png" --time <秒>` でフレームを書き出す。
   - `read_file` で書き出されたPNG画像を目視確認し、映像・テロップ・配置・表示崩れの有無を監査・修正する。
5. **プロジェクト保存・完パケ書き出しと最終納品**:
   - `save_or_export_premiere` または `node .agents/mcp/premiere-mcp/cli.js save --save-as "02_Creative_Dept/premiere/final_outputs/[テーマ名].prproj"`（映像書き出し時は `--export-out` と `--preset <.epr>` を指定）で保存・書き出しを行う。
   - 最終成果物を `04_Delivery_Dept/outputs/premiere/` に格納する。
