import numpy as np
import os

draft_dir = r"g:\マイドライブ\git\nobuyukitakahashi\02_Creative_Dept\davinci\drafts\2026-11-13_南信州広域連合議会_全員協議会"
data = np.load(os.path.join(draft_dir, "audio_envelopes_10hz.npz"))

pb19_rms = data["PB130019"]
pb19_db = data["PB130019_db"]
mp3_1412_rms = data["MP3_1412"]
mp3_1412_db = data["MP3_1412_db"]

pb17_rms = data["PB130017"]
pb17_db = data["PB130017_db"]
mp3_1328_rms = data["MP3_1328"]
mp3_1328_db = data["MP3_1328_db"]

# 1. Exact transition point in PB130019 where audio turns ON
for idx in range(10550, 10750):
    if pb19_db[idx] > -60:
        print(f"PB130019 audio turns ON at index {idx} ({idx/10.0:.1f}s): {pb19_db[idx]:.1f} dB")
        break

# Print 1s around turn-on
for idx in range(10600, 10680):
    print(f"  t={idx/10.0:6.1f}s: {pb19_db[idx]:5.1f} dB")

# 2. Cross-correlate PB130019 active audio (e.g. 1100s to 2000s) with MP3_1412
# Let's test segment 1: t_pb19 = 1100s to 1700s (600s = 6000 samples at 10Hz)
def correlate_segment(pb_arr, mp3_arr, t_start_sec, duration_sec):
    s_idx = int(t_start_sec * 10)
    e_idx = int((t_start_sec + duration_sec) * 10)
    sub = pb_arr[s_idx:e_idx].astype(np.float64)
    sub = (sub - sub.mean()) / (sub.std() + 1e-12)
    
    full = mp3_arr.astype(np.float64)
    n_lags = len(full) - len(sub)
    corrs = np.zeros(n_lags)
    for lag in range(n_lags):
        w = full[lag:lag+len(sub)]
        corrs[lag] = np.dot(sub, (w - w.mean()) / (w.std() + 1e-12)) / len(sub)
    best_lag = np.argmax(corrs)
    best_corr = corrs[best_lag]
    # lag is where t_start_sec of PB19 aligns in MP3_1412
    # So t_pb19 = 0.0 aligns with (best_lag/10.0 - t_start_sec) in MP3_1412
    mp3_at_pb0 = best_lag / 10.0 - t_start_sec
    return best_lag / 10.0, mp3_at_pb0, best_corr

for t_start in [1100, 1800, 2500, 3200, 3900]:
    mp3_t, offset_at_0, c = correlate_segment(pb19_db, mp3_1412_db, t_start, 500)
    print(f"PB19 [{t_start}s..{t_start+500}s] -> MP3_1412 at {mp3_t:.1f}s | Implies PB19(0s) = MP3_1412({offset_at_0:.2f}s) | corr={c:.4f}")

# 3. Also check if PB130017 has any faint correlation with MP3_1328
mp3_t17, offset17, c17 = correlate_segment(pb17_rms, mp3_1328_rms, 50, 500)
print(f"\nPB17 faint RMS correlation test -> MP3_1328 at {mp3_t17:.1f}s | Implies PB17(0s) = MP3_1328({offset17:.2f}s) | corr={c17:.4f}")
