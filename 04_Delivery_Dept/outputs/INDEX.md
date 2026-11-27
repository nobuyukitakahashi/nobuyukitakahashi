# 最終成果物（Output）納品インデックス（12大ジャンル別台帳）

本フォルダ（`04_Delivery_Dept/outputs/`）は、AIバーチャル組織のすべての最終成果物を単一正本として格納する**唯一の固定出力フォルダ**です。各案件は必ず `<genre>/<案件サブフォルダ>/` 配下に格納し、技術詳細は各案件の `output_*_full.md` に記録します。

| # | ジャンル | 格納フォルダ | スキル | 主な用途・形式 |
| :---: | :--- | :--- | :---: | :--- |
| 1 | **Blender** | [`blender/`](blender/) | `/blender` | 3Dモデリング・CG・3Dアニメ（`.blend`, `.glb`, `.png`, `.mp4`） |
| 2 | **Adobe Illustrator** | [`illustrator/`](illustrator/) | `/illustrator` | ベクターロゴ・CMYK印刷入稿・DTP（`.ai`, `.pdf`, `.svg`, `.png`） |
| 3 | **Adobe Photoshop** | [`photoshop/`](photoshop/) | `/photoshop` | 画像編集・PSD合成・バナー/サムネイル（`.psd`, `.png`, `.jpg`） |
| 4 | **DaVinci Resolve** | [`davinci/`](davinci/) | `/davinci` | 映像編集・カラグレ・テロップ・整音（`.mp4`, `.mov`, `.drp`） |
| 5 | **Writing & Documents** | [`writing/`](writing/) | `/writing` | 記事・調査レポート・会議資料・仕様書（`.md`, `.pdf`, `.html`） |
| 6 | **Adobe Premiere Pro** | [`premiere/`](premiere/) | `/premiere` | シーケンス編集・メディア書き出し（`.prproj`, `.mp4`, `.mov`） |
| 7 | **Adobe After Effects** | [`aftereffects/`](aftereffects/) | `/aftereffects` | モーショングラフィックス・TVCM・VFX（`.aep`, `.mp4`, `.wav`） |
| 8 | **Moho Pro 14** | [`moho/`](moho/) | `/moho` | 2Dベクターキャラアニメ・透過動画（`.moho`, `.mov`, `.webm`, `.mp4`） |
| 9 | **Pano2VR 8** | [`pano2vr/`](pano2vr/) | `/pano2vr` | 360°バーチャルツアー・スキン制作（`.ggsk`, HTML5, `.ggpkg`） |
| 10 | **krpano 1.24** | [`krpano/`](krpano/) | `/krpano` | 360°VRツアー・WebXR・ThreeJS・3DGS（`tour.xml`, HTML5タイル） |
| 11 | **PTGui Pro 13** | [`ptgui/`](ptgui/) | `/ptgui` | 360°パノラマスティッチ・HDR合成（`.pts`, `.jpg`, `.tif`, `.exr`） |
| 12 | **Web / WordPress・Avada** | [`web/`](web/) | `/wordpress-avada-maintenance` | WordPress/Avada保守・スタンドアロンWebアプリ（`.html`, `.php`, `.css`） |

---

## 🎨 1. Blender（3Dモデリング・CG・3Dアニメーション） — `outputs/blender/`

| 納品日 | 案件サブフォルダ / テーマ | メイン出力ファイル | フォーマット | 要約 |
| :--- | :--- | :--- | :--- | :--- |
| 2026-11-19 | `ケーブル兄弟アニメーション/`<br>CVN公式キャラ「ケーブル兄弟」2体ペア3Dアニメ（v10完成版・v9温存・旧版アーカイブ） | [`output_20261119_v10_cvn_pair_mascot_anim_full.md`](blender/ケーブル兄弟アニメーション/output_20261119_v10_cvn_pair_mascot_anim_full.md)<br>[`output_20261119_v10_cvn_pair_run_bow_wave.mp4`](blender/ケーブル兄弟アニメーション/output_20261119_v10_cvn_pair_run_bow_wave.mp4)<br>[`output_20261119_v10_cvn_pair_anim.blend`](blender/ケーブル兄弟アニメーション/output_20261119_v10_cvn_pair_anim.blend)<br>[`output_20261119_v10_cvn_pair_sfx.wav`](blender/ケーブル兄弟アニメーション/output_20261119_v10_cvn_pair_sfx.wav)<br>（v9温存: [`output_20261119_cvn_pair_mascot_anim_full.md`](blender/ケーブル兄弟アニメーション/output_20261119_cvn_pair_mascot_anim_full.md) / v8: [`output_20261118_cvn_pair_mascot_anim_full.md`](blender/ケーブル兄弟アニメーション/output_20261118_cvn_pair_mascot_anim_full.md)） | MP4 (`1920×1080`, 30fps, 15s) / WAV / PNG / `.blend` / MD | Blender 5.3 Cycles GPU。しなやか尻尾2次バネ物理＋柔和な瞬き＋腕付け根隙間ゼロ＋完全同期48kHz効果音SE統合（v9/v8/v6/v1一式も同フォルダ内管理）。 |
| 2026-11-19 | `2026-11-19_cvn_gold_logo/`<br>「cvn」24K純金ベベル3Dロゴ | [`cvn_gold_logo.png`](blender/2026-11-19_cvn_gold_logo/cvn_gold_logo.png)<br>[`cvn_gold_logo.blend`](blender/2026-11-19_cvn_gold_logo/cvn_gold_logo.blend) | PNG (`1920×1080`) / `.blend` | Blender 5.3 Cycles GPU（AgX Punchy）。45°ジュエリーカットベベル・24K純金質感・漆黒鏡面床リフレクション・2段グレア適用。 |
| 2026-11-10 | `2026-11-05_cvn_cable_brothers_3d/`<br>CVN公式キャラ「いい-NETくん」「いい-ch」単体＆2体ペア3Dモデル（バランス改修済） | [`output_20261110_cvn_pair_balance_adjust_full.md`](blender/2026-11-05_cvn_cable_brothers_3d/output_20261110_cvn_pair_balance_adjust_full.md)<br>[`output_20261110_cvn_pair_iich_and_iinet_front.png`](blender/2026-11-05_cvn_cable_brothers_3d/output_20261110_cvn_pair_iich_and_iinet_front.png)<br>[`output_20261110_cvn_pair_iich_and_iinet.blend`](blender/2026-11-05_cvn_cable_brothers_3d/output_20261110_cvn_pair_iich_and_iinet.blend) / [`.glb`](blender/2026-11-05_cvn_cable_brothers_3d/output_20261110_cvn_pair_iich_and_iinet.glb)<br>（単体: [`output_20261105_cvn_iich_kun.blend`](blender/2026-11-05_cvn_cable_brothers_3d/output_20261105_cvn_iich_kun.blend) / [`output_20261104_cvn_iinet_kun.blend`](blender/2026-11-05_cvn_cable_brothers_3d/output_20261104_cvn_iinet_kun.blend)） | MD / PNG / `.blend` / `.glb` | 原画正面シルエット一致率 IoU 98.11%。ソフビ一体成型シームレス腕・微細グレイン質感・いい-ch（Rev.4）＆いい-NETくん（Rev.13）単体モデル一式同梱。 |
| 2026-11-02 | `2026-11-02_iinet_logo_3d/`<br>いい-Net光 ＆ いい-NET光10G 3DロゴCG（黒背景・白背景） | [`output_20261102_iinet_logo_3d_render_full.md`](blender/2026-11-02_iinet_logo_3d/output_20261102_iinet_logo_3d_render_full.md)<br>[`output_20261102_iinet_logo_3d_front.png`](blender/2026-11-02_iinet_logo_3d/output_20261102_iinet_logo_3d_front.png) / [`output_20261102_iinet_10g_logo_3d_front.png`](blender/2026-11-02_iinet_logo_3d/output_20261102_iinet_10g_logo_3d_front.png)<br>[`output_20261102_iinet_logo_3d_front_white.png`](blender/2026-11-02_iinet_logo_3d/output_20261102_iinet_logo_3d_front_white.png) / [`output_20261102_iinet_10g_logo_3d_front_white.png`](blender/2026-11-02_iinet_logo_3d/output_20261102_iinet_10g_logo_3d_front_white.png) | PNG (`2560×1440`) / SVG / `.blend` / `.glb` / MD | `.ai` ベクターからSVG変換後、Blender Cycles GPU で立体ベベル＆スタジオ照明レンダリング（通常版・10G版・純白背景版）。 |

---

## ✒️ 2. Adobe Illustrator（ベクターロゴ・CMYK印刷・DTP） — `outputs/illustrator/`

| 納品日 | 案件サブフォルダ / テーマ | メイン出力ファイル | フォーマット | 要約 |
| :--- | :--- | :--- | :--- | :--- |
| 2026-11-11 | `2026-11-11_illustrator_mcp_setup/`<br>Illustrator 2027 ローカルMCP構築＆実機検証 | [`output_20261111_illustrator_mcp_setup_full.md`](illustrator/2026-11-11_illustrator_mcp_setup/output_20261111_illustrator_mcp_setup_full.md)<br>[`output_20261111_illustrator_mcp_verify.ai`](illustrator/2026-11-11_illustrator_mcp_setup/output_20261111_illustrator_mcp_verify.ai)<br>[`output_20261111_illustrator_mcp_verify.png`](illustrator/2026-11-11_illustrator_mcp_setup/output_20261111_illustrator_mcp_verify.png) | MD / `.ai` (CMYK) / PNG | Win/Mac対応 stdio MCPサーバー構築・CMYKベクター生成・全テキストアウトライン化・200% PNG監査完了。 |
| 2026-11-05 | `2026-11-05_cvn_plus_mobile_logo/`<br>株式会社cvn「cvn プラスモバイル」ロゴ全6案提案書 | [`output_20261105_cvn_plus_mobile_logo_proposal.html`](illustrator/2026-11-05_cvn_plus_mobile_logo/output_20261105_cvn_plus_mobile_logo_proposal.html)<br>[`output_20261105_cvn_plus_mobile_logo_full.md`](illustrator/2026-11-05_cvn_plus_mobile_logo/output_20261105_cvn_plus_mobile_logo_full.md)<br>[`output_20261105_cvn_plus_mobile_logo_board.png`](illustrator/2026-11-05_cvn_plus_mobile_logo/output_20261105_cvn_plus_mobile_logo_board.png) | HTML / MD / SVG×6 / PNG×7 | CMYK `C:90 M:0 Y:70 K:0`（`#00a273`）単色統一・3表記×各2案（計6案）。法務審査 `APPROVED`・3デバイス目視監査済。 |

---

## 🖼️ 3. Adobe Photoshop（画像編集・PSD合成・バナー） — `outputs/photoshop/`

| 納品日 | 案件サブフォルダ / テーマ | メイン出力ファイル | フォーマット | 要約 |
| :--- | :--- | :--- | :--- | :--- |
| 2026-11-26 | `2026-12-27_furusato_cm_thumbnail/`<br>ふるさと合同企業説明会2026 YouTubeサムネイル一式 | [`2026-12-27_ふるさと合同企業説明会2026_YouTubeサムネイル_1280x720.png`](photoshop/2026-12-27_furusato_cm_thumbnail/2026-12-27_ふるさと合同企業説明会2026_YouTubeサムネイル_1280x720.png) / [`.jpg`](photoshop/2026-12-27_furusato_cm_thumbnail/2026-12-27_ふるさと合同企業説明会2026_YouTubeサムネイル_1280x720.jpg)<br>[`2026-12-27_ふるさと合同企業説明会2026_YouTubeサムネイル_master.psd`](photoshop/2026-12-27_furusato_cm_thumbnail/2026-12-27_ふるさと合同企業説明会2026_YouTubeサムネイル_master.psd) | PNG / JPG / `.psd` (5グループ) | Photoshop 2027実機構築＆独立QA合格。YouTube 2MB制限適合・モバイル視認性＆右下バッジ回避設計。 |
| 2026-11-11 | `2026-11-11_kinoshita_aimeikai_2027_images/`<br>木下建設「愛名会 2027企業案内」採用ビジュアル11枚 | [`output_20261111_kinoshita_aimeikai_2027_images_full.md`](photoshop/2026-11-11_kinoshita_aimeikai_2027_images/output_20261111_kinoshita_aimeikai_2027_images_full.md)<br>[`kinoshita_photo01.jpg`](photoshop/2026-11-11_kinoshita_aimeikai_2027_images/kinoshita_photo01.jpg)〜`06.jpg` / [`voice01_hk.jpg`](photoshop/2026-11-11_kinoshita_aimeikai_2027_images/voice01_hk.jpg)〜`05` | MD / JPG×11 | 愛名会規定（JPG・5MB以下・半角小文字）100%適合。イメージカード6枚＋先輩社員顔写真5枚。法務 `APPROVED`。 |
| 2026-11-11 | `2026-11-11_photoshop_mcp_setup/`<br>Photoshop 2027 ローカルMCP構築＆実機検証 | [`output_20261111_photoshop_mcp_setup_full.md`](photoshop/2026-11-11_photoshop_mcp_setup/output_20261111_photoshop_mcp_setup_full.md)<br>[`output_20261111_photoshop_mcp_verify.psd`](photoshop/2026-11-11_photoshop_mcp_setup/output_20261111_photoshop_mcp_verify.psd)<br>[`output_20261111_photoshop_mcp_verify.png`](photoshop/2026-11-11_photoshop_mcp_setup/output_20261111_photoshop_mcp_verify.png) | MD / `.psd` / PNG | Win/Mac対応 stdio MCPサーバー構築・18レイヤーPSD生成・300dpi文字DPI補正＆PNG視覚監査完了。 |

---

## 🎬 4. DaVinci Resolve（映像編集・カラーグレーディング・VFX） — `outputs/davinci/`

| 納品日 | 案件サブフォルダ / テーマ | メイン出力ファイル | フォーマット | 要約 |
| :--- | :--- | :--- | :--- | :--- |
| 2026-11-21 | `2026-11-19_ワインとジャズのコンサート/`<br>HONKA music SALON 4K完パケ（ピアノ面3Dパース公式ロゴ合成・全23曲テロップ） | [`content_ワインとジャズのコンサート.md`](davinci/2026-11-19_ワインとジャズのコンサート/content_ワインとジャズのコンサート.md)<br>[`ワインとジャズのコンサート.drp`](davinci/2026-11-19_ワインとジャズのコンサート/ワインとジャズのコンサート.drp)<br>[`keyframes_audit_board.png`](davinci/2026-11-19_ワインとジャズのコンサート/keyframes_audit_board.png) | 4K MP4 (1h27m30s, デスクトップ直出力) / `.drp` / PNG / MD | 5分割4K統合・公式OP/ED・ピアノ面3Dパースロゴ合成・スタビライズ・露出マッチ・メンバー5名＆全23曲テロップ完パケ。 |
| 2026-11-15 | `2026-11-15_PC初期化用_DaVinci全プロジェクト完全バックアップ/`<br>DaVinci Resolve 21.2 全15プロジェクト完全バックアップ | [`output_20261115_davinci_full_backup_guide.md`](davinci/2026-11-15_PC初期化用_DaVinci全プロジェクト完全バックアップ/output_20261115_davinci_full_backup_guide.md)<br>[`RESTORE_DAVINCI_PROJECTS.ps1`](davinci/2026-11-15_PC初期化用_DaVinci全プロジェクト完全バックアップ/RESTORE_DAVINCI_PROJECTS.ps1)<br>[`Resolve_Project_Library_FullBackup_20261115.zip`](davinci/2026-11-15_PC初期化用_DaVinci全プロジェクト完全バックアップ/02_Resolve_Project_Library_丸ごとバックアップ/Resolve_Project_Library_FullBackup_20261115.zip) | `.drp`×15 / ZIP / `.ps1` / MD | 全15案件 `.drp`＋DB丸ごとバックアップ＋カスタムLUT/Gallery退避＋1クリック自動復元スクリプト。 |
| 2026-11-14 | `2026-11-13_南信州広域連合議会_全員協議会/`<br>全員協議会 音声同期・明るさ改善・全78区間テロップ完パケ | [`output_20261114_council_video_audio_sync_full.md`](davinci/2026-11-13_南信州広域連合議会_全員協議会/output_20261114_council_video_audio_sync_full.md)<br>[`PB130017_全員協議会_前半_音声同期済_FullHD.mp4`](davinci/2026-11-13_南信州広域連合議会_全員協議会/PB130017_全員協議会_前半_音声同期済_FullHD.mp4)<br>[`PB130019_全員協議会_資料3_桐林クリーンセンター解体_音声同期済_FullHD.mp4`](davinci/2026-11-13_南信州広域連合議会_全員協議会/PB130019_全員協議会_資料3_桐林クリーンセンター解体_音声同期済_FullHD.mp4)<br>[`council_bright_telop_audit_board.png`](davinci/2026-11-13_南信州広域連合議会_全員協議会/council_bright_telop_audit_board.png) | MP4 (`1920×1080`) / `.drp` / PNG / MD | 別録りMP3フレーム精度同期・逆光暗部+55〜57%改善・公式議員名簿照合78区間発言者テロップ合成。 |
| 2026-11-14 | `2026-11-13_南信州広域連合へ要望書提出/`<br>要望書提出 映像編集・35カットテロップ・整音完パケ | [`output_20261114_minamishinsyu_petition_video_full.md`](davinci/2026-11-13_南信州広域連合へ要望書提出/output_20261114_minamishinsyu_petition_video_full.md)<br>[`PB130002_編集済_FullHD.mp4`](davinci/2026-11-13_南信州広域連合へ要望書提出/PB130002_編集済_FullHD.mp4)<br>[`PB130002_編集済_FullHD.srt`](davinci/2026-11-13_南信州広域連合へ要望書提出/PB130002_編集済_FullHD.srt)<br>[`keyframes_telop_audit_board.png`](davinci/2026-11-13_南信州広域連合へ要望書提出/keyframes_telop_audit_board.png) | MP4 (`1920×1080`, 162s) / SRT / WAV / `.drp` / MD | トリミング・スタビライズ・明るさ+72%改善・全35カット話者テロップ＆SRT・ノイズ軽減＋発話音量+5.62dB整音。 |

---

## 📝 5. Writing & Documents（記事・調査レポート・会議資料・システム文書） — `outputs/writing/`

| 納品日 | 案件サブフォルダ / テーマ | メイン出力ファイル | フォーマット | 要約 |
| :--- | :--- | :--- | :--- | :--- |
| 2026-11-11 | `2026-11-11_kinoshita_aimeikai_2027/`<br>木下建設「愛名会 2027企業案内」ピッチブック＆チラシ | [`output_20261111_kinoshita_aimeikai_2027_full.md`](writing/2026-11-11_kinoshita_aimeikai_2027/output_20261111_kinoshita_aimeikai_2027_full.md)<br>[`kinoshita_2027_recruit_pitchbook.pdf`](writing/2026-11-11_kinoshita_aimeikai_2027/kinoshita_2027_recruit_pitchbook.pdf)<br>[`kinoshita_2027_briefing_flyer.pdf`](writing/2026-11-11_kinoshita_aimeikai_2027/kinoshita_2027_briefing_flyer.pdf) | MD / PDF (28P + 1P) | 全12項目校正・全28P再構成（4.0MB）・A4チラシ（1.73MB）・管理画面コピペシート同梱。法務審査 `APPROVED`。 |
| 2026-11-01 | `2026-11-01_legal_dept_setup/`<br>法務・コンプライアンス部門新設＆組織運用マニュアル | [`output_20261101_legal_dept_setup_full.md`](writing/2026-11-01_legal_dept_setup/output_20261101_legal_dept_setup_full.md) | MD | 5大法務リスクトリガー・3段階審査ステータス・部門運用設計マニュアル。 |
| 2026-11-01 | `2026-11-01_kiribayashi_meeting_materials/`<br>桐林クリーンセンター解体工事 諸課題検証会議 当日資料 | [`output_20261101_kiribayashi_meeting_materials_full.md`](writing/2026-11-01_kiribayashi_meeting_materials/output_20261101_kiribayashi_meeting_materials_full.md) | MD / Obsidian Note | 検証会議当日用資料一式（Obsidian Vault 同時格納済）。 |

---

## 🎞️ 6. Adobe Premiere Pro（シーケンス編集・書き出し） — `outputs/premiere/`

| 納品日 | 案件サブフォルダ / テーマ | メイン出力ファイル | フォーマット | 要約 |
| :--- | :--- | :--- | :--- | :--- |
| （随時追記） | — | — | `.prproj` / `.mp4` / `.mov` | 専任スキル [`.agents/skills/premiere/SKILL.md`](../../.agents/skills/premiere/SKILL.md) により管理。 |

---

## ✨ 7. Adobe After Effects（モーショングラフィックス・TVCM・VFX） — `outputs/aftereffects/`

| 納品日 | 案件サブフォルダ / テーマ | メイン出力ファイル | フォーマット | 要約 |
| :--- | :--- | :--- | :--- | :--- |
| 2026-11-26 | `2026-12-27_furusato_cm/`<br>ふるさと合同企業説明会2026 TVCM（30秒＋前後3秒カラーバー） | [`2026-12-27_ふるさと合同企業説明会2026_CM_36sec.mp4`](aftereffects/2026-12-27_furusato_cm/2026-12-27_ふるさと合同企業説明会2026_CM_36sec.mp4)<br>[`2026-12-27_ふるさと合同企業説明会2026_CM_36sec_BGMのみ.mp4`](aftereffects/2026-12-27_furusato_cm/2026-12-27_ふるさと合同企業説明会2026_CM_36sec_BGMのみ.mp4)<br>[`furusato2026_cm_master.aep`](aftereffects/2026-12-27_furusato_cm/furusato2026_cm_master.aep)<br>[`narration_script_30sec.md`](aftereffects/2026-12-27_furusato_cm/narration_script_30sec.md) / [`preview_contact_36s.png`](aftereffects/2026-12-27_furusato_cm/preview_contact_36s.png) | MP4×2 (`1920×1080`, 30fps, `-18.7 LUFS`) / `.aep` / WAV×3 / MD / PNG | AE 2027実機構築＆独立QA PASS。Gemini TTS (`Leda`)＋本番BGM自動ダッキングMA完パケ・YouTubeサムネイル同梱。 |

---

## 🎞️ 8. Moho Pro 14（2Dベクターアニメーション・ボーンリグ・透過動画） — `outputs/moho/`

| 納品日 | 案件サブフォルダ / テーマ | メイン出力ファイル | フォーマット | 要約 |
| :--- | :--- | :--- | :--- | :--- |
| （随時追記） | — | — | `.moho` / ProRes 4444 `.mov` / VP9 `.webm` / `.mp4` | 専任スキル [`.agents/skills/moho/SKILL.md`](../../.agents/skills/moho/SKILL.md) により管理。 |

---

## 🌐 9. Pano2VR 8（360°パノラマ・バーチャルツアー・スキン制作） — `outputs/pano2vr/`

| 納品日 | 案件サブフォルダ / テーマ | メイン出力ファイル | フォーマット | 要約 |
| :--- | :--- | :--- | :--- | :--- |
| （随時追記） | — | — | `.ggsk` / HTML5出力 / `.ggpkg` | 専任スキル [`.agents/skills/pano2vr/SKILL.md`](../../.agents/skills/pano2vr/SKILL.md) により管理。 |

---

## 🥽 10. krpano 1.24（360°VRツアー・WebXR・ThreeJS・3DGS） — `outputs/krpano/`

| 納品日 | 案件サブフォルダ / テーマ | メイン出力ファイル | フォーマット | 要約 |
| :--- | :--- | :--- | :--- | :--- |
| 2026-11-17 | `2026-08-12_桐林クリーンセンター跡地解体後の状況_VR_krpano/`<br>桐林クリーンセンター跡地 解体後360°VRツアー（空間解析ハイスペック版） | [`SPATIAL_ANALYSIS_REPORT.md`](krpano/2026-08-12_桐林クリーンセンター跡地解体後の状況_VR_krpano/SPATIAL_ANALYSIS_REPORT.md)<br>[`tour.html`](krpano/2026-08-12_桐林クリーンセンター跡地解体後の状況_VR_krpano/tour.html) / [`tour.xml`](krpano/2026-08-12_桐林クリーンセンター跡地解体後の状況_VR_krpano/tour.xml)<br>[`audit_gis_hybrid_map.png`](krpano/2026-08-12_桐林クリーンセンター跡地解体後の状況_VR_krpano/audit_gis_hybrid_map.png) | HTML5 / krpano XML / JS / GISタイル / MD | 200MP 15点（Cube 6400px 4階層）・3Dドリー遷移・真北＆標高テレメトリHUD・国土地理院ハイブリッドGISマップ実装。 |

---

## 📸 11. PTGui Pro 13（360°パノラマスティッチ・HDR合成） — `outputs/ptgui/`

| 納品日 | 案件サブフォルダ / テーマ | メイン出力ファイル | フォーマット | 要約 |
| :--- | :--- | :--- | :--- | :--- |
| （随時追記） | — | — | `.pts` / `.jpg` / `.tif` / `.psd` / `.exr` | 専任スキル [`.agents/skills/ptgui/SKILL.md`](../../.agents/skills/ptgui/SKILL.md) により管理。 |

---

## 🌐 12. Web / WordPress・Avada（Web保守・スタンドアロンHTML） — `outputs/web/`

| 納品日 | 案件サブフォルダ / テーマ | メイン出力ファイル | フォーマット | 要約 |
| :--- | :--- | :--- | :--- | :--- |
| （随時追記） | — | — | `.html` / `.php` / `.css` / `.md` | 専任スキル [`.agents/skills/wordpress-avada-maintenance/SKILL.md`](../../.agents/skills/wordpress-avada-maintenance/SKILL.md) により管理。 |
