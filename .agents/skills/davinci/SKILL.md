---
name: davinci
description: >-
  DaVinci Resolve Studio 21.2（Python DaVinciResolveScript / Fusion Scripting API / MCP davinci-resolve）および
  FFmpeg を連携させた映像編集、タイムライン構築、スタビライズ手ブレ補正、カラーグレーディング（ASC CDL / LUT）、
  テロップ・VFX合成、および完パケ映像（.mp4 / .mov / .drp）書き出しを専任で実行し、
  中間成果物を案件別サブフォルダ 02_Creative_Dept/davinci/{drafts,final_outputs}/<案件サブフォルダ>/ に、
  最終成果物を 04_Delivery_Dept/outputs/davinci/<案件サブフォルダ>/ に格納するスキル。
  ユーザーが /davinci を指定した際、またはジャンル選択で「DaVinci Resolve（動画編集・グレーディング・テロップ）」を選択した際に使用する。
---

# 🎬 DaVinci Resolve Studio 21.2 映像編集・カラーグレーディング・VFX専任スキル (`/davinci`)

## 1. ジャンル別 ＆ 案件別サブフォルダ管理規約（厳守）
複数案件のファイル混在を防ぐため、必ずジャンルフォルダ直下に**案件別サブフォルダ（`<案件サブフォルダ>`：例 `2026-11-13_南信州広域連合へ要望書提出` 等）**を作成して分離管理すること：
- **編集スクリプト・解析フレーム・コンタクトシート置き場**:
  - `02_Creative_Dept/davinci/drafts/<案件サブフォルダ>/`
- **制作部門の完成中間成果物置き場**:
  - `02_Creative_Dept/davinci/final_outputs/<案件サブフォルダ>/`
- **最終納品フォルダ（`04_Delivery_Dept` による格納先）**:
  - `04_Delivery_Dept/outputs/davinci/<案件サブフォルダ>/`
  - ※納品台帳 [`04_Delivery_Dept/outputs/INDEX.md`](../../../04_Delivery_Dept/outputs/INDEX.md) の「`## 🎬 4. DaVinci Resolve`」セクションに案件別サブフォルダへの相対リンク（`davinci/<案件サブフォルダ>/ファイル名`）を追記する。

---

## 2. DaVinci Resolve Studio 21.2 自動制御（Python `DaVinciResolveScript`）環境設定

Windows 環境で起動中の DaVinci Resolve Studio（v21.2.0.6 等）に外部 Python スクリプトから接続する際は、スクリプト冒頭で必ず以下の環境変数およびモジュールパスを設定する：

```python
import os
import sys

os.environ["RESOLVE_SCRIPT_API"] = r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting"
os.environ["RESOLVE_SCRIPT_LIB"] = r"C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll"
sys.path.append(r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules")

import DaVinciResolveScript as dvr_script
resolve = dvr_script.scriptapp("Resolve")
```

- DaVinci Resolve が未起動の場合は `Start-Process "C:\Program Files\Blackmagic Design\DaVinci Resolve\Resolve.exe"` で起動し、`dvr_script.scriptapp("Resolve")` がオブジェクトを返すまで待機する。
- 新規プロジェクト作成時は `pm = resolve.GetProjectManager()` ➔ `pm.CreateProject("<プロジェクト名>")`（既存時は `pm.LoadProject("<プロジェクト名>")`）でプロジェクトを開き、`proj.SetSetting("timelineResolutionWidth", "1920")`, `proj.SetSetting("timelineResolutionHeight", "1080")` 等で解像度・フレームレートを設定する。

---

## 3. 実写映像の編集・スタビライズ・露出補正の鉄則（ベストプラクティス）

### ① 前後不要区間の精密トリミング（映像コンタクトシート × 音声RMS波形ハイブリッド解析）
- 冒頭の「録画ボタン押下時の床映り・カメラ構え直し・急激なパン・AFピント迷い」や、末尾の「閉会礼後の姿勢戻し・録画停止ボタン操作音（カチッというスパイク音）・カメラ微動」を正確に除外するため、0.17〜0.5秒間隔のフレーム画像コンタクトシート目視監査と音声 RMS (dBFS) 解析を併用して In点 (`startFrame`) と Out点 (`endFrame`) をフレーム単位で特定する。
- `mediaPool.AppendToTimeline([{"mediaPoolItem": clip, "startFrame": in_frame, "endFrame": out_frame}])` により、不要区間を除外したクリーンなサブクリップをタイムラインへ配置する。

### ② 移動パン区間と定点手持ち区間の「セクション分割スタビライズ」（過度なクロップ・見切れ防止）
- カメラマンが室内を歩いて移動する「カメラ移動・大パン区間」と、立ち止まって撮影している「定点手持ち区間」が1本の動画内に混在している場合、**クリップ全体に一括で `TimelineItem.Stabilize()` を実行してはならない**（移動パンの動きまで無理に固定しようとして極端なズームイン・被写体見切れが発生するため）。
- 必ず移動パン区間と定点手持ち区間をフレーム連続（例：`[215..485]`, `[485..810]`, `[810..1845]`, `[1845..5080]`、フレーム欠損・重複ゼロ）でサブクリップ分割してタイムラインへ並べ、**定点手持ちセクションの `TimelineItem` にのみ個別に `item.Stabilize()` を実行**し、移動パン区間は自然なカメラワークを保持する。

### ③ 逆光暗転・照明変化に対する区間別 `TimelineItem.SetCDL()` 露出・色味統一
- 逆光カーテンやカメラアングル変化によってカメラの自動露出（AE）が暗転する区間と通常露出の区間が混在する場合、全区間へ一律の補正をかけると後半が白飛びするか前半が暗いまま残る。
- 各セクションの平均輝度（Y）および色温度（RGBバランス）を計測し、セクションごとに最適な ASC CDL パラメータを `item.SetCDL({"NodeIndex": "1", "Slope": "R G B", "Offset": "R G B", "Power": "R G B", "Saturation": "S"})` で適用する（特に暗転区間は `Power`〔ガンマ〕を `0.56〜0.68` に下げて中間調を持ち上げつつ、`Slope` の Blue をわずかに抑えて室内の寒色・緑かぶりを自然なスキントーンへ補正する）。

### ④ DaVinci Resolve `V2` トラック透過PNG（短尺連番 `telop_[0000-NNNN].png` ／ 長尺区間別 `recordFrame` 配置）＋ `.srt` 生成による放送品質テロップ・発言者ネームプレート合成
- DaVinci Resolve 標準の字幕トラックはスクリプトからのフォント装飾制御に制約があるため、放送品質の話者バッジ付きテロップや議会中継の「左上常時議題バー＋下部発言者ネームプレート（Lower-Third）」を焼き込む際は、以下の2方式を尺に応じて使い分ける：
  1. **短尺映像（数分程度：要望書提出等）**: ユニークなテロップ状態ごとの透過PNGをレンダリングし、タイムライン全フレームに対応するハードリンク連番（`telop_0000.png` 〜 `telop_NNNN.png`）を生成して Media Pool へ1本の連番クリップ（`telop_[0000-NNNN].png`）としてインポートし、`V2` ビデオトラック（`trackIndex: 2, mediaType: 1`）へ配置する。
  2. **長尺議会・会議映像（1時間超・数十〜百区間：全員協議会等）**:
     - **公式議員名簿・議事録クロスチェックによるASR誤変換100%校正**: 自動文字起こし（ASR）で頻発する人名・役職の同音異義誤変換（例：「広島刑事」→「木下 啓爾 議員」、「ディーラーの席でもいい」→「関島 百合 議員」、「一之瀬義明」→「市瀬 芳明 議員」等）を、必ず公式の議員名簿（選出市町村・役職・委員会）および会議次第と照合して100%校正する。
     - **32bit RGBA 透過ネームプレートPNGの `V2` トラック区間配置**: 数十万フレームの連番生成を避け、発言区間ごと（例：前半6区間＋後半72区間＝計78枚）の `1920×1080` 32bit RGBA 透過PNG（役割別カラーバッジ：議事進行＝ゴールド、説明・答弁＝ティールブルー、質疑・意見＝コーラルレッド ＋ 公式肩書き・選出市町村 ＋ 発言者氏名 ＋ 質疑/答弁テーマ）を生成し、Media Pool インポート後に `mediaPool.AppendToTimeline([{"mediaPoolItem": png_clip, "startFrame": 0, "endFrame": dur, "mediaType": 1, "trackIndex": 2, "recordFrame": timeline_start_frame}])` で `V2` トラックの正確なタイムコード位置へ区間配置する。
     - **暗所・逆光議場の `SetCDL` 大幅露出ブースト（`+55〜57%` 改善）**: 天井照明と逆光で暗く沈んだ議場ホール映像（平均輝度 `Y ≈ 85〜89`）に対しては、`V1` トラックのクリップに `SetCDL({"NodeIndex": "1", "Slope": "1.38 1.36 1.32", "Offset": "0.04 0.04 0.05", "Power": "0.65 0.65 0.65", "Saturation": "1.14"})` を適用し、天井照明の白飛びを抑えつつ人物の表情・机上資料を平均輝度 `Y ≈ 134〜138`（`+55.5%〜+57.4%` 向上）まで明るく見やすく引き上げる。

### ⑤ 会議・要望書提出等の実写音声に対する自然なノイズ軽減 ＆ 音量ブースト（`A1` トラック配置）
- 室内の空調ハム音や低周波ランブルを抑えつつ、遠距離マイクの発言音声を音割れやロボット声（ミュージカルノイズ）なしで聞き取りやすく引き上げる際は、以下の5段DSPパイプラインでマスタリング WAV（48kHz / 16-bit Stereo）を生成してタイムラインの `A1` トラック（`mediaType: 2, trackIndex: 1`）へ配置する：
  1. **High-Pass Filter (`100 Hz`) ＋ Low-Pass Filter (`11 kHz`)**: 空調ゴロゴロ音・マイク保持振動および高域ヒスノイズを除去。
  2. **STFT ソフト・スペクトルゲート（Floor `0.45` ＝ 最大 `-6.9 dB` 減衰 ＋ 時間/周波数平滑化）**: 強い減算によるロボット声を防ぎつつ定常背景ノイズを自然に抑制。
  3. **明瞭度エンハンスEQ（`2.3 kHz` 中心 `+2.4 dB` プレゼンスブースト）**: 日本語の子音・発話輪郭を明瞭化。
  4. **ソフトニー・コンプレッサー（Threshold `-18.5 dBFS`, Ratio `2.8:1`, Makeup `+7.8 dB`）＋ 静寂部ソフトエクスパンダー**: 小さな声を持ち上げ、発話平均RMSを約 `-20.3 dBFS ➔ -14.6 dBFS`（`+5.6 dB`、SN比 `+4.8 dB` 改善）へ均一化。
  5. **True-Peak リミッター（`-1.00 dBFS` シーリング）**: 突発的な拍手や紙めくり音でもクリッピング（音割れ）を100%防止。

### ⑥ 無音欠落動画（外部マイク電源OFF等）と別録りICレコーダー音声（MP3/M4A）の高精度自動同期手法
- カメラ側の外部マイク電源入れ忘れ等により「全編無音」または「途中から有音」となっている動画ファイル（`.MOV` / `.MP4`）に対し、別録りのICレコーダー音声（`.mp3` / `.m4a`）から該当区間をミリ秒・フレーム精度で特定して `A1` トラックへ同期合成する際は、以下の2段階ハイブリッド同期アルゴリズムを適用する：
  1. **部分有音動画（途中からマイクON等）の音響エンベロープ相互相関（Cross-Correlation）同期**:
     - 動画の有音区間と別録り音声ファイルの振幅エンベロープ（10Hz＝100ms 粗探索 ➔ 100Hz＝10ms 精密探索）の正規化相互相関（Normalized Cross-Correlation）を計算し、相関係数 `r > 0.90` で一致するミリ秒単位のオフセット（例：`+12.63秒` ＝ `379フレーム @ 29.97fps`）を特定する。
     - 同時に1時間以上の長尺クリップでは冒頭・中盤・終盤の複数ウィンドウでオフセットを計測し、カメラとICレコーダー間の水晶発振器クロックドリフト有無を検証する。
     - タイムライン構築時は、マイク電源投入時のスイッチ操作ノイズや前後の音質段差をなくすため、①全編を別録り音声で統一したタイムラインと、②無音区間のみ別録り音声で補完し有音区間はカメラ内蔵音声へ切り替えるハイブリッドタイムラインの両方を構築・提供するとよい。
  2. **完全無音動画の QuickTime `mvhd` 内部結晶クロック差分 × 視覚ランドマーク照合同期**:
     - 全編無音で音響相関が取れない動画は、同一カメラで撮影された後続（または先行）の部分有音動画との QuickTime `mvhd` アトム `creation_time` 差分（カメラ内部結晶クロック経過秒数）と、ICレコーダー側の `.m4a` `mvhd` タイムスタンプ差分から初期オフセットを秒単位で逆算する。
     - さらに、映像内の明確な人物動作ランドマーク（開会号令での全員起立・一礼、議長や発言者の起立・挨拶開始・お辞儀の頂点・着席タイミング）をフレーム抽出し、別録り音声の発声・会場返礼・着席音と照合して1フレーム単位の確定 In点（`startFrame`）を決定する。

### ⑦ Deliver ページ自動レンダリングと `.drp` プロジェクトアーカイブ保存
- `resolve.OpenPage("deliver")` 後、`proj.SetCurrentRenderFormatAndCodec("mp4", "H264_NVIDIA")`（または `"H264"`）および `proj.SetRenderSettings({"SelectAllFrames": True, "TargetDir": out_dir, "CustomName": out_name, "FormatWidth": 1920, "FormatHeight": 1080, "FrameRate": 29.97, "ExportVideo": True, "ExportAudio": True})` を設定し、`job_id = proj.AddRenderJob()` ➔ `proj.StartRendering(job_id)` で書き出す。
- 書き出し完了後、必ず `pm.SaveProject()` で Resolve データベースに保存するとともに、`pm.ExportProject(proj.GetName(), drp_path, False)` で `.drp` プロジェクトアーカイブを案件別サブフォルダへ出力する。

---

## 4. 視覚監査ループと最終納品手順

1. **Before / After キーフレーム比較ボードによる `read_file` 視覚監査**:
   - `proj.ExportCurrentFrameAsStill(path)` および書き出し後の MP4 から抽出した主要フレームを並べた Before/After 監査シート（`keyframes_audit_board.png`）を生成し、`read_file` で明るさ・肌色・白飛び有無・スタビライズ後の構図余白を目視監査する。
2. **中間成果物出力と最終納品**:
   - 完成した映像ファイル（`.mp4` / `.mov`）、プロジェクトアーカイブ（`.drp`）、キーフレーム確認シート（`.png`）、および制作仕様書 `content_[テーマ名].md` を `02_Creative_Dept/davinci/final_outputs/<案件サブフォルダ>/` に保存する（ユーザーから元動画フォルダへの同時出力指示がある場合は指定先へもコピーする）。
   - 続けて `04_Delivery_Dept` を通じて `04_Delivery_Dept/outputs/davinci/<案件サブフォルダ>/` に最終成果物一式を格納し、`04_Delivery_Dept/outputs/INDEX.md` を更新する。
