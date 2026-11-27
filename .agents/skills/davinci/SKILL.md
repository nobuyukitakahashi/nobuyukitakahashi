---
name: davinci
description: >-
  DaVinci Resolve Studio 21.2（Python Scripting / MCP）とFFmpegによる映像編集・スタビライズ・カラーグレーディング・テロップ・整音・完パケ書き出しスキル。
  /davinci 指定時、または動画編集依頼時に使用。
---

# 🎬 DaVinci Resolve Studio 21.2 映像編集・グレーディング専任スキル (`/davinci`)

## 1. ディレクトリ規約（案件別サブフォルダ必須）
- 試作・スクリプト・解析フレーム：`02_Creative_Dept/davinci/drafts/<案件サブフォルダ>/`
- 中間成果物：`02_Creative_Dept/davinci/final_outputs/<案件サブフォルダ>/`
- 最終納品先：`04_Delivery_Dept/outputs/davinci/<案件サブフォルダ>/`（[`INDEX.md`](../../../04_Delivery_Dept/outputs/INDEX.md) の `4. DaVinci Resolve` を更新）

## 2. Python `DaVinciResolveScript` 接続初期化（Windows）
```python
import os, sys
os.environ["RESOLVE_SCRIPT_API"] = r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting"
os.environ["RESOLVE_SCRIPT_LIB"] = r"C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll"
sys.path.append(r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules")
import DaVinciResolveScript as dvr_script
resolve = dvr_script.scriptapp("Resolve")
```
- 未起動時は `C:\Program Files\Blackmagic Design\DaVinci Resolve\Resolve.exe` を起動して待機。
- `pm = resolve.GetProjectManager()` ➔ `CreateProject` / `LoadProject` 後、`proj.SetSetting("timelineResolutionWidth", ...)` 等で設定。

## 3. 実写編集・整音・同期・テロップ専門手順
- トリミング・セクション分割スタビライズ・区間別 `SetCDL`・`V2` 透過PNGテロップ（短尺連番／長尺議会ネームプレート）・5段DSP整音・無音動画×ICレコーダー相互相関同期の詳細は、着手前に必ず [`references/live-action-production-guide.md`](references/live-action-production-guide.md) を参照。

## 4. Deliver 書き出し ＆ 視覚監査 ＆ 納品
1. `resolve.OpenPage("deliver")` ➔ `proj.SetCurrentRenderFormatAndCodec("mp4", "H264_NVIDIA")`（または `"H264"`）➔ `SetRenderSettings(...)` ➔ `AddRenderJob()` ➔ `StartRendering(job_id)`。
2. 完了後、必ず `pm.SaveProject()` と `pm.ExportProject(proj.GetName(), drp_path, False)` で `.drp` を保存。
3. `ExportCurrentFrameAsStill` や書き出し MP4 抜粋から Before/After 比較ボード（`keyframes_audit_board.png`）を作成し `read_file` で目視監査、`qa-verifier`（`global-master-rules` §5）合格後に `04_Delivery_Dept/outputs/davinci/<案件サブフォルダ>/` へ納品し `INDEX.md` 更新。
