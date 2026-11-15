import wave
import numpy as np
import os

draft_dir = r"g:\マイドライブ\git\nobuyukitakahashi\02_Creative_Dept\davinci\drafts\2026-11-13_南信州広域連合へ要望書提出"
wav_path = os.path.join(draft_dir, "edited_audio_16k.wav")

with wave.open(wav_path, "rb") as wf:
    sr = wf.getframerate()
    nframes = wf.getnframes()
    pcm = np.frombuffer(wf.readframes(nframes), dtype=np.int16).astype(np.float32) / 32768.0

total_sec = nframes / sr
step = 0.25
for i in range(int(total_sec / step)):
    t0 = i * step
    t1 = min(total_sec, (i + 1) * step)
    c = pcm[int(t0*sr):int(t1*sr)]
    rms = float(np.sqrt(np.mean(c**2))) if len(c) > 0 else 0.0
    db = 20 * np.log10(max(rms, 1e-7))
    active = "SPEECH" if db > -21.5 else ("soft  " if db > -24.0 else "      ")
    bar = "#" * max(0, int((db + 45) * 1.0))
    print(f"{t0:6.2f}-{t1:6.2f}s | {db:5.1f} dB | {active} | {bar}")
