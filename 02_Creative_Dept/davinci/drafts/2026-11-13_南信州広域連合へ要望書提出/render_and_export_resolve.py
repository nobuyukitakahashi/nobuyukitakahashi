import os
import sys
import time
import shutil

os.environ["RESOLVE_SCRIPT_API"] = r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting"
os.environ["RESOLVE_SCRIPT_LIB"] = r"C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll"
sys.path.append(r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules")

import DaVinciResolveScript as dvr_script

final_dir = r"g:\マイドライブ\git\nobuyukitakahashi\02_Creative_Dept\davinci\final_outputs\2026-11-13_南信州広域連合へ要望書提出"
input_dir = r"H:\2026-11-13_南信州広域連合_連合長へ_要望書提出_録音一式"
os.makedirs(final_dir, exist_ok=True)

resolve = dvr_script.scriptapp("Resolve")
pm = resolve.GetProjectManager()
proj = pm.GetCurrentProject()
tl = proj.GetCurrentTimeline()
print("Current Project:", proj.GetName(), "Timeline:", tl.GetName())

resolve.OpenPage("deliver")
time.sleep(0.5)

formats = proj.GetRenderFormats()
print("Render Formats:", formats)
mp4_codecs = proj.GetRenderCodecs("mp4")
print("MP4 Codecs:", mp4_codecs)

# Choose H.264 codec
codec_val = "H264_NVIDIA" if "H264_NVIDIA" in mp4_codecs.values() else ("H264" if "H264" in mp4_codecs.values() else list(mp4_codecs.values())[0])
print("Selected Codec:", codec_val)

proj.SetCurrentRenderFormatAndCodec("mp4", codec_val)

out_filename = "PB130002_編集済_FullHD.mp4"
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
set_res = proj.SetRenderSettings(render_settings)
print("SetRenderSettings:", set_res)

proj.DeleteAllRenderJobs()
job_id = proj.AddRenderJob()
print("Added Render Job ID:", job_id)

proj.StartRendering(job_id)
while proj.IsRenderingInProgress():
    status = proj.GetRenderJobStatus(job_id)
    print("Rendering...", status)
    time.sleep(2.0)

final_status = proj.GetRenderJobStatus(job_id)
print("Final Render Status:", final_status)

rendered_mp4 = os.path.join(final_dir, out_filename)
print("Rendered file exists:", os.path.exists(rendered_mp4), "Size:", os.path.getsize(rendered_mp4) if os.path.exists(rendered_mp4) else 0)

# Copy to H:\2026-11-13_南信州広域連合_連合長へ_要望書提出_録音一式\PB130002_編集済_FullHD.mp4
dest_h_mp4 = os.path.join(input_dir, out_filename)
shutil.copy2(rendered_mp4, dest_h_mp4)
print("Copied to H drive:", dest_h_mp4, os.path.getsize(dest_h_mp4))

# Also save project and export .drp
pm.SaveProject()
drp_path = os.path.join(final_dir, "2026-11-13 南信州広域連合へ要望書提出.drp")
if os.path.exists(drp_path):
    os.remove(drp_path)
exp_drp = pm.ExportProject(proj.GetName(), drp_path, False)
print("ExportProject (.drp):", exp_drp, os.path.exists(drp_path))
