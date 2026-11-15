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
os.makedirs(frames_dir, exist_ok=True)

resolve = dvr_script.scriptapp("Resolve")
pm = resolve.GetProjectManager()
proj = pm.GetCurrentProject()
mp = proj.GetMediaPool()
root = mp.GetRootFolder()

clips = {c.GetName(): c for c in root.GetClipList()}
pb17 = clips["PB130017.MOV"]

# Create temporary timeline for PB130017 frame inspection
tl_name = "Temp_PB17_Inspect"
for i in range(1, proj.GetTimelineCount() + 1):
    t = proj.GetTimelineByIndex(i)
    if t and t.GetName() == tl_name:
        mp.DeleteTimelines([t])
        break

tl = mp.CreateEmptyTimeline(tl_name)
proj.SetCurrentTimeline(tl)
mp.AppendToTimeline([pb17])

resolve.OpenPage("color")
fps = 29.97
start_tc_frame = tl.GetStartFrame()

# Grab frames at key intervals:
# 1) 0s to 65s every 2.0s (to see opening, bows, Chair standing)
# 2) 220s to 240s every 1.0s (to see Chair -> Union Head Sato transition)
# 3) 355s to 390s every 1.0s (to see Union Head Sato -> Staff transition)
sample_secs = (
    list(range(0, 66, 2)) +
    list(range(220, 241, 1)) +
    list(range(355, 391, 1))
)

for sec in sample_secs:
    f_num = start_tc_frame + int(round(sec * fps))
    tl.SetCurrentTimecode(str(f_num))
    out_png = os.path.join(frames_dir, f"pb17_s{sec:04d}.png")
    proj.ExportCurrentFrameAsStill(out_png)

print(f"Exported {len(sample_secs)} frames from PB130017.MOV")

# Also copy first 7.5 MB of MP3_1328 (~450s at 128kbps) to draft_dir for audio listening
mp3_1328_path = r"H:\2026-11-13_南信州広域連合_連合長へ_要望書提出_録音一式\11月13日（13-28）南信州広域連合議会 第2回 全員協議会\11月13日（13-28）南信州広域連合議会 第2回 全員協議会.mp3"
with open(mp3_1328_path, "rb") as f_in:
    chunk = f_in.read(7500000)
with open(os.path.join(draft_dir, "mp3_1328_first450s.mp3"), "wb") as f_out:
    f_out.write(chunk)
print("Saved mp3_1328_first450s.mp3")
