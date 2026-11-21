import os
import json
import subprocess
import numpy as np
from PIL import Image

FFMPEG = r"C:\Users\nobuy\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.1-full_build\bin\ffmpeg.exe"
SRC_DIR = r"H:\2026-11-19_ワインとジャズのコンサート\DJI_001"
DRAFT_DIR = r"G:\マイドライブ\git\nobuyukitakahashi\02_Creative_Dept\davinci\drafts\2026-11-19_ワインとジャズのコンサート"
PROBE_DIR = os.path.join(DRAFT_DIR, "precision_probes")
os.makedirs(PROBE_DIR, exist_ok=True)

def cut_mp3(mp4_name, start_s, dur_s, out_name):
    src = os.path.join(SRC_DIR, mp4_name)
    out = os.path.join(PROBE_DIR, out_name)
    subprocess.check_call([
        FFMPEG, "-v", "error", "-y",
        "-ss", f"{start_s:.2f}", "-t", f"{dur_s:.2f}",
        "-i", src, "-vn", "-ac", "1", "-ar", "24000", "-b:a", "64k", out
    ])
    return out

# 1. Precision audio probes for Checkers Medley verification (4 parts)
cut_mp3("DJI_20000101090033_0004_D.MP4", 1940, 68, "checkers_1_c04_1940-2008.mp3")
cut_mp3("DJI_20000101090033_0004_D.MP4", 2005, 81, "checkers_2_c04_2005-2086.mp3")
cut_mp3("DJI_20000101093520_0005_D.MP4", 0, 150, "checkers_3_c05_0-150.mp3")

# 2. Precision audio probe for Clip 03 end + Clip 04 start (Seiko Matsuda medley gap)
cut_mp3("DJI_20261119202831_0003_D.MP4", 235, 32, "seiko_end_c03_235-267.mp3")
cut_mp3("DJI_20000101090033_0004_D.MP4", 0, 66, "seiko_resume_c04_0-66.mp3")

# 3. Full-res 4K sample frames (cropped/scaled to 1920x1080 for visual & color audit)
for tag, mp4, ts in [
    ("c01_play", "DJI_20261119192743_0001_D.MP4", 220),
    ("c01_intro", "DJI_20261119192743_0001_D.MP4", 600),
    ("c03_play", "DJI_20261119202831_0003_D.MP4", 60),
    ("c04_start", "DJI_20000101090033_0004_D.MP4", 15),
    ("c04_mid", "DJI_20000101090033_0004_D.MP4", 650),
    ("c05_encore", "DJI_20000101093520_0005_D.MP4", 550),
]:
    out_jpg = os.path.join(PROBE_DIR, f"frame_{tag}.jpg")
    subprocess.check_call([
        FFMPEG, "-v", "error", "-y", "-ss", str(ts), "-i", os.path.join(SRC_DIR, mp4),
        "-frames:v", "1", "-vf", "scale=1920:1080", "-q:v", "3", out_jpg
    ])
    im = np.array(Image.open(out_jpg), dtype=np.float32)
    y = 0.299*im[:,:,0] + 0.587*im[:,:,1] + 0.114*im[:,:,2]
    print(f"Frame {tag}: meanY={y.mean():.1f}, R={im[:,:,0].mean():.1f}, G={im[:,:,1].mean():.1f}, B={im[:,:,2].mean():.1f}, p99={np.percentile(y,99):.1f}")

# 4. Shake / Vibration measurement using ffmpeg vidstabdetect or frame-diff on LRF clips (sample 10-second windows!)
print("\n=== Camera Vibration / Shake Measurement (Frame-to-Frame 2D Shift on 10s windows) ===")
def measure_shake(lrf_name, start_s, dur_s=8.0):
    src = os.path.join(SRC_DIR, lrf_name)
    # Extract 320x180 gray frames at 15fps
    raw = subprocess.check_output([
        FFMPEG, "-v", "error", "-ss", str(start_s), "-t", str(dur_s),
        "-i", src, "-vf", "fps=15,scale=320:180,format=gray", "-f", "rawvideo", "-"
    ])
    n = len(raw) // (320 * 180)
    frames = np.frombuffer(raw[:n*320*180], dtype=np.uint8).reshape(n, 180, 320).astype(np.float32)
    # Use static background region (top-left painting & top-right wall/arch: y=10..80, x=0..320)
    bg = frames[:, 10:80, :]
    diffs = np.mean(np.abs(np.diff(bg, axis=0)), axis=(1,2))
    # Phase correlation on top wall strip for pixel shift
    shifts = []
    for i in range(len(bg)-1):
        f1 = np.fft.fft2(bg[i] - bg[i].mean())
        f2 = np.fft.fft2(bg[i+1] - bg[i+1].mean())
        R = (f1 * np.conj(f2)) / (np.abs(f1 * np.conj(f2)) + 1e-8)
        cc = np.abs(np.fft.ifft2(R))
        py, px = np.unravel_index(np.argmax(cc), cc.shape)
        if py > bg.shape[1]//2: py -= bg.shape[1]
        if px > bg.shape[2]//2: px -= bg.shape[2]
        shifts.append(np.hypot(px, py))
    return float(np.mean(diffs)), float(np.max(diffs)), float(np.mean(shifts)), float(np.max(shifts))

for label, lrf, ts in [
    ("Clip01 Song1 (t=240s)", "DJI_20261119192743_0001_D.LRF", 240),
    ("Clip01 MC (t=600s)", "DJI_20261119192743_0001_D.LRF", 600),
    ("Clip01 SingSingSing (t=1900s)", "DJI_20261119192743_0001_D.LRF", 1900),
    ("Clip02 SingSingSing (t=60s)", "DJI_20261119200046_0002_D.LRF", 60),
    ("Clip03 Seiko (t=60s)", "DJI_20261119202831_0003_D.LRF", 60),
    ("Clip04 Start (t=10s)", "DJI_20000101090033_0004_D.LRF", 10),
    ("Clip04 Stevie (t=600s)", "DJI_20000101090033_0004_D.LRF", 600),
    ("Clip04 Matsuken (t=1650s)", "DJI_20000101090033_0004_D.LRF", 1650),
    ("Clip05 Encore (t=600s)", "DJI_20000101093520_0005_D.LRF", 600),
]:
    md, xd, ms, xs = measure_shake(lrf, ts)
    print(f"  {label:30s}: bgDiff mean={md:.2f} max={xd:.2f} | shift(px@180p) mean={ms:.2f} max={xs:.2f}")

# 5. Exact RMS timeline (0.5s bins) around Member Intros & Song Transitions for pinpoint timing
def fine_rms(mp4_name, start_s, end_s):
    src = os.path.join(SRC_DIR, mp4_name)
    raw = subprocess.check_output([
        FFMPEG, "-v", "error", "-ss", str(start_s), "-t", str(end_s - start_s),
        "-i", src, "-ac", "1", "-ar", "8000", "-f", "s16le", "-"
    ])
    s = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
    step = 4000 # 0.5s
    vals = []
    for i in range(0, len(s) - step + 1, step):
        r = np.sqrt(np.mean(s[i:i+step]**2) + 1e-12)
        vals.append((round(start_s + i/8000.0, 1), round(float(20*np.log10(r)), 1)))
    return vals

# Check exact silence/start points of each song
print("\n=== Fine RMS around Song Starts / Ends ===")
windows = [
    ("C01 Song1 start", "DJI_20261119192743_0001_D.MP4", 170, 195),
    ("C01 Song2 start (Take5)", "DJI_20261119192743_0001_D.MP4", 805, 830),
    ("C01 Song3 start (Champs)", "DJI_20261119192743_0001_D.MP4", 1120, 1140),
    ("C01 Song4 start (ATrain)", "DJI_20261119192743_0001_D.MP4", 1475, 1495),
    ("C01 Song5 start (Sing)", "DJI_20261119192743_0001_D.MP4", 1860, 1880),
    ("C02 End / Break", "DJI_20261119200046_0002_D.MP4", 190, 235),
    ("C03 Start (Seiko)", "DJI_20261119202831_0003_D.MP4", 5, 25),
    ("C04 Song2 start (Cherbourg)", "DJI_20000101090033_0004_D.MP4", 180, 200),
    ("C04 Song3 start (Stevie)", "DJI_20000101090033_0004_D.MP4", 560, 585),
    ("C04 Song4 start (BeatIt)", "DJI_20000101090033_0004_D.MP4", 818, 838),
    ("C04 Song5 start (Beauty)", "DJI_20000101090033_0004_D.MP4", 1088, 1110),
    ("C04 Song6 start (Matsuken)", "DJI_20000101090033_0004_D.MP4", 1625, 1645),
    ("C04 Song7 start (Checkers)", "DJI_20000101090033_0004_D.MP4", 1940, 1960),
    ("C05 Song8 start (Miagete)", "DJI_20000101093520_0005_D.MP4", 258, 278),
    ("C05 Encore start (Sept)", "DJI_20000101093520_0005_D.MP4", 492, 520),
]
for label, mp4, a, b in windows:
    vals = fine_rms(mp4, a, b)
    s = " ".join(f"{t}:{db}" for t, db in vals[::2])
    print(f"  {label:28s} -> {s}")
