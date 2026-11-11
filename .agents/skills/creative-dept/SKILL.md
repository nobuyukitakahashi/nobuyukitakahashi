---
name: creative-dept
description: >-
  制作・編集部門（02_Creative_Dept）を4大ジャンル（blender / illustrator / davinci / writing）別に稼働させ、
  01_Research_Dept/reports/ の調査レポートや制作指示をもとに 02_Creative_Dept/<genre>/{drafts,final_outputs}/ で
  制作を実行した後、04_Delivery_Dept を通じてジャンル別固定出力フォルダ 04_Delivery_Dept/outputs/<genre>/ に最終成果物を納品するスキル。
  /creative-dept コマンド実行時、または制作部門の単体稼働時に使用する。
---

# 制作・編集・3D・DTP・映像部門（`02_Creative_Dept`）実行スキル

1. **ジャンル選択ルーティング（未指定時は `ask_question`）**:
   - 対象ジャンル `<genre>`（`blender` / `illustrator` / `davinci` / `writing`）が明示されていない場合は、作業開始前に `ask_question` ツールで以下4択を提示してユーザーに選択させる：
     1. `Blender（3Dモデリング・CG・3Dアニメ）` ➔ `<genre> = blender`（[`.agents/skills/blender/SKILL.md`](../blender/SKILL.md)）
     2. `Illustrator（ベクターロゴ・DTP・印刷データ）` ➔ `<genre> = illustrator`（[`.agents/skills/illustrator/SKILL.md`](../illustrator/SKILL.md)）
     3. `DaVinci Resolve（動画編集・グレーディング・テロップ）` ➔ `<genre> = davinci`（[`.agents/skills/davinci/SKILL.md`](../davinci/SKILL.md)）
     4. `Writing / Document（記事執筆・企画書・Web HTML）` ➔ `<genre> = writing`（[`.agents/skills/writing/SKILL.md`](../writing/SKILL.md)）
2. [`02_Creative_Dept/AGENTS.md`](../../../02_Creative_Dept/AGENTS.md) および [`.agents/rules/global-policy.md`](../../rules/global-policy.md) を読み込む。
3. `define_subagent`（**`EnableWriteTools: true`, `EnableMCPTools: true`, `EnableSubagentTools: false`**）および `invoke_subagent` で `creative-dept` サブエージェントを起動し、選択された `<genre>` のサブフォルダ（`02_Creative_Dept/<genre>/drafts/` および `02_Creative_Dept/<genre>/final_outputs/`）で制作を実行させる。
4. **ジャンル別固定出力ルールの適用**: 単体実行時であっても、続けて `delivery-dept` サブエージェントを起動し、ジャンル別固定フォルダ `04_Delivery_Dept/outputs/<genre>/` に最終成果物を格納・`04_Delivery_Dept/outputs/INDEX.md` を更新する。
