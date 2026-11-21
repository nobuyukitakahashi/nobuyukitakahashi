# -*- coding: utf-8 -*-
"""
Convert all 4K graphics PNGs into exact-duration 29.97fps MOV clips for DaVinci Resolve:
  - 4 full-screen cards -> H.264 visually lossless MP4/MOV (exact duration)
  - 28 transparent RGBA telops -> QuickTime Animation (qtrle argb) MOV with straight alpha (exact duration)
Runs in parallel via ThreadPoolExecutor.
"""
import os
import glob
import time
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed

DRAFT_DIR = r"G:\マイドライブ\git\nobuyukitakahashi\02_Creative_Dept\davinci\drafts\2026-11-19_ワインとジャズのコンサート"
GFX_DIR = os.path.join(DRAFT_DIR, "graphics")
MOV_DIR = os.path.join(DRAFT_DIR, "graphics_mov")
os.makedirs(MOV_DIR, exist_ok=True)

ff_candidates = glob.glob(r"C:\Users\nobuy\AppData\Local\Microsoft\WinGet\Packages\*FFmpeg*\**\ffmpeg.exe", recursive=True)
FFMPEG = ff_candidates[0]

# (png_name, frames_at_29_97, is_alpha)
JOBS = [
    # Full-screen cards (RGB, H.264 high quality)
    ("00_opening_title.png",   300, False),  # 10.0s
    ("01_part2_card.png",      150, False),  #  5.0s
    ("02_gap_bridge_card.png", 105, False),  #  3.5s
    ("99_ending_credits.png",  180, False),  #  6.0s

    # Member intros (RGBA straight alpha, 14s = 420f)
    ("member_01_suzuki.png",    420, True),
    ("member_02_watanabe.png",  420, True),
    ("member_03_takahashi.png", 420, True),
    ("member_04_tanaka.png",    420, True),
    ("member_05_nishiura.png",  420, True),

    # Songs & Medleys (RGBA straight alpha)
    ("song_01_jounetsu.png",     420, True),  # 14s
    ("song_02_takefive.png",     420, True),  # 14s
    ("song_03_champs.png",       420, True),  # 14s
    ("song_04_atrain.png",       420, True),  # 14s
    ("song_05_singsing.png",     420, True),  # 14s
    ("song_06_seiko_01.png",     420, True),  # 14s
    ("song_07_seiko_02.png",     420, True),  # 14s
    ("song_08_seiko_03.png",     480, True),  # 16s
    ("song_09_seiko_04.png",     420, True),  # 14s
    ("song_10_cherbourg.png",    420, True),  # 14s
    ("song_11_stevie_01.png",    390, True),  # 13s
    ("song_12_stevie_02.png",    390, True),  # 13s
    ("song_13_stevie_03.png",    390, True),  # 13s
    ("song_14_stevie_04.png",    390, True),  # 13s
    ("song_15_beatit.png",       420, True),  # 14s
    ("song_16_beauty.png",       420, True),  # 14s
    ("song_17_matsuken.png",     420, True),  # 14s
    ("song_18_checkers_01.png",  390, True),  # 13s
    ("song_19_checkers_02.png",  360, True),  # 12s
    ("song_20_checkers_03.png",  390, True),  # 13s
    ("song_21_checkers_04.png",  420, True),  # 14s
    ("song_22_miagete.png",      420, True),  # 14s
    ("song_23_september.png",    450, True),  # 15s
]

def encode_one(png_name, frames, is_alpha):
    src = os.path.join(GFX_DIR, png_name)
    base = os.path.splitext(png_name)[0]
    dst = os.path.join(MOV_DIR, base + ".mov")
    if is_alpha:
        cmd = [
            FFMPEG, "-y", "-hide_banner", "-loglevel", "error",
            "-loop", "1", "-framerate", "30000/1001", "-i", src,
            "-frames:v", str(frames),
            "-c:v", "qtrle", "-pix_fmt", "argb",
            dst
        ]
    else:
        cmd = [
            FFMPEG, "-y", "-hide_banner", "-loglevel", "error",
            "-loop", "1", "-framerate", "30000/1001", "-i", src,
            "-frames:v", str(frames),
            "-c:v", "libx264", "-crf", "12", "-preset", "fast", "-pix_fmt", "yuv420p",
            dst
        ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"FFmpeg failed for {png_name}: {r.stderr}")
    return base + ".mov", os.path.getsize(dst)

def main():
    t0 = time.time()
    total_bytes = 0
    with ThreadPoolExecutor(max_workers=4) as ex:
        futs = {ex.submit(encode_one, p, f, a): p for p, f, a in JOBS}
        done = 0
        for fut in as_completed(futs):
            name, sz = fut.result()
            total_bytes += sz
            done += 1
            if done % 8 == 0 or done == len(JOBS):
                print(f"[{done}/{len(JOBS)}] Latest: {name} ({sz/1024/1024:.1f} MB)")
    print(f"Encoded all {len(JOBS)} MOV assets in {time.time()-t0:.1f}s (total {total_bytes/1024/1024:.1f} MB)")

if __name__ == "__main__":
    main()
