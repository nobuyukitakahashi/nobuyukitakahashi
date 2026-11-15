import os
import sys
import json
import time
import shutil

os.environ["RESOLVE_SCRIPT_API"] = r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting"
os.environ["RESOLVE_SCRIPT_LIB"] = r"C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll"
sys.path.append(r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules")

import DaVinciResolveScript as dvr_script

draft_dir = r"g:\マイドライブ\git\nobuyukitakahashi\02_Creative_Dept\davinci\drafts\2026-11-13_南信州広域連合へ要望書提出"
final_dir = r"g:\マイドライブ\git\nobuyukitakahashi\02_Creative_Dept\davinci\final_outputs\2026-11-13_南信州広域連合へ要望書提出"
h_dir = r"H:\2026-11-13_南信州広域連合_連合長へ_要望書提出_録音一式"
alpha_dir = os.path.join(draft_dir, "telops_alpha")

seq_dir = r"C:\Users\nobuy\.gemini\antigravity\brain\a50e7947-c634-4e5b-a3d8-d2ec20749ea6\scratch\telop_seq"
if os.path.exists(seq_dir):
    shutil.rmtree(seq_dir)
os.makedirs(seq_dir, exist_ok=True)

manifest_path = os.path.join(draft_dir, "subtitles_manifest.json")
with open(manifest_path, "r", encoding="utf-8") as f:
    subs = json.load(f)

# Copy the 36 source PNGs (35 telops + 1 blank) to scratch on C: drive so os.link works on same NTFS volume
src_local_dir = r"C:\Users\nobuy\.gemini\antigravity\brain\a50e7947-c634-4e5b-a3d8-d2ec20749ea6\scratch\telop_sources"
if os.path.exists(src_local_dir):
    shutil.rmtree(src_local_dir)
os.makedirs(src_local_dir, exist_ok=True)

local_blanks = []
for b_i in range(8):
    lb = os.path.join(src_local_dir, f"blank_{b_i}.png")
    shutil.copy2(os.path.join(alpha_dir, "telop_zz_blank.png"), lb)
    local_blanks.append(lb)

frame_map = [local_blanks[f_idx // 700] for f_idx in range(4865)]
for item in subs:
    local_p = os.path.join(src_local_dir, f"sub_{item['id']:03d}.png")
    shutil.copy2(item["alpha_png"], local_p)
    s_f = max(0, int(item["s_frame"]))
    e_f = min(4865, int(item["e_frame"]))
    for f_idx in range(s_f, e_f):
        frame_map[f_idx] = local_p

t0 = time.time()
for f_idx in range(4865):
    dst_frame = os.path.join(seq_dir, f"telop_{f_idx:04d}.png")
    os.link(frame_map[f_idx], dst_frame)
print(f"Created 4865 NTFS hardlinks in {time.time() - t0:.2f}s")

resolve = dvr_script.scriptapp("Resolve")
pm = resolve.GetProjectManager()
proj = pm.GetCurrentProject()
mp = proj.GetMediaPool()
root_folder = mp.GetRootFolder()
mp.SetCurrentFolder(root_folder)

target_clip = [c for c in root_folder.GetClipList() if "PB130002.MOV" in c.GetName()][0]

for sf in list(root_folder.GetSubFolderList()):
    if sf.GetName() in ["Telops_And_Audio", "Telops_Alpha"]:
        mp.DeleteFolders([sf])

assets_folder = mp.AddSubFolder(root_folder, "Telops_And_Audio")
mp.SetCurrentFolder(assets_folder)

wav_path = os.path.join(draft_dir, "enhanced_audio_48k.wav")
srt_path = os.path.join(draft_dir, "PB130002_編集済_FullHD.srt")

# Import wav, srt, and the 4865-frame PNG sequence!
ms = resolve.GetMediaStorage()
imp1 = mp.ImportMedia([wav_path, srt_path])
imp_seq = ms.AddItemListToMediaPool([seq_dir])
print("Imported wav/srt:", len(imp1), "Imported seq:", len(imp_seq))

clip_by_name = {c.GetName(): c for c in assets_folder.GetClipList()}
print("Clips in Telops_And_Audio:", list(clip_by_name.keys()))

audio_clip = clip_by_name["enhanced_audio_48k.wav"]
seq_clip = [c for k, c in clip_by_name.items() if "telop_" in k][0]
print("Seq clip name:", seq_clip.GetName(), "Frames:", seq_clip.GetClipProperty().get("Frames"), "FPS:", seq_clip.GetClipProperty().get("FPS"))
seq_clip.SetClipProperty("FPS", "29.97")
seq_clip.SetClipProperty("Alpha mode", "Straight")

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

# 3. Add V2 track and append the 4865-frame telop overlay sequence!
if new_tl.GetTrackCount("video") < 2:
    new_tl.AddTrack("video")

v2_res = mp.AppendToTimeline([{
    "mediaPoolItem": seq_clip,
    "startFrame": 0,
    "endFrame": 4865,
    "mediaType": 1,
    "trackIndex": 2,
    "recordFrame": tl_start
}])
print("Appended V2 sequence clip:", v2_res)
for it in new_tl.GetItemListInTrack("video", 2):
    print("  V2 item:", it.GetName(), "start:", it.GetStart(), "end:", it.GetEnd(), "dur:", it.GetDuration())

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
