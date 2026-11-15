import os
import sys
import json
import numpy as np

os.environ["RESOLVE_SCRIPT_API"] = r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting"
os.environ["RESOLVE_SCRIPT_LIB"] = r"C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll"
sys.path.append(r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules")
import DaVinciResolveScript as dvr

draft_dir = r"g:\マイドライブ\git\nobuyukitakahashi\02_Creative_Dept\davinci\drafts\2026-11-13_南信州広域連合議会_全員協議会"
final_dir = r"g:\マイドライブ\git\nobuyukitakahashi\02_Creative_Dept\davinci\final_outputs\2026-11-13_南信州広域連合議会_全員協議会"
os.makedirs(final_dir, exist_ok=True)

with open(os.path.join(draft_dir, "council_telops_meta.json"), "r", encoding="utf-8") as f:
    cards_meta = json.load(f)

resolve = dvr.scriptapp("Resolve")
pm = resolve.GetProjectManager()
proj = pm.GetCurrentProject()
print("Connected to project:", proj.GetName())

mp = proj.GetMediaPool()
root_folder = mp.GetRootFolder()

# Create or clear 04_Speaker_Telops folder in MediaPool
telop_folder = None
for sub in root_folder.GetSubFolderList():
    if sub.GetName() == "04_Speaker_Telops":
        telop_folder = sub
        break
if telop_folder is None:
    telop_folder = mp.AddSubFolder(root_folder, "04_Speaker_Telops")
mp.SetCurrentFolder(telop_folder)
existing_clips = telop_folder.GetClipList()
if existing_clips:
    mp.DeleteClips(existing_clips)

# Import all 78 PNGs
png_paths = [c["path"] for c in cards_meta]
imported = mp.ImportMedia(png_paths)
print(f"Imported {len(imported)} still clips into 04_Speaker_Telops (expected {len(png_paths)})")

clip_by_fname = {}
for c in telop_folder.GetClipList():
    clip_by_fname[c.GetClipProperty("File Name")] = c

FPS = 29.97
BASE_FRAME = 108000

def build_append_list(video_key, max_frames):
    segs = [c for c in cards_meta if c["video"] == video_key]
    append_list = []
    prev_end_f = BASE_FRAME
    for i, seg in enumerate(segs):
        clip = clip_by_fname[seg["filename"]]
        f_s = BASE_FRAME + int(round(seg["start_s"] * FPS))
        f_e = BASE_FRAME + int(round(seg["end_s"] * FPS))
        if f_s < prev_end_f:
            f_s = prev_end_f
        if i + 1 < len(segs):
            next_s = BASE_FRAME + int(round(segs[i+1]["start_s"] * FPS))
            if f_e > next_s:
                f_e = next_s
        if f_e > BASE_FRAME + max_frames:
            f_e = BASE_FRAME + max_frames
        dur = f_e - f_s
        if dur < 150:
            f_e = min(BASE_FRAME + max_frames, f_s + 150)
            dur = f_e - f_s
        # Tile 150-frame blocks across [f_s, f_e]
        r = f_s
        while r + 150 < f_e:
            append_list.append({
                "mediaPoolItem": clip,
                "startFrame": 0,
                "endFrame": 149,
                "trackIndex": 2,
                "recordFrame": r
            })
            r += 150
        # Final block ending at f_e
        last_r = max(f_s, f_e - 150)
        append_list.append({
            "mediaPoolItem": clip,
            "startFrame": 0,
            "endFrame": 149,
            "trackIndex": 2,
            "recordFrame": last_r
        })
        prev_end_f = last_r + 150
    return append_list

CDL_BRIGHT = {
    "NodeIndex": "1",
    "Slope": "1.38 1.36 1.32",
    "Offset": "0.04 0.04 0.05",
    "Power": "0.65 0.65 0.65",
    "Saturation": "1.14"
}

CDL_NEUTRAL = {
    "NodeIndex": "1",
    "Slope": "1.0 1.0 1.0",
    "Offset": "0.0 0.0 0.0",
    "Power": "1.0 1.0 1.0",
    "Saturation": "1.0"
}

# 1. Process Timeline 1 (PB130017)
tl1 = proj.GetTimelineByIndex(1)
proj.SetCurrentTimeline(tl1)
while tl1.GetTrackCount("video") < 2:
    tl1.AddTrack("video")
v2_items1 = tl1.GetItemListInTrack("video", 2)
if v2_items1:
    tl1.DeleteClips(v2_items1, False)

# Export Before still on PB130017 (at 01:04:30:00 = Mayor Sato greeting)
v1_item1 = tl1.GetItemListInTrack("video", 1)[0]
v1_item1.SetCDL(CDL_NEUTRAL)
tl1.SetCurrentTimecode("01:04:30:00")
pb17_before_path = os.path.join(draft_dir, "audit_pb17_before.png")
proj.ExportCurrentFrameAsStill(pb17_before_path)

# Apply CDL + V2 Telops on Timeline 1
v1_item1.SetCDL(CDL_BRIGHT)
list_pb17 = build_append_list("pb17", 18435)
res1 = mp.AppendToTimeline(list_pb17)
print(f"Timeline 1 ({tl1.GetName()}): placed {len(res1)} still blocks on V2")

tl1.SetCurrentTimecode("01:04:30:00")
pb17_after_sato = os.path.join(draft_dir, "audit_pb17_after_sato.png")
proj.ExportCurrentFrameAsStill(pb17_after_sato)

tl1.SetCurrentTimecode("01:02:00:00")
pb17_after_takemura = os.path.join(draft_dir, "audit_pb17_after_takemura.png")
proj.ExportCurrentFrameAsStill(pb17_after_takemura)

tl1.SetCurrentTimecode("01:07:30:00")
pb17_after_takada = os.path.join(draft_dir, "audit_pb17_after_takada.png")
proj.ExportCurrentFrameAsStill(pb17_after_takada)

# 2. Process Timeline 2 (PB130019 full MP3 sync)
tl2 = proj.GetTimelineByIndex(2)
proj.SetCurrentTimeline(tl2)
while tl2.GetTrackCount("video") < 2:
    tl2.AddTrack("video")
v2_items2 = tl2.GetItemListInTrack("video", 2)
if v2_items2:
    tl2.DeleteClips(v2_items2, False)

v1_item2 = tl2.GetItemListInTrack("video", 1)[0]
v1_item2.SetCDL(CDL_NEUTRAL)
tl2.SetCurrentTimecode("01:27:15:00")
pb19_before_path = os.path.join(draft_dir, "audit_pb19_before.png")
proj.ExportCurrentFrameAsStill(pb19_before_path)

v1_item2.SetCDL(CDL_BRIGHT)
list_pb19 = build_append_list("pb19", 138915)
res2 = mp.AppendToTimeline(list_pb19)
print(f"Timeline 2 ({tl2.GetName()}): placed {len(res2)} still blocks on V2")

tl2.SetCurrentTimecode("01:27:15:00")
pb19_after_kobayashi = os.path.join(draft_dir, "audit_pb19_after_kobayashi.png")
proj.ExportCurrentFrameAsStill(pb19_after_kobayashi)

tl2.SetCurrentTimecode("01:15:10:00")
pb19_after_goto = os.path.join(draft_dir, "audit_pb19_after_goto.png")
proj.ExportCurrentFrameAsStill(pb19_after_goto)

tl2.SetCurrentTimecode("01:36:50:00")
pb19_after_sekijima = os.path.join(draft_dir, "audit_pb19_after_sekijima.png")
proj.ExportCurrentFrameAsStill(pb19_after_sekijima)

tl2.SetCurrentTimecode("02:00:30:00")
pb19_after_ichinose = os.path.join(draft_dir, "audit_pb19_after_ichinose.png")
proj.ExportCurrentFrameAsStill(pb19_after_ichinose)

# 3. Also apply CDL + V2 Telops to Timeline 3 (Hybrid audio timeline)
tl3 = proj.GetTimelineByIndex(3)
proj.SetCurrentTimeline(tl3)
while tl3.GetTrackCount("video") < 2:
    tl3.AddTrack("video")
v2_items3 = tl3.GetItemListInTrack("video", 2)
if v2_items3:
    tl3.DeleteClips(v2_items3, False)
for it in tl3.GetItemListInTrack("video", 1):
    it.SetCDL(CDL_BRIGHT)
mp.AppendToTimeline(list_pb19)
print(f"Timeline 3 ({tl3.GetName()}): updated CDL and V2 telops")

print("Exported all verification stills successfully.")
