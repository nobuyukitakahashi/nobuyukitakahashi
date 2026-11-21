# -*- coding: utf-8 -*-
"""Verify Clip 05 encore onset & c05a/c05b boundary, and export an accurately synced 12-frame audit board."""
import json
import os
import sys
import time
from PIL import Image, ImageDraw, ImageFont

DRAFT_DIR = r"G:\マイドライブ\git\nobuyukitakahashi\02_Creative_Dept\davinci\drafts\2026-11-19_ワインとジャズのコンサート"
STILLS_DIR = os.path.join(DRAFT_DIR, "audit_stills_v2")
os.makedirs(STILLS_DIR, exist_ok=True)

FPS = 30000.0 / 1001.0
def s2f(sec):
    return int(round(sec * FPS))

def frames_to_tc(frame_abs, fps_int=30):
    f = int(round(frame_abs))
    ff = f % fps_int
    tot_s = f // fps_int
    ss = tot_s % 60
    mm = (tot_s // 60) % 60
    hh = tot_s // 3600
    return f"{hh:02d}:{mm:02d}:{ss:02d}:{ff:02d}"

# 1. Check Clip 05 RMS around Encore September (495..535s)
s = json.load(open(os.path.join(DRAFT_DIR, "analysis_summary.json"), encoding="utf-8"))
rms05 = s["rms"]["05"]["rms_per_sec"]
print("Clip 05 RMS 495..535s:")
for sec in range(495, 536):
    bar = "#" * max(0, int((rms05[sec] + 45) / 2))
    print(f"  {sec:3d}s ({sec//60}:{sec%60:02d}): {rms05[sec]:5.1f} dB  {bar}")

# 2. Connect to Resolve & export properly settled 12-frame audit board
os.environ["RESOLVE_SCRIPT_API"] = r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting"
os.environ["RESOLVE_SCRIPT_LIB"] = r"C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll"
sys.path.append(r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules")
import DaVinciResolveScript as dvr

res = dvr.scriptapp("Resolve")
pm = res.GetProjectManager()
proj = pm.GetCurrentProject()
tl = proj.GetCurrentTimeline()
manifest = json.load(open(os.path.join(DRAFT_DIR, "timeline_cue_manifest.json"), encoding="utf-8"))
segs = manifest["segments"]

res.OpenPage("color")
time.sleep(0.8)

# Export 2-frame settle helper (avoids 1-step stale GPU frame buffer on Color page)
def export_clean_still(abs_f, out_png):
    tc = frames_to_tc(abs_f, 30)
    tl.SetCurrentTimecode(tc)
    time.sleep(0.9)
    # Trigger a tiny 1-frame nudge + back so Color GPU buffer flushes deterministically
    tl.SetCurrentTimecode(frames_to_tc(abs_f + 1, 30))
    time.sleep(0.25)
    tl.SetCurrentTimecode(tc)
    time.sleep(0.6)
    return proj.ExportCurrentFrameAsStill(out_png), tc

def seg_mid(seg_key, offset_s):
    return segs[seg_key]["rec_start"] + s2f(offset_s)

audit_points = [
    ("01_OpeningTitle",     seg_mid("open",  5.0),  "01. Opening Title (Official Logos)"),
    ("02_Song01_Jounetsu",  seg_mid("c01",   9.0),  "02. Part 1: 情熱大陸 + Telop"),
    ("03_Member_Suzuki",    seg_mid("c01", 400.0),  "03. Member Intro: 鈴木 真明地"),
    ("04_Member_Nishiura",  seg_mid("c01", 565.0),  "04. Member Intro: 西浦 颯"),
    ("05_Part2_Card",       seg_mid("part2", 2.5),  "05. Part 2 Intermission Card"),
    ("06_Seiko01_SweetMem", seg_mid("c03",   8.0),  "06. 松田聖子メドレー 01: SWEET MEMORIES"),
    ("07_GapBridge_Card",   seg_mid("gap",   1.7),  "07. Recording-Gap Bridge Card"),
    ("08_Seiko04_Resume",   seg_mid("c04",   7.0),  "08. Clip 04 Resume (CDL + 青い珊瑚礁)"),
    ("09_Stevie01_SirDuke", seg_mid("c04", 574.0),  "09. Stevie Medley 01: Sir Duke"),
    ("10_Checkers04_Julia", seg_mid("c05a", 44.0),  "10. チェッカーズ 04: ジュリアに傷心"),
    ("11_Encore_September", seg_mid("c05a",508.0),  "11. ★ ENCORE: September"),
    ("12_Ending_Credits",   seg_mid("end",   3.0),  "12. Ending Credits"),
]

# Also check c05a end vs c05b start boundary
boundary_pts = [
    ("90_c05a_end",   segs["c05a"]["rec_end"] - 30),
    ("91_c05b_start", segs["c05b"]["rec_start"] + 30),
]

exported = []
for fname, abs_f, cap in audit_points:
    out_png = os.path.join(STILLS_DIR, fname + ".png")
    ok, tc = export_clean_still(abs_f, out_png)
    print(f"  Still {fname:22s} @ {tc} -> {ok}", flush=True)
    if ok and os.path.exists(out_png):
        exported.append((out_png, cap))

for fname, abs_f in boundary_pts:
    out_png = os.path.join(STILLS_DIR, fname + ".png")
    ok, tc = export_clean_still(abs_f, out_png)
    print(f"  Boundary {fname:18s} @ {tc} -> {ok}", flush=True)

# Build clean 4x3 contact sheet board
if exported:
    cols, rows = 4, 3
    tw, th = 640, 360
    cap_h = 36
    board = Image.new("RGB", (cols * tw, rows * (th + cap_h)), (14, 10, 12))
    draw = ImageDraw.Draw(board)
    f_cap = ImageFont.truetype(r"C:\Windows\Fonts\yumindb.ttf", 20)
    for idx, (p, cap) in enumerate(exported[:12]):
        r, c = divmod(idx, cols)
        im = Image.open(p).convert("RGB").resize((tw, th), Image.Resampling.LANCZOS)
        x, y = c * tw, r * (th + cap_h)
        board.paste(im, (x, y))
        draw.rectangle([x, y + th, x + tw, y + th + cap_h], fill=(32, 12, 16))
        draw.text((x + 12, y + th + 7), cap, font=f_cap, fill=(244, 224, 180))
    board_path = os.path.join(DRAFT_DIR, "keyframes_audit_board.png")
    board.save(board_path, quality=94)
    print("Saved synced audit board:", board_path)
