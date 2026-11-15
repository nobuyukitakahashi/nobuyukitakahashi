import os
import sys
import numpy as np

os.environ["RESOLVE_SCRIPT_API"] = r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting"
os.environ["RESOLVE_SCRIPT_LIB"] = r"C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll"
sys.path.append(r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules")

import DaVinciResolveScript as dvr_script

draft_dir = r"g:\マイドライブ\git\nobuyukitakahashi\02_Creative_Dept\davinci\drafts\2026-11-13_南信州広域連合へ要望書提出"
frames_dir = os.path.join(draft_dir, "frames_raw")

resolve = dvr_script.scriptapp("Resolve")
proj = resolve.GetProjectManager().GetCurrentProject()
tl = proj.GetCurrentTimeline()
start_frame = tl.GetStartFrame() # 108000

# Sample Start: 0 to 450 step 15 (0.5s)
start_offsets = list(range(0, 465, 15))
# Sample End: 4650 to 5099 step 15 (0.5s)
end_offsets = list(range(4650, 5100, 15))
if 5099 not in end_offsets:
    end_offsets.append(5099)
# Sample Middle: 600 to 4500 step 300 (10s)
mid_offsets = list(range(600, 4501, 300))

all_offsets = sorted(list(set(start_offsets + mid_offsets + end_offsets)))
print(f"Exporting {len(all_offsets)} sample frames from DaVinci Resolve...")

for off in all_offsets:
    out_png = os.path.join(frames_dir, f"f_{off:04d}.png")
    if not os.path.exists(out_png):
        tl.SetCurrentTimecode(str(start_frame + off))
        proj.ExportCurrentFrameAsStill(out_png)

print("Done exporting frames!")
