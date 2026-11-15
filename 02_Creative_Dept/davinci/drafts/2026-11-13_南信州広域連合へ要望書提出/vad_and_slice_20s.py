import wave
import numpy as np
import os

draft_dir = r"g:\マイドライブ\git\nobuyukitakahashi\02_Creative_Dept\davinci\drafts\2026-11-13_南信州広域連合へ要望書提出"
wav_path = os.path.join(draft_dir, "edited_audio_16k.wav")

with wave.open(wav_path, "rb") as wf:
    sr = wf.getframerate()
    nframes = wf.getnframes()
    raw = wf.readframes(nframes)
    pcm = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0

total_sec = nframes / sr
print(f"Total duration: {total_sec:.2f}s")

# Print 0.2s resolution dB profile grouped by 20s blocks
for b_start in range(0, 165, 20):
    b_end = min(total_sec, b_start + 20)
    if b_start >= total_sec:
        break
    out_w = os.path.join(draft_dir, f"seg_{b_start:03d}_{int(round(b_end)):03d}.wav")
    i0 = int(b_start * sr) * 2
    i1 = int(b_end * sr) * 2
    with wave.open(out_w, "wb") as wf_out:
        wf_out.setnchannels(1)
        wf_out.setsampwidth(2)
        wf_out.setframerate(sr)
        wf_out.writeframes(raw[i0:i1])
    
    print(f"\n================ BLOCK {b_start:03d}s - {b_end:05.2f}s ================")
    step = 0.25
    t = float(b_start)
    while t < b_end - 0.05:
        t_next = min(b_end, t + step)
        c = pcm[int(t*sr):int(t_next*sr)]
        rms = float(np.sqrt(np.mean(c**2))) if len(c) > 0 else 0.0
        db = 20 * np.log10(max(rms, 1e-7))
        bar = "#" * max(0, int((db + 35) * 1.2))
        if db > -23.5:
            print(f"  {t:6.2f}-{t_next:6.2f}s (rel {t-b_start:5.2f}s) | {db:5.1f} dB | {bar}")
        t += step
