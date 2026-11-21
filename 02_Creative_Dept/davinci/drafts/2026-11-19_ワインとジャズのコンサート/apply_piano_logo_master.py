# -*- coding: utf-8 -*-
"""
Composite perspective-matched 4K piano-cloth logos
  (HONKA + HONKA music SALON + ワインとジャズのコンサート + SALON De TATSUH)
onto the 4K Desktop concert master MP4 via a SINGLE GPU overlay_cuda pipeline
(zero chained CUDA context issues, exact frame-locked fades, lossless AAC audio copy).

Timeline segment frame map (from timeline_cue_manifest.json, total 157,338f @ 30000/1001):
  1. open      :    299f -> transparent blank
  2. c01 + c02 :  60942f -> piano_p1_box.png (FI 1.20s, FO 1.50s)
  3. part2     :    149f -> transparent blank
  4. c03       :   7641f -> piano_p1_box.png (FI 1.00s, FO 2.50s)
  5. gap       :    104f -> transparent blank
  6. c04 + c05a:  87096f -> piano_p2_box.png (FI 2.00s, FO 1.50s before standing bow tilt)
  7. c05b + end:   1167f -> transparent blank (covers bow tilt + ending credits + pad)
"""
import os
import sys
import glob
import json
import time
import shutil
import subprocess
from PIL import Image, ImageDraw, ImageFont

DRAFT_DIR    = r"G:\マイドライブ\git\nobuyukitakahashi\02_Creative_Dept\davinci\drafts\2026-11-19_ワインとジャズのコンサート"
FINAL_DIR    = r"G:\マイドライブ\git\nobuyukitakahashi\02_Creative_Dept\davinci\final_outputs\2026-11-19_ワインとジャズのコンサート"
DELIVERY_DIR = r"G:\マイドライブ\git\nobuyukitakahashi\04_Delivery_Dept\outputs\davinci\2026-11-19_ワインとジャズのコンサート"
GFX_DIR      = os.path.join(DRAFT_DIR, "graphics")
WORK_DIR     = os.path.join(DRAFT_DIR, "piano_logo_work")
DESKTOP_DIR  = r"C:\Users\nobuy\Desktop"

MP4_FINAL = os.path.join(DESKTOP_DIR, "2026-11-19_ワインとジャズのコンサート_Master_4K.mp4")
MP4_TMP   = os.path.join(DESKTOP_DIR, "_tmp_2026-11-19_ワインとジャズのコンサート_Master_4K_PianoLogo.mp4")

P1_FULL   = os.path.join(GFX_DIR, "piano_logo_part1.png")
P2_FULL   = os.path.join(GFX_DIR, "piano_logo_part2.png")
BOX_BLANK = os.path.join(WORK_DIR, "piano_box_blank.png")
BOX_P1    = os.path.join(WORK_DIR, "piano_box_p1.png")
BOX_P2    = os.path.join(WORK_DIR, "piano_box_p2.png")

FFMPEG  = glob.glob(r"C:\Users\nobuy\AppData\Local\Microsoft\WinGet\Packages\*FFmpeg*\**\ffmpeg.exe", recursive=True)[0]
FFPROBE = glob.glob(r"C:\Users\nobuy\AppData\Local\Microsoft\WinGet\Packages\*FFmpeg*\**\ffprobe.exe", recursive=True)[0]

# Shared bounding box covering both Part 1 and Part 2 piano logos (even dimensions for yuva420p)
BOX_X0, BOX_Y0, BOX_X1, BOX_Y1 = 0, 770, 780, 1590  # 780 x 820

def archive_in_resolve():
    """Refresh 4K piano logo assets in Resolve Media Pool bin 04_Piano_Logo & export .drp."""
    try:
        os.environ["RESOLVE_SCRIPT_API"] = r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting"
        os.environ["RESOLVE_SCRIPT_LIB"] = r"C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll"
        sys.path.append(r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules")
        import DaVinciResolveScript as dvr
        res = dvr.scriptapp("Resolve")
        if not res:
            return
        pm = res.GetProjectManager()
        proj = pm.GetCurrentProject()
        mp = proj.GetMediaPool()
        root = mp.GetRootFolder()
        subs = {sf.GetName(): sf for sf in root.GetSubFolderList()}
        b = subs.get("04_Piano_Logo") or mp.AddSubFolder(root, "04_Piano_Logo")
        mp.SetCurrentFolder(b)
        # Re-import fresh PNGs (replace existing if present)
        old_clips = b.GetClipList() or []
        if old_clips:
            mp.DeleteClips(old_clips)
        mp.ImportMedia([P1_FULL, P2_FULL])
        pm.SaveProject()
        drp_out = os.path.join(FINAL_DIR, "ワインとジャズのコンサート.drp")
        pm.ExportProject(proj.GetName(), drp_out, True)
        shutil.copy2(drp_out, os.path.join(DELIVERY_DIR, "ワインとジャズのコンサート.drp"))
        print("Updated Resolve bin 04_Piano_Logo & .drp archive.", flush=True)
    except Exception as e:
        print(f"Resolve archive note: {e}", flush=True)

def main():
    os.makedirs(WORK_DIR, exist_ok=True)
    bw, bh = BOX_X1 - BOX_X0, BOX_Y1 - BOX_Y0
    Image.new("RGBA", (bw, bh), (0, 0, 0, 0)).save(BOX_BLANK)
    Image.open(P1_FULL).crop((BOX_X0, BOX_Y0, BOX_X1, BOX_Y1)).save(BOX_P1)
    Image.open(P2_FULL).crop((BOX_X0, BOX_Y0, BOX_X1, BOX_Y1)).save(BOX_P2)
    print(f"Prepared shared {bw}x{bh} overlay boxes at ({BOX_X0},{BOX_Y0}).", flush=True)

    archive_in_resolve()

    # Exact frame-locked concat into ONE single overlay_cuda filter (zero context conflict!)
    FPS_STR = "30000/1001"
    fc = (
        "[0:v]scale_cuda=format=yuv420p[base];"
        f"[1:v]format=yuva420p,split=4[b0][b1][b2][b3];"
        f"[b0]loop=loop=298:size=1:start=0,setpts=N/({FPS_STR})/TB[s0];"
        f"[2:v]format=yuva420p,split=2[p1a][p1b];"
        f"[p1a]loop=loop=60941:size=1:start=0,setpts=N/({FPS_STR})/TB,"
        "fade=t=in:st=0:d=1.20:alpha=1,fade=t=out:st=2031.93:d=1.50:alpha=1[s1];"
        f"[b1]loop=loop=148:size=1:start=0,setpts=N/({FPS_STR})/TB[s2];"
        f"[p1b]loop=loop=7640:size=1:start=0,setpts=N/({FPS_STR})/TB,"
        "fade=t=in:st=0:d=1.00:alpha=1,fade=t=out:st=252.45:d=2.50:alpha=1[s3];"
        f"[b2]loop=loop=103:size=1:start=0,setpts=N/({FPS_STR})/TB[s4];"
        f"[3:v]format=yuva420p,loop=loop=87095:size=1:start=0,setpts=N/({FPS_STR})/TB,"
        "fade=t=in:st=0:d=2.00:alpha=1,fade=t=out:st=2904.61:d=1.50:alpha=1[s5];"
        f"[b3]loop=loop=1166:size=1:start=0,setpts=N/({FPS_STR})/TB[s6];"
        "[s0][s1][s2][s3][s4][s5][s6]concat=n=7:v=1:a=0,hwupload_cuda[ov];"
        f"[base][ov]overlay_cuda=x={BOX_X0}:y={BOX_Y0}:shortest=1[out]"
    )

    t0 = time.time()
    print("Starting single-stage GPU overlay_cuda + h264_nvenc 4K render...", flush=True)
    cmd = [
        FFMPEG, "-y", "-hide_banner", "-loglevel", "warning", "-stats",
        "-hwaccel", "cuda", "-hwaccel_output_format", "cuda",
        "-i", MP4_FINAL,
        "-i", BOX_BLANK,
        "-i", BOX_P1,
        "-i", BOX_P2,
        "-filter_complex", fc,
        "-map", "[out]", "-map", "0:a",
        "-c:v", "h264_nvenc", "-preset", "p4", "-rc", "vbr", "-cq", "20",
        "-b:v", "22M", "-maxrate", "28M", "-bufsize", "40M",
        "-profile:v", "high",
        "-c:a", "copy",
        "-movflags", "+faststart",
        MP4_TMP
    ]
    r = subprocess.run(cmd)
    if r.returncode != 0:
        raise RuntimeError(f"FFmpeg overlay_cuda render failed with code {r.returncode}")

    sz_gb = os.path.getsize(MP4_TMP) / (1024 ** 3)
    print(f"GPU render finished in {time.time()-t0:.1f}s -> {sz_gb:.2f} GB", flush=True)

    # Verify with ffprobe
    pr = subprocess.run(
        [FFPROBE, "-v", "error", "-show_format", "-show_streams", "-of", "json", MP4_TMP],
        capture_output=True, text=True, check=True
    )
    info = json.loads(pr.stdout)
    dur = float(info["format"]["duration"])
    br = int(info["format"]["bit_rate"]) // 1000
    print(f"FFprobe verified: duration={dur:.2f}s | bitrate={br} kbps", flush=True)
    if dur < 5240:
        raise RuntimeError(f"Unexpected short duration: {dur}")

    # Atomic swap into final Desktop master MP4
    os.replace(MP4_TMP, MP4_FINAL)
    print(f"Updated Desktop final 4K master: {MP4_FINAL} ({sz_gb:.2f} GB)", flush=True)

    # Extract updated 12-frame audit board directly from the final Desktop MP4
    v_dir = os.path.join(WORK_DIR, "final_mp4_stills")
    os.makedirs(v_dir, exist_ok=True)
    audit_spots = [
        ("01_open.jpg",     5.0,    "01. Opening Title (Official Logos)"),
        ("02_jounetsu.jpg", 20.0,   "02. Part 1: 情熱大陸 + Piano Logo"),
        ("03_suzuki.jpg",   410.0,  "03. Member Intro: 鈴木 真明地 + Piano Logo"),
        ("04_nishiura.jpg", 575.0,  "04. Member Intro: 西浦 颯 + Piano Logo"),
        ("05_part2.jpg",    2045.8, "05. Part 2 Card (Logo OFF)"),
        ("06_seiko1.jpg",   2057.0, "06. 松田聖子メドレー 01 + Piano Logo"),
        ("07_bridge.jpg",   2304.8, "07. Recording-Gap Bridge (Logo OFF)"),
        ("08_seiko4.jpg",   2314.0, "08. Clip 04 Resume + Piano Logo (Part 2)"),
        ("09_stevie1.jpg",  2880.0, "09. Stevie Medley 01 + Piano Logo"),
        ("10_julia.jpg",    4437.0, "10. チェッカーズ 04 + Piano Logo"),
        ("11_encore.jpg",   4900.0, "11. ★ ENCORE: September + Piano Logo"),
        ("12_ending.jpg",   5246.5, "12. Ending Credits (Logo OFF)"),
    ]
    thumbs = []
    for fn, sec, cap in audit_spots:
        out_jpg = os.path.join(v_dir, fn)
        subprocess.run(
            [FFMPEG, "-y", "-hide_banner", "-loglevel", "error", "-ss", str(sec), "-i", MP4_FINAL, "-frames:v", "1", "-q:v", "2", out_jpg],
            check=True
        )
        thumbs.append((out_jpg, cap))

    cols, rows = 4, 3
    tw, th, ch = 640, 360, 36
    board = Image.new("RGB", (cols * tw, rows * (th + ch)), (14, 10, 12))
    draw = ImageDraw.Draw(board)
    f_cap = ImageFont.truetype(r"C:\Windows\Fonts\yumindb.ttf", 20)
    for i, (p, cap) in enumerate(thumbs):
        r_i, c_i = divmod(i, cols)
        im = Image.open(p).convert("RGB").resize((tw, th), Image.Resampling.LANCZOS)
        x, y = c_i * tw, r_i * (th + ch)
        board.paste(im, (x, y))
        draw.rectangle([x, y + th, x + tw, y + th + ch], fill=(32, 12, 16))
        draw.text((x + 12, y + th + 7), cap, font=f_cap, fill=(244, 224, 180))

    for dst in (
        os.path.join(DRAFT_DIR, "keyframes_audit_board.png"),
        os.path.join(FINAL_DIR, "keyframes_audit_board.png"),
        os.path.join(DELIVERY_DIR, "keyframes_audit_board.png"),
    ):
        board.save(dst, quality=94)
    print("Updated 12-frame keyframes_audit_board.png across all folders!", flush=True)
    print("PIANO LOGO MASTER UPDATE COMPLETE!", flush=True)

if __name__ == "__main__":
    main()
