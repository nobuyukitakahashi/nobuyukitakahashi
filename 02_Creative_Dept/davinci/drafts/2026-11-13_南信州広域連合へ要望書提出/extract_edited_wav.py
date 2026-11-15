import aud
import wave
import numpy as np
import os

final_dir = r"g:\マイドライブ\git\nobuyukitakahashi\02_Creative_Dept\davinci\final_outputs\2026-11-13_南信州広域連合へ要望書提出"
draft_dir = r"g:\マイドライブ\git\nobuyukitakahashi\02_Creative_Dept\davinci\drafts\2026-11-13_南信州広域連合へ要望書提出"
mp4_path = os.path.join(final_dir, "PB130002_編集済_FullHD.mp4")
wav_path = os.path.join(draft_dir, "edited_audio_16k.wav")

s = aud.Sound(mp4_path)
s_16k = s.resample(16000.0, True)
data = s_16k.data()
print("Resampled shape:", data.shape)
# Mix to mono and normalize slightly for crystal-clear transcription
mono = np.mean(data, axis=1) if data.ndim > 1 else data
peak = np.max(np.abs(mono))
if peak > 0:
    mono = mono / peak * 0.92
pcm16 = np.clip(mono * 32767.0, -32768, 32767).astype(np.int16)

with wave.open(wav_path, "wb") as wf:
    wf.setnchannels(1)
    wf.setsampwidth(2)
    wf.setframerate(16000)
    wf.writeframes(pcm16.tobytes())

print("Saved WAV:", wav_path, "Size:", os.path.getsize(wav_path))

# Also print fine 0.5s RMS timeline of the edited video (0.0s to 162.33s) so we have exact timestamps!
sr = 16000
total_sec = len(mono) / sr
for i in range(int(total_sec * 2) + 1):
    t0 = i * 0.5
    t1 = min(total_sec, (i + 1) * 0.5)
    c = mono[int(t0*sr):int(t1*sr)]
    if len(c) == 0:
        continue
    rms = float(np.sqrt(np.mean(c**2)))
    db = 20 * np.log10(max(rms, 1e-7))
    bar = "#" * max(0, int((db + 50) * 0.9))
    print(f"{t0:6.1f}-{t1:6.1f}s | {db:5.1f} dB | {bar}")
