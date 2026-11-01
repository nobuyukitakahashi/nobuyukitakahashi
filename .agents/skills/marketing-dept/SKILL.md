---
name: marketing-dept
description: >-
  マーケティング部門（03_Marketing_Dept）を単体稼働させ、02_Creative_Dept/final_outputs/ の完成原稿から
  X（旧Twitter）用140字投稿・ビジネス向け長文投稿・ターゲット層へのアプローチアドバイスを作成し
  03_Marketing_Dept/promos/ に出力するスキル。PR文のみを作成・再作成したい場合や /marketing-dept 実行時に使用する。
---

# マーケティング部門（`03_Marketing_Dept`）単体実行スキル

1. [`03_Marketing_Dept/AGENTS.md`](../../../03_Marketing_Dept/AGENTS.md) および [`.agents/rules/global-policy.md`](../../rules/global-policy.md) を読み込む。
2. 対象となる `02_Creative_Dept/final_outputs/content_[テーマ名].md` が存在することを確認する。
3. `define_subagent`（未定義の場合）および `invoke_subagent` で `marketing-dept` サブエージェントを起動し、以下を実行させる：
   - 完成原稿のコアバリュー・フックの抽出
   - 指定フォーマット（X用140字以内・文字数カウント付、ビジネス向け400字程度、ターゲット層アプローチ提案）での `03_Marketing_Dept/promos/promo_[テーマ名].md` 作成
4. 生成されたPRテキストを検収し、ファイルリンク付きでユーザーに報告する。
