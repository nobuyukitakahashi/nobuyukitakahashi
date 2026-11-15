import aud
import numpy as np
import os

base_dir = r"H:\2026-11-13_南信州広域連合_連合長へ_要望書提出_録音一式"
draft_dir = r"g:\マイドライブ\git\nobuyukitakahashi\02_Creative_Dept\davinci\drafts\2026-11-13_南信州広域連合議会_全員協議会"

files = {
    "PB130017": os.path.join(base_dir, "PB130017.MOV"),
    "PB130018": os.path.join(base_dir, "PB130018.MOV"),
    "PB130019": os.path.join(base_dir, "PB130019.MOV"),
    "MP3_1240": os.path.join(base_dir, "11月13日（12-40）事前打合せ", "11月13日（12-40）事前打合せ.m4a"),
    "MP3_1328": os.path.join(base_dir, "11月13日（13-28）南信州広域連合議会 第2回 全員協議会", "11月13日（13-28）南信州広域連合議会 第2回 全員協議会.mp3"),
    "MP3_1412": os.path.join(base_dir, "11月13日（14-12）南信州広域連合議会 第2回 全員協議会 資料3 桐林クリーンセンター解体について", "11月13日（14-12）南信州広域連合議会 第2回 全員協議会 資料3 桐林クリーンセンター解体について.mp3"),
}

sr = 8000  # 8kHz is fast and plenty for envelope & cross-correlation

envelopes = {}

for name, path in files.items():
    print(f"\n--- Loading {name}: {os.path.basename(path)} ---")
    try:
        s = aud.Sound(path).rechannel(1).resample(sr, False)
        data = s.data()
        print(f"Shape: {data.shape}, Duration: {len(data)/sr:.2f}s")
        # Compute 0.1s (10Hz) RMS envelope
        hop = sr // 10  # 800 samples = 0.1s
        n_frames = len(data) // hop
        trimmed = data[:n_frames * hop, 0]
        frames = trimmed.reshape(n_frames, hop)
        rms = np.sqrt(np.mean(frames**2, axis=1) + 1e-12)
        db = 20 * np.log10(rms)
        envelopes[name] = (rms, db)
        
        # Analyze active vs silent segments (1-second chunks)
        sec_hop = 10 # 10 * 0.1s = 1s
        n_sec = n_frames // sec_hop
        sec_db = db[:n_sec * sec_hop].reshape(n_sec, sec_hop).max(axis=1)
        
        # Print summary stats
        print(f"Max dB: {db.max():.1f} dBFS, Min dB: {db.min():.1f} dBFS, Median dB: {np.median(db):.1f} dBFS")
        
        # Find where audio is active (> -45 dBFS) vs silent (< -55 dBFS)
        active_secs = np.where(sec_db > -45.0)[0]
        if len(active_secs) > 0:
            print(f"Active seconds (> -45 dBFS): count={len(active_secs)}/{n_sec}s, first={active_secs[0]}s, last={active_secs[-1]}s")
            # Find contiguous regions of active audio
            diffs = np.diff(active_secs)
            splits = np.where(diffs > 5)[0]
            start_idx = 0
            regions = []
            for sp in splits:
                regions.append((active_secs[start_idx], active_secs[sp]))
                start_idx = sp + 1
            regions.append((active_secs[start_idx], active_secs[-1]))
            print(f"Active regions (gap > 5s): {regions[:10]}")
        else:
            print("COMPLETELY SILENT (no seconds > -45 dBFS)")
            
        # Also print every 30s or transitions for MOVs
        if name.startswith("PB"):
            for sec in range(0, min(n_sec, 600), 10):
                chunk = sec_db[sec:sec+10]
                print(f"  {sec:4d}s - {sec+10:4d}s: max={chunk.max():5.1f} dB, min={chunk.min():5.1f} dB")
    except Exception as e:
        print(f"Error loading {name}: {e}")

# Save envelopes for fast correlation analysis
np.savez(os.path.join(draft_dir, "audio_envelopes_10hz.npz"), **{k: v[0] for k, v in envelopes.items()}, **{k+"_db": v[1] for k, v in envelopes.items()})
print("\nSaved audio_envelopes_10hz.npz")
