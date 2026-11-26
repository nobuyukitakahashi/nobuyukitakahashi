import base64
import json
import math
import os
import subprocess
import urllib.request
import wave
from array import array

BASE_DIR = r"g:\マイドライブ\git\nobuyukitakahashi\02_Creative_Dept\aftereffects\drafts\furusato2026_cm"
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
NARR_DIR = os.path.join(BASE_DIR, "google_tts_clips")
os.makedirs(NARR_DIR, exist_ok=True)
os.makedirs(ASSETS_DIR, exist_ok=True)

KEY = os.environ["GEMINI_API_KEY"]
MODEL = "gemini-2.5-pro-preview-tts"
VOICE = "Leda"

COMMON_DIR = (
    "あなたは日本の地上波テレビCMで大人気の一流女性ナレーターです。"
    "聴いた瞬間に心が躍って『絶対に行きたい！』と思わせる、"
    "とても高いテンション・熱い情熱・満面の笑顔・弾けるエネルギッシュな声で読み上げてください！"
    "声のトーンを普段よりワントーン明るく高く張り、一音一音の滑舌をはっきり明瞭に発声してください。"
    "指示文・前置き・相槌は一切入れず、指定されたセリフ本文だけを一言一句そのまま発声してください。"
)

# Retake ALL 6 scenes with elevated high-energy, passionate, enthusiastic CM tone!
# New timeline (total 30.0s):
#   S1:  0.00..2.20 (2.2s)  — ultra-speedy, passionate hook (cut -1.3s)
#   S2:  2.20..6.00 (3.8s)  — event title ONLY! (cut -2.2s -> total opening -3.5s!)
#   S3:  6.00..13.80 (7.8s) — +1.8s extra room! natural 1.0x speed, super clear & energetic
#   S4: 13.80..20.20 (6.4s) — +1.4s extra room! natural 1.0x speed, super warm & high-energy
#   S5: 20.20..25.00 (4.8s) — +0.3s extra room! excited reward delivery + 24.73s BGM break hit
#   S6: 25.00..30.00 (5.0s) — upbeat finale synced with official BGM ending
RETAKE_IDS = {"s1", "s2", "s6"}

SCENES = [
    (
        "s1", 0.08, 2.08,
        "【演技指定】CM冒頭0秒の電撃インパクト！疾走感のあるスピーディなテンポと熱い情熱・高いテンションで一気に力強く言い切る！語尾は絶対に『うごきます』ではなく『うごきだす！』と明確に『だ・す』をはっきり発音すること！",
        "あなたの未来が、ここから動きだす！"
    ),
    (
        "s2", 2.40, 3.25,
        "【演技指定】冒頭の熱い勢いのまま、最高に華やかで情熱的なハイテンション！イベント名『ふるさと合同企業説明会！』を『せつ・めい・かい！』と1音ずつ明瞭な滑舌で、力強く晴れやかに宣言する！",
        "ふるさと合同企業説明会！"
    ),
    (
        "s3", 6.25, 7.25,
        "KEEP",
        "12月27日、エスバードで開催！服装自由！しゅうかつセミナーも同時開催！"
    ),
    (
        "s4", 14.05, 5.85,
        "KEEP",
        "地元就職やUIJターン、中高生や保護者の方も大歓迎！"
    ),
    (
        "s5", 20.42, 4.00,
        "KEEP",
        "よんしゃ訪問で、クオカード500円分をプレゼント！"
    ),
    (
        "s6", 25.18, 4.25,
        "【演技指定】ラストの決め！高いテンションと爽快感MAX、元気いっぱいのリズムで晴れやかにキレよく！特に『いいだかいしゃなび（ナ・ビ）』を絶対に『のび』にならず明瞭に『ナビ』と発音すること！",
        "詳しくは、いいだかいしゃナビで検索！インスタもチェック！"
    ),
]


def run_ffmpeg(args):
    p = subprocess.run(["ffmpeg", "-y", "-v", "error"] + args, capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError(f"ffmpeg failed: {p.stderr}")


def get_wav_duration(path):
    with wave.open(path, "rb") as wf:
        return wf.getnframes() / wf.getframerate()


def synth_scene(sid, scene_dir, transcript):
    prompt = f"{COMMON_DIR}\n{scene_dir}\n\nセリフ本文：\n{transcript}"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={KEY}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseModalities": ["AUDIO"],
            "speechConfig": {
                "voiceConfig": {
                    "prebuiltVoiceConfig": {"voiceName": VOICE}
                }
            }
        }
    }
    last_err = None
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=60) as resp:
                d = json.loads(resp.read().decode("utf-8"))
            cands = d.get("candidates") or []
            if not cands or "content" not in cands[0] or not cands[0]["content"].get("parts"):
                raise RuntimeError(f"Empty candidate (attempt {attempt+1}): {str(d)[:200]}")
            part = cands[0]["content"]["parts"][0]["inlineData"]
            raw = base64.b64decode(part["data"])
            raw_wav = os.path.join(NARR_DIR, f"{sid}_high_raw.wav")
            if "wav" in part.get("mimeType", "").lower():
                with open(raw_wav, "wb") as f:
                    f.write(raw)
            else:
                with wave.open(raw_wav, "wb") as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(2)
                    wf.setframerate(24000)
                    wf.writeframes(raw)
            return raw_wav
        except Exception as e:
            last_err = e
            print(f"  WARN {sid} attempt {attempt+1}: {e}")
    raise last_err


def main():
    sr = 48000
    total_samples = int(sr * 30.0)
    narr_buf = [0.0] * total_samples
    activity = [0.0] * total_samples

    print("=== RECORDING ALL 6 SCENES (HIGH-TENSION / PASSIONATE / NEW TIMELINE) ===")
    prev_end = 0.0
    for sid, start_s, max_dur, scene_dir, transcript in SCENES:
        raw_wav = os.path.join(NARR_DIR, f"{sid}_high_raw.wav")
        if sid in RETAKE_IDS or not os.path.exists(raw_wav):
            raw_wav = synth_scene(sid, scene_dir, transcript)
            status = "REC"
        else:
            status = "KEPT"

        trim_wav = os.path.join(NARR_DIR, f"{sid}_high_trim.wav")
        fit_wav = os.path.join(NARR_DIR, f"{sid}_high_fit.wav")

        # Energetic broadcast voice chain (crisp presence + brightness)
        af_chain = (
            "highpass=f=90,"
            "equalizer=f=3400:t=q:w=1.1:g=2.2,"
            "acompressor=threshold=-18dB:ratio=2.8:attack=8:release=110:makeup=2,"
            "silenceremove=start_periods=1:start_silence=0.02:start_threshold=-40dB,"
            "areverse,silenceremove=start_periods=1:start_silence=0.03:start_threshold=-40dB,areverse"
        )
        run_ffmpeg(["-i", raw_wav, "-af", af_chain, "-ar", str(sr), "-ac", "1", "-c:a", "pcm_s16le", trim_wav])
        dur = get_wav_duration(trim_wav)
        tempo = 1.0
        if dur > max_dur:
            tempo = min(1.20, dur / max_dur)
            run_ffmpeg(["-i", trim_wav, "-af", f"atempo={tempo:.4f}", "-ar", str(sr), "-ac", "1", "-c:a", "pcm_s16le", fit_wav])
        else:
            fit_wav = trim_wav
        final_dur = get_wav_duration(fit_wav)
        end_s = start_s + final_dur
        gap = start_s - prev_end
        print(f"  {sid} [{status}]: start={start_s:.2f}s (gap={gap:.2f}s), raw={dur:.2f}s, tempo={tempo:.3f}, final={final_dur:.2f}s -> end={end_s:.2f}s (limit={start_s+max_dur:.2f}s)")
        prev_end = end_s

        with wave.open(fit_wav, "rb") as wf:
            raw_frames = wf.readframes(wf.getnframes())
        samples = array("h")
        samples.frombytes(raw_frames)
        rms = math.sqrt(sum((x / 32767.0) ** 2 for x in samples) / max(1, len(samples)))
        peak = max((abs(x) for x in samples), default=1) / 32767.0
        gain = min(0.90 / max(1e-6, peak), 0.24 / max(1e-6, rms))

        i0 = int(start_s * sr)
        for k, s_val in enumerate(samples):
            idx = i0 + k
            if 0 <= idx < total_samples:
                narr_buf[idx] += (s_val / 32767.0) * gain
                activity[idx] = 1.0

    # Save standalone narration track
    narr_only_path = os.path.join(ASSETS_DIR, "google_tts_narration_only_30sec.wav")
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

    # Smooth ducking envelope
    hop = 480
    n_blocks = (total_samples + hop - 1) // hop
    blk_act = [0.0] * n_blocks
    for b in range(n_blocks):
        s0 = b * hop
        s1 = min(total_samples, s0 + hop)
        if any(activity[i] > 0.5 for i in range(s0, s1)):
            blk_act[b] = 1.0

    padded = [0.0] * n_blocks
    for b in range(n_blocks):
        if blk_act[b] > 0.5:
            for j in range(max(0, b - 7), min(n_blocks, b + 15)):
                padded[j] = 1.0

    smooth = [0.0] * n_blocks
    win = 12
    acc = 0.0
    for b in range(n_blocks):
        acc += padded[b]
        if b >= win:
            acc -= padded[b - win]
        smooth[b] = acc / min(b + 1, win)

    prod_bgm_wav = os.path.join(ASSETS_DIR, "prod_bgm_30sec.wav")
    bgm_eq_path = os.path.join(NARR_DIR, "prod_bgm_30sec_eq.wav")
    run_ffmpeg(["-i", prod_bgm_wav, "-af", "equalizer=f=2500:t=q:w=1.2:g=-2.5", "-ar", str(sr), "-ac", "2", "-c:a", "pcm_s16le", bgm_eq_path])
    with wave.open(bgm_eq_path, "rb") as wf:
        bgm_raw = wf.readframes(wf.getnframes())
    bgm_arr = array("h")
    bgm_arr.frombytes(bgm_raw)

    mix_raw_path = os.path.join(NARR_DIR, "ma_google_tts_high_raw_30sec.wav")
    mix_pcm = array("h")
    n_bgm = len(bgm_arr) // 2
    for i in range(total_samples):
        b = i // hop
        duck = smooth[b] if b < n_blocks else 0.0
        bgm_gain = 0.74 * (1.0 - duck) + 0.25 * duck
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

    ma_out_path = os.path.join(ASSETS_DIR, "ma_30sec_prod_bgm_google_tts.wav")
    run_ffmpeg([
        "-i", mix_raw_path,
        "-af", "loudnorm=I=-18:TP=-1.5:LRA=7,afade=t=in:st=0:d=0.025,afade=t=out:st=29.75:d=0.22",
        "-t", "30.000",
        "-ar", str(sr), "-ac", "2", "-c:a", "pcm_s16le",
        ma_out_path
    ])
    print("SAVED HIGH-TENSION GOOGLE TTS MA WAV:", ma_out_path, "dur=", round(get_wav_duration(ma_out_path), 3))


if __name__ == "__main__":
    main()
