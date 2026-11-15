import os
import numpy as np

base_dir = r"H:\2026-11-13_南信州広域連合_連合長へ_要望書提出_録音一式"
draft_dir = r"g:\マイドライブ\git\nobuyukitakahashi\02_Creative_Dept\davinci\drafts\2026-11-13_南信州広域連合議会_全員協議会"

# 1. Slice 400s..660s of 13-28.mp3 (128kbps = 16000 bytes/sec)
mp3_1328 = os.path.join(base_dir, "11月13日（13-28）南信州広域連合議会 第2回 全員協議会", "11月13日（13-28）南信州広域連合議会 第2回 全員協議会.mp3")
sz_1328 = os.path.getsize(mp3_1328)
bps_1328 = sz_1328 / 2611.696
print(f"13-28.mp3 size={sz_1328}, bps={bps_1328:.1f}")

with open(mp3_1328, "rb") as f:
    f.seek(int(400 * bps_1328))
    data = f.read(int(260 * bps_1328))
with open(os.path.join(draft_dir, "mp3_1328_400_660.mp3"), "wb") as f:
    f.write(data)

# 2. Slice 14-12_48.mp3 (48kbps = 6000 bytes/sec) into 6 chunks of 800s
mp3_1412_48 = os.path.join(base_dir, "11月13日（14-12）南信州広域連合議会 第2回 全員協議会 資料3 桐林クリーンセンター解体について", "11月13日（14-12）南信州広域連合議会 第2回 全員協議会 資料3 桐林クリーンセンター解体について_48.mp3")
sz_1412 = os.path.getsize(mp3_1412_48)
bps_1412 = sz_1412 / 5107.696
print(f"14-12_48.mp3 size={sz_1412}, bps={bps_1412:.1f}")

chunks = [
    (0, 800),
    (800, 1600),
    (1600, 2400),
    (2400, 3200),
    (3200, 4000),
    (4000, 4660),
]

with open(mp3_1412_48, "rb") as f:
    for s, e in chunks:
        f.seek(int(s * bps_1412))
        d = f.read(int((e - s) * bps_1412))
        out_p = os.path.join(draft_dir, f"mp3_1412_{s:04d}_{e:04d}.mp3")
        with open(out_p, "wb") as fo:
            fo.write(d)
        print(f"Saved {out_p} ({len(d)} bytes)")
