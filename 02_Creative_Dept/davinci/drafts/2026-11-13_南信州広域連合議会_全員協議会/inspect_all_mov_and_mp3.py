import os
import sys
import datetime

os.environ["RESOLVE_SCRIPT_API"] = r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting"
os.environ["RESOLVE_SCRIPT_LIB"] = r"C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll"
sys.path.append(r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules")

import DaVinciResolveScript as dvr_script

base_h = r"H:\2026-11-13_南信州広域連合_連合長へ_要望書提出_録音一式"
draft_dir = r"g:\マイドライブ\git\nobuyukitakahashi\02_Creative_Dept\davinci\drafts\2026-11-13_南信州広域連合議会_全員協議会"
final_dir = r"g:\マイドライブ\git\nobuyukitakahashi\02_Creative_Dept\davinci\final_outputs\2026-11-13_南信州広域連合議会_全員協議会"

os.makedirs(draft_dir, exist_ok=True)
os.makedirs(final_dir, exist_ok=True)

print("=== Scanning H: Drive Folder & Subfolders ===")
all_media_paths = []
for root, dirs, files in os.walk(base_h):
    rel_root = os.path.relpath(root, base_h)
    for f in sorted(files):
        fp = os.path.join(root, f)
        ext = os.path.splitext(f)[1].lower()
        if ext in [".mov", ".mp3", ".wav", ".m4a", ".mp4", ".txt", ".md", ".docx", ".pdf"]:
            st = os.stat(fp)
            mtime = datetime.datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
            ctime = datetime.datetime.fromtimestamp(st.st_ctime).strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{rel_root}] {f} | Size: {st.st_size:,} bytes | mtime: {mtime} | ctime: {ctime}")
            if ext in [".mov", ".mp3", ".wav", ".m4a"] and f in ["PB130017.MOV", "PB130018.MOV", "PB130019.MOV"] or ext in [".mp3", ".wav", ".m4a"]:
                all_media_paths.append(fp)

resolve = dvr_script.scriptapp("Resolve")
pm = resolve.GetProjectManager()
# Save current project before switching
cur_proj = pm.GetCurrentProject()
if cur_proj:
    pm.SaveProject()

proj_name = "2026-11-13 南信州広域連合議会 全員協議会"
proj = pm.LoadProject(proj_name)
if not proj:
    proj = pm.CreateProject(proj_name)
print("\nOpened Project:", proj.GetName())

proj.SetSetting("timelineResolutionWidth", "1920")
proj.SetSetting("timelineResolutionHeight", "1080")
proj.SetSetting("timelineFrameRate", "29.97")

mp = proj.GetMediaPool()
root_folder = mp.GetRootFolder()
mp.SetCurrentFolder(root_folder)

existing_names = {c.GetName() for c in root_folder.GetClipList()}
to_import = [p for p in all_media_paths if os.path.basename(p) not in existing_names]
if to_import:
    imp = mp.ImportMedia(to_import)
    print(f"Imported {len(imp)} clips into MediaPool.")

print("\n=== MediaPool Clip Properties ===")
for c in sorted(root_folder.GetClipList(), key=lambda x: x.GetName()):
    p = c.GetClipProperty()
    print(f"\n--- {c.GetName()} ---")
    for k in ["File Path", "Type", "Format", "Video Codec", "Audio Codec", "Resolution", "FPS", "Frames", "Duration", "Start TC", "End TC", "Date Created", "Date Modified", "Audio Ch", "Sample Rate"]:
        print(f"  {k}: {p.get(k)}")
