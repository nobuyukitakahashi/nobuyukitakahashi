import numpy as np
import os

draft_dir = r"g:\マイドライブ\git\nobuyukitakahashi\02_Creative_Dept\davinci\drafts\2026-11-13_南信州広域連合議会_全員協議会"
data = np.load(os.path.join(draft_dir, "audio_envelopes_10hz.npz"))
mp3_1328_db = data["MP3_1328_db"]

print("=== MP3_1328 first 70 seconds (1s resolution) ===")
for s in range(0, 70):
    chunk = mp3_1328_db[s*10:(s+1)*10]
    print(f"  MP3_1328 t={s:3d}s (PB17 ~ {s-36.6:5.1f}s): max={chunk.max():5.1f} dB, min={chunk.min():5.1f} dB, mean={chunk.mean():5.1f} dB")

print("\n=== Look for major pauses (gaps > 1.5s where dB < -38 dB) in MP3_1328 [0s..660s] ===")
is_quiet = mp3_1328_db[:6600] < -35.0
# find runs of True >= 12 (1.2s)
in_run = False
run_start = 0
for i, q in enumerate(is_quiet):
    if q and not in_run:
        in_run = True
        run_start = i
    elif not q and in_run:
        in_run = False
        dur = (i - run_start) / 10.0
        if dur >= 1.2:
            mp3_s = run_start / 10.0
            mp3_e = i / 10.0
            print(f"  Pause in MP3_1328: {mp3_s:6.1f}s .. {mp3_e:6.1f}s (dur={dur:4.1f}s) | In PB17 (if offset=36.6s): {mp3_s-36.6:6.1f}s .. {mp3_e-36.6:6.1f}s")
