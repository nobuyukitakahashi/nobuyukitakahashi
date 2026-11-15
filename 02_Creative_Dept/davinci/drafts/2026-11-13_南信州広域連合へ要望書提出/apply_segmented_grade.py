import os
import sys
import time

os.environ["RESOLVE_SCRIPT_API"] = r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting"
os.environ["RESOLVE_SCRIPT_LIB"] = r"C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll"
sys.path.append(r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules")

import DaVinciResolveScript as dvr_script

draft_dir = r"g:\マイドライブ\git\nobuyukitakahashi\02_Creative_Dept\davinci\drafts\2026-11-13_南信州広域連合へ要望書提出"
ba_dir = os.path.join(draft_dir, "before_after")

resolve = dvr_script.scriptapp("Resolve")
pm = resolve.GetProjectManager()
proj = pm.GetCurrentProject()
mp = proj.GetMediaPool()
root_folder = mp.GetRootFolder()
target_clip = [c for c in root_folder.GetClipList() if "PB130002" in c.GetName()][0]

# Recreate timeline cleanly
tl_name = "2026-11-13_南信州広域連合へ要望書提出_FullHD"
for i in range(proj.GetTimelineCount(), 0, -1):
    tl_existing = proj.GetTimelineByIndex(i)
    if tl_existing and tl_existing.GetName() in [tl_name, "Analyze_Full"]:
        mp.DeleteTimelines([tl_existing])

new_tl = mp.CreateEmptyTimeline(tl_name)
proj.SetCurrentTimeline(new_tl)

segs = [
    {"mediaPoolItem": target_clip, "startFrame": 215, "endFrame": 485},
    {"mediaPoolItem": target_clip, "startFrame": 485, "endFrame": 810},
    {"mediaPoolItem": target_clip, "startFrame": 810, "endFrame": 1845},
    {"mediaPoolItem": target_clip, "startFrame": 1845, "endFrame": 5080},
]
items = mp.AppendToTimeline(segs)
v_items = new_tl.GetItemListInTrack("video", 1)
for idx, it in enumerate(v_items):
    print(f"Seg {idx+1}: start={it.GetStart()}, end={it.GetEnd()}, dur={it.GetDuration()}, leftOff={it.GetLeftOffset()}, rightOff={it.GetRightOffset()}")

# Stabilize stationary handheld segments (Seg 1, Seg 3, Seg 4)
# Note: Seg 2 (485..810) is an intentional camera walk across the room; stabilizing it locks against the walk and causes extreme border zoom.
resolve.OpenPage("edit")
time.sleep(0.3)
for idx in [0, 2, 3]:
    res = v_items[idx].Stabilize()
    print(f"Stabilize Seg {idx+1}: {res}")

# Apply tailored CDL to each segment on Color page
resolve.OpenPage("color")
time.sleep(0.3)

# Seg 1 (215..485: Opening bow, indoor wall lighting, Before Y~75)
v_items[0].SetCDL({
    "NodeIndex": "1",
    "Slope": "1.08 1.07 1.04",
    "Offset": "0.012 0.010 0.006",
    "Power": "0.68 0.68 0.70",
    "Saturation": "1.12"
})

# Seg 2 (485..810: Repositioning transition)
v_items[1].SetCDL({
    "NodeIndex": "1",
    "Slope": "1.08 1.07 1.04",
    "Offset": "0.012 0.010 0.006",
    "Power": "0.66 0.66 0.68",
    "Saturation": "1.12"
})

# Seg 3 (810..1845: Petition reading first half, dark backlit auto-exposure Before Y~67)
v_items[2].SetCDL({
    "NodeIndex": "1",
    "Slope": "1.12 1.11 1.07",
    "Offset": "0.018 0.016 0.010",
    "Power": "0.56 0.56 0.58",
    "Saturation": "1.14"
})

# Seg 4 (1845..5080: Petition reading second half, handoff, closing bow, Before Y~111)
v_items[3].SetCDL({
    "NodeIndex": "1",
    "Slope": "1.03 1.02 1.00",
    "Offset": "0.010 0.008 0.004",
    "Power": "0.74 0.74 0.76",
    "Saturation": "1.10"
})

tl_start = new_tl.GetStartFrame()
key_src_frames = [215, 300, 1200, 3600, 5000, 5080]
for sf in key_src_frames:
    tl_f = tl_start + (sf - 215)
    if tl_f >= new_tl.GetEndFrame():
        tl_f = new_tl.GetEndFrame() - 1
    new_tl.SetCurrentTimecode(str(tl_f))
    time.sleep(0.18)
    out_p = os.path.join(ba_dir, f"after_src_{sf:04d}.png")
    if os.path.exists(out_p):
        os.remove(out_p)
    proj.ExportCurrentFrameAsStill(out_p)
    print(f"Exported AFTER src={sf} (tl={tl_f}) -> {os.path.exists(out_p)}")
