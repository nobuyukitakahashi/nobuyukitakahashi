import os
import sys

os.environ["RESOLVE_SCRIPT_API"] = r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting"
os.environ["RESOLVE_SCRIPT_LIB"] = r"C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll"
sys.path.append(r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules")

import DaVinciResolveScript as dvr_script

seq_dir = r"C:\Users\nobuy\.gemini\antigravity\brain\a50e7947-c634-4e5b-a3d8-d2ec20749ea6\scratch\telop_seq"
resolve = dvr_script.scriptapp("Resolve")
proj = resolve.GetProjectManager().GetCurrentProject()
mp = proj.GetMediaPool()
root = mp.GetRootFolder()

for sf in list(root.GetSubFolderList()):
    if sf.GetName() == "Test_Seq":
        mp.DeleteFolders([sf])

tf = mp.AddSubFolder(root, "Test_Seq")
mp.SetCurrentFolder(tf)

imp = mp.ImportMedia([{
    "FilePath": os.path.join(seq_dir, "telop_%04d.png"),
    "StartIndex": 0,
    "EndIndex": 4864
}])
print("ImportMedia sequence result:", imp)
for c in tf.GetClipList():
    print("  Clip:", c.GetName(), "Frames:", c.GetClipProperty().get("Frames"), "FPS:", c.GetClipProperty().get("FPS"))
