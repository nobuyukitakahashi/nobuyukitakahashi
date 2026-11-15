import os
import sys
import json
import shutil

os.environ["RESOLVE_SCRIPT_API"] = r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting"
os.environ["RESOLVE_SCRIPT_LIB"] = r"C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll"
sys.path.append(r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules")

import DaVinciResolveScript as dvr_script

draft_dir = r"g:\マイドライブ\git\nobuyukitakahashi\02_Creative_Dept\davinci\drafts\2026-11-13_南信州広域連合へ要望書提出"
alpha_dir = os.path.join(draft_dir, "telops_alpha")
os.makedirs(alpha_dir, exist_ok=True)

manifest_path = os.path.join(draft_dir, "subtitles_manifest.json")
with open(manifest_path, "r", encoding="utf-8") as f:
    subs = json.load(f)

alpha_paths = []
for idx, item in enumerate(subs):
    # Generate pure alphabetic 2-letter code: aa, ab, ac ...
    c1 = chr(ord('a') + (idx // 26))
    c2 = chr(ord('a') + (idx % 26))
    alpha_name = f"telop_{c1}{c2}.png"
    old_p = item["png"]
    if not os.path.exists(old_p):
        old_p = old_p.replace(".png", "_sub.png")
    new_p = os.path.join(alpha_dir, alpha_name)
    shutil.copy2(old_p, new_p)
    item["alpha_png"] = new_p
    item["alpha_name"] = alpha_name
    alpha_paths.append(new_p)

with open(manifest_path, "w", encoding="utf-8") as f:
    json.dump(subs, f, ensure_ascii=False, indent=2)

resolve = dvr_script.scriptapp("Resolve")
proj = resolve.GetProjectManager().GetCurrentProject()
mp = proj.GetMediaPool()
root_folder = mp.GetRootFolder()

for sf in root_folder.GetSubFolderList():
    if sf.GetName() == "Telops_Alpha":
        mp.DeleteFolders([sf])

tf = mp.AddSubFolder(root_folder, "Telops_Alpha")
mp.SetCurrentFolder(tf)
imp = mp.ImportMedia(alpha_paths)
print("Imported count with alphabetic names:", len(imp))
for c in tf.GetClipList()[:5]:
    print(" ", c.GetName(), "Frames:", c.GetClipProperty().get("Frames"))
