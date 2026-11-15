import os
import struct
import datetime
import aud
import numpy as np

base_dir = r"H:\2026-11-13_南信州広域連合_連合長へ_要望書提出_録音一式"

def read_mvhd_times(filepath):
    """Search for mvhd atom in MOV/M4A file and extract creation_time, modification_time, timescale, duration."""
    with open(filepath, "rb") as f:
        # Read first 10MB and last 10MB
        size = os.path.getsize(filepath)
        chunks = [(0, f.read(min(size, 10 * 1024 * 1024)))]
        if size > 10 * 1024 * 1024:
            f.seek(max(0, size - 10 * 1024 * 1024))
            chunks.append((f.tell(), f.read()))
        
        for base_off, data in chunks:
            idx = data.find(b"mvhd")
            if idx != -1:
                version = data[idx+4]
                if version == 0:
                    ctime, mtime, ts, dur = struct.unpack(">IIII", data[idx+8:idx+24])
                else:
                    ctime, mtime, ts, dur = struct.unpack(">QQIQ", data[idx+8:idx+36])
                epoch_1904 = datetime.datetime(1904, 1, 1, tzinfo=datetime.timezone.utc)
                dt_c = epoch_1904 + datetime.timedelta(seconds=ctime)
                dt_m = epoch_1904 + datetime.timedelta(seconds=mtime)
                return ctime, mtime, ts, dur, dt_c, dt_m
    return None

files_to_check = [
    os.path.join(base_dir, "PB130017.MOV"),
    os.path.join(base_dir, "PB130018.MOV"),
    os.path.join(base_dir, "PB130019.MOV"),
    os.path.join(base_dir, "11月13日（12-40）事前打合せ", "11月13日（12-40）事前打合せ.m4a"),
    os.path.join(base_dir, "11月13日（13-28）南信州広域連合議会 第2回 全員協議会", "11月13日（13-28）南信州広域連合議会 第2回 全員協議会.m4a"),
    os.path.join(base_dir, "11月13日（14-12）南信州広域連合議会 第2回 全員協議会 資料3 桐林クリーンセンター解体について", "11月13日（14-12）南信州広域連合議会 第2回 全員協議会 資料3 桐林クリーンセンター解体について.m4a"),
]

print("=== 1. QuickTime mvhd Atom & Filesystem Exact Timestamps ===")
mvhd_info = {}
for p in files_to_check:
    name = os.path.basename(p)
    st = os.stat(p)
    res = read_mvhd_times(p)
    mvhd_info[name] = (st, res)
    print(f"\nFile: {name}")
    print(f"  FS ctime: {datetime.datetime.fromtimestamp(st.st_ctime)} ({st.st_ctime:.3f})")
    print(f"  FS mtime: {datetime.datetime.fromtimestamp(st.st_mtime)} ({st.st_mtime:.3f})")
    if res:
        ctime, mtime, ts, dur, dt_c, dt_m = res
        print(f"  mvhd ctime: {dt_c} (raw={ctime}), mtime: {dt_m} (raw={mtime}), dur={dur/ts:.3f}s (ts={ts})")

# Compare camera mvhd ctime difference between PB130017 and PB130019
c17 = mvhd_info["PB130017.MOV"][1][0]
c18 = mvhd_info["PB130018.MOV"][1][0]
c19 = mvhd_info["PB130019.MOV"][1][0]
print(f"\nCamera mvhd creation_time diffs:")
print(f"  PB130018 - PB130017 = {c18 - c17}s")
print(f"  PB130019 - PB130017 = {c19 - c17}s ({(c19 - c17)//60}m {(c19 - c17)%60}s)")

# Compare recorder mvhd ctime difference between 13-28.m4a and 14-12.m4a
r1328 = mvhd_info["11月13日（13-28）南信州広域連合議会 第2回 全員協議会.m4a"][1]
r1412 = mvhd_info["11月13日（14-12）南信州広域連合議会 第2回 全員協議会 資料3 桐林クリーンセンター解体について.m4a"][1]
if r1328 and r1412:
    # Note: on some recorders mvhd ctime is recording start or end
    print(f"\nRecorder mvhd ctime diff (14-12 - 13-28): {r1412[0] - r1328[0]}s")
    start_1328 = r1328[0] - r1328[3]/r1328[2]
    start_1412 = r1412[0] - r1412[3]/r1412[2]
    print(f"If mvhd ctime is END time, then start_1412 - start_1328 = {start_1412 - start_1328:.2f}s")

print("\n=== 2. High-Precision (1000 Hz) Envelope Cross-Correlation for PB130019 vs MP3_1412 ===")
sr = 1000
pb19_s = aud.Sound(os.path.join(base_dir, "PB130019.MOV")).rechannel(1).resample(sr, False).data()[:, 0]
mp3_1412_s = aud.Sound(os.path.join(base_dir, "11月13日（14-12）南信州広域連合議会 第2回 全員協議会 資料3 桐林クリーンセンター解体について", "11月13日（14-12）南信州広域連合議会 第2回 全員協議会 資料3 桐林クリーンセンター解体について.mp3")).rechannel(1).resample(sr, False).data()[:, 0]
m4a_1412_s = aud.Sound(os.path.join(base_dir, "11月13日（14-12）南信州広域連合議会 第2回 全員協議会 資料3 桐林クリーンセンター解体について", "11月13日（14-12）南信州広域連合議会 第2回 全員協議会 資料3 桐林クリーンセンター解体について.m4a")).rechannel(1).resample(sr, False).data()[:, 0]

# Compute 100Hz (10ms) amplitude envelope
hop = 10 # 10ms at 1000Hz
pb19_env = np.abs(pb19_s[:len(pb19_s)//hop * hop]).reshape(-1, hop).mean(axis=1)
mp3_env = np.abs(mp3_1412_s[:len(mp3_1412_s)//hop * hop]).reshape(-1, hop).mean(axis=1)
m4a_env = np.abs(m4a_1412_s[:len(m4a_1412_s)//hop * hop]).reshape(-1, hop).mean(axis=1)

for t_sec in [1100, 1500, 2000, 2500, 3000, 3500, 4000, 4400]:
    s_i = t_sec * 100
    e_i = (t_sec + 120) * 100 # 120s window
    sub = pb19_env[s_i:e_i]
    sub = (sub - sub.mean()) / (sub.std() + 1e-12)
    # Search lag around 12.60s (10.0s to 15.0s -> 1000 to 1500 in 10ms units)
    best_lag_mp3 = None
    best_c_mp3 = -1
    best_lag_m4a = None
    best_c_m4a = -1
    for lag_offset in range(1000, 1500):
        idx = s_i + lag_offset
        w1 = mp3_env[idx:idx+len(sub)]
        c1 = np.dot(sub, (w1 - w1.mean()) / (w1.std() + 1e-12)) / len(sub)
        if c1 > best_c_mp3:
            best_c_mp3 = c1
            best_lag_mp3 = lag_offset / 100.0
        w2 = m4a_env[idx:idx+len(sub)]
        c2 = np.dot(sub, (w2 - w2.mean()) / (w2.std() + 1e-12)) / len(sub)
        if c2 > best_c_m4a:
            best_c_m4a = c2
            best_lag_m4a = lag_offset / 100.0
    print(f"  t={t_sec:4d}s: MP3 offset = +{best_lag_mp3:.2f}s (corr={best_c_mp3:.4f}) | M4A offset = +{best_lag_m4a:.2f}s (corr={best_c_m4a:.4f})")
