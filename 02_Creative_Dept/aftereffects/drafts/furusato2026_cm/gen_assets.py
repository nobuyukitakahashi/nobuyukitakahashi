import os
import math
import random
import wave
from array import array
from PIL import Image, ImageDraw

OUT_DIR = r"g:\マイドライブ\git\nobuyukitakahashi\02_Creative_Dept\aftereffects\drafts\furusato2026_cm\assets"
PARTS_DIR = r"C:\Users\nobuy\OneDrive\My Documents\クライアント別\飯田商工会議所_飯田職業安定協会\2026-12-27_ふるさと合同企業説明会\2026-12-27_ふるさと合同企業説明会_パーツ"
os.makedirs(OUT_DIR, exist_ok=True)


def generate_smpte_hd_bars():
    W, H = 1920, 1080
    img = Image.new("RGB", (W, H), (0, 0, 0))
    draw = ImageDraw.Draw(img)

    y1 = int(H * 7 / 12)   # 630
    y2 = int(H * 8 / 12)   # 720
    y3 = int(H * 9 / 12)   # 810
    left_w = 240
    right_x = 1680
    bar_xs = [left_w + round(i * 1440 / 7) for i in range(8)]

    c_gray40 = (104, 104, 104)
    c_white75 = (191, 191, 191)
    c_yellow75 = (191, 191, 0)
    c_cyan75 = (0, 191, 191)
    c_green75 = (0, 191, 0)
    c_magenta75 = (191, 0, 191)
    c_red75 = (191, 0, 0)
    c_blue75 = (0, 0, 191)
    c_white100 = (255, 255, 255)
    c_black = (16, 16, 16)
    c_superblack = (0, 0, 0)
    c_pluge_plus = (28, 28, 28)
    c_i = (0, 33, 76)
    c_q = (50, 0, 106)
    c_cyan100 = (0, 255, 255)
    c_blue100 = (0, 0, 255)
    c_yellow100 = (255, 255, 0)
    c_red100 = (255, 0, 0)

    # Row 1: Top 7/12
    draw.rectangle([0, 0, left_w, y1], fill=c_gray40)
    for i, col in enumerate([c_white75, c_yellow75, c_cyan75, c_green75, c_magenta75, c_red75, c_blue75]):
        draw.rectangle([bar_xs[i], 0, bar_xs[i + 1], y1], fill=col)
    draw.rectangle([right_x, 0, W, y1], fill=c_gray40)

    # Row 2: 1/12 strip
    draw.rectangle([0, y1, left_w, y2], fill=c_cyan100)
    draw.rectangle([left_w, y1, bar_xs[1], y2], fill=c_i)
    draw.rectangle([bar_xs[1], y1, bar_xs[7], y2], fill=c_white75)
    draw.rectangle([right_x, y1, W, y2], fill=c_blue100)

    # Row 3: 1/12 Y-ramp strip
    draw.rectangle([0, y2, left_w, y3], fill=c_yellow100)
    draw.rectangle([left_w, y2, bar_xs[1], y3], fill=c_q)
    ramp_w = right_x - bar_xs[1]
    for x in range(ramp_w):
        v = int(16 + (235 - 16) * (x / max(1, ramp_w - 1)))
        draw.line([(bar_xs[1] + x, y2), (bar_xs[1] + x, y3)], fill=(v, v, v))
    draw.rectangle([right_x, y2, W, y3], fill=c_red100)

    # Row 4: Bottom 3/12 PLUGE
    draw.rectangle([0, y3, left_w, H], fill=(38, 38, 38))
    b1 = left_w + int(1440 * 1.5 / 7)
    b2 = left_w + int(1440 * 3.5 / 7)
    b3 = left_w + int(1440 * 4.5 / 7)
    b4 = left_w + int(1440 * 5.0 / 7)
    b5 = left_w + int(1440 * 5.33 / 7)
    b6 = left_w + int(1440 * 5.66 / 7)
    b7 = left_w + int(1440 * 6.0 / 7)
    draw.rectangle([left_w, y3, b1, H], fill=c_black)
    draw.rectangle([b1, y3, b2, H], fill=c_white100)
    draw.rectangle([b2, y3, b3, H], fill=c_black)
    draw.rectangle([b3, y3, b4, H], fill=c_superblack)
    draw.rectangle([b4, y3, b5, H], fill=c_black)
    draw.rectangle([b5, y3, b6, H], fill=c_pluge_plus)
    draw.rectangle([b6, y3, b7, H], fill=c_black)
    draw.rectangle([b7, y3, right_x, H], fill=c_black)
    draw.rectangle([right_x, y3, W, H], fill=(38, 38, 38))

    out_path = os.path.join(OUT_DIR, "smpte_hd_bars_1920x1080.png")
    img.save(out_path)
    print("SAVED:", out_path)


def extract_search_bar_only():
    src = os.path.join(PARTS_DIR, "イイダカイシャナビで検索.png")
    im = Image.open(src).convert("RGBA")
    # Crop left portion excluding right QR code (QR starts around x=1060)
    w, h = im.size
    # Find exact empty vertical column gap between search cursor and QR code
    alpha = im.split()[3]
    cut_x = 1045
    for x in range(1060, 950, -1):
        col_max = max(alpha.getpixel((x, y)) for y in range(h))
        if col_max == 0:
            cut_x = x
            break
    cropped = im.crop((0, 0, cut_x, h))
    bb = cropped.getbbox()
    if bb:
        cropped = cropped.crop(bb)
    out_path = os.path.join(OUT_DIR, "search_bar_only.png")
    cropped.save(out_path)
    print("SAVED:", out_path, "size=", cropped.size, "cut_x=", cut_x)


def generate_temp_bgm():
    # Bright, uplifting corporate-pop temporary BGM (30.0s, 48kHz stereo, BPM=120)
    # Pure Python stdlib (no scipy/numpy DLL dependency)
    sr = 48000
    dur = 30.0
    n_samples = int(sr * dur)
    L = [0.0] * n_samples
    R = [0.0] * n_samples
    two_pi = 2.0 * math.pi
    inv_sr = 1.0 / sr
    rng = random.Random(2026)

    def midi_to_hz(m):
        return 440.0 * (2.0 ** ((m - 69.0) / 12.0))

    def add_note(start_s, dur_s, freq, amp=0.1, pan=0.0, wave_type="pluck"):
        i0 = int(start_s * sr)
        n = int(dur_s * sr)
        if i0 >= n_samples or n <= 0:
            return
        i1 = min(n_samples, i0 + n)
        gl = math.sqrt(0.5 * (1.0 - pan)) * amp
        gr = math.sqrt(0.5 * (1.0 + pan)) * amp
        w1 = two_pi * freq * inv_sr
        w2 = w1 * 2.0
        w3 = w1 * 3.0
        if wave_type == "pluck":
            dec = -5.8 * inv_sr
            att_n = max(1, int(0.008 * sr))
            for k in range(i1 - i0):
                a = 1.0 if k >= att_n else k / att_n
                e = a * math.exp(dec * k)
                v = (math.sin(w1 * k) * 0.65 + math.sin(w2 * k) * 0.25 + math.sin(w3 * k) * 0.10) * e
                idx = i0 + k
                L[idx] += v * gl
                R[idx] += v * gr
        elif wave_type == "pad":
            w1b = w1 * 1.0025
            att_n = max(1, int(0.18 * sr))
            rel_n = max(1, int(0.28 * sr))
            total = i1 - i0
            for k in range(total):
                a = 1.0 if k >= att_n else k / att_n
                rem = total - k
                r = 1.0 if rem >= rel_n else rem / rel_n
                e = a * r
                v = (math.sin(w1 * k) * 0.55 + math.sin(w1b * k) * 0.30 + math.sin(w2 * k) * 0.15) * e
                idx = i0 + k
                L[idx] += v * gl
                R[idx] += v * gr
        elif wave_type == "bass":
            dec = -2.8 * inv_sr
            att_n = max(1, int(0.01 * sr))
            for k in range(i1 - i0):
                a = 1.0 if k >= att_n else k / att_n
                e = a * math.exp(dec * k)
                s = math.sin(w1 * k)
                v = (s * 0.72 + math.sin(w2 * k) * 0.28) * e
                idx = i0 + k
                L[idx] += v * gl
                R[idx] += v * gr
        elif wave_type == "bell":
            dec = -4.2 * inv_sr
            att_n = max(1, int(0.004 * sr))
            for k in range(i1 - i0):
                a = 1.0 if k >= att_n else k / att_n
                e = a * math.exp(dec * k)
                v = (math.sin(w1 * k) * 0.60 + math.sin(w2 * k) * 0.25 + math.sin(w3 * k) * 0.15) * e
                idx = i0 + k
                L[idx] += v * gl
                R[idx] += v * gr

    def add_kick(start_s, amp=0.26):
        i0 = int(start_s * sr)
        n = int(0.16 * sr)
        if i0 >= n_samples:
            return
        i1 = min(n_samples, i0 + n)
        phase = 0.0
        for k in range(i1 - i0):
            lt = k * inv_sr
            freq = 48.0 + 110.0 * math.exp(-lt * 34.0)
            phase += two_pi * freq * inv_sr
            env = math.exp(-lt * 17.0) * (1.0 if lt > 0.003 else lt / 0.003)
            v = math.sin(phase) * env * amp
            idx = i0 + k
            L[idx] += v
            R[idx] += v

    def add_hat(start_s, amp=0.045, open_hat=False):
        i0 = int(start_s * sr)
        n = int((0.11 if open_hat else 0.04) * sr)
        if i0 >= n_samples:
            return
        i1 = min(n_samples, i0 + n)
        dec = -19.0 if open_hat else -72.0
        prev = 0.0
        for k in range(i1 - i0):
            lt = k * inv_sr
            x = rng.uniform(-1.0, 1.0)
            hp = x - prev
            prev = x
            v = hp * math.exp(dec * lt) * amp
            idx = i0 + k
            L[idx] += v * 0.9
            R[idx] += v * 1.1

    def add_clap(start_s, amp=0.10):
        i0 = int(start_s * sr)
        n = int(0.12 * sr)
        if i0 >= n_samples:
            return
        i1 = min(n_samples, i0 + n)
        lp = 0.0
        prev = 0.0
        for k in range(i1 - i0):
            lt = k * inv_sr
            x = rng.uniform(-1.0, 1.0)
            # simple crude bandpass
            lp = lp * 0.72 + x * 0.28
            bp = lp - prev * 0.55
            prev = lp
            burst = 1.0 + 0.55 * math.exp(-((lt - 0.011) / 0.004) ** 2)
            v = bp * math.exp(-24.0 * lt) * burst * amp
            idx = i0 + k
            L[idx] += v * 1.05
            R[idx] += v * 0.95

    def add_whoosh(center_s, span=0.40, amp=0.075):
        start_s = max(0.0, center_s - span * 0.62)
        i0 = int(start_s * sr)
        n = int(span * sr)
        if i0 >= n_samples:
            return
        i1 = min(n_samples, i0 + n)
        total = i1 - i0
        lp = 0.0
        prev = 0.0
        for k in range(total):
            frac = k / max(1, total - 1)
            x = rng.uniform(-1.0, 1.0)
            alpha = 0.08 + 0.35 * math.sin(math.pi * frac)
            lp = lp * (1.0 - alpha) + x * alpha
            bp = lp - prev * 0.7
            prev = lp
            env = (math.sin(math.pi * frac) ** 1.5) * amp
            pan = -0.7 + 1.4 * frac
            idx = i0 + k
            L[idx] += bp * env * (1.0 - 0.45 * pan)
            R[idx] += bp * env * (1.0 + 0.45 * pan)

    # Chord progression (Bright C Major corporate pop: Fmaj7 -> G6 -> Em7 -> Am7)
    chords = [
        ([53, 57, 60, 64], 41),  # Fmaj7
        ([55, 59, 62, 64], 43),  # G6
        ([52, 55, 59, 62], 40),  # Em7
        ([57, 60, 64, 67], 45),  # Am7
    ]

    for sec in range(0, 28):
        ch_notes, bass_m = chords[sec % 4]
        # Warm soft pad every 2 seconds
        if sec % 2 == 0:
            pad_amp = 0.040 if (sec < 9 or sec >= 20) else 0.028
            for idx, m in enumerate(ch_notes):
                add_note(sec, 2.05, midi_to_hz(m), amp=pad_amp, pan=(-0.35 + 0.23 * idx), wave_type="pad")
        # Bass groove from 3s
        if sec >= 3:
            add_note(sec, 0.48, midi_to_hz(bass_m), amp=0.14, pan=0.0, wave_type="bass")
            add_note(sec + 0.75, 0.28, midi_to_hz(bass_m + 12), amp=0.07, pan=0.0, wave_type="bass")
        # Arpeggio pluck (BPM=120 16th/8th feel)
        arp = [ch_notes[0] + 12, ch_notes[1] + 12, ch_notes[2] + 12, ch_notes[3] + 12]
        for step in range(4):
            st_t = sec + step * 0.25
            if st_t >= 28.0:
                break
            amp = 0.052 if (sec < 4 or sec >= 20) else 0.038
            add_note(st_t, 0.34, midi_to_hz(arp[step]), amp=amp, pan=(-0.38 if step % 2 == 0 else 0.38), wave_type="pluck")
        # Drums
        if 4 <= sec < 28:
            add_kick(sec, amp=0.22)
            add_kick(sec + 0.5, amp=0.18)
            add_clap(sec + 0.5, amp=0.095)
            for h in range(4):
                add_hat(sec + h * 0.25, amp=0.030 if h % 2 == 0 else 0.045, open_hat=(h == 3 and sec % 2 == 1))
        elif sec == 3:
            add_kick(3.5, amp=0.26)
            add_clap(3.5, amp=0.11)

    # Visual-sync bright chime hits
    hits = [
        (0.3, 76), (1.2, 79),
        (3.5, 84), (5.2, 79), (6.5, 84),
        (9.8, 76), (11.2, 79), (12.4, 81),
        (16.0, 76), (16.55, 79), (17.1, 84),
        (20.8, 84), (21.1, 88),
        (25.2, 79), (25.6, 84),
    ]
    for ht, m in hits:
        add_note(ht, 0.60, midi_to_hz(m), amp=0.075, pan=0.12, wave_type="bell")

    # Transition whooshes
    for wt in [3.4, 9.4, 15.4, 20.4, 24.9]:
        add_whoosh(wt, span=0.40, amp=0.085)

    # Final resolving bright Cmaj9 finish (28.0..29.75s)
    for idx, m in enumerate([48, 60, 64, 67, 71, 74]):
        add_note(28.0 + idx * 0.035, 1.75, midi_to_hz(m), amp=0.050, pan=(-0.4 + 0.16 * idx), wave_type="pad")
    add_note(28.0, 1.5, midi_to_hz(84), amp=0.09, pan=0.0, wave_type="bell")
    add_kick(28.0, amp=0.20)

    # Fade in (0.04s) & fade out (29.0..29.85s, silent 29.85..30.0s)
    fade_in_n = int(0.04 * sr)
    fo_start = int(29.0 * sr)
    fo_end = int(29.85 * sr)
    for i in range(fade_in_n):
        g = i / fade_in_n
        L[i] *= g
        R[i] *= g
    for i in range(fo_start, fo_end):
        g = (fo_end - i) / (fo_end - fo_start)
        L[i] *= g
        R[i] *= g
    for i in range(fo_end, n_samples):
        L[i] = 0.0
        R[i] = 0.0

    # Peak normalize to -6 dBFS (0.50)
    peak = max(max(abs(x) for x in L), max(abs(x) for x in R))
    scale = (0.50 / peak) if peak > 0 else 1.0
    pcm = array("h")
    for i in range(n_samples):
        vl = int(max(-32767, min(32767, round(L[i] * scale * 32767.0))))
        vr = int(max(-32767, min(32767, round(R[i] * scale * 32767.0))))
        pcm.append(vl)
        pcm.append(vr)

    wav_path = os.path.join(OUT_DIR, "temp_bgm_30sec_bpm120.wav")
    with wave.open(wav_path, "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(pcm.tobytes())
    print("SAVED:", wav_path, "samples=", n_samples, "peak_norm=0.50 (-6dBFS)")


if __name__ == "__main__":
    generate_smpte_hd_bars()
    extract_search_bar_only()
    generate_temp_bgm()
