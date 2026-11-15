import os
import sys

RESOLVE_SCRIPT_API = r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting"
RESOLVE_SCRIPT_LIB = r"C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll"
os.environ["RESOLVE_SCRIPT_API"] = RESOLVE_SCRIPT_API
os.environ["RESOLVE_SCRIPT_LIB"] = RESOLVE_SCRIPT_LIB
sys.path.append(os.path.join(RESOLVE_SCRIPT_API, "Modules"))

import DaVinciResolveScript as dvr_script

draft_dir = r"g:\マイドライブ\git\nobuyukitakahashi\02_Creative_Dept\davinci\drafts\2026-11-13_南信州広域連合議会_全員協議会"
frames_dir = os.path.join(draft_dir, "pb17_sync_frames")

resolve = dvr_script.scriptapp("Resolve")
pm = resolve.GetProjectManager()
proj = pm.GetCurrentProject()
tl = proj.GetCurrentTimeline()
resolve.OpenPage("color")

fps = 29.97
start_tc_frame = tl.GetStartFrame()

# Export 1s resolution frames for 25s..60s as well
for sec in range(25, 61):
    out_png = os.path.join(frames_dir, f"pb17_s{sec:04d}.png")
    if not os.path.exists(out_png):
        f_num = start_tc_frame + int(round(sec * fps))
        tl.SetCurrentTimecode(str(f_num))
        proj.ExportCurrentFrameAsStill(out_png)

print("Done exporting 1s frames for 25..60s")
