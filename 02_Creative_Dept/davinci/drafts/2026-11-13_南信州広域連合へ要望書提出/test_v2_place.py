import os
import sys

os.environ["RESOLVE_SCRIPT_API"] = r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting"
os.environ["RESOLVE_SCRIPT_LIB"] = r"C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll"
sys.path.append(r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules")

import DaVinciResolveScript as dvr_script

resolve = dvr_script.scriptapp("Resolve")
proj = resolve.GetProjectManager().GetCurrentProject()
mp = proj.GetMediaPool()
tl = proj.GetCurrentTimeline()
root = mp.GetRootFolder()

tf = [f for f in root.GetSubFolderList() if f.GetName() == "Telops_Alpha"][0]
c_aa = [c for c in tf.GetClipList() if c.GetName() == "telop_aa.png"][0]

# Test 1: Append with startFrame=0, endFrame=90, trackIndex=2, recordFrame=108000
r1 = mp.AppendToTimeline([{"mediaPoolItem": c_aa, "startFrame": 0, "endFrame": 90, "trackIndex": 2, "recordFrame": 108000}])
print("Test 1 (startFrame=0, endFrame=90):", r1)
for it in tl.GetItemListInTrack("video", 2):
    print("  V2 item:", it.GetName(), "start:", it.GetStart(), "end:", it.GetEnd(), "dur:", it.GetDuration())

# Test 2: Append without startFrame/endFrame at recordFrame=108200
r2 = mp.AppendToTimeline([{"mediaPoolItem": c_aa, "trackIndex": 2, "recordFrame": 108200}])
print("Test 2 (no start/end):", r2)
for it in tl.GetItemListInTrack("video", 2):
    print("  V2 item:", it.GetName(), "start:", it.GetStart(), "end:", it.GetEnd(), "dur:", it.GetDuration())
