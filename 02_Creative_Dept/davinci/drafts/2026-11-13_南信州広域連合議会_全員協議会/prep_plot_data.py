import numpy as np
import os

draft_dir = r"g:\マイドライブ\git\nobuyukitakahashi\02_Creative_Dept\davinci\drafts\2026-11-13_南信州広域連合議会_全員協議会"
data = np.load(os.path.join(draft_dir, "audio_envelopes_10hz.npz"))

pb17_db = data["PB130017_db"]
mp3_1328_db = data["MP3_1328_db"]
pb19_db = data["PB130019_db"]
mp3_1412_db = data["MP3_1412_db"]

# Downsample to 1000 points for plotting in PowerShell
def sample_1000(arr, start_idx, length):
    idx = np.linspace(start_idx, min(len(arr)-1, start_idx + length - 1), 1000).astype(int)
    return arr[idx]

# 1) PB17 (0..615s = 6150 samples) vs MP3_1328 (36.6s..651.6s = 366..6516)
p17 = sample_1000(pb17_db, 0, 6150)
m1328 = sample_1000(mp3_1328_db, 366, 6150)

# 2) PB19 (0..4635s = 46350 samples) vs MP3_1412 (12.6s..4647.6s = 126..46476)
p19 = sample_1000(pb19_db, 0, 46350)
m1412 = sample_1000(mp3_1412_db, 126, 46350)

# 3) Zoomed overlay of PB19 [1040s..1140s] vs MP3_1412 [1052.6s..1152.6s] (1000 samples at 10Hz!)
p19_zoom = pb19_db[10400:11400]
m1412_zoom = mp3_1412_db[10526:11526]

with open(os.path.join(draft_dir, "plot_data.csv"), "w", encoding="utf-8") as f:
    for i in range(1000):
        f.write(f"{p17[i]:.1f},{m1328[i]:.1f},{p19[i]:.1f},{m1412[i]:.1f},{p19_zoom[i]:.1f},{m1412_zoom[i]:.1f}\n")
print("Saved plot_data.csv")
