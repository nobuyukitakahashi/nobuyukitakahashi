---
name: creative-dept
description: >-
  制作・編集部門（02_Creative_Dept）を単体稼働させ、01_Research_Dept/reports/ の調査レポートをもとに
  ドラフト執筆（drafts/）とセルフ校正を経て完成原稿（final_outputs/）を出力するスキル。
  記事執筆やリライトのみを実行したい場合、または /creative-dept コマンド実行時に使用する。
---

# 制作・編集部門（`02_Creative_Dept`）単体実行スキル

1. [`02_Creative_Dept/AGENTS.md`](../../../02_Creative_Dept/AGENTS.md) および [`.agents/rules/global-policy.md`](../../rules/global-policy.md) を読み込む。
2. 対象となる `01_Research_Dept/reports/report_[テーマ名].md` が存在することを確認する（存在しない場合は先に `/research-dept` の実行を提案または実行する）。
3. `define_subagent`（未定義の場合）および `invoke_subagent` で `creative-dept` サブエージェントを起動し、以下を実行させる：
   - レポートのファクト・出典・引き継ぎ事項の読み込み
   - 初稿 `02_Creative_Dept/drafts/draft_[テーマ名].md` の作成
   - セルフ校正（誤字脱字、論理構成、ハルシネーション有無、専門用語解説のチェック）
   - 完成版 `02_Creative_Dept/final_outputs/content_[テーマ名].md` の保存
4. 生成されたドラフトと完成版を検収し、ファイルリンク付きでユーザーに報告する。
