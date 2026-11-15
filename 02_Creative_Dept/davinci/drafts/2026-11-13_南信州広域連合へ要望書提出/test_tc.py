import os
import sys

os.environ["RESOLVE_SCRIPT_API"] = r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting"
os.environ["RESOLVE_SCRIPT_LIB"] = r"C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll"
sys.path.append(r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules")

import DaVinciResolveScript as dvr_script

resolve = dvr_script.scriptapp("Resolve")
proj = resolve.GetProjectManager().GetCurrentProject()
tl = proj.GetCurrentTimeline()
start_frame = tl.GetStartFrame()
end_frame = tl.GetEndFrame()
print("start_frame:", start_frame, "end_frame:", end_frame)
print(" timeline frame rate:", tl.GetSetting("timelineFrameRate"), "dropFrame:", tl.GetSetting("timelineDropFrameTimecode"))

for off in [0, 15, 30, 300, 600, 900, 1200, 1500, 1800, 2100, 2400, 5099]:
    target = start_frame + off
    r = tl.SetCurrentTimecode(str(target))
    tc = tl.GetCurrentTimecode()
    print(f"off={off:4d} (target={target}) -> res={r}, tc={tc}")
