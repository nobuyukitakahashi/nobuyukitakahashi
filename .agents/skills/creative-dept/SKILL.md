---
name: creative-dept
description: >-
  制作部門（02_Creative_Dept）を11大ジャンル別に稼働させ、中間制作から 04_Delivery_Dept 納品まで実行するスキル。
  /creative-dept 実行時、または制作部門の単体稼働時に使用。
---

# 制作部門（`02_Creative_Dept`）実行スキル (`/creative-dept`)

1. **ジャンル確定**: 11ジャンル（主要5：`blender` / `illustrator` / `photoshop` / `davinci` / `writing`、拡張6：`premiere` / `aftereffects` / `moho` / `pano2vr` / `krpano` / `ptgui`）が未指定なら `ask_question` で主要5択を提示。
2. [`02_Creative_Dept/AGENTS.md`](../../../02_Creative_Dept/AGENTS.md)、対象ジャンルの `.agents/skills/<genre>/SKILL.md`、および [`.agents/rules/global-policy.md`](../../rules/global-policy.md) を読み込む。
3. `creative-dept`（`EnableWriteTools: true, EnableMCPTools: true`）を起動し、`02_Creative_Dept/<genre>/{drafts,final_outputs}/<案件サブフォルダ>/` で制作を実行。
4. `qa-verifier`（`global-master-rules` §5）で検収後、`delivery-dept` により `04_Delivery_Dept/outputs/<genre>/<案件サブフォルダ>/` へ格納・`INDEX.md` 更新を行う。
