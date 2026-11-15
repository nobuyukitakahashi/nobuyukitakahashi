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

resolve = dvr_script.scriptapp("Resolve")
pm = resolve.GetProjectManager()
proj = pm.GetCurrentProject()
proj.DeleteAllRenderJobs()

def get_tl_by_name(name):
    for i in range(1, proj.GetTimelineCount() + 1):
        t = proj.GetTimelineByIndex(i)
        if t and t.GetName() == name:
            return t
    return None

# Render PB130018 (0.5s)
tl4 = get_tl_by_name("04_PB130018_誤操作0.5秒_音声同期確認用")
proj.SetCurrentTimeline(tl4)
proj.SetCurrentRenderFormatAndCodec("mp4", "H264")
proj.SetRenderSettings({
    "SelectAllFrames": True,
    "TargetDir": final_dir,
    "CustomName": "PB130018_誤操作0.5秒_音声同期済_FullHD",
    "FormatWidth": 1920,
    "FormatHeight": 1080,
    "FrameRate": "29.97",
    "ExportVideo": True,
    "ExportAudio": True,
})
job4 = proj.AddRenderJob()
proj.StartRendering([job4])
while proj.IsRenderingInProgress():
    time.sleep(1)
out4 = os.path.join(final_dir, "PB130018_誤操作0.5秒_音声同期済_FullHD.mp4")
if os.path.exists(out4):
    shutil.copy2(out4, os.path.join(h_dir, "PB130018_誤操作0.5秒_音声同期済_FullHD.mp4"))
    print("Rendered & copied PB130018 MP4")

# Render PB130019 (1h 17m 15s)
proj.DeleteAllRenderJobs()
tl2 = get_tl_by_name("02_PB130019_全員協議会_資料3_桐林クリーンセンター解体_音声同期済")
proj.SetCurrentTimeline(tl2)
proj.SetCurrentRenderFormatAndCodec("mp4", "H264")
proj.SetRenderSettings({
    "SelectAllFrames": True,
    "TargetDir": final_dir,
    "CustomName": "PB130019_全員協議会_資料3_桐林クリーンセンター解体_音声同期済_FullHD",
    "FormatWidth": 1920,
    "FormatHeight": 1080,
    "FrameRate": "29.97",
    "ExportVideo": True,
    "ExportAudio": True,
})
job2 = proj.AddRenderJob()
print("Added Render Job 2 (PB130019):", job2)

t0 = time.time()
proj.StartRendering([job2])
last_pct = -1
while proj.IsRenderingInProgress():
    st = proj.GetRenderJobStatus(job2)
    pct = st.get("CompletionPercentage", 0)
    if pct != last_pct:
        elapsed = time.time() - t0
        print(f"  [PB130019] {pct}% ({elapsed:.1f}s elapsed)")
        last_pct = pct
    time.sleep(5)

elapsed2 = time.time() - t0
st2 = proj.GetRenderJobStatus(job2)
print(f"PB130019 render finished in {elapsed2:.1f}s ({138915/max(elapsed2,0.1):.1f} fps): {st2}")

out2 = os.path.join(final_dir, "PB130019_全員協議会_資料3_桐林クリーンセンター解体_音声同期済_FullHD.mp4")
if os.path.exists(out2):
    shutil.copy2(out2, os.path.join(h_dir, "PB130019_全員協議会_資料3_桐林クリーンセンター解体_音声同期済_FullHD.mp4"))
    print("Copied PB130019 MP4 to H:\\")

# Re-save and re-export DRP so active timeline is 02_PB130019
pm.SaveProject()
drp_path = os.path.join(final_dir, "2026-11-13 南信州広域連合議会 全員協議会.drp")
if os.path.exists(drp_path):
    os.remove(drp_path)
pm.ExportProject(proj.GetName(), drp_path, False)
shutil.copy2(drp_path, os.path.join(h_dir, "2026-11-13 南信州広域連合議会 全員協議会.drp"))
print("Updated DRP in both folders.")
