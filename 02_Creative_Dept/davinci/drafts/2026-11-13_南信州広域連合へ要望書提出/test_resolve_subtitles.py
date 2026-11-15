import os
import sys
import wave

os.environ["RESOLVE_SCRIPT_API"] = r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting"
os.environ["RESOLVE_SCRIPT_LIB"] = r"C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll"
sys.path.append(r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules")

import DaVinciResolveScript as dvr_script

draft_dir = r"g:\マイドライブ\git\nobuyukitakahashi\02_Creative_Dept\davinci\drafts\2026-11-13_南信州広域連合へ要望書提出"
wav_path = os.path.join(draft_dir, "edited_audio_16k.wav")

# Split wav_path into 5 chunks of 33s for precise timestamp verification
with wave.open(wav_path, "rb") as wf:
    sr = wf.getframerate()
    nframes = wf.getnframes()
    raw = wf.readframes(nframes)

chunks = [(0, 35), (35, 70), (70, 105), (105, 135), (135, 163)]
for t0, t1 in chunks:
    i0 = min(nframes, int(t0 * sr)) * 2
    i1 = min(nframes, int(t1 * sr)) * 2
    c_path = os.path.join(draft_dir, f"audio_chunk_{t0:03d}_{t1:03d}.wav")
    with wave.open(c_path, "wb") as out_wf:
        out_wf.setnchannels(1)
        out_wf.setsampwidth(2)
        out_wf.setframerate(sr)
        out_wf.writeframes(raw[i0:i1])
    print("Saved chunk:", c_path)

resolve = dvr_script.scriptapp("Resolve")
proj = resolve.GetProjectManager().GetCurrentProject()
tl = proj.GetCurrentTimeline()
print("Timeline:", tl.GetName())
print("Sub track count before:", tl.GetTrackCount("subtitle"))

# Check if CreateSubtitlesFromAudio works
try:
    sub_settings = {
        resolve.SUBTITLE_LANGUAGE: resolve.AUTO_CAPTION_JAPANESE,
        resolve.SUBTITLE_CHARS_PER_LINE: 28,
        resolve.SUBTITLE_LINE_BREAK: resolve.AUTO_CAPTION_LINE_SINGLE,
        resolve.SUBTITLE_GAP: 0
    }
    print("Calling CreateSubtitlesFromAudio with settings:", sub_settings)
    res = tl.CreateSubtitlesFromAudio(sub_settings)
    print("CreateSubtitlesFromAudio result:", res)
except Exception as e:
    print("CreateSubtitlesFromAudio exception:", e)

print("Sub track count after:", tl.GetTrackCount("subtitle"))
if tl.GetTrackCount("subtitle") >= 1:
    sub_items = tl.GetItemListInTrack("subtitle", 1)
    print(f"Found {len(sub_items)} subtitle items:")
    tl_start = tl.GetStartFrame()
    for it in sub_items:
        s_sec = (it.GetStart() - tl_start) / 29.97
        e_sec = (it.GetEnd() - tl_start) / 29.97
        print(f"  [{s_sec:6.2f}s - {e_sec:6.2f}s] ({it.GetStart()}-{it.GetEnd()}): {it.GetName()}")
