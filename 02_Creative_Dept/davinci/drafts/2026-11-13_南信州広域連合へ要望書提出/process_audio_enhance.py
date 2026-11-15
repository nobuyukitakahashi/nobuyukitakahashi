import aud
import wave
import numpy as np
import os

draft_dir = r"g:\マイドライブ\git\nobuyukitakahashi\02_Creative_Dept\davinci\drafts\2026-11-13_南信州広域連合へ要望書提出"
final_dir = r"g:\マイドライブ\git\nobuyukitakahashi\02_Creative_Dept\davinci\final_outputs\2026-11-13_南信州広域連合へ要望書提出"
mp4_path = os.path.join(final_dir, "PB130002_編集済_FullHD.mp4")
out_wav_path = os.path.join(draft_dir, "enhanced_audio_48k.wav")

s = aud.Sound(mp4_path).resample(48000.0, True)
data = s.data() # shape (N, 2), float32
sr = 48000

# Measure BEFORE metrics
before_rms = float(np.sqrt(np.mean(data**2)))
before_rms_db = 20 * np.log10(max(before_rms, 1e-7))
before_peak_db = 20 * np.log10(max(float(np.max(np.abs(data))), 1e-7))

# Quiet room noise window (t=135.5s to 138.0s) and active speech window (t=3.5s to 20.0s)
q0, q1 = int(135.5 * sr), int(138.0 * sr)
sp0, sp1 = int(3.5 * sr), int(20.0 * sr)
before_noise_db = 20 * np.log10(max(float(np.sqrt(np.mean(data[q0:q1]**2))), 1e-7))
before_speech_db = 20 * np.log10(max(float(np.sqrt(np.mean(data[sp0:sp1]**2))), 1e-7))

print(f"BEFORE: Overall RMS={before_rms_db:.2f} dBFS | Speech RMS={before_speech_db:.2f} dBFS | Quiet Noise={before_noise_db:.2f} dBFS | Peak={before_peak_db:.2f} dBFS")

# STFT-based gentle noise reduction + High-Pass (100Hz) + Voice Presence EQ (1.5-3.8kHz)
n_fft = 2048
hop = 512
win = np.hanning(n_fft).astype(np.float32)
freqs = np.fft.rfftfreq(n_fft, 1.0 / sr)

hp_curve = 1.0 / np.sqrt(1.0 + (100.0 / np.maximum(freqs, 1.0))**4)
hp_curve[0] = 0.0
presence_boost = 1.0 + 0.32 * np.exp(-0.5 * ((freqs - 2300.0) / 1100.0)**2)
lp_curve = 1.0 / np.sqrt(1.0 + (freqs / 11000.0)**4)
eq_curve = (hp_curve * presence_boost * lp_curve).astype(np.float32)

def process_channel(ch_in):
    L = len(ch_in)
    pad = n_fft
    x = np.pad(ch_in, (pad, pad), mode='reflect')
    n_frames = 1 + (len(x) - n_fft) // hop
    
    frames = np.lib.stride_tricks.sliding_window_view(x, n_fft)[::hop][:n_frames]
    spec = np.fft.rfft(frames * win, axis=1)
    mag = np.abs(spec)
    
    # Estimate stationary noise profile from quietest 15% frames per frequency bin
    noise_mag = np.percentile(mag, 15, axis=0)
    
    # Soft Wiener-like spectral gain with minimum floor = 0.45 (-6.9 dB natural noise reduction)
    snr = np.maximum(0.0, (mag / (noise_mag[None, :] + 1e-7))**2 - 1.0)
    gain = np.clip(snr / (snr + 1.5), 0.45, 1.0)
    
    # Smooth gain in time and frequency so voice remains 100% natural
    for _ in range(2):
        gain = 0.25 * np.roll(gain, 1, axis=0) + 0.50 * gain + 0.25 * np.roll(gain, -1, axis=0)
        gain = 0.25 * np.roll(gain, 1, axis=1) + 0.50 * gain + 0.25 * np.roll(gain, -1, axis=1)
    
    spec_out = spec * gain * eq_curve[None, :]
    frames_out = np.fft.irfft(spec_out, n=n_fft, axis=1) * win[None, :]
    
    y = np.zeros(len(x), dtype=np.float32)
    w_sum = np.zeros(len(x), dtype=np.float32)
    w_sq = (win ** 2)
    for i in range(n_frames):
        s_idx = i * hop
        y[s_idx:s_idx+n_fft] += frames_out[i]
        w_sum[s_idx:s_idx+n_fft] += w_sq
    y = y / np.maximum(w_sum, 1e-6)
    return y[pad:pad+L]

y_L = process_channel(data[:, 0])
y_R = process_channel(data[:, 1])
y_stereo = np.stack([y_L, y_R], axis=1)

# Dynamic Range Compression + Gentle Downward Expansion on pauses
mono_env = np.sqrt(0.5 * (y_L**2 + y_R**2))
block = int(0.010 * sr)
n_b = len(mono_env) // block
env_b = np.sqrt(np.mean(mono_env[:n_b*block].reshape(n_b, block)**2, axis=1) + 1e-10)

env_smooth = np.zeros_like(env_b)
cur = env_b[0]
for i in range(n_b):
    val = env_b[i]
    cur = (0.35 * val + 0.65 * cur) if val > cur else (0.05 * val + 0.95 * cur)
    env_smooth[i] = cur

env_db = 20.0 * np.log10(np.maximum(env_smooth, 1e-7))

# Compressor threshold at -18.5 dBFS (ratio 2.8:1) so speech (-22 to -18 dBFS) gets full +7.8 dB makeup gain!
thresh_db = -18.5
ratio = 2.8
gain_db = np.zeros_like(env_db)
over = env_db > thresh_db
gain_db[over] = (thresh_db + (env_db[over] - thresh_db) / ratio) - env_db[over]

# Gentle downward expander below -27.5 dBFS (up to -4.0 dB attenuation during non-speech pauses)
under = env_db < -27.5
gain_db[under] = np.clip((env_db[under] - (-27.5)) * 0.45, -4.0, 0.0)

# Makeup gain: +7.8 dB
gain_db += 7.8
gain_lin_b = 10.0 ** (gain_db / 20.0)
t_b = (np.arange(n_b) + 0.5) * block
Gain_full = np.interp(np.arange(len(y_L)), t_b, gain_lin_b).astype(np.float32)

y_boosted = y_stereo * Gain_full[:, None]

# True-peak soft-knee limiter at -1.0 dBFS (0.89125)
limit_ceil = 0.89125
knee = 0.65
abs_y = np.abs(y_boosted)
over_knee = abs_y > knee
if np.any(over_knee):
    span = limit_ceil - knee
    y_boosted[over_knee] = np.sign(y_boosted[over_knee]) * (
        knee + span * np.tanh((abs_y[over_knee] - knee) / span)
    )

after_rms_db = 20 * np.log10(max(float(np.sqrt(np.mean(y_boosted**2))), 1e-7))
after_peak_db = 20 * np.log10(max(float(np.max(np.abs(y_boosted))), 1e-7))
after_noise_db = 20 * np.log10(max(float(np.sqrt(np.mean(y_boosted[q0:q1]**2))), 1e-7))
after_speech_db = 20 * np.log10(max(float(np.sqrt(np.mean(y_boosted[sp0:sp1]**2))), 1e-7))

before_snr = before_speech_db - before_noise_db
after_snr = after_speech_db - after_noise_db

print(f"AFTER : Overall RMS={after_rms_db:.2f} dBFS | Speech RMS={after_speech_db:.2f} dBFS ({after_speech_db - before_speech_db:+.2f} dB boost!) | Quiet Noise={after_noise_db:.2f} dBFS | Peak={after_peak_db:.2f} dBFS")
print(f"SNR Improvement (Speech vs Quiet Room): {before_snr:.2f} dB -> {after_snr:.2f} dB ({after_snr - before_snr:+.2f} dB)")

pcm16 = np.clip(y_boosted * 32767.0, -32768, 32767).astype(np.int16)
with wave.open(out_wav_path, "wb") as wf:
    wf.setnchannels(2)
    wf.setsampwidth(2)
    wf.setframerate(sr)
    wf.writeframes(pcm16.tobytes())

print("Saved enhanced_audio_48k.wav:", os.path.exists(out_wav_path))
