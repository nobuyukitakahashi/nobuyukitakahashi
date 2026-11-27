---
name: delivery-dept
description: >-
  納品・出力統合部門（04_Delivery_Dept）を稼働させ、各部門（01〜03および06）の中間成果物を回収し、
  ユーザーが指定したあらゆるファイル形式に変換・統合して、11ジャンル別の固定出力フォルダ
  04_Delivery_Dept/outputs/<genre>/（主要5ジャンル＋拡張6ジャンル：premiere / aftereffects / moho / pano2vr / krpano / ptgui）に格納するスキル。
  出力形式の変換・再パッケージングを行いたい場合や /delivery-dept 実行時に使用する。
---

# 納品・出力統合部門（`04_Delivery_Dept`）実行スキル

1. [`04_Delivery_Dept/AGENTS.md`](../../../04_Delivery_Dept/AGENTS.md) および [`.agents/rules/global-policy.md`](../../rules/global-policy.md) を読み込む。
2. 案件の制作ジャンル `<genre>`（主要5ジャンル：`blender` / `illustrator` / `photoshop` / `davinci` / `writing`、拡張6ジャンル：`premiere` / `aftereffects` / `moho` / `pano2vr` / `krpano` / `ptgui`）を確認する。
3. `define_subagent`（未定義の場合）および `invoke_subagent` で `delivery-dept` サブエージェントを起動し、以下を実行させる：
   - 上流の中間成果物（`01_Research_Dept/reports/`、`02_Creative_Dept/<genre>/final_outputs/`、`03_Marketing_Dept/promos/`、および該当時は `06_Legal_Dept/reviews/`）の読み込み
   - 統合納品パッケージ `04_Delivery_Dept/outputs/<genre>/output_[YYYYMMDD]_[テーマ名]_full.md` の生成
   - 指定フォーマットファイル・バイナリ成果物（`.html`, `.blend`, `.glb`, `.ai`, `.pdf`, `.svg`, `.psd`, `.png`, `.jpg`, `.tiff`, `.mp4`, `.mov`, `.webm`, `.moho`, `.aep`, `.prproj`, `.pts` 等）の `04_Delivery_Dept/outputs/<genre>/` への格納
   - 納品台帳 `04_Delivery_Dept/outputs/INDEX.md` の該当ジャンルセクション更新（リンク形式：`<genre>/ファイル名`）
4. `04_Delivery_Dept/outputs/<genre>/` 内の出力ファイルおよび `INDEX.md` のリンク実在性を検収し、ファイルリンク付きでユーザーに報告する。
