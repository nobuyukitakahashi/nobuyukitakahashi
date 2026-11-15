import os
import sys
import json
import time
import shutil
import zlib
import struct

os.environ["RESOLVE_SCRIPT_API"] = r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting"
os.environ["RESOLVE_SCRIPT_LIB"] = r"C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll"
sys.path.append(r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules")

import DaVinciResolveScript as dvr_script

draft_dir = r"g:\マイドライブ\git\nobuyukitakahashi\02_Creative_Dept\davinci\drafts\2026-11-13_南信州広域連合へ要望書提出"
final_dir = r"g:\マイドライブ\git\nobuyukitakahashi\02_Creative_Dept\davinci\final_outputs\2026-11-13_南信州広域連合へ要望書提出"
h_dir = r"H:\2026-11-13_南信州広域連合_連合長へ_要望書提出_録音一式"
alpha_dir = os.path.join(draft_dir, "telops_alpha")

# Create a 100% transparent 1920x1080 RGBA PNG (telop_blank.png) using pure Python zlib/struct
def create_blank_png(path, w=1920, h=1080):
    def chunk(ctype, data):
        c = ctype + data
        return struct.pack(">I", len(data)) + c + struct.pack(">I", zlib.crc32(c) & 0xffffffff)
    ihdr = struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0)
    raw_row = b"\x00" + (b"\x00\x00\x00\x00" * w)
    compressed = zlib.compress(raw_row * h, 1)
    with open(path, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n")
        f.write(chunk(b"IHDR", ihdr))
        f.write(chunk(b"IDAT", compressed))
        f.write(chunk(b"IEND", b""))

blank_png_path = os.path.join(alpha_dir, "telop_zz_blank.png")
create_blank_png(blank_png_path)

manifest_path = os.path.join(draft_dir, "subtitles_manifest.json")
with open(manifest_path, "r", encoding="utf-8") as f:
    subs = json.load(f)

resolve = dvr_script.scriptapp("Resolve")
pm = resolve.GetProjectManager()
proj = pm.GetCurrentProject()
mp = proj.GetMediaPool()
root_folder = mp.GetRootFolder()
mp.SetCurrentFolder(root_folder)

target_clip = [c for c in root_folder.GetClipList() if "PB130002.MOV" in c.GetName()][0]

# Clean up old subfolders and create Telops_And_Audio
for sf in list(root_folder.GetSubFolderList()):
    if sf.GetName() in ["Telops_And_Audio", "Telops_Alpha"]:
        mp.DeleteFolders([sf])

assets_folder = mp.AddSubFolder(root_folder, "Telops_And_Audio")
mp.SetCurrentFolder(assets_folder)

wav_path = os.path.join(draft_dir, "enhanced_audio_48k.wav")
srt_path = os.path.join(draft_dir, "PB130002_編集済_FullHD.srt")
alpha_paths = [item["alpha_png"] for item in subs] + [blank_png_path]

imp = mp.ImportMedia([wav_path, srt_path] + alpha_paths)
print("Imported assets count:", len(imp))

clip_by_name = {c.GetName(): c for c in assets_folder.GetClipList()}
audio_clip = clip_by_name["enhanced_audio_48k.wav"]
blank_clip = clip_by_name["telop_zz_blank.png"]

mp.SetCurrentFolder(root_folder)

# Recreate timeline cleanly
tl_name = "2026-11-13_南信州広域連合へ要望書提出_FullHD"
for i in range(proj.GetTimelineCount(), 0, -1):
    tl_existing = proj.GetTimelineByIndex(i)
    if tl_existing and tl_existing.GetName() == tl_name:
        mp.DeleteTimelines([tl_existing])

new_tl = mp.CreateEmptyTimeline(tl_name)
proj.SetCurrentTimeline(new_tl)
resolve.OpenPage("edit")
time.sleep(0.3)

# 1. Append V1 video segments
segs_v1 = [
    {"mediaPoolItem": target_clip, "startFrame": 215, "endFrame": 485, "mediaType": 1, "trackIndex": 1},
    {"mediaPoolItem": target_clip, "startFrame": 485, "endFrame": 810, "mediaType": 1, "trackIndex": 1},
    {"mediaPoolItem": target_clip, "startFrame": 810, "endFrame": 1845, "mediaType": 1, "trackIndex": 1},
    {"mediaPoolItem": target_clip, "startFrame": 1845, "endFrame": 5080, "mediaType": 1, "trackIndex": 1},
]
mp.AppendToTimeline(segs_v1)

# 2. Append A1 enhanced stereo audio
tl_start = new_tl.GetStartFrame() # 108000
mp.AppendToTimeline([{
    "mediaPoolItem": audio_clip,
    "startFrame": 0,
    "endFrame": 4865,
    "mediaType": 2,
    "trackIndex": 1,
    "recordFrame": tl_start
}])

# 3. Add V2 track and place telops + blank cutoffs at exact frames
if new_tl.GetTrackCount("video") < 2:
    new_tl.AddTrack("video")

for i, item in enumerate(subs):
    t_clip = clip_by_name[item["alpha_name"]]
    s_f = tl_start + int(item["s_frame"])
    e_f = tl_start + int(item["e_frame"])
    mp.AppendToTimeline([{
        "mediaPoolItem": t_clip,
        "trackIndex": 2,
        "recordFrame": s_f
    }])
    # Check if next subtitle starts before s_f + 150; if there's a gap before next subtitle, place blank_clip at e_f
    next_s_f = (tl_start + int(subs[i+1]["s_frame"])) if (i + 1 < len(subs)) else (tl_start + 4865)
    if e_f < next_s_f:
        mp.AppendToTimeline([{
            "mediaPoolItem": blank_clip,
            "trackIndex": 2,
            "recordFrame": e_f
        }])

v2_items = new_tl.GetItemListInTrack("video", 2)
print("Total V2 items (telops + blank cutoffs):", len(v2_items))
for it in v2_items[:6]:
    print(f"  V2: {it.GetName()} [{it.GetStart()}..{it.GetEnd()}] dur={it.GetDuration()}")

# 4. Run Stabilize() on V1 stationary handheld segments (Seg 1, Seg 3, Seg 4)
v1_track_items = new_tl.GetItemListInTrack("video", 1)
for idx in [0, 2, 3]:
    res = v1_track_items[idx].Stabilize()
    print(f"Stabilize V1 Seg {idx+1}: {res}")

# 5. Apply ASC CDL brightness/color grading on V1 segments
resolve.OpenPage("color")
time.sleep(0.3)

v1_track_items[0].SetCDL({"NodeIndex": "1", "Slope": "1.08 1.07 1.04", "Offset": "0.012 0.010 0.006", "Power": "0.68 0.68 0.70", "Saturation": "1.12"})
v1_track_items[1].SetCDL({"NodeIndex": "1", "Slope": "1.08 1.07 1.04", "Offset": "0.012 0.010 0.006", "Power": "0.66 0.66 0.68", "Saturation": "1.12"})
v1_track_items[2].SetCDL({"NodeIndex": "1", "Slope": "1.12 1.11 1.07", "Offset": "0.018 0.016 0.010", "Power": "0.56 0.56 0.58", "Saturation": "1.14"})
v1_track_items[3].SetCDL({"NodeIndex": "1", "Slope": "1.03 1.02 1.00", "Offset": "0.010 0.008 0.004", "Power": "0.74 0.74 0.76", "Saturation": "1.10"})

# 6. Export 6 sample frames with telops for visual audit
telop_audit_dir = os.path.join(draft_dir, "telop_audit_frames")
os.makedirs(telop_audit_dir, exist_ok=True)
sample_secs = [1.5, 8.0, 53.0, 99.0, 128.0, 155.5]
for i, sec in enumerate(sample_secs):
    tl_f = tl_start + int(round(sec * 29.97))
    new_tl.SetCurrentTimecode(str(tl_f))
    time.sleep(0.18)
    out_p = os.path.join(telop_audit_dir, f"telop_check_{i+1}_{int(sec)}s.png")
    if os.path.exists(out_p):
        os.remove(out_p)
    proj.ExportCurrentFrameAsStill(out_p)
    print(f"Exported telop audit frame t={sec}s -> {os.path.exists(out_p)}")

# 7. Render Full-HD MP4 (with burned-in V2 telops and enhanced A1 audio)
resolve.OpenPage("deliver")
time.sleep(0.4)

mp4_codecs = proj.GetRenderCodecs("mp4")
codec_val = "H264_NVIDIA" if "H264_NVIDIA" in mp4_codecs.values() else ("H264" if "H264" in mp4_codecs.values() else list(mp4_codecs.values())[0])
proj.SetCurrentRenderFormatAndCodec("mp4", codec_val)

render_settings = {
    "SelectAllFrames": True,
    "TargetDir": final_dir,
    "CustomName": "PB130002_編集済_FullHD",
    "FormatWidth": 1920,
    "FormatHeight": 1080,
    "FrameRate": 29.97,
    "ExportVideo": True,
    "ExportAudio": True,
}
proj.SetRenderSettings(render_settings)
proj.DeleteAllRenderJobs()
job_id = proj.AddRenderJob()
proj.StartRendering(job_id)
while proj.IsRenderingInProgress():
    time.sleep(2.0)

print("Render Job Status:", proj.GetRenderJobStatus(job_id))

rendered_mp4 = os.path.join(final_dir, "PB130002_編集済_FullHD.mp4")
telop_named_mp4 = os.path.join(final_dir, "PB130002_編集済_テロップ付_FullHD.mp4")
shutil.copy2(rendered_mp4, telop_named_mp4)
shutil.copy2(rendered_mp4, os.path.join(h_dir, "PB130002_編集済_FullHD.mp4"))
shutil.copy2(rendered_mp4, os.path.join(h_dir, "PB130002_編集済_テロップ付_FullHD.mp4"))
shutil.copy2(wav_path, os.path.join(final_dir, "PB130002_編集済_音声ノイズ除去_音量調整済.wav"))

resolve.OpenPage("edit")
pm.SaveProject()
drp_path = os.path.join(final_dir, "2026-11-13 南信州広域連合へ要望書提出.drp")
if os.path.exists(drp_path):
    os.remove(drp_path)
pm.ExportProject(proj.GetName(), drp_path, False)
print("All exports completed successfully!")
