import os
import sys

RESOLVE_SCRIPT_API = r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting"
RESOLVE_SCRIPT_LIB = r"C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll"
os.environ["RESOLVE_SCRIPT_API"] = RESOLVE_SCRIPT_API
os.environ["RESOLVE_SCRIPT_LIB"] = RESOLVE_SCRIPT_LIB
sys.path.append(os.path.join(RESOLVE_SCRIPT_API, "Modules"))

import DaVinciResolveScript as dvr_script

resolve = dvr_script.scriptapp("Resolve")
pm = resolve.GetProjectManager()
proj = pm.GetCurrentProject()
mp = proj.GetMediaPool()
root = mp.GetRootFolder()

clips = {c.GetName(): c for c in root.GetClipList()}
for name, c in clips.items():
    print(f"Clip: {name} | FPS={c.GetClipProperty('FPS')} | Frames={c.GetClipProperty('Frames')} | Duration={c.GetClipProperty('Duration')} | AudioCh={c.GetClipProperty('Audio Ch')}")
