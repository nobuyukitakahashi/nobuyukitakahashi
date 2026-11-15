import os
import subprocess
import json
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

input_dir = r"H:\2026-11-13_南信州広域連合_連合長へ_要望書提出_録音一式"
video_path = os.path.join(input_dir, "PB130002.MOV")
draft_dir = r"g:\マイドライブ\git\nobuyukitakahashi\02_Creative_Dept\davinci\drafts\2026-11-13_南信州広域連合へ要望書提出"
final_dir = r"g:\マイドライブ\git\nobuyukitakahashi\02_Creative_Dept\davinci\final_outputs\2026-11-13_南信州広域連合へ要望書提出"

os.makedirs(draft_dir, exist_ok=True)
os.makedirs(final_dir, exist_ok=True)

print("=== Directory Contents ===")
for f in os.listdir(input_dir):
    fp = os.path.join(input_dir, f)
    print(f, os.path.getsize(fp) if os.path.isfile(fp) else "DIR")

cap = cv2.VideoCapture(video_path)
fps = cap.get(cv2.CAP_PROP_FPS)
frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
duration = frame_count / fps if fps > 0 else 0

print(f"\n=== Video Metadata ===")
print(f"Resolution: {width}x{height}")
print(f"FPS: {fps}")
print(f"Frame Count: {frame_count}")
print(f"Duration: {duration:.2f} sec ({duration/60:.2f} min)")

# Analyze every 0.5 sec for first 25 sec and last 25 sec, plus overall brightness
def analyze_range(start_sec, end_sec, step_sec, out_img_name, cols=5):
    times = np.arange(start_sec, min(end_sec, duration), step_sec)
    thumbs = []
    stats = []
    prev_gray = None
    for t in times:
        f_idx = int(round(t * fps))
        cap.set(cv2.CAP_PROP_POS_FRAMES, f_idx)
        ret, frame = cap.read()
        if not ret:
            continue
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        mean_luma = float(np.mean(gray))
        p5 = float(np.percentile(gray, 5))
        p95 = float(np.percentile(gray, 95))
        diff = float(np.mean(cv2.absdiff(gray, prev_gray))) if prev_gray is not None else 0.0
        prev_gray = gray
        stats.append((t, f_idx, mean_luma, p5, p95, diff))
        
        # Resize for contact sheet
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(rgb).resize((384, 216), Image.Resampling.LANCZOS)
        draw = ImageDraw.Draw(pil_img)
        draw.rectangle([0, 0, 384, 32], fill=(0, 0, 0))
        draw.text((6, 6), f"t={t:.2f}s (f={f_idx}) Y={mean_luma:.1f} diff={diff:.1f}", fill=(255, 255, 0))
        thumbs.append(pil_img)
    
    rows = (len(thumbs) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * 384, rows * 216), (30, 30, 30))
    for i, th in enumerate(thumbs):
        r = i // cols
        c = i % cols
        sheet.paste(th, (c * 384, r * 216))
    out_path = os.path.join(draft_dir, out_img_name)
    sheet.save(out_path)
    print(f"Saved {out_path}")
    return stats

print("\n--- Analyzing Start (0s to 20s, step 0.5s) ---")
start_stats = analyze_range(0, 20, 0.5, "contact_start_0_20s.png", cols=5)
for s in start_stats:
    print(f"t={s[0]:5.2f}s | frame={s[1]:5d} | Y={s[2]:5.1f} (p5={s[3]:4.1f}, p95={s[4]:5.1f}) | diff={s[5]:5.2f}")

print(f"\n--- Analyzing End ({max(0, duration-20):.1f}s to {duration:.1f}s, step 0.5s) ---")
end_stats = analyze_range(max(0, duration - 20), duration, 0.5, "contact_end_last20s.png", cols=5)
for s in end_stats:
    print(f"t={s[0]:5.2f}s | frame={s[1]:5d} | Y={s[2]:5.1f} (p5={s[3]:4.1f}, p95={s[4]:5.1f}) | diff={s[5]:5.2f}")

print("\n--- Analyzing Overall Video (25 evenly spaced frames) ---")
step_all = max(0.5, duration / 25.0)
overall_stats = analyze_range(0, duration, step_all, "contact_overall.png", cols=5)
for s in overall_stats:
    print(f"t={s[0]:6.2f}s | frame={s[1]:5d} | Y={s[2]:5.1f} (p5={s[3]:4.1f}, p95={s[4]:5.1f})")

cap.release()
