---
name: davinci
description: >-
  DaVinci Resolve（Python DaVinciResolveScript / Fusion Scripting API / MCP davinci-resolve）および
  FFmpeg を連携させた映像編集、タイムライン構築、カラーグレーディング、テロップ・VFX合成、
  および完パケ映像（.mp4 / .mov / .drp）書き出しを専任で実行し、
  中間成果物を 02_Creative_Dept/davinci/ に、最終成果物を 04_Delivery_Dept/outputs/davinci/ に格納するスキル。
  ユーザーが /davinci を指定した際、またはジャンル選択で「DaVinci Resolve（動画編集・グレーディング・テロップ）」を選択した際に使用する。
---

# 🎬 DaVinci Resolve 映像編集・カラーグレーディング・VFX専任スキル (`/davinci`)

## 1. ジャンル別ディレクトリ規約（厳守）
- **編集スクリプト・絵コンテ・素材・中間フレーム置き場**:
  - [`02_Creative_Dept/davinci/drafts/`](../../../02_Creative_Dept/davinci/drafts/)
- **制作部門の完成中間成果物置き場**:
  - [`02_Creative_Dept/davinci/final_outputs/`](../../../02_Creative_Dept/davinci/final_outputs/)
- **最終納品フォルダ（`04_Delivery_Dept` による格納先）**:
  - [`04_Delivery_Dept/outputs/davinci/`](../../../04_Delivery_Dept/outputs/davinci/)
  - ※納品台帳 [`04_Delivery_Dept/outputs/INDEX.md`](../../../04_Delivery_Dept/outputs/INDEX.md) の「`## 🎬 3. DaVinci Resolve`」セクションにリンク（`davinci/ファイル名`）を追記する。

---

## 2. 実行手順（DaVinci Resolve Scripting API / MCP ＆ FFmpeg ハイブリッド運用）

1. **DaVinci Resolve 接続確認と環境チェック**:
   - MCPサーバー `davinci-resolve`（macOS / Windows 対応環境時）または Python `DaVinciResolveScript`（`RESOLVE_SCRIPT_API` 環境変数経由）の接続状態を確認する。
   - DaVinci Resolve Studio（外部スクリプト制御対応版）が未起動または Free 版制限環境の場合は、Fusion スクリプトまたは FFmpeg / Python MoviePy / PIL 高精度コンポジットパイプラインと連携してタイムライン編集・テロップ合成・カラーLUT適用・エンコードを実行する。
2. **タイムライン構築・グレーディング・テロップ合成**:
   - 構成スクリプトを `02_Creative_Dept/davinci/drafts/` に作成する。
   - `02_Creative_Dept/blender/final_outputs/` で生成された3Dアニメーション連番PNG/MP4や、`02_Creative_Dept/illustrator/final_outputs/` で生成されたベクターロゴPNG/SVGをタイムライン素材として取り込む。
3. **キーフレーム・コンタクトシート抽出と `read_file` 視覚監査ループ**:
   - 書き出した動画（`.mp4` / `.mov`）から主要フレームのコンタクトシート画像（`.png`）を抽出し、`read_file` で目視監査してテロップ見切れ・色味・トランジションタイミングを検証する。
4. **中間成果物出力と最終納品**:
   - 完成した映像ファイル（`.mp4` / `.mov`）、プロジェクト（`.drp`）、キーフレーム確認シート（`.png`）、および制作仕様書 `content_[テーマ名].md` を `02_Creative_Dept/davinci/final_outputs/` に保存する。
   - 続けて `04_Delivery_Dept` を通じて `04_Delivery_Dept/outputs/davinci/` に最終成果物を格納し、`04_Delivery_Dept/outputs/INDEX.md` を更新する。
