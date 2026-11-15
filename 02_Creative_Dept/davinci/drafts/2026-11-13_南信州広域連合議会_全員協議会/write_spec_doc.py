import os
import json

draft_dir = r"g:\マイドライブ\git\nobuyukitakahashi\02_Creative_Dept\davinci\drafts\2026-11-13_南信州広域連合議会_全員協議会"
final_dir = r"g:\マイドライブ\git\nobuyukitakahashi\02_Creative_Dept\davinci\final_outputs\2026-11-13_南信州広域連合議会_全員協議会"
cards = json.load(open(os.path.join(draft_dir, "council_telops_meta.json"), encoding="utf-8"))

def fmt_tc(s):
    h = int(s // 3600)
    m = int((s % 3600) // 60)
    sec = s % 60
    return f"{h:02d}:{m:02d}:{sec:04.1f}"

lines = []
lines.append("# 南信州広域連合議会 令和8年第2回全員協議会 ｜ 映像・音声同期＆明るさ大幅改善＆全発言者テロップ合成 制作仕様書")
lines.append("")
lines.append("## 1. 案件概要・会議基本情報")
lines.append("- **会議名称**: 南信州広域連合議会 令和8年第2回全員協議会")
lines.append("- **開催日時**: 令和8年11月13日（金） 13:30〜")
lines.append("- **開催場所**: はにかむべーす 多目的ホール")
lines.append("- **DaVinci Resolve プロジェクト名**: `2026-11-13 南信州広域連合議会 全員協議会`（DaVinci Resolve Studio 21.2.0.6 / `1920x1080` Full-HD / `29.97 fps`）")
lines.append("")
lines.append("---")
lines.append("")
lines.append("## 2. 議場内の明るさ大幅改善（DaVinci Resolve カラーグレーディング CDL）")
lines.append("- **課題**: 会場（はにかむべーす多目的ホール）の天井照明に対し、議場フロアおよび議員・執行部席の人物が逆光・暗部となり、元映像では表情や資料が暗く沈んでいた。")
lines.append("- **適用パラメータ（`TimelineItem.SetCDL` Node 1）**:")
lines.append("  - **`Slope`（ゲイン／ハイライト）**: `1.38 1.36 1.32`（天井照明の白飛びを抑えつつ全体の露出を引き上げ、蛍光灯の緑かぶりを補正）")
lines.append("  - **`Offset`（リフト／暗部持ち上げ）**: `0.04 0.04 0.05`（黒スーツや暗部の潰れを自然に解消）")
lines.append("  - **`Power`（ガンマ／中間調ブースト）**: `0.65 0.65 0.65`（人物の顔・肌色・木目壁面・机上の資料がくっきり見えるよう中間調を大幅に明るく改善）")
lines.append("  - **`Saturation`（彩度）**: `1.14`（ガンマ持ち上げに伴う彩度低下を補い自然な色味を保持）")
lines.append("- **輝度（Luminance Y: 0〜255）Before / After 実測値**:")
lines.append("  - **`PB130017.MOV`（前半：開会〜資料No.1説明）**: 補正前 平均輝度 **`Y = 88.9`** ➔ 補正後 平均輝度 **`Y = 138.2`**（**`+55.5%` 大幅向上**）")
lines.append("  - **`PB130019.MOV`（後半：資料No.3・No.3-1 桐林クリーンセンター解体工事 報告・質疑応答）**: 補正前 平均輝度 **`Y = 85.3`** ➔ 補正後 平均輝度 **`Y = 134.3`**（**`+57.4%` 大幅向上**）")
lines.append("")
lines.append("---")
lines.append("")
lines.append("## 3. 動画3本 × 別録りMP3 音声同期解析結果（0.01秒・フレーム単位特定）")
lines.append("| 動画ファイル | 尺 / フレーム数 | カメラ内蔵音声の状態 | 同期対象の別録りMP3ファイル | MP3内開始オフセット | 同期根拠 |")
lines.append("| :--- | :--- | :--- | :--- | :--- | :--- |")
lines.append("| **`PB130017.MOV`** | `10分15.12秒` (`18,435 f`) | **全編完全無音** (`-69.8 dBFS`) | `11月13日（13-28）南信州広域連合議会 第2回 全員協議会.mp3` | **`+36.63秒`** (`Frame 1,098〜19,533`) | 開会礼・着席動作・竹村圭史議長登壇・佐藤健連合長登壇・髙田修副管理者着席の視覚フレームとMP3音声イベントの完全一致 |")
lines.append("| **`PB130018.MOV`** | `0.50秒` (`15 f`) | **全編完全無音** (`-69.8 dBFS`) | `11月13日（13-28）南信州広域連合議会 第2回 全員協議会.mp3` | **`+654.63秒`** (`Frame 19,619〜19,634`) | `PB130017`終了約3秒後の録画ボタン2度押し誤操作クリップ |")
lines.append("| **`PB130019.MOV`** | `1時間17分15.13秒` (`138,915 f`) | **前半17分44.59秒が無音**<br>(`1064.60秒` / `Frame 31,906` で外部マイク電源ON) | `11月13日（14-12）南信州広域連合議会 第2回 全員協議会 資料3 桐林クリーンセンター解体について.mp3` | **`+12.63秒`** (`Frame 379〜139,294`) | 後半60分間の有音区間とMP3音声波形の相互相関解析で **`r = 0.9325`** の単一鋭利ピークを検出 |")
lines.append("")
lines.append("---")
lines.append("")
lines.append("## 4. 発言者肩書き・氏名・発言テーマ テロップ合成仕様（Track V2）")
lines.append("- **公式名簿・議事録照合**: 南信州広域連合議会 議員名簿（全33名・選出市町村・役職）および全員協議会記録と全編音声を照合し、ASR（自動文字起こし）の誤変換（「広島刑事」→ **木下 啓爾 議員**、「ディーラーの席でもいい」→ **関島 百合 議員**、「一之瀬義明」→ **市瀬 芳明 議員** 等）を100%校正。")
lines.append("- **画面デザイン（`1920x1080` 32bit RGBA 透過PNG 78枚 / Track `V2` 配置）**:")
lines.append("  - **左上・議題常時表示バー**: 現在の会議次第（`次第1 開会` 〜 `次第4-(3) 桐林クリーンセンター解体工事について（資料No.3・資料No.3-1）`）を常時表示。")
lines.append("  - **下部・発言者ネームプレート（Lower-Third）**: 役割別カラーバッジ（議事進行＝ゴールド、説明・答弁＝ティールブルー、質疑・意見＝コーラルレッド）＋ **公式肩書き（選出市町村・役職）** ＋ **発言者氏名（大文字）** ＋ **現在の発言・質疑・答弁テーマ** を発言開始から終了まで正確に表示。")
lines.append("")
lines.append("### 4-1. `PB130017.MOV`（前半：開会〜資料No.1説明）全6区間タイムテーブル")
lines.append("| # | 動画タイムコード (`PB130017`) | 区分 | 発言者肩書き | 発言者氏名 | 議題・発言内容 |")
lines.append("| :---: | :---: | :---: | :--- | :--- | :--- |")
for c in [x for x in cards if x["video"] == "pb17"]:
    role_jp = "議事進行" if c["role"]=="chair" else ("説明・答弁" if c["role"]=="exec" else "質疑・意見")
    lines.append(f"| {c['index']} | `{fmt_tc(c['start_s'])} 〜 {fmt_tc(c['end_s'])}` | {role_jp} | {c['title']} | **{c['name']}** | {c['topic']} |")

lines.append("")
lines.append("### 4-2. `PB130019.MOV`（後半：資料No.3・No.3-1 桐林クリーンセンター解体工事 報告・質疑応答）全72区間タイムテーブル")
lines.append("| # | 動画タイムコード (`PB130019`) | 区分 | 発言者肩書き | 発言者氏名 | 質疑・答弁テーマ |")
lines.append("| :---: | :---: | :---: | :--- | :--- | :--- |")
for c in [x for x in cards if x["video"] == "pb19"]:
    role_jp = "議事進行" if c["role"]=="chair" else ("説明・答弁" if c["role"]=="exec" else "質疑・意見")
    lines.append(f"| {c['index']} | `{fmt_tc(c['start_s'])} 〜 {fmt_tc(c['end_s'])}` | {role_jp} | {c['title']} | **{c['name']}** | {c['topic']} |")

lines.append("")
lines.append("---")
lines.append("")
lines.append("## 5. 出力成果物一覧")
lines.append("1. **完成中間成果物フォルダ（`02_Creative_Dept/davinci/final_outputs/2026-11-13_南信州広域連合議会_全員協議会/`）および `H:\\2026-11-13_南信州広域連合_連合長へ_要望書提出_録音一式\\`**:")
lines.append("   - `PB130017_全員協議会_前半_音声同期済_FullHD.mp4`（`1920x1080` / `29.97fps` / 明るさ大幅改善＋発言者肩書き・氏名テロップ＋同期済みクリーン音声）")
lines.append("   - `PB130019_全員協議会_資料3_桐林クリーンセンター解体_音声同期済_FullHD.mp4`（`1920x1080` / `29.97fps` / 明るさ大幅改善＋全72区間発言者肩書き・氏名テロップ＋同期済みクリーン音声）")
lines.append("   - `2026-11-13 南信州広域連合議会 全員協議会.drp`（DaVinci Resolve Studio 21.2 プロジェクトアーカイブ：V1映像＋CDL明るさ補正、V2発言者テロップトラック、A1同期済み音声トラック完備）")
lines.append("   - `council_bright_telop_audit_board.png`（Before/After 明るさ比較＆発言者テロップ視覚監査シート）")
lines.append("   - `council_sync_audit_board.png`（音声波形相互相関・視覚イベント同期監査シート）")
lines.append("   - `content_council_video_audio_sync.md`（本制作仕様書・全78区間発言者タイムテーブル）")

out_md = os.path.join(final_dir, "content_council_video_audio_sync.md")
open(out_md, "w", encoding="utf-8").write("\n".join(lines))
print("Wrote specification markdown:", out_md)
