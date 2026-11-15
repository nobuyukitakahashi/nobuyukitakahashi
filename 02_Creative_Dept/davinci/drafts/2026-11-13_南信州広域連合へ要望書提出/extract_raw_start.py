import aud
import wave
import numpy as np
import os

draft_dir = r"g:\マイドライブ\git\nobuyukitakahashi\02_Creative_Dept\davinci\drafts\2026-11-13_南信州広域連合へ要望書提出"
raw_mov = r"H:\2026-11-13_南信州広域連合_連合長へ_要望書提出_録音一式\PB130002.MOV"
out_wav = os.path.join(draft_dir, "raw_start_0_15s.wav")

s = aud.Sound(raw_mov).resample(16000.0, True)
data = s.data()[:16000*15]
mono = np.mean(data, axis=1) if data.ndim > 1 else data
mono = mono / max(np.max(np.abs(mono)), 1e-5) * 0.9
pcm16 = np.clip(mono * 32767.0, -32768, 32767).astype(np.int16)

with wave.open(out_wav, "wb") as wf:
    wf.setnchannels(1)
    wf.setsampwidth(2)
    wf.setframerate(16000)
    wf.writeframes(pcm16.tobytes())
print("Saved raw_start_0_15s.wav")
