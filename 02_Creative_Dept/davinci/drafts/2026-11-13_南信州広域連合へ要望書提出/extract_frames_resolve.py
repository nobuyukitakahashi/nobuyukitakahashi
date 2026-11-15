import os
import sys
import time

os.environ["RESOLVE_SCRIPT_API"] = r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting"
os.environ["RESOLVE_SCRIPT_LIB"] = r"C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll"
sys.path.append(r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules")

import DaVinciResolveScript as dvr_script

draft_dir = r"g:\マイドライブ\git\nobuyukitakahashi\02_Creative_Dept\davinci\drafts\2026-11-13_南信州広域連合へ要望書提出"
frames_dir = os.path.join(draft_dir, "frames_raw")
os.makedirs(frames_dir, exist_ok=True)

resolve = dvr_script.scriptapp("Resolve")
pm = resolve.GetProjectManager()
proj = pm.GetCurrentProject()

# Set project settings to 1920x1080 29.97fps
proj.SetSetting("timelineResolutionWidth", "1920")
proj.SetSetting("timelineResolutionHeight", "1080")
proj.SetSetting("timelineFrameRate", "29.97")

mp = proj.GetMediaPool()
root_folder = mp.GetRootFolder()
clips = root_folder.GetClipList()
target_clip = [c for c in clips if "PB130002" in c.GetName()][0]

# Check if temp timeline exists
tl_count = proj.GetTimelineCount()
temp_tl = None
for i in range(1, tl_count + 1):
    tl = proj.GetTimelineByIndex(i)
    if tl.GetName() == "Analyze_Full":
        temp_tl = tl
        break

if not temp_tl:
    temp_tl = mp.CreateTimelineFromClips("Analyze_Full", [target_clip])

proj.SetCurrentTimeline(temp_tl)
resolve.OpenPage("color")

start_frame = temp_tl.GetStartFrame()
end_frame = temp_tl.GetEndFrame()
print(f"Timeline Analyze_Full: start_frame={start_frame}, end_frame={end_frame}, total={end_frame - start_frame + 1}")

# Helper to convert frame offset (0..5099) to timecode or frame number
# Note: SetCurrentTimecode accepts frame number as string or TC string? Let's test!
print("Initial CurrentTimecode:", temp_tl.GetCurrentTimecode())

# Let's test setting current timecode by frame or TC
# Note: in Resolve API, SetCurrentTimecode can take timecode string. Let's check how start_frame maps to TC.
# Or does SetCurrentTimecode(str(start_frame + offset)) work? Let's test both!
res1 = temp_tl.SetCurrentTimecode(str(start_frame + 300))
print("SetCurrentTimecode(str(frame)):", res1, "-> now:", temp_tl.GetCurrentTimecode())

out_test = os.path.join(frames_dir, "test_300.png")
exp_res = proj.ExportCurrentFrameAsStill(out_test)
print("ExportCurrentFrameAsStill:", exp_res, os.path.exists(out_test))
