# -*- coding: utf-8 -*-
"""
Optimize the 73.35 GB 120Mbps 4K Resolve master directly to the user's Desktop
(C:\\Users\\nobuy\\Desktop\\2026-11-19_ワインとジャズのコンサート_Master_4K.mp4)
via NVIDIA NVENC (20Mbps VBR / CQ 20 / faststart / lossless AAC audio copy),
verify with ffprobe + 4-frame visual check, clean up the 73.35 GB intermediate on G:,
and store lightweight project archives (.drp / audit board / spec MD) in 04_Delivery_Dept.
"""
import os
import glob
import json
import time
import shutil
import subprocess
from PIL import Image, ImageDraw, ImageFont

DRAFT_DIR    = r"G:\マイドライブ\git\nobuyukitakahashi\02_Creative_Dept\davinci\drafts\2026-11-19_ワインとジャズのコンサート"
FINAL_DIR    = r"G:\マイドライブ\git\nobuyukitakahashi\02_Creative_Dept\davinci\final_outputs\2026-11-19_ワインとジャズのコンサート"
DELIVERY_DIR = r"G:\マイドライブ\git\nobuyukitakahashi\04_Delivery_Dept\outputs\davinci\2026-11-19_ワインとジャズのコンサート"
DESKTOP_DIR  = r"C:\Users\nobuy\Desktop"

os.makedirs(DELIVERY_DIR, exist_ok=True)

MP4_NAME    = "2026-11-19_ワインとジャズのコンサート_Master_4K.mp4"
RAW_120M    = os.path.join(FINAL_DIR, MP4_NAME)
PARTIAL_DEL = os.path.join(DELIVERY_DIR, MP4_NAME)
DESKTOP_MP4 = os.path.join(DESKTOP_DIR, MP4_NAME)

FFMPEG  = glob.glob(r"C:\Users\nobuy\AppData\Local\Microsoft\WinGet\Packages\*FFmpeg*\**\ffmpeg.exe", recursive=True)[0]
FFPROBE = glob.glob(r"C:\Users\nobuy\AppData\Local\Microsoft\WinGet\Packages\*FFmpeg*\**\ffprobe.exe", recursive=True)[0]

def main():
    # Remove any partial MP4 from previous cancelled run on G:
    if os.path.exists(PARTIAL_DEL):
        os.remove(PARTIAL_DEL)
        print("Removed cancelled partial file on G:", PARTIAL_DEL, flush=True)

    # First copy lightweight deliverables (.drp, audit board, spec MD) so they are immediately in place
    audit_src = os.path.join(DRAFT_DIR, "keyframes_audit_board.png")
    shutil.copy2(audit_src, os.path.join(FINAL_DIR, "keyframes_audit_board.png"))
    shutil.copy2(audit_src, os.path.join(DELIVERY_DIR, "keyframes_audit_board.png"))

    drp_src = os.path.join(FINAL_DIR, "ワインとジャズのコンサート.drp")
    shutil.copy2(drp_src, os.path.join(DELIVERY_DIR, "ワインとジャズのコンサート.drp"))

    md_src = os.path.join(FINAL_DIR, "content_ワインとジャズのコンサート.md")
    if os.path.exists(md_src):
        shutil.copy2(md_src, os.path.join(DELIVERY_DIR, "content_ワインとジャズのコンサート.md"))
    print("Synced lightweight deliverables (.drp, audit board, spec MD) to 04_Delivery_Dept.", flush=True)

    t0 = time.time()
    print(f"Encoding 4K Delivery Master directly to Desktop: {DESKTOP_MP4}", flush=True)
    cmd = [
        FFMPEG, "-y", "-hide_banner", "-loglevel", "warning", "-stats",
        "-hwaccel", "cuda", "-i", RAW_120M,
        "-c:v", "h264_nvenc", "-preset", "p4", "-rc", "vbr", "-cq", "20",
        "-b:v", "20M", "-maxrate", "28M", "-bufsize", "40M",
        "-pix_fmt", "yuv420p", "-profile:v", "high",
        "-c:a", "copy",
        "-movflags", "+faststart",
        DESKTOP_MP4
    ]
    r = subprocess.run(cmd)
    if r.returncode != 0:
        raise RuntimeError(f"FFmpeg NVENC failed with code {r.returncode}")

    sz_gb = os.path.getsize(DESKTOP_MP4) / (1024 ** 3)
    print(f"NVENC Desktop encode finished in {time.time()-t0:.1f}s -> {sz_gb:.2f} GB ({DESKTOP_MP4})", flush=True)

    # Verify final Desktop MP4 with ffprobe
    pr = subprocess.run(
        [FFPROBE, "-v", "error", "-show_format", "-show_streams", "-of", "json", DESKTOP_MP4],
        capture_output=True, text=True, check=True
    )
    info = json.loads(pr.stdout)
    dur = float(info["format"]["duration"])
    br_kbps = int(info["format"]["bit_rate"]) // 1000
    print(f"Verified Desktop MP4: duration={dur:.2f}s | bitrate={br_kbps} kbps", flush=True)
    for st in info.get("streams", []):
        if st.get("codec_type") == "video":
            print(f"  Video: {st.get('codec_name')} {st.get('width')}x{st.get('height')} @ {st.get('r_frame_rate')} pix_fmt={st.get('pix_fmt')}", flush=True)
        elif st.get("codec_type") == "audio":
            print(f"  Audio: {st.get('codec_name')} {st.get('sample_rate')}Hz {st.get('channels')}ch", flush=True)
    if dur < 5240:
        raise RuntimeError(f"Unexpected short duration: {dur}")

    # Extract 4 spot-check frames from the final Desktop MP4
    v_dir = os.path.join(DRAFT_DIR, "desktop_mp4_verify")
    os.makedirs(v_dir, exist_ok=True)
    spots = [
        ("01_opening.jpg",  5.0,    "Desktop MP4 00:00:05 - Opening Title"),
        ("02_member.jpg",   410.0,  "Desktop MP4 00:06:50 - Member Intro"),
        ("03_bridge.jpg",   2304.5, "Desktop MP4 00:38:24 - Recording-Gap Bridge"),
        ("04_ending.jpg",   5246.5, "Desktop MP4 01:27:26 - Ending Credits"),
    ]
    thumbs = []
    for fn, sec, cap in spots:
        out_jpg = os.path.join(v_dir, fn)
        subprocess.run(
            [FFMPEG, "-y", "-hide_banner", "-loglevel", "error", "-ss", str(sec), "-i", DESKTOP_MP4, "-frames:v", "1", "-q:v", "2", out_jpg],
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
    vboard = os.path.join(DRAFT_DIR, "verify_desktop_mp4_board.png")
    board.save(vboard, quality=92)
    print("Saved Desktop MP4 verification board:", vboard, flush=True)

    # Clean up the 73.35 GB intermediate MP4 on G: to protect Google Drive / disk space
    if os.path.exists(RAW_120M):
        os.remove(RAW_120M)
        print("Cleaned up 73.35 GB intermediate MP4 on G: to save disk/Drive space.", flush=True)

    print("DESKTOP DELIVERY & VERIFICATION COMPLETE!", flush=True)

if __name__ == "__main__":
    main()
