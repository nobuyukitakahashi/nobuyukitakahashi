import os
import sys

RESOLVE_SCRIPT_API = r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting"
RESOLVE_SCRIPT_LIB = r"C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll"
os.environ["RESOLVE_SCRIPT_API"] = RESOLVE_SCRIPT_API
os.environ["RESOLVE_SCRIPT_LIB"] = RESOLVE_SCRIPT_LIB
sys.path.append(os.path.join(RESOLVE_SCRIPT_API, "Modules"))

import DaVinciResolveScript as dvr_script

resolve = dvr_script.scriptapp("Resolve")
pm = resolve.GetProjectManager()
proj = pm.GetCurrentProject()
tl = proj.GetCurrentTimeline()
print("Current TL:", tl.GetName(), "Start TC:", tl.GetStartTimecode(), "Start Frame:", tl.GetStartFrame())

# Test setting timecode formats
for tc_try in ["01:00:30:00", "01:00:30;00", str(tl.GetStartFrame() + 900)]:
    ok = tl.SetCurrentTimecode(tc_try)
    print(f"Try {tc_try!r} -> ok={ok}, CurrentTC={tl.GetCurrentTimecode()}")
