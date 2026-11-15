import aud
import numpy as np

video_path = r"H:\2026-11-13_南信州広域連合_連合長へ_要望書提出_録音一式\PB130002.MOV"
s = aud.Sound(video_path)
print("Specs:", s.specs)
data = s.data()
print("Audio data shape:", data.shape, "dtype:", data.dtype)

sr = s.specs[0]
fps = 29.97
total_sec = len(data) / sr
print(f"Total audio duration: {total_sec:.2f}s (sr={sr})")

# Compute RMS in 0.5s windows for the first 35s and last 25s
print("\n=== Audio RMS: First 35 seconds (0.5s windows) ===")
for i in range(70):
    t0 = i * 0.5
    t1 = (i + 1) * 0.5
    idx0 = int(t0 * sr)
    idx1 = min(len(data), int(t1 * sr))
    chunk = data[idx0:idx1]
    rms = float(np.sqrt(np.mean(chunk**2))) if len(chunk) > 0 else 0.0
    db = 20 * np.log10(max(rms, 1e-7))
    f0 = int(round(t0 * fps))
    bar = "#" * max(0, int((db + 60) * 0.8))
    print(f"t={t0:5.1f}-{t1:5.1f}s (f={f0:4d}) | {db:6.1f} dBFS | {bar}")

print("\n=== Audio RMS: Last 25 seconds (0.5s windows) ===")
start_i = int((total_sec - 25.0) * 2)
for i in range(start_i, int(total_sec * 2) + 1):
    t0 = i * 0.5
    t1 = min(total_sec, (i + 1) * 0.5)
    idx0 = int(t0 * sr)
    idx1 = min(len(data), int(t1 * sr))
    if idx1 <= idx0:
        continue
    chunk = data[idx0:idx1]
    rms = float(np.sqrt(np.mean(chunk**2)))
    db = 20 * np.log10(max(rms, 1e-7))
    f0 = int(round(t0 * fps))
    bar = "#" * max(0, int((db + 60) * 0.8))
    print(f"t={t0:6.1f}-{t1:6.1f}s (f={f0:4d}) | {db:6.1f} dBFS | {bar}")
