import os
import sys
import time

os.environ["RESOLVE_SCRIPT_API"] = r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting"
os.environ["RESOLVE_SCRIPT_LIB"] = r"C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll"
sys.path.append(r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules")

import DaVinciResolveScript as dvr_script

draft_dir = r"g:\マイドライブ\git\nobuyukitakahashi\02_Creative_Dept\davinci\drafts\2026-11-13_南信州広域連合へ要望書提出"
frames_dir = os.path.join(draft_dir, "frames_raw")

resolve = dvr_script.scriptapp("Resolve")
proj = resolve.GetProjectManager().GetCurrentProject()
tl = proj.GetCurrentTimeline()
start_frame = tl.GetStartFrame()

fine_start = list(range(150, 245, 5))
fine_end = list(range(5025, 5100, 3))
if 5099 not in fine_end:
    fine_end.append(5099)

for off in fine_start + fine_end:
    out_png = os.path.join(frames_dir, f"f_{off:04d}.png")
    if not os.path.exists(out_png):
        tl.SetCurrentTimecode(str(start_frame + off))
        time.sleep(0.08)
        proj.ExportCurrentFrameAsStill(out_png)

print("Exported fine start and end frames.")
