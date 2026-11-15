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
mp = proj.GetMediaPool()
root = mp.GetRootFolder()
clips = {c.GetName(): c for c in root.GetClipList()}

# Delete Temp_PB17_Inspect if exists
for i in range(proj.GetTimelineCount(), 0, -1):
    t = proj.GetTimelineByIndex(i)
    if t and t.GetName().startswith("Temp_"):
        mp.DeleteTimelines([t])

tl = mp.CreateEmptyTimeline("Temp_Audio_Test")
proj.SetCurrentTimeline(tl)

pb17 = clips["PB130017.MOV"]
mp3_1328 = clips["11月13日（13-28）南信州広域連合議会 第2回 全員協議会.mp3"]

res_v = mp.AppendToTimeline([{
    "mediaPoolItem": pb17,
    "startFrame": 0,
    "endFrame": 18434,
    "mediaType": 1,
    "trackIndex": 1,
    "recordFrame": 108000
}])
print("Video append:", res_v)

res_a = mp.AppendToTimeline([{
    "mediaPoolItem": mp3_1328,
    "startFrame": 1098,
    "endFrame": 1098 + 18434,
    "mediaType": 2,
    "trackIndex": 1,
    "recordFrame": 108000
}])
print("Audio append:", res_a)

v_items = tl.GetItemListInTrack("video", 1)
a_items = tl.GetItemListInTrack("audio", 1)
for it in v_items:
    print("V1 item:", it.GetName(), "Start:", it.GetStart(), "End:", it.GetEnd(), "Dur:", it.GetDuration(), "LeftOffset:", it.GetLeftOffset())
for it in a_items:
    print("A1 item:", it.GetName(), "Start:", it.GetStart(), "End:", it.GetEnd(), "Dur:", it.GetDuration(), "LeftOffset:", it.GetLeftOffset())
