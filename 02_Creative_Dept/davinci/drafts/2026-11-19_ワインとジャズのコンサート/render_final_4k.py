# -*- coding: utf-8 -*-
"""
Export .drp archive and render the final 4K UHD (3840x2160 @ 29.97fps) H.264 NVIDIA MP4 master
from DaVinci Resolve Studio 21.2, then verify the rendered MP4 with ffprobe + frame extraction.
"""
import os
import sys
import glob
import time
import json
import subprocess
from PIL import Image, ImageDraw, ImageFont

os.environ["RESOLVE_SCRIPT_API"] = r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting"
os.environ["RESOLVE_SCRIPT_LIB"] = r"C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll"
sys.path.append(r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules")
import DaVinciResolveScript as dvr

FINAL_DIR = r"G:\マイドライブ\git\nobuyukitakahashi\02_Creative_Dept\davinci\final_outputs\2026-11-19_ワインとジャズのコンサート"
DRAFT_DIR = r"G:\マイドライブ\git\nobuyukitakahashi\02_Creative_Dept\davinci\drafts\2026-11-19_ワインとジャズのコンサート"
os.makedirs(FINAL_DIR, exist_ok=True)

OUT_NAME = "2026-11-19_ワインとジャズのコンサート_Master_4K"
OUT_MP4  = os.path.join(FINAL_DIR, OUT_NAME + ".mp4")
OUT_DRP  = os.path.join(FINAL_DIR, "ワインとジャズのコンサート.drp")

FFMPEG  = glob.glob(r"C:\Users\nobuy\AppData\Local\Microsoft\WinGet\Packages\*FFmpeg*\**\ffmpeg.exe", recursive=True)[0]
FFPROBE = glob.glob(r"C:\Users\nobuy\AppData\Local\Microsoft\WinGet\Packages\*FFmpeg*\**\ffprobe.exe", recursive=True)[0]

def main():
    res = dvr.scriptapp("Resolve")
    if not res:
        raise RuntimeError("Could not connect to DaVinci Resolve Studio!")
    pm = res.GetProjectManager()
    proj = pm.GetCurrentProject()
    tl = proj.GetCurrentTimeline()
    print(f"Connected: {res.GetVersionString()} | Project: {proj.GetName()} | Timeline: {tl.GetName()}", flush=True)

    # 1. Save project & export .drp archive (with stills & LUTs)
    pm.SaveProject()
    ok_drp = pm.ExportProject(proj.GetName(), OUT_DRP, True)
    print(f"Exported .drp -> {ok_drp}: {OUT_DRP} ({os.path.getsize(OUT_DRP)//1024 if os.path.exists(OUT_DRP) else 0} KB)", flush=True)

    # 2. Configure Deliver page for 4K UHD 29.97fps H.264 NVIDIA MP4
    res.OpenPage("deliver")
    proj.DeleteAllRenderJobs()

    ok_fc = proj.SetCurrentRenderFormatAndCodec("mp4", "H264_NVIDIA")
    print("SetCurrentRenderFormatAndCodec(mp4, H264_NVIDIA):", ok_fc, flush=True)
    if not ok_fc:
        ok_fc = proj.SetCurrentRenderFormatAndCodec("mp4", "H264")
        print("Fallback H264:", ok_fc, flush=True)

    settings = {
        "SelectAllFrames": True,
        "TargetDir": FINAL_DIR,
        "CustomName": OUT_NAME,
        "ExportVideo": True,
        "ExportAudio": True,
        "FormatWidth": 3840,
        "FormatHeight": 2160,
        "FrameRate": 29.97,
        "VideoQuality": 22000,
        "EncodingProfile": "High",
        "AudioCodec": "aac",
        "AudioSampleRate": 48000,
        "NetworkOptimization": True,
        "ReplaceExistingFilesInPlace": True,
    }
    ok_set = proj.SetRenderSettings(settings)
    print("SetRenderSettings:", ok_set, flush=True)

    job_id = proj.AddRenderJob()
    if not job_id:
        raise RuntimeError("Failed to add render job!")
    print(f"Added Render Job ID: {job_id}", flush=True)

    t0 = time.time()
    ok_start = proj.StartRendering(job_id)
    print(f"StartRendering: {ok_start}", flush=True)
    if not ok_start:
        raise RuntimeError("Failed to start rendering!")

    last_pct = -1
    while proj.IsRenderingInProgress():
        st = proj.GetRenderJobStatus(job_id)
        pct = st.get("CompletionPercentage", 0)
        eta = st.get("EstimatedTimeRemainingInMs", 0) / 1000.0
        if pct != last_pct and (pct % 5 == 0 or pct >= 99):
            print(f"  Rendering: {pct:3d}% | Elapsed: {time.time()-t0:6.1f}s | ETA: {eta:6.1f}s | Status: {st.get('JobStatus')}", flush=True)
            last_pct = pct
        time.sleep(5)

    final_st = proj.GetRenderJobStatus(job_id)
    elapsed = time.time() - t0
    print(f"Render finished in {elapsed:.1f}s | Status: {final_st}", flush=True)

    if not os.path.exists(OUT_MP4):
        raise RuntimeError(f"Expected rendered MP4 not found at {OUT_MP4}")

    sz_gb = os.path.getsize(OUT_MP4) / (1024 ** 3)
    print(f"Rendered MP4 size: {sz_gb:.2f} GB ({OUT_MP4})", flush=True)

    # 3. Verify rendered MP4 via ffprobe
    pr = subprocess.run(
        [FFPROBE, "-v", "error", "-show_format", "-show_streams", "-of", "json", OUT_MP4],
        capture_output=True, text=True
    )
    info = json.loads(pr.stdout)
    fmt = info.get("format", {})
    print(f"FFprobe Duration: {float(fmt.get('duration', 0)):.2f}s | Bitrate: {int(fmt.get('bit_rate', 0))//1000} kbps", flush=True)
    for st in info.get("streams", []):
        if st.get("codec_type") == "video":
            print(f"  Video: {st.get('codec_name')} {st.get('width')}x{st.get('height')} @ {st.get('r_frame_rate')} pix_fmt={st.get('pix_fmt')}", flush=True)
        elif st.get("codec_type") == "audio":
            print(f"  Audio: {st.get('codec_name')} {st.get('sample_rate')}Hz {st.get('channels')}ch", flush=True)

    # 4. Extract 4 spot-check frames directly from the final encoded MP4 into verify_rendered_mp4_board.png
    v_dir = os.path.join(DRAFT_DIR, "mp4_verify_frames")
    os.makedirs(v_dir, exist_ok=True)
    spots = [
        ("01_opening.jpg",   5.0,    "MP4 00:00:05 - Opening Title"),
        ("02_member.jpg",    410.0,  "MP4 00:06:50 - Member Intro (Machi Suzuki)"),
        ("03_bridge.jpg",    2303.0, "MP4 00:38:23 - Recording-Gap Bridge"),
        ("04_ending.jpg",    5246.5, "MP4 01:27:26 - Ending Credits"),
    ]
    thumbs = []
    for fn, sec, cap in spots:
        out_jpg = os.path.join(v_dir, fn)
        subprocess.run(
            [FFMPEG, "-y", "-hide_banner", "-loglevel", "error", "-ss", str(sec), "-i", OUT_MP4, "-frames:v", "1", "-q:v", "2", out_jpg],
            check=True
        )
        thumbs.append((out_jpg, cap))

    tw, th, ch = 960, 540, 40
    board = Image.new("RGB", (tw * 2, (th + ch) * 2), (16, 10, 12))
    draw = ImageDraw.Draw(board)
    f_cap = ImageFont.truetype(r"C:\Windows\Fonts\yumindb.ttf", 24)
    for i, (p, cap) in enumerate(thumbs):
        r, c = divmod(i, 2)
        im = Image.open(p).convert("RGB").resize((tw, th), Image.Resampling.LANCZOS)
        x, y = c * tw, r * (th + ch)
        board.paste(im, (x, y))
        draw.rectangle([x, y + th, x + tw, y + th + ch], fill=(32, 12, 16))
        draw.text((x + 16, y + th + 8), cap, font=f_cap, fill=(244, 224, 180))
    vboard = os.path.join(DRAFT_DIR, "verify_rendered_mp4_board.png")
    board.save(vboard, quality=92)
    print("Saved final MP4 verification board:", vboard, flush=True)
    print("RENDER + VERIFICATION COMPLETE!", flush=True)

if __name__ == "__main__":
    main()
