import os
import sys
import time

os.environ["RESOLVE_SCRIPT_API"] = r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting"
os.environ["RESOLVE_SCRIPT_LIB"] = r"C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll"
sys.path.append(r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules")

import DaVinciResolveScript as dvr_script

draft_dir = r"g:\マイドライブ\git\nobuyukitakahashi\02_Creative_Dept\davinci\drafts\2026-11-13_南信州広域連合へ要望書提出"

resolve = dvr_script.scriptapp("Resolve")
pm = resolve.GetProjectManager()
proj = pm.GetCurrentProject()

# Ensure Full-HD 1920x1080 29.97fps project settings
proj.SetSetting("timelineResolutionWidth", "1920")
proj.SetSetting("timelineResolutionHeight", "1080")
proj.SetSetting("timelineFrameRate", "29.97")

mp = proj.GetMediaPool()
root_folder = mp.GetRootFolder()
clips = root_folder.GetClipList()
target_clip = [c for c in clips if "PB130002" in c.GetName()][0]

# Delete Analyze_Full or existing Main_Edit_FullHD if needed, or create new timeline
tl_name = "2026-11-13_南信州広域連合へ要望書提出_FullHD"
for i in range(proj.GetTimelineCount(), 0, -1):
    tl_existing = proj.GetTimelineByIndex(i)
    if tl_existing and tl_existing.GetName() == tl_name:
        mp.DeleteTimelines([tl_existing])

new_tl = mp.CreateEmptyTimeline(tl_name)
proj.SetCurrentTimeline(new_tl)

in_frame = 215
out_frame = 5080

append_info = [{
    "mediaPoolItem": target_clip,
    "startFrame": in_frame,
    "endFrame": out_frame
}]
res_items = mp.AppendToTimeline(append_info)
print("AppendToTimeline result:", res_items)

tl_item = new_tl.GetItemListInTrack("video", 1)[0]
print("Timeline item name:", tl_item.GetName())
print("Timeline item duration:", tl_item.GetDuration(), "start:", tl_item.GetStart(), "end:", tl_item.GetEnd())
print("Timeline item leftOffset:", tl_item.GetLeftOffset(), "rightOffset:", tl_item.GetRightOffset())

# Export BEFORE frames at key moments from this timeline
# Timeline start frame is 108000 (01:00:00:00)
tl_start = new_tl.GetStartFrame()
# Key source frames: 215 (In), 300 (Bow 1), 1200 (Speech dark), 3600 (Handoff), 5000 (Final bow), 5080 (Out)
key_src_frames = [215, 300, 1200, 3600, 5000, 5080]

resolve.OpenPage("color")
time.sleep(0.5)

before_dir = os.path.join(draft_dir, "before_after")
os.makedirs(before_dir, exist_ok=True)

for sf in key_src_frames:
    tl_f = tl_start + (sf - in_frame)
    # Clamp last frame to tl_item.GetEnd() - 1
    if tl_f >= new_tl.GetEndFrame():
        tl_f = new_tl.GetEndFrame() - 1
    new_tl.SetCurrentTimecode(str(tl_f))
    time.sleep(0.15)
    out_p = os.path.join(before_dir, f"before_src_{sf:04d}.png")
    proj.ExportCurrentFrameAsStill(out_p)
    print(f"Exported BEFORE src={sf} (tl={tl_f}) -> {os.path.exists(out_p)}")

# Now run Stabilize()
resolve.OpenPage("edit")
time.sleep(0.3)
print("Running tl_item.Stabilize()...")
stab_res = tl_item.Stabilize()
print("Stabilize() result:", stab_res)

# Now apply CDL brightness/color grading on Color page
resolve.OpenPage("color")
time.sleep(0.3)

# Test CDL:
# Power = 0.68 (lifts shadows and midtones strongly without clipping 1.0 highlights)
# Slope = 1.08 1.07 1.04 (slight warmth + crisp white level)
# Offset = 0.012 0.010 0.006 (lifts deep blacks slightly so suits have detail)
# Saturation = 1.12 (natural skin tone and room color)
cdl_map = {
    "NodeIndex": "1",
    "Slope": "1.08 1.07 1.04",
    "Offset": "0.012 0.010 0.006",
    "Power": "0.68 0.68 0.70",
    "Saturation": "1.12"
}
cdl_res = tl_item.SetCDL(cdl_map)
print("SetCDL result:", cdl_res)

for sf in key_src_frames:
    tl_f = tl_start + (sf - in_frame)
    if tl_f >= new_tl.GetEndFrame():
        tl_f = new_tl.GetEndFrame() - 1
    new_tl.SetCurrentTimecode(str(tl_f))
    time.sleep(0.15)
    out_p = os.path.join(before_dir, f"after_src_{sf:04d}.png")
    proj.ExportCurrentFrameAsStill(out_p)
    print(f"Exported AFTER src={sf} (tl={tl_f}) -> {os.path.exists(out_p)}")
