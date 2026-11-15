import os
import sys
import time
import shutil

os.environ["RESOLVE_SCRIPT_API"] = r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting"
os.environ["RESOLVE_SCRIPT_LIB"] = r"C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll"
sys.path.append(r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules")

import DaVinciResolveScript as dvr_script

draft_dir = r"g:\マイドライブ\git\nobuyukitakahashi\02_Creative_Dept\davinci\drafts\2026-11-13_南信州広域連合へ要望書提出"
final_dir = r"g:\マイドライブ\git\nobuyukitakahashi\02_Creative_Dept\davinci\final_outputs\2026-11-13_南信州広域連合へ要望書提出"
h_dir = r"H:\2026-11-13_南信州広域連合_連合長へ_要望書提出_録音一式"

resolve = dvr_script.scriptapp("Resolve")
pm = resolve.GetProjectManager()
proj = pm.GetCurrentProject()
mp = proj.GetMediaPool()
tl = proj.GetCurrentTimeline()
root = mp.GetRootFolder()

resolve.OpenPage("edit")
time.sleep(0.2)

# Remove old V2 items
old_v2 = tl.GetItemListInTrack("video", 2)
if old_v2:
    tl.DeleteClips(old_v2)

# Get telop_[0000-4864].png from Test_Seq
tf = [f for f in root.GetSubFolderList() if f.GetName() == "Test_Seq"][0]
seq_clip = tf.GetClipList()[0]
seq_clip.SetClipProperty("Alpha mode", "Straight")

tl_start = tl.GetStartFrame() # 108000
v2_res = mp.AppendToTimeline([{
    "mediaPoolItem": seq_clip,
    "startFrame": 0,
    "endFrame": 4865,
    "mediaType": 1,
    "trackIndex": 2,
    "recordFrame": tl_start
}])
print("Appended 4865-frame telop sequence on V2:", v2_res)
for it in tl.GetItemListInTrack("video", 2):
    print("  V2 item:", it.GetName(), "start:", it.GetStart(), "end:", it.GetEnd(), "dur:", it.GetDuration())

# Export 6 sample frames with telops for visual audit
resolve.OpenPage("color")
time.sleep(0.3)
telop_audit_dir = os.path.join(draft_dir, "telop_audit_frames")
os.makedirs(telop_audit_dir, exist_ok=True)
sample_secs = [1.5, 8.0, 53.0, 99.0, 128.0, 155.5]
for i, sec in enumerate(sample_secs):
    tl_f = tl_start + int(round(sec * 29.97))
    tl.SetCurrentTimecode(str(tl_f))
    time.sleep(0.18)
    out_p = os.path.join(telop_audit_dir, f"telop_check_{i+1}_{int(sec)}s.png")
    if os.path.exists(out_p):
        os.remove(out_p)
    proj.ExportCurrentFrameAsStill(out_p)
    print(f"Exported telop audit frame t={sec}s -> {os.path.exists(out_p)}")

# Render Full-HD MP4
resolve.OpenPage("deliver")
time.sleep(0.3)

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

resolve.OpenPage("edit")
pm.SaveProject()
drp_path = os.path.join(final_dir, "2026-11-13 南信州広域連合へ要望書提出.drp")
if os.path.exists(drp_path):
    os.remove(drp_path)
pm.ExportProject(proj.GetName(), drp_path, False)
print("Done updating V2 telops and rendering Full-HD MP4!")
