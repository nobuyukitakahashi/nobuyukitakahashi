import os
import sys
import shutil

os.environ["RESOLVE_SCRIPT_API"] = r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting"
os.environ["RESOLVE_SCRIPT_LIB"] = r"C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll"
sys.path.append(r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules")

import DaVinciResolveScript as dvr_script

draft_dir = r"g:\マイドライブ\git\nobuyukitakahashi\02_Creative_Dept\davinci\drafts\2026-11-13_南信州広域連合へ要望書提出"
final_dir = r"g:\マイドライブ\git\nobuyukitakahashi\02_Creative_Dept\davinci\final_outputs\2026-11-13_南信州広域連合へ要望書提出"
rendered_mp4 = os.path.join(final_dir, "PB130002_編集済_FullHD.mp4")

resolve = dvr_script.scriptapp("Resolve")
pm = resolve.GetProjectManager()
proj = pm.GetCurrentProject()
mp = proj.GetMediaPool()

imported = mp.ImportMedia([rendered_mp4])
if imported:
    c = imported[0]
    props = c.GetClipProperty()
    print("=== Rendered MP4 Properties ===")
    for k in ["File Name", "Format", "Video Codec", "Resolution", "FPS", "Frames", "Duration", "Audio Codec", "Audio Ch", "Sample Rate"]:
        print(f"  {k}: {props.get(k)}")
    # Remove the rendered clip from MediaPool so the project remains clean with only the source media and edit timeline, then re-save and re-export .drp
    mp.DeleteClips([c])

resolve.OpenPage("edit")
pm.SaveProject()
drp_path = os.path.join(final_dir, "2026-11-13 南信州広域連合へ要望書提出.drp")
if os.path.exists(drp_path):
    os.remove(drp_path)
pm.ExportProject(proj.GetName(), drp_path, False)

# Copy before_after_audit.png to keyframes_audit_board.png in final_outputs
src_board = os.path.join(draft_dir, "before_after_audit.png")
dst_board = os.path.join(final_dir, "keyframes_audit_board.png")
shutil.copy2(src_board, dst_board)
print("Copied keyframes_audit_board.png:", os.path.exists(dst_board))
