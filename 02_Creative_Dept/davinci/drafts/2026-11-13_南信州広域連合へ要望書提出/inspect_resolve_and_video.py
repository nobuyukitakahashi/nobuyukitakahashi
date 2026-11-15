import os
import sys

os.environ["RESOLVE_SCRIPT_API"] = r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting"
os.environ["RESOLVE_SCRIPT_LIB"] = r"C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll"
sys.path.append(r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules")

import DaVinciResolveScript as dvr_script

input_dir = r"H:\2026-11-13_南信州広域連合_連合長へ_要望書提出_録音一式"
print("=== Directory Contents ===")
for f in os.listdir(input_dir):
    fp = os.path.join(input_dir, f)
    print(f, os.path.getsize(fp) if os.path.isfile(fp) else "DIR")

resolve = dvr_script.scriptapp("Resolve")
print("Resolve instance:", resolve)
print("Product Name:", resolve.GetProductName(), resolve.GetVersionString())

pm = resolve.GetProjectManager()
proj_name = "2026-11-13 南信州広域連合へ要望書提出"
proj = pm.LoadProject(proj_name)
if not proj:
    proj = pm.CreateProject(proj_name)
if not proj:
    proj = pm.GetCurrentProject()
print("Current Project:", proj.GetName())

mp = proj.GetMediaPool()
root_folder = mp.GetRootFolder()
clips = root_folder.GetClipList()
print("Existing clips in MediaPool:", [c.GetName() for c in clips] if clips else [])

video_path = os.path.join(input_dir, "PB130002.MOV")
imported = mp.ImportMedia([video_path])
print("Imported:", imported)

clips = root_folder.GetClipList()
target_clip = None
for c in clips:
    if "PB130002" in c.GetName():
        target_clip = c
        break

if target_clip:
    props = target_clip.GetClipProperty()
    print("\n=== Clip Properties in DaVinci Resolve ===")
    for k, v in sorted(props.items()):
        print(f"  {k}: {v}")
