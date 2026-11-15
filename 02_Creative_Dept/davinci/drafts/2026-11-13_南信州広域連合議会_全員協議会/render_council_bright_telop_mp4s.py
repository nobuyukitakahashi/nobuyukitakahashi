import os
import sys
import time
import shutil

os.environ["RESOLVE_SCRIPT_API"] = r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting"
os.environ["RESOLVE_SCRIPT_LIB"] = r"C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll"
sys.path.append(r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules")
import DaVinciResolveScript as dvr

final_dir = r"g:\マイドライブ\git\nobuyukitakahashi\02_Creative_Dept\davinci\final_outputs\2026-11-13_南信州広域連合議会_全員協議会"
h_dir = r"H:\2026-11-13_南信州広域連合_連合長へ_要望書提出_録音一式"
os.makedirs(final_dir, exist_ok=True)

resolve = dvr.scriptapp("Resolve")
pm = resolve.GetProjectManager()
proj = pm.GetCurrentProject()
print("Connected to project:", proj.GetName())

# Clear old render jobs
proj.DeleteAllRenderJobs()

def render_timeline(tl_index, out_filename):
    tl = proj.GetTimelineByIndex(tl_index)
    proj.SetCurrentTimeline(tl)
    proj.SetRenderSettings({
        "SelectAllFrames": True,
        "TargetDir": final_dir,
        "CustomName": out_filename,
        "FormatWidth": 1920,
        "FormatHeight": 1080,
        "FrameRate": 29.97,
        "ExportVideo": True,
        "ExportAudio": True,
        "AudioCodec": "aac",
        "AudioBitDepth": 16,
        "AudioSampleRate": 48000,
    })
    proj.SetCurrentRenderFormatAndCodec("mp4", "H264_NVIDIA")
    job_id = proj.AddRenderJob()
    print(f"Added render job {job_id} for {tl.GetName()} -> {out_filename}.mp4")
    t0 = time.time()
    proj.StartRendering(job_id)
    while proj.IsRenderingInProgress():
        st = proj.GetRenderJobStatus(job_id)
        pct = st.get("CompletionPercentage", 0)
        print(f"  Rendering {out_filename}.mp4 ... {pct}% ({time.time()-t0:.1f}s)", flush=True)
        time.sleep(10)
    st = proj.GetRenderJobStatus(job_id)
    dt = time.time() - t0
    out_path = os.path.join(final_dir, out_filename + ".mp4")
    sz_mb = os.path.getsize(out_path) / (1024*1024) if os.path.exists(out_path) else 0
    print(f"Completed {out_filename}.mp4 in {dt:.1f}s | Status: {st} | Size: {sz_mb:.1f} MB", flush=True)
    # Copy to H drive
    if os.path.exists(out_path) and os.path.exists(h_dir):
        h_dest = os.path.join(h_dir, out_filename + ".mp4")
        shutil.copy2(out_path, h_dest)
        print(f"Copied to {h_dest}", flush=True)

# 1. Render PB130017
render_timeline(1, "PB130017_全員協議会_前半_音声同期済_FullHD")

# 2. Render PB130019
render_timeline(2, "PB130019_全員協議会_資料3_桐林クリーンセンター解体_音声同期済_FullHD")

# 3. Export DRP to final_dir and H drive
drp_path = os.path.join(final_dir, "2026-11-13 南信州広域連合議会 全員協議会.drp")
if os.path.exists(drp_path):
    os.remove(drp_path)
ok_drp = pm.ExportProject(proj.GetName(), drp_path, False)
print(f"Exported DRP: {ok_drp} -> {drp_path}")
if os.path.exists(drp_path) and os.path.exists(h_dir):
    shutil.copy2(drp_path, os.path.join(h_dir, "2026-11-13 南信州広域連合議会 全員協議会.drp"))
    print("Copied DRP to H drive.")
