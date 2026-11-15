import os
import sys
import time

RESOLVE_SCRIPT_API = r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting"
RESOLVE_SCRIPT_LIB = r"C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll"
os.environ["RESOLVE_SCRIPT_API"] = RESOLVE_SCRIPT_API
os.environ["RESOLVE_SCRIPT_LIB"] = RESOLVE_SCRIPT_LIB
sys.path.append(os.path.join(RESOLVE_SCRIPT_API, "Modules"))

import DaVinciResolveScript as dvr_script

resolve = dvr_script.scriptapp("Resolve")
pm = resolve.GetProjectManager()
proj = pm.GetCurrentProject()
mp = proj.GetMediaPool()
root = mp.GetRootFolder()

# Ensure project settings are Full-HD 1920x1080 @ 29.97 fps
proj.SetSetting("timelineResolutionWidth", "1920")
proj.SetSetting("timelineResolutionHeight", "1080")
proj.SetSetting("timelineFrameRate", "29.97")

clips = {c.GetName(): c for c in root.GetClipList()}
pb17 = clips["PB130017.MOV"]
pb18 = clips["PB130018.MOV"]
pb19 = clips["PB130019.MOV"]
mp3_1328 = clips["11月13日（13-28）南信州広域連合議会 第2回 全員協議会.mp3"]
mp3_1412 = clips["11月13日（14-12）南信州広域連合議会 第2回 全員協議会 資料3 桐林クリーンセンター解体について.mp3"]

# Delete any temporary or old timelines
for i in range(proj.GetTimelineCount(), 0, -1):
    t = proj.GetTimelineByIndex(i)
    if t:
        mp.DeleteTimelines([t])

# 1. Timeline 1: PB130017 (18,435 frames = 10m 15.12s) synced with MP3_1328 (+36.63s = frame 1098)
tl1_name = "01_PB130017_全員協議会_前半_音声同期済"
tl1 = mp.CreateEmptyTimeline(tl1_name)
proj.SetCurrentTimeline(tl1)
start_rec = tl1.GetStartFrame() # 108000

mp.AppendToTimeline([{
    "mediaPoolItem": pb17,
    "startFrame": 0,
    "endFrame": 18435,
    "mediaType": 1,
    "trackIndex": 1,
    "recordFrame": start_rec
}])
mp.AppendToTimeline([{
    "mediaPoolItem": mp3_1328,
    "startFrame": 1098,
    "endFrame": 1098 + 18434,
    "mediaType": 2,
    "trackIndex": 1,
    "recordFrame": start_rec
}])
print(f"Created {tl1_name}: V1={len(tl1.GetItemListInTrack('video', 1))}, A1={len(tl1.GetItemListInTrack('audio', 1))}, EndFrame={tl1.GetEndFrame()}")

# 2. Timeline 2: PB130019 Hybrid (0..32024 = MP3_1412 [379..32403], 32024..138915 = PB130019 native audio, plus full MP3_1412 on A2 disabled/reference)
tl2_name = "02_PB130019_全員協議会_資料3_桐林クリーンセンター解体_音声同期済"
tl2 = mp.CreateEmptyTimeline(tl2_name)
proj.SetCurrentTimeline(tl2)
start_rec2 = tl2.GetStartFrame()

# Place full PB130019 video on V1
mp.AppendToTimeline([{
    "mediaPoolItem": pb19,
    "startFrame": 0,
    "endFrame": 138915,
    "mediaType": 1,
    "trackIndex": 1,
    "recordFrame": start_rec2
}])

# On A1: Place full continuous MP3_1412 from frame 379 (+12.63s) to 379 + 138914 (139293)
mp.AppendToTimeline([{
    "mediaPoolItem": mp3_1412,
    "startFrame": 379,
    "endFrame": 379 + 138914,
    "mediaType": 2,
    "trackIndex": 1,
    "recordFrame": start_rec2
}])
print(f"Created {tl2_name}: V1={len(tl2.GetItemListInTrack('video', 1))}, A1={len(tl2.GetItemListInTrack('audio', 1))}, EndFrame={tl2.GetEndFrame()}")

# 3. Timeline 3: PB130019 Hybrid (First 17m48.5s from MP3_1412 + remaining 59m26.6s from PB130019 internal mic)
tl3_name = "03_PB130019_ハイブリッド音声版_前半MP3補完_後半カメラ音声"
tl3 = mp.CreateEmptyTimeline(tl3_name)
proj.SetCurrentTimeline(tl3)
start_rec3 = tl3.GetStartFrame()

mp.AppendToTimeline([{
    "mediaPoolItem": pb19,
    "startFrame": 0,
    "endFrame": 138915,
    "mediaType": 1,
    "trackIndex": 1,
    "recordFrame": start_rec3
}])
# Part 1 of A1: frames 0..32023 (0s..1068.5s) from MP3_1412 (frames 379..32402)
mp.AppendToTimeline([{
    "mediaPoolItem": mp3_1412,
    "startFrame": 379,
    "endFrame": 379 + 32023,
    "mediaType": 2,
    "trackIndex": 1,
    "recordFrame": start_rec3
}])
# Part 2 of A1: frames 32024..138914 (1068.5s..4635.1s) from PB130019 native audio
mp.AppendToTimeline([{
    "mediaPoolItem": pb19,
    "startFrame": 32024,
    "endFrame": 138914,
    "mediaType": 2,
    "trackIndex": 1,
    "recordFrame": start_rec3 + 32024
}])
print(f"Created {tl3_name}: V1={len(tl3.GetItemListInTrack('video', 1))}, A1={len(tl3.GetItemListInTrack('audio', 1))}, EndFrame={tl3.GetEndFrame()}")

# 4. Timeline 4: PB130018 (15 frames = 0.50s) synced with MP3_1328 (+654.63s = frame 19619)
tl4_name = "04_PB130018_誤操作0.5秒_音声同期確認用"
tl4 = mp.CreateEmptyTimeline(tl4_name)
proj.SetCurrentTimeline(tl4)
start_rec4 = tl4.GetStartFrame()

mp.AppendToTimeline([{
    "mediaPoolItem": pb18,
    "startFrame": 0,
    "endFrame": 15,
    "mediaType": 1,
    "trackIndex": 1,
    "recordFrame": start_rec4
}])
mp.AppendToTimeline([{
    "mediaPoolItem": mp3_1328,
    "startFrame": 19619,
    "endFrame": 19619 + 14,
    "mediaType": 2,
    "trackIndex": 1,
    "recordFrame": start_rec4
}])
print(f"Created {tl4_name}: V1={len(tl4.GetItemListInTrack('video', 1))}, A1={len(tl4.GetItemListInTrack('audio', 1))}, EndFrame={tl4.GetEndFrame()}")

pm.SaveProject()
print("Saved project successfully.")
