# -*- coding: utf-8 -*-
"""
Build the complete 4K (3840x2160 @ 29.97fps) DaVinci Resolve Studio 21.2 timeline for:
  2026-11-19 ワインとジャズのコンサート (HONKA music SALON / DALUMA x 田中 良明)

Steps performed:
  1. Configure Resolve project settings (3840x2160 @ 29.97fps).
  2. Import 5 raw DJI clips (explicit chronological order 0001..0005) + 4 cards + 28 telops into Media Pool bins.
  3. Assemble master V1/A1 timeline with exact trims, smooth audio/video fades, and Recording-Gap Bridge.
  4. Place all 5 member-intro telops and 23 song/medley telops on V2 with smooth FadeIn/FadeOut.
  5. Apply gentle ASC CDL color-match lift to Clip 04 & Clip 05 (post-restart exposure match).
  6. Run DaVinci Resolve native Stabilization on fixed-table clips (Clip 01, 02, 03, 04, 05A) — skipping Clip 05B (standing bow tilt).
  7. Save project and export 12-frame visual audit board (keyframes_audit_board.png) for pre-render inspection.
"""
import os
import sys
import time
import json
from PIL import Image, ImageDraw, ImageFont

os.environ["RESOLVE_SCRIPT_API"] = r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting"
os.environ["RESOLVE_SCRIPT_LIB"] = r"C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll"
sys.path.append(r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules")
import DaVinciResolveScript as dvr

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

RAW_DIR = r"H:\2026-11-19_ワインとジャズのコンサート\DJI_001"
DRAFT_DIR = r"G:\マイドライブ\git\nobuyukitakahashi\02_Creative_Dept\davinci\drafts\2026-11-19_ワインとジャズのコンサート"
MOV_DIR = os.path.join(DRAFT_DIR, "graphics_mov")
STILLS_DIR = os.path.join(DRAFT_DIR, "audit_stills")
os.makedirs(STILLS_DIR, exist_ok=True)

RAW_CLIPS = [
    ("01", "DJI_20261119192743_0001_D.MP4"),
    ("02", "DJI_20261119200046_0002_D.MP4"),
    ("03", "DJI_20261119202831_0003_D.MP4"),
    ("04", "DJI_20000101090033_0004_D.MP4"),
    ("05", "DJI_20000101093520_0005_D.MP4"),
]

CARDS = [
    "00_opening_title.mov",
    "01_part2_card.mov",
    "02_gap_bridge_card.mov",
    "99_ending_credits.mov",
]

# Telop cues: (mov_name, source_seg_key, clip_local_sec, duration_frames, label)
TELOP_CUES = [
    # Part 1 — Clip 01
    ("song_01_jounetsu.mov",     "c01",  183.0, 420, "01. 情熱大陸"),
    ("member_01_suzuki.mov",     "c01",  573.0, 420, "Member: 鈴木 真明地"),
    ("member_02_watanabe.mov",   "c01",  611.0, 420, "Member: 渡邊 丈留"),
    ("member_03_takahashi.mov",  "c01",  650.0, 420, "Member: 高橋 幹太"),
    ("member_04_tanaka.mov",     "c01",  692.0, 420, "Member: 田中 良明"),
    ("member_05_nishiura.mov",   "c01",  738.0, 420, "Member: 西浦 颯"),
    ("song_02_takefive.mov",     "c01",  813.0, 420, "02. Take Five"),
    ("song_03_champs.mov",       "c01", 1127.0, 420, "03. オー・シャンゼリゼ"),
    ("song_04_atrain.mov",       "c01", 1483.0, 420, "04. A列車で行こう"),
    ("song_05_singsing.mov",     "c01", 1867.0, 420, "05. Sing, Sing, Sing"),

    # Part 2 — Clip 03 (Seiko Matsuda Medley 1-3)
    ("song_06_seiko_01.mov",     "c03",   13.0, 420, "06. SWEET MEMORIES"),
    ("song_07_seiko_02.mov",     "c03",  120.0, 420, "07. 赤いスイートピー"),
    ("song_08_seiko_03.mov",     "c03",  245.0, 480, "08. 瑠璃色の地球"),

    # Part 2 — Clip 04 (Seiko 4 + Cherbourg + Stevie Medley + Beat It + Beauty + Matsuken + Checkers 1-3)
    ("song_09_seiko_04.mov",     "c04",    2.0, 420, "09. 青い珊瑚礁"),
    ("song_10_cherbourg.mov",    "c04",  187.0, 420, "10. シェルブールの雨傘"),
    ("song_11_stevie_01.mov",    "c04",  569.0, 390, "11. Sir Duke"),
    ("song_12_stevie_02.mov",    "c04",  639.0, 390, "12. Superstition"),
    ("song_13_stevie_03.mov",    "c04",  700.0, 390, "13. I Wish"),
    ("song_14_stevie_04.mov",    "c04",  761.0, 390, "14. Isn't She Lovely"),
    ("song_15_beatit.mov",       "c04",  828.0, 420, "15. Beat It"),
    ("song_16_beauty.mov",       "c04", 1096.0, 420, "16. 美女と野獣"),
    ("song_17_matsuken.mov",     "c04", 1631.0, 420, "17. マツケンサンバ II"),
    ("song_18_checkers_01.mov",  "c04", 1946.0, 390, "18. ギザギザハートの子守唄"),
    ("song_19_checkers_02.mov",  "c04", 2012.0, 360, "19. 星屑のステージ"),
    ("song_20_checkers_03.mov",  "c04", 2028.0, 390, "20. 涙のリクエスト"),

    # Part 2 — Clip 05A (Checkers 4 + Miagete + Encore September)
    ("song_21_checkers_04.mov",  "c05a",  39.0, 420, "21. ジュリアに傷心"),
    ("song_22_miagete.mov",      "c05a", 265.0, 420, "22. 見上げてごらん夜の星を"),
    ("song_23_september.mov",    "c05a", 502.0, 450, "23. ENCORE September"),
]

def main():
    t_all = time.time()
    resolve = dvr.scriptapp("Resolve")
    if not resolve:
        raise RuntimeError("Could not connect to DaVinci Resolve Studio!")
    pm = resolve.GetProjectManager()
    proj = pm.GetCurrentProject()
    print(f"Connected to Resolve {resolve.GetVersionString()} | Project: {proj.GetName()}")

    # 1. Clean existing timeline if re-running & configure 4K 29.97fps project settings
    mp = proj.GetMediaPool()
    tl_name = "2026-11-19_ワインとジャズのコンサート_Master"
    for i in range(1, proj.GetTimelineCount() + 1):
        t = proj.GetTimelineByIndex(i)
        if t and t.GetName() == tl_name:
            mp.DeleteTimelines([t])
            print(f"Deleted previous timeline: {tl_name}")
            break

    proj.SetSetting("timelineResolutionWidth", "3840")
    proj.SetSetting("timelineResolutionHeight", "2160")
    proj.SetSetting("timelineFrameRate", "29.97")
    proj.SetSetting("timelinePlaybackFrameRate", "29.97")
    proj.SetSetting("useDropFrameTimecode", "0")

    # 2. Organize Media Pool bins cleanly
    root = mp.GetRootFolder()
    existing_subs = {sf.GetName(): sf for sf in root.GetSubFolderList()}
    def get_or_make_bin(name):
        if name in existing_subs:
            return existing_subs[name]
        b = mp.AddSubFolder(root, name)
        existing_subs[name] = b
        return b

    bin_raw   = get_or_make_bin("01_Footage")
    bin_cards = get_or_make_bin("02_Titles_Cards")
    bin_telop = get_or_make_bin("03_Telops")

    def import_map(folder, paths):
        mp.SetCurrentFolder(folder)
        existing = {}
        for c in (folder.GetClipList() or []):
            key = c.GetClipProperty("File Name") or c.GetName()
            existing[key] = c
        to_add = [p for p in paths if os.path.basename(p) not in existing]
        if to_add:
            added = mp.ImportMedia(to_add)
            for c in (added or []):
                key = c.GetClipProperty("File Name") or c.GetName()
                existing[key] = c
        return existing

    raw_paths = [os.path.join(RAW_DIR, fn) for _, fn in RAW_CLIPS]
    raw_map = import_map(bin_raw, raw_paths)
    print("Imported raw footage:", list(raw_map.keys()))

    card_paths = [os.path.join(MOV_DIR, fn) for fn in CARDS]
    card_map = import_map(bin_cards, card_paths)
    print("Imported cards:", len(card_map))

    telop_paths = [os.path.join(MOV_DIR, cue[0]) for cue in TELOP_CUES]
    telop_map = import_map(bin_telop, telop_paths)
    print("Imported telops:", len(telop_map))

    # Inspect exact frame counts reported by Resolve for all raw clips
    raw_frames = {}
    for key, fn in RAW_CLIPS:
        c = raw_map[fn]
        nf = int(c.GetClipProperty("Frames"))
        raw_frames[key] = nf
        print(f"  Clip {key} ({fn}): {nf} frames ({nf/FPS:.2f}s), FPS={c.GetClipProperty('FPS')}")

    # 3. Create Master Timeline
    mp.SetCurrentFolder(root)
    tl = mp.CreateEmptyTimeline(tl_name)
    if not tl:
        raise RuntimeError("Failed to create timeline!")
    proj.SetCurrentTimeline(tl)
    tl_start = tl.GetStartFrame()
    print(f"Created Timeline '{tl_name}' | StartFrame={tl_start} | FPS={tl.GetSetting('timelineFrameRate')}")

    # Ensure V2 track exists
    if tl.GetTrackCount("video") < 2:
        tl.AddTrack("video")

    # V1 Sequence definition:
    # (seg_key, clip_obj, startFrame, endFrame, fadeIn_f, fadeOut_f, stabilize, apply_cdl)
    c01_clip = raw_map[RAW_CLIPS[0][1]]
    c02_clip = raw_map[RAW_CLIPS[1][1]]
    c03_clip = raw_map[RAW_CLIPS[2][1]]
    c04_clip = raw_map[RAW_CLIPS[3][1]]
    c05_clip = raw_map[RAW_CLIPS[4][1]]

    c01_in  = s2f(178.0)
    c01_out = raw_frames["01"] - 1
    c02_in  = 0
    c02_out = min(s2f(230.0) - 1, raw_frames["02"] - 1)
    c03_in  = s2f(10.0)
    c03_out = min(s2f(265.0) - 1, raw_frames["03"] - 1)
    c04_in  = 0
    c04_out = raw_frames["04"] - 1
    c05a_in  = 0
    c05a_out = s2f(820.0) - 1
    c05b_in  = c05a_out + 1
    c05b_out = min(s2f(851.0) - 1, raw_frames["05"] - 1)

    v1_plan = [
        ("open",  card_map["00_opening_title.mov"],   0, 299,      36, 36, False, False),
        ("c01",   c01_clip,                           c01_in,  c01_out,  36,  0, True,  False),
        ("c02",   c02_clip,                           c02_in,  c02_out,   0, 45, True,  False),
        ("part2", card_map["01_part2_card.mov"],      0, 149,      30, 30, False, False),
        ("c03",   c03_clip,                           c03_in,  c03_out,  30, 75, True,  False),
        ("gap",   card_map["02_gap_bridge_card.mov"], 0, 104,      24, 24, False, False),
        ("c04",   c04_clip,                           c04_in,  c04_out,  60,  0, True,  True),
        ("c05a",  c05_clip,                           c05a_in, c05a_out,  0,  0, True,  True),
        ("c05b",  c05_clip,                           c05b_in, c05b_out,  0, 60, False, True),
        ("end",   card_map["99_ending_credits.mov"],  0, 179,      30, 45, False, False),
    ]

    seg_records = {}  # seg_key -> {v_item, rec_start, rec_end, src_in, stabilize, apply_cdl}
    cursor = tl_start

    for seg_key, clip_obj, sf, ef, fi, fo, do_stab, do_cdl in v1_plan:
        info = {
            "mediaPoolItem": clip_obj,
            "startFrame": sf,
            "endFrame": ef,
            "trackIndex": 1,
            "recordFrame": cursor,
        }
        items = mp.AppendToTimeline([info])
        if not items:
            raise RuntimeError(f"Failed to append V1 segment {seg_key} at recordFrame={cursor}")
        v_item = items[0]
        rec_s = v_item.GetStart()
        rec_e = v_item.GetEnd()
        dur = v_item.GetDuration()
        if fi > 0 or fo > 0:
            v_item.SetFades({"FadeIn": fi, "FadeOut": fo})
        seg_records[seg_key] = {
            "v_item": v_item,
            "rec_start": rec_s,
            "rec_end": rec_e,
            "src_in": sf,
            "fade_in": fi,
            "fade_out": fo,
            "stabilize": do_stab,
            "apply_cdl": do_cdl,
        }
        print(f"V1 [{seg_key:5s}] start={rec_s} end={rec_e} dur={dur}f ({dur/FPS:.2f}s) fades=({fi},{fo})")
        cursor = rec_e

    # Apply matching audio fades on A1 items (matched by GetStart())
    a1_items = tl.GetItemListInTrack("audio", 1) or []
    a1_by_start = {it.GetStart(): it for it in a1_items}
    print(f"Found {len(a1_items)} audio items on A1.")
    for seg_key, rec in seg_records.items():
        ai = a1_by_start.get(rec["rec_start"])
        if ai and (rec["fade_in"] > 0 or rec["fade_out"] > 0):
            ok = ai.SetFades({"FadeIn": rec["fade_in"], "FadeOut": rec["fade_out"]})
            print(f"  A1 [{seg_key:5s}] SetFades({rec['fade_in']}, {rec['fade_out']}) -> {ok}")

    # 4. Place all 28 Telops on V2 with exact frame calculation and smooth fades
    print("\nPlacing 28 telops on V2...")
    telop_log = []
    for mov_name, seg_key, clip_sec, dur_f, label in TELOP_CUES:
        rec = seg_records[seg_key]
        offset_in_seg = s2f(clip_sec) - rec["src_in"]
        rec_frame = int(rec["rec_start"] + offset_in_seg)
        # Ensure telop stays inside segment if near Clip 03 end
        clip_obj = telop_map[mov_name]
        clip_max_end = int(clip_obj.GetClipProperty("Frames")) - 1
        use_end = min(dur_f - 1, clip_max_end)
        # If Clip 03 last telop (瑠璃色の地球), trim end cleanly 0.5s before Clip 03 cut
        if seg_key == "c03" and rec_frame + use_end + 1 > rec["rec_end"] - 15:
            use_end = max(90, int(rec["rec_end"] - 15 - rec_frame - 1))

        info = {
            "mediaPoolItem": clip_obj,
            "mediaType": 1,  # video only
            "startFrame": 0,
            "endFrame": use_end,
            "trackIndex": 2,
            "recordFrame": rec_frame,
        }
        items = mp.AppendToTimeline([info])
        if not items:
            raise RuntimeError(f"Failed to append V2 telop {mov_name} at {rec_frame}")
        t_item = items[0]
        t_item.SetFades({"FadeIn": 18, "FadeOut": 24})
        tl_rel_sec = (t_item.GetStart() - tl_start) / FPS
        mm, ss = divmod(int(round(tl_rel_sec)), 60)
        hh, mm = divmod(mm, 60)
        ts_str = f"{hh:02d}:{mm:02d}:{ss:02d}"
        telop_log.append({
            "label": label,
            "mov": mov_name,
            "timeline_time": ts_str,
            "timeline_sec": round(tl_rel_sec, 2),
            "record_frame": t_item.GetStart(),
            "duration_frames": t_item.GetDuration(),
        })
        print(f"  V2 [{ts_str}] {label:32s} ({t_item.GetDuration()}f)")

    # Save master cue log for documentation
    total_frames = tl.GetEndFrame() - tl_start
    cue_meta = {
        "timeline_name": tl_name,
        "start_frame": tl_start,
        "end_frame": tl.GetEndFrame(),
        "total_frames": total_frames,
        "total_seconds": round(total_frames / FPS, 2),
        "segments": {
            k: {
                "rec_start": v["rec_start"],
                "rec_end": v["rec_end"],
                "rel_start_s": round((v["rec_start"] - tl_start) / FPS, 2),
                "rel_end_s": round((v["rec_end"] - tl_start) / FPS, 2),
                "stabilized": v["stabilize"],
                "cdl_applied": v["apply_cdl"],
            }
            for k, v in seg_records.items()
        },
        "telops": telop_log,
    }
    with open(os.path.join(DRAFT_DIR, "timeline_cue_manifest.json"), "w", encoding="utf-8") as f:
        json.dump(cue_meta, f, ensure_ascii=False, indent=2)

    # 5. Apply gentle ASC CDL Color Match on Clip 04 & Clip 05 (post-restart exposure match)
    print("\nApplying gentle ASC CDL color-match lift to Clip 04 & Clip 05...")
    resolve.OpenPage("color")
    cdl_params = {
        "NodeIndex": "1",
        "Slope": "1.06 1.05 1.04",
        "Offset": "0.010 0.010 0.010",
        "Power": "0.90 0.90 0.90",
        "Saturation": "1.04",
    }
    for seg_key in ("c04", "c05a", "c05b"):
        ok = seg_records[seg_key]["v_item"].SetCDL(cdl_params)
        print(f"  SetCDL [{seg_key}] -> {ok}")

    # Save project before stabilization
    pm.SaveProject()
    print("Project saved before stabilization.", flush=True)

    # 6. Run DaVinci Resolve Native Stabilization on fixed-table clips (skip c05b standing bow!)
    print("\nRunning DaVinci Resolve native Stabilization on fixed-table clips...", flush=True)
    for seg_key in ("c01", "c02", "c03", "c04", "c05a"):
        t0 = time.time()
        print(f"  Stabilizing [{seg_key}] ({(seg_records[seg_key]['rec_end']-seg_records[seg_key]['rec_start'])/FPS:.1f}s)...", flush=True)
        ok = seg_records[seg_key]["v_item"].Stabilize()
        print(f"    -> {ok} ({time.time()-t0:.1f}s)", flush=True)
        pm.SaveProject()

    # Save project right after build + stabilization
    pm.SaveProject()
    print("Project saved after timeline build, CDL, and stabilization.", flush=True)

    # 7. Export 12-frame Visual Audit Board from Resolve live timeline
    print("\nExporting 12 representative stills from Resolve timeline for visual audit...")
    resolve.OpenPage("color")

    def seg_mid(seg_key, offset_s):
        return seg_records[seg_key]["rec_start"] + s2f(offset_s)

    audit_points = [
        ("01_OpeningTitle",     seg_mid("open",  5.0),  "01. Opening Title (Official Logos)"),
        ("02_Song01_Jounetsu",  seg_mid("c01",   9.0),  "02. Part 1: Jounetsu Tairiku + Telop"),
        ("03_Member_Suzuki",    seg_mid("c01", 400.0),  "03. Member Intro: Machi Suzuki"),
        ("04_Member_Nishiura",  seg_mid("c01", 565.0),  "04. Member Intro: Hayate Nishiura"),
        ("05_Part2_Card",       seg_mid("part2", 2.5),  "05. Part 2 Intermission Card"),
        ("06_Seiko01_SweetMem", seg_mid("c03",   8.0),  "06. Seiko Medley 01: SWEET MEMORIES"),
        ("07_GapBridge_Card",   seg_mid("gap",   1.7),  "07. Recording-Gap Bridge Card"),
        ("08_Seiko04_Resume",   seg_mid("c04",   7.0),  "08. Clip 04 Resume (CDL + AoSango)"),
        ("09_Stevie01_SirDuke", seg_mid("c04", 574.0),  "09. Stevie Medley 01: Sir Duke"),
        ("10_Checkers04_Julia", seg_mid("c05a", 44.0),  "10. Checkers Medley 04: Julia"),
        ("11_Encore_September", seg_mid("c05a",508.0),  "11. ENCORE: September"),
        ("12_Ending_Credits",   seg_mid("end",   3.0),  "12. Ending Credits"),
    ]

    exported = []
    for fname, abs_f, caption in audit_points:
        tc = frames_to_tc(abs_f, 30)
        tl.SetCurrentTimecode(tc)
        time.sleep(0.35)
        out_png = os.path.join(STILLS_DIR, fname + ".png")
        ok = proj.ExportCurrentFrameAsStill(out_png)
        print(f"  Still {fname:22s} @ {tc} -> {ok}")
        if ok and os.path.exists(out_png):
            exported.append((out_png, caption))

    # Build 4x3 contact sheet board (2560 x 1200)
    if exported:
        cols, rows = 4, 3
        tw, th = 640, 360
        cap_h = 34
        board = Image.new("RGB", (cols * tw, rows * (th + cap_h)), (14, 10, 12))
        draw = ImageDraw.Draw(board)
        f_cap = ImageFont.truetype(r"C:\Windows\Fonts\yumin.ttf", 20)
        for idx, (p, cap) in enumerate(exported[:12]):
            r, c = divmod(idx, cols)
            im = Image.open(p).convert("RGB").resize((tw, th), Image.Resampling.LANCZOS)
            x, y = c * tw, r * (th + cap_h)
            board.paste(im, (x, y))
            draw.rectangle([x, y + th, x + tw, y + th + cap_h], fill=(28, 12, 16))
            draw.text((x + 12, y + th + 6), cap, font=f_cap, fill=(242, 224, 180))
        board_path = os.path.join(DRAFT_DIR, "keyframes_audit_board.png")
        board.save(board_path, quality=92)
        print("Saved audit board:", board_path)

    print(f"\nTIMELINE BUILD + STABILIZATION + AUDIT COMPLETE in {time.time()-t_all:.1f}s!")
    print(f"Total Timeline Duration: {total_frames} frames = {total_frames/FPS:.2f}s ({int(total_frames/FPS)//60}m {int(total_frames/FPS)%60}s)")

if __name__ == "__main__":
    main()
