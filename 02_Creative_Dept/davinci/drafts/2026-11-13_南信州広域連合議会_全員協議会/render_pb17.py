import os
import sys
import time
import shutil

RESOLVE_SCRIPT_API = r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting"
RESOLVE_SCRIPT_LIB = r"C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll"
os.environ["RESOLVE_SCRIPT_API"] = RESOLVE_SCRIPT_API
os.environ["RESOLVE_SCRIPT_LIB"] = RESOLVE_SCRIPT_LIB
sys.path.append(os.path.join(RESOLVE_SCRIPT_API, "Modules"))

import DaVinciResolveScript as dvr_script

final_dir = r"g:\マイドライブ\git\nobuyukitakahashi\02_Creative_Dept\davinci\final_outputs\2026-11-13_南信州広域連合議会_全員協議会"
h_dir = r"H:\2026-11-13_南信州広域連合_連合長へ_要望書提出_録音一式"
os.makedirs(final_dir, exist_ok=True)

resolve = dvr_script.scriptapp("Resolve")
pm = resolve.GetProjectManager()
proj = pm.GetCurrentProject()

# 1. Export .drp to final_dir and h_dir
drp_path = os.path.join(final_dir, "2026-11-13 南信州広域連合議会 全員協議会.drp")
if os.path.exists(drp_path):
    os.remove(drp_path)
ok_drp = pm.ExportProject(proj.GetName(), drp_path, False)
print(f"Exported DRP to {drp_path}: {ok_drp}")
if os.path.exists(drp_path):
    shutil.copy2(drp_path, os.path.join(h_dir, "2026-11-13 南信州広域連合議会 全員協議会.drp"))

# 2. Render Timeline 1 (PB130017) first and measure speed
proj.DeleteAllRenderJobs()

def get_tl_by_name(name):
    for i in range(1, proj.GetTimelineCount() + 1):
        t = proj.GetTimelineByIndex(i)
        if t and t.GetName() == name:
            return t
    return None

tl1 = get_tl_by_name("01_PB130017_全員協議会_前半_音声同期済")
proj.SetCurrentTimeline(tl1)
proj.SetCurrentRenderFormatAndCodec("mp4", "H264")
proj.SetRenderSettings({
    "SelectAllFrames": True,
    "TargetDir": final_dir,
    "CustomName": "PB130017_全員協議会_前半_音声同期済_FullHD",
    "FormatWidth": 1920,
    "FormatHeight": 1080,
    "FrameRate": "29.97",
    "ExportVideo": True,
    "ExportAudio": True,
})
job1 = proj.AddRenderJob()
print("Added Render Job 1 (PB130017):", job1)

t0 = time.time()
proj.StartRendering([job1])
while proj.IsRenderingInProgress():
    st = proj.GetRenderJobStatus(job1)
    pct = st.get("CompletionPercentage", 0)
    elapsed = time.time() - t0
    print(f"  [PB130017] {pct}% ({elapsed:.1f}s elapsed)")
    time.sleep(3)

elapsed1 = time.time() - t0
st1 = proj.GetRenderJobStatus(job1)
print(f"PB130017 render finished in {elapsed1:.1f}s ({18435/max(elapsed1,0.1):.1f} fps): {st1}")

out1 = os.path.join(final_dir, "PB130017_全員協議会_前半_音声同期済_FullHD.mp4")
if os.path.exists(out1):
    shutil.copy2(out1, os.path.join(h_dir, "PB130017_全員協議会_前半_音声同期済_FullHD.mp4"))
    print("Copied PB130017 MP4 to H:\\")
