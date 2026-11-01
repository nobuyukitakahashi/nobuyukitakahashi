---
name: delivery-dept
description: >-
  納品・出力統合部門（04_Delivery_Dept）を稼働させ、各部門（01〜03）の中間成果物を回収し、
  ユーザーが指定したあらゆるファイル形式（Markdown, HTML, CSV, JSON, テキスト等）に変換・統合して
  唯一の固定出力フォルダ 04_Delivery_Dept/outputs/ に格納するスキル。
  出力形式の変換・再パッケージングを行いたい場合や /delivery-dept 実行時に使用する。
---

# 納品・出力統合部門（`04_Delivery_Dept`）実行スキル

1. [`04_Delivery_Dept/AGENTS.md`](../../../04_Delivery_Dept/AGENTS.md) および [`.agents/rules/global-policy.md`](../../rules/global-policy.md) を読み込む。
2. `define_subagent`（未定義の場合）および `invoke_subagent` で `delivery-dept` サブエージェントを起動し、以下を実行させる：
   - 上流の中間成果物（`01_Research_Dept/reports/`、`02_Creative_Dept/final_outputs/`、`03_Marketing_Dept/promos/`）の読み込み
   - 統合納品パッケージ `04_Delivery_Dept/outputs/output_[YYYYMMDD]_[テーマ名]_full.md` の生成
   - ユーザー指定フォーマット（HTML `.html`, CSV `.csv`, JSON `.json`, 単体 `.txt` 等）がある場合は `04_Delivery_Dept/outputs/output_[YYYYMMDD]_[テーマ名].[拡張子]` として同時生成
   - 納品台帳 `04_Delivery_Dept/outputs/INDEX.md` の更新
3. `04_Delivery_Dept/outputs/` 内の出力ファイルを検収し、ファイルリンク付きでユーザーに報告する。
