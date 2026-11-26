import asyncio
import math
import os
import subprocess
import wave
from array import array
import edge_tts

BASE_DIR = r"g:\マイドライブ\git\nobuyukitakahashi\02_Creative_Dept\aftereffects\drafts\furusato2026_cm"
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
NARR_DIR = os.path.join(BASE_DIR, "narration_clips")
PROD_BGM_SRC = r"C:\Users\nobuy\.gemini\antigravity\brain\bf6616b4-651d-49fa-b04f-8ac546983604\.user_uploaded\uploaded_media_1795696979787.wav"
os.makedirs(NARR_DIR, exist_ok=True)
os.makedirs(ASSETS_DIR, exist_ok=True)

# Exact 30.00s highlight window from uploaded production BGM:
# 54.52s (quiet valley just before pickup + chorus drop at 54.64s) .. 84.52s (official ending + natural reverb tail)
BGM_START_S = 54.52
BGM_DUR_S = 30.00

VOICE = "ja-JP-NanamiNeural"
RATE = "+12%"
PITCH = "+2Hz"

# 6 scenes naturally timed inside 01_MainCM_30sec (0.0s .. 30.0s)
# (id, start_s, max_dur_s, text)
SCENES = [
    ("s1", 0.35, 2.80, "あなたの未来が、ここから動き出す！"),
    ("s2", 3.65, 5.45, "地元企業103社が大集結！ふるさと合同企業説明会を開催。"),
    ("s3", 9.65, 5.45, "12月27日エスバードで開催！服装自由、就活セミナーも同時開催。"),
    ("s4", 15.65, 4.45, "地元就職やユーアイジェイターン、中高生や保護者の方も大歓迎！"),
    ("s5", 20.65, 3.95, "よんしゃ訪問で、クオカード500円分をプレゼント！"),
    ("s6", 25.25, 4.10, "詳しくはイイダカイシャナビで検索！インスタもチェック！"),
]


async def synth_all():
    for sid, _, _, text in SCENES:
        mp3_path = os.path.join(NARR_DIR, f"{sid}_raw.mp3")
        comm = edge_tts.Communicate(text, voice=VOICE, rate=RATE, pitch=PITCH)
        await comm.save(mp3_path)
        print(f"SYNTH OK: {sid}")


def run_ffmpeg(args):
    p = subprocess.run(["ffmpeg", "-y", "-v", "error"] + args, capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError(f"ffmpeg failed: {p.stderr}")


def get_wav_duration(path):
    with wave.open(path, "rb") as wf:
        return wf.getnframes() / wf.getframerate()


def extract_prod_bgm_30sec():
    out_bgm = os.path.join(ASSETS_DIR, "prod_bgm_30sec.wav")
    # Clean 30.000s cut from chorus drop to official ending tail with gentle 25ms head fade & 180ms tail fade
    run_ffmpeg([
        "-ss", f"{BGM_START_S:.3f}",
        "-t", f"{BGM_DUR_S:.3f}",
        "-i", PROD_BGM_SRC,
        "-af", "afade=t=in:st=0:d=0.025,afade=t=out:st=29.72:d=0.25",
        "-ar", "48000", "-ac", "2", "-c:a", "pcm_s16le",
        out_bgm
    ])
    print(f"EXTRACTED PROD BGM 30s: {out_bgm} (dur={get_wav_duration(out_bgm):.3f}s)")
    return out_bgm


def process_clips_and_mix(prod_bgm_wav):
    sr = 48000
    total_samples = int(sr * 30.0)
    narr_buf = [0.0] * total_samples
    activity = [0.0] * total_samples

    print("=== CLIP TIMING & FIT ===")
    prev_end = 0.0
    for sid, start_s, max_dur, _ in SCENES:
        raw_mp3 = os.path.join(NARR_DIR, f"{sid}_raw.mp3")
        trim_wav = os.path.join(NARR_DIR, f"{sid}_trim.wav")
        fit_wav = os.path.join(NARR_DIR, f"{sid}_fit.wav")

        run_ffmpeg([
            "-i", raw_mp3,
            "-af", "highpass=f=85,silenceremove=start_periods=1:start_silence=0.02:start_threshold=-42dB,areverse,silenceremove=start_periods=1:start_silence=0.03:start_threshold=-42dB,areverse",
            "-ar", str(sr), "-ac", "1", "-c:a", "pcm_s16le", trim_wav
        ])
        dur = get_wav_duration(trim_wav)
        tempo = 1.0
        if dur > max_dur:
            tempo = min(1.22, dur / max_dur)
            run_ffmpeg([
                "-i", trim_wav,
                "-af", f"atempo={tempo:.4f}",
                "-ar", str(sr), "-ac", "1", "-c:a", "pcm_s16le", fit_wav
            ])
        else:
            fit_wav = trim_wav
        final_dur = get_wav_duration(fit_wav)
        end_s = start_s + final_dur
        gap = start_s - prev_end
        print(f"  {sid}: start={start_s:.2f}s (gap={gap:.2f}s), raw={dur:.2f}s, tempo={tempo:.3f}, final={final_dur:.2f}s -> end={end_s:.2f}s (limit={start_s+max_dur:.2f}s)")
        assert gap >= 0.30, f"Too small gap before {sid}: {gap:.2f}s"
        assert end_s <= start_s + max_dur + 0.06, f"Overflow on {sid}: end={end_s:.2f} > limit={start_s+max_dur:.2f}"
        prev_end = end_s

        with wave.open(fit_wav, "rb") as wf:
            raw_frames = wf.readframes(wf.getnframes())
        samples = array("h")
        samples.frombytes(raw_frames)
        # Consistent speech RMS loudness normalization (clear & warm above energetic EDM/pop BGM)
        rms = math.sqrt(sum((x / 32767.0) ** 2 for x in samples) / max(1, len(samples)))
        target_rms = 0.22
        gain = min(0.88 / max(1e-6, max(abs(x) for x in samples) / 32767.0), target_rms / max(1e-6, rms))

        i0 = int(start_s * sr)
        for k, s_val in enumerate(samples):
            idx = i0 + k
            if 0 <= idx < total_samples:
                narr_buf[idx] += (s_val / 32767.0) * gain
                activity[idx] = 1.0

    # Save standalone narration track (30s stereo 48kHz)
    narr_only_path = os.path.join(ASSETS_DIR, "temp_narration_only_30sec.wav")
    narr_pcm = array("h")
    for x in narr_buf:
        v = int(max(-32767, min(32767, round(x * 32767.0))))
        narr_pcm.append(v)
        narr_pcm.append(v)
    with wave.open(narr_only_path, "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(narr_pcm.tobytes())
    print("SAVED NARRATION ONLY:", narr_only_path)

    # Smooth ducking envelope (10ms blocks)
    hop = 480
    n_blocks = (total_samples + hop - 1) // hop
    blk_act = [0.0] * n_blocks
    for b in range(n_blocks):
        s0 = b * hop
        s1 = min(total_samples, s0 + hop)
        if any(activity[i] > 0.5 for i in range(s0, s1)):
            blk_act[b] = 1.0

    # Hold 80ms before & 160ms after speech for smooth pro ducking
    padded = [0.0] * n_blocks
    for b in range(n_blocks):
        if blk_act[b] > 0.5:
            for j in range(max(0, b - 8), min(n_blocks, b + 16)):
                padded[j] = 1.0

    smooth = [0.0] * n_blocks
    win = 14  # 140ms glide
    acc = 0.0
    for b in range(n_blocks):
        acc += padded[b]
        if b >= win:
            acc -= padded[b - win]
        smooth[b] = acc / min(b + 1, win)

    # Load 30s production BGM (pre-process slight mid-presence pocket at 2.5kHz -2dB so voice cuts through cleanly)
    bgm_eq_path = os.path.join(NARR_DIR, "prod_bgm_30sec_eq.wav")
    run_ffmpeg([
        "-i", prod_bgm_wav,
        "-af", "equalizer=f=2400:t=q:w=1.2:g=-2.5",
        "-ar", str(sr), "-ac", "2", "-c:a", "pcm_s16le",
        bgm_eq_path
    ])
    with wave.open(bgm_eq_path, "rb") as wf:
        bgm_raw = wf.readframes(wf.getnframes())
    bgm_arr = array("h")
    bgm_arr.frombytes(bgm_raw)

    # Mix: Production BGM (0.72 open -> 0.25 ducked under speech, ~-9dB ducking for ultra-clear broadcast voice)
    mix_raw_path = os.path.join(NARR_DIR, "ma_raw_30sec.wav")
    mix_pcm = array("h")
    n_bgm = len(bgm_arr) // 2
    for i in range(total_samples):
        b = i // hop
        duck = smooth[b] if b < n_blocks else 0.0
        bgm_gain = 0.72 * (1.0 - duck) + 0.25 * duck
        bl = (bgm_arr[2 * i] / 32767.0) * bgm_gain if i < n_bgm else 0.0
        br = (bgm_arr[2 * i + 1] / 32767.0) * bgm_gain if i < n_bgm else 0.0
        nv = narr_buf[i] * 0.96
        ol = max(-0.98, min(0.98, bl + nv))
        or_ = max(-0.98, min(0.98, br + nv))
        mix_pcm.append(int(round(ol * 32767.0)))
        mix_pcm.append(int(round(or_ * 32767.0)))

    with wave.open(mix_raw_path, "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(mix_pcm.tobytes())

    # Broadcast loudness mastering (-18 LUFS / TP -1.5 dBTP, clean 30.000s)
    ma_out_path = os.path.join(ASSETS_DIR, "ma_30sec_prod_bgm_temp_narr.wav")
    run_ffmpeg([
        "-i", mix_raw_path,
        "-af", "loudnorm=I=-18:TP=-1.5:LRA=7,afade=t=in:st=0:d=0.025,afade=t=out:st=29.75:d=0.22",
        "-t", "30.000",
        "-ar", str(sr), "-ac", "2", "-c:a", "pcm_s16le",
        ma_out_path
    ])
    print("SAVED FINAL MA WAV:", ma_out_path, "dur=", round(get_wav_duration(ma_out_path), 3))


if __name__ == "__main__":
    prod_bgm = extract_prod_bgm_30sec()
    asyncio.run(synth_all())
    process_clips_and_mix(prod_bgm)
