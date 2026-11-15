import numpy as np
import os

draft_dir = r"g:\マイドライブ\git\nobuyukitakahashi\02_Creative_Dept\davinci\drafts\2026-11-13_南信州広域連合議会_全員協議会"
data = np.load(os.path.join(draft_dir, "audio_envelopes_10hz.npz"))
mp3_1412_db = data["MP3_1412_db"]

is_quiet = mp3_1412_db[:46600] < -36.0
in_run = False
run_start = 0
print("=== Pauses >= 1.5s in MP3_1412 (0s..4660s) ===")
for i, q in enumerate(is_quiet):
    if q and not in_run:
        in_run = True
        run_start = i
    elif not q and in_run:
        in_run = False
        dur = (i - run_start) / 10.0
        if dur >= 1.5:
            mp3_s = run_start / 10.0
            mp3_e = i / 10.0
            pb19_s = mp3_s - 12.63
            pb19_e = mp3_e - 12.63
            m_s, s_s = divmod(max(0, pb19_s), 60)
            print(f"MP3: {mp3_s:6.1f}s..{mp3_e:6.1f}s (dur={dur:4.1f}s) | PB19: {pb19_s:6.1f}s..{pb19_e:6.1f}s ({int(m_s):02d}:{s_s:04.1f})")
