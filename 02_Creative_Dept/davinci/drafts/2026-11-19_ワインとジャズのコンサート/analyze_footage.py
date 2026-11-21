import os
import json
import subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont

FFMPEG = r"C:\Users\nobuy\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.1-full_build\bin\ffmpeg.exe"
FFPROBE = r"C:\Users\nobuy\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.1-full_build\bin\ffprobe.exe"
SRC_DIR = r"H:\2026-11-19_ワインとジャズのコンサート\DJI_001"
DRAFT_DIR = r"G:\マイドライブ\git\nobuyukitakahashi\02_Creative_Dept\davinci\drafts\2026-11-19_ワインとジャズのコンサート"
AUDIO_DIR = os.path.join(DRAFT_DIR, "audio_chunks")
SHEET_DIR = os.path.join(DRAFT_DIR, "contact_sheets")
os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(SHEET_DIR, exist_ok=True)

CLIPS = [
    ("01", "DJI_20261119192743_0001_D", 1981.568, 59386),
    ("02", "DJI_20261119200046_0002_D", 255.6554, 7662),
    ("03", "DJI_20261119202831_0003_D", 267.0668, 8004),
    ("04", "DJI_20000101090033_0004_D", 2086.229333, 62523),
    ("05", "DJI_20000101093520_0005_D", 856.789267, 25678),
]

def fmt_ts(sec):
    m = int(sec // 60)
    s = int(sec % 60)
    return f"{m:02d}:{s:02d}"

def analyze_audio_stats(path):
    # Read 1-second RMS values using ffmpeg -> raw s16le 8kHz mono
    cmd = [
        FFMPEG, "-v", "error", "-i", path,
        "-ac", "1", "-ar", "8000", "-f", "s16le", "-"
    ]
    raw = subprocess.check_output(cmd)
    samples = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
    n_sec = len(samples) // 8000
    if n_sec == 0:
        return {"mean_dbfs": -99, "peak_dbfs": -99, "rms_per_sec": []}
    blocks = samples[:n_sec * 8000].reshape(n_sec, 8000)
    rms = np.sqrt(np.mean(blocks ** 2, axis=1) + 1e-12)
    rms_db = 20.0 * np.log10(rms)
    peak_db = float(20.0 * np.log10(np.max(np.abs(samples)) + 1e-12))
    mean_db = float(20.0 * np.log10(np.sqrt(np.mean(samples ** 2) + 1e-12)))
    return {
        "duration_s": round(len(samples) / 8000.0, 2),
        "mean_dbfs": round(mean_db, 2),
        "peak_dbfs": round(peak_db, 2),
        "rms_per_sec": [round(float(x), 1) for x in rms_db],
    }

def check_wav_vs_mp4():
    print("=== Comparing MP4 AAC vs WAV PCM (first 60s of Clip 01 and Clip 03) ===")
    for cid, base, dur, frames in [CLIPS[0], CLIPS[2]]:
        mp4 = os.path.join(SRC_DIR, base + ".MP4")
        wav = os.path.join(SRC_DIR, base + ".WAV")
        for label, p in [("MP4", mp4), ("WAV", wav)]:
            cmd = [FFMPEG, "-v", "error", "-t", "60", "-i", p, "-ac", "2", "-ar", "48000", "-f", "s16le", "-"]
            raw = subprocess.check_output(cmd)
            arr = np.frombuffer(raw, dtype=np.int16).reshape(-1, 2).astype(np.float32) / 32768.0
            l_db = 20 * np.log10(np.sqrt(np.mean(arr[:,0]**2) + 1e-12))
            r_db = 20 * np.log10(np.sqrt(np.mean(arr[:,1]**2) + 1e-12))
            pk = 20 * np.log10(np.max(np.abs(arr)) + 1e-12)
            corr = float(np.corrcoef(arr[::10,0], arr[::10,1])[0,1])
            print(f"  Clip {cid} {label}: L={l_db:.2f}dBFS, R={r_db:.2f}dBFS, Peak={pk:.2f}dBFS, StereoCorr={corr:.3f}")

def export_audio_chunks():
    print("\n=== Exporting MP3 audio chunks for listening/song identification ===")
    chunk_manifest = []
    for cid, base, dur, frames in CLIPS:
        # Use WAV if same duration, else MP4 (we'll check MP4 audio which is guaranteed frame-synced)
        src = os.path.join(SRC_DIR, base + ".MP4")
        # Split into ~540s (9 min) chunks with 10s overlap
        step = 540
        start = 0
        part = 1
        while start < dur:
            end = min(dur, start + step + 10)
            out_mp3 = os.path.join(AUDIO_DIR, f"clip{cid}_part{part}_{int(start)}s-{int(end)}s.mp3")
            if not os.path.exists(out_mp3):
                cmd = [
                    FFMPEG, "-v", "error", "-y",
                    "-ss", str(start), "-t", str(end - start),
                    "-i", src,
                    "-vn", "-ac", "1", "-ar", "24000", "-b:a", "48k",
                    out_mp3
                ]
                subprocess.check_call(cmd)
            chunk_manifest.append({
                "clip": cid, "base": base, "part": part,
                "start_s": start, "end_s": round(end, 1),
                "start_ts": fmt_ts(start), "end_ts": fmt_ts(end),
                "file": out_mp3
            })
            if start + step >= dur:
                break
            start += step
            part += 1
    print(f"  Exported {len(chunk_manifest)} audio chunks.")
    return chunk_manifest

def make_contact_sheet(video_path, timestamps, out_path, title, cols=4, thumb_w=384, thumb_h=216):
    imgs = []
    for ts in timestamps:
        cmd = [
            FFMPEG, "-v", "error",
            "-ss", f"{ts:.2f}", "-i", video_path,
            "-frames:v", "1", "-vf", f"scale={thumb_w}:{thumb_h}",
            "-f", "image2pipe", "-vcodec", "png", "-"
        ]
        try:
            data = subprocess.check_output(cmd)
            from io import BytesIO
            im = Image.open(BytesIO(data)).convert("RGB")
        except Exception:
            im = Image.new("RGB", (thumb_w, thumb_h), (30, 30, 30))
        draw = ImageDraw.Draw(im)
        label = f"{fmt_ts(ts)} ({ts:.1f}s)"
        draw.rectangle([4, 4, 150, 26], fill=(0, 0, 0))
        draw.text((8, 7), label, fill=(255, 230, 120))
        imgs.append(im)
    rows = (len(imgs) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * thumb_w, rows * thumb_h + 32), (18, 18, 18))
    draw = ImageDraw.Draw(sheet)
    draw.text((10, 8), title, fill=(255, 255, 255))
    for i, im in enumerate(imgs):
        r, c = divmod(i, cols)
        sheet.paste(im, (c * thumb_w, 32 + r * thumb_h))
    sheet.save(out_path, quality=85)

def build_sheets():
    print("\n=== Generating visual contact sheets (using fast .LRF proxy) ===")
    for cid, base, dur, frames in CLIPS:
        lrf = os.path.join(SRC_DIR, base + ".LRF")
        src = lrf if os.path.exists(lrf) else os.path.join(SRC_DIR, base + ".MP4")
        # Overview: 16 evenly spaced frames
        ts_over = [round(dur * i / 16.0, 1) for i in range(16)]
        make_contact_sheet(src, ts_over, os.path.join(SHEET_DIR, f"clip{cid}_overview.jpg"),
                           f"Clip {cid}: {base} (dur={fmt_ts(dur)}, {frames}f)")
        # Start (first 60s every 4s -> 16 frames)
        ts_start = [round(min(dur - 1, i * 4.0), 1) for i in range(16)]
        make_contact_sheet(src, ts_start, os.path.join(SHEET_DIR, f"clip{cid}_start.jpg"),
                           f"Clip {cid} START (0s..60s)")
        # End (last 60s every 4s -> 16 frames)
        t0 = max(0, dur - 62)
        ts_end = [round(min(dur - 0.5, t0 + i * 4.0), 1) for i in range(16)]
        make_contact_sheet(src, ts_end, os.path.join(SHEET_DIR, f"clip{cid}_end.jpg"),
                           f"Clip {cid} END ({fmt_ts(t0)}..{fmt_ts(dur)})")
    print("  Contact sheets generated.")

def summarize_rms(all_rms):
    print("\n=== Audio RMS Energy & Low-Level Gaps (potential song breaks / MC) ===")
    for cid, info in all_rms.items():
        arr = np.array(info["rms_per_sec"])
        print(f"  Clip {cid}: dur={info['duration_s']}s, mean={info['mean_dbfs']}dBFS, peak={info['peak_dbfs']}dBFS")
        # Find segments where 5-second smoothed RMS drops below (median - 10dB) -> breaks/MC
        if len(arr) >= 10:
            kernel = np.ones(5) / 5.0
            sm = np.convolve(arr, kernel, mode="same")
            med = float(np.median(sm))
            low = sm < (med - 8.0)
            in_seg = False
            s0 = 0
            segs = []
            for i, v in enumerate(low):
                if v and not in_seg:
                    in_seg = True
                    s0 = i
                elif not v and in_seg:
                    in_seg = False
                    if i - s0 >= 4:
                        segs.append((s0, i, round(float(np.mean(sm[s0:i])), 1)))
            if in_seg and len(low) - s0 >= 4:
                segs.append((s0, len(low), round(float(np.mean(sm[s0:])), 1)))
            print(f"    Median 5s-RMS={med:.1f}dBFS | Quieter/MC/Break segments ({len(segs)}):")
            for a, b, db in segs[:25]:
                print(f"      {fmt_ts(a)} - {fmt_ts(b)} ({b-a}s, avg {db}dBFS)")

if __name__ == "__main__":
    check_wav_vs_mp4()
    manifest = export_audio_chunks()
    build_sheets()
    all_rms = {}
    for cid, base, dur, frames in CLIPS:
        mp4 = os.path.join(SRC_DIR, base + ".MP4")
        all_rms[cid] = analyze_audio_stats(mp4)
    summarize_rms(all_rms)
    with open(os.path.join(DRAFT_DIR, "analysis_summary.json"), "w", encoding="utf-8") as f:
        json.dump({"clips": CLIPS, "chunks": manifest, "rms": all_rms}, f, ensure_ascii=False, indent=2)
    print("\nSaved analysis_summary.json successfully.")
