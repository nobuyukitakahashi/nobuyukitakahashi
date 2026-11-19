# CVN公式マスコット「いい-ch（LILI-ch）＆ いい-NETくん（LILI-net）」2体ペア3Dアニメーション動画 制作仕様・品質監査レポート（Blender 5.3 / v10 完成版：しなやか尻尾物理エンジン〔2次バネ減衰＋S字波動カンチレバー＋地球儀完全真球追従〕＋ 瞬き柔和化 ＋ v9腕隙間ゼロ＆目の表情継承 Full HD 30fps）

## 1. 概要・制作スペック
- **完成動画ファイル（v10 効果音SE統合・音声付きMP4）**: [`02_Creative_Dept/blender/final_outputs/pair_iich_and_iinet_run_bow_wave.mp4`](file:///g:/マイドライブ/git/nobuyukitakahashi/02_Creative_Dept/blender/final_outputs/pair_iich_and_iinet_run_bow_wave.mp4)
- **完全同期マスコット効果音（SE）トラック（48kHz / 16-bit ステレオWAV）**: [`02_Creative_Dept/blender/final_outputs/pair_iich_and_iinet_sfx.wav`](file:///g:/マイドライブ/git/nobuyukitakahashi/02_Creative_Dept/blender/final_outputs/pair_iich_and_iinet_sfx.wav)
- **しなやか尻尾＆地球儀 8ポーズ監査シート**: [`02_Creative_Dept/blender/drafts/audit_tail_supple_motion.png`](file:///g:/マイドライブ/git/nobuyukitakahashi/02_Creative_Dept/blender/drafts/audit_tail_supple_motion.png)
- **2キャラクター目の表情クローズアップ監査シート（6ポーズ）**: [`02_Creative_Dept/blender/drafts/audit_eye_expressions.png`](file:///g:/マイドライブ/git/nobuyukitakahashi/02_Creative_Dept/blender/drafts/audit_eye_expressions.png)
- **歩行1サイクル連続監査シート（8コマ・16:9）**: [`02_Creative_Dept/blender/drafts/audit_walk_cycle_8frames.png`](file:///g:/マイドライブ/git/nobuyukitakahashi/02_Creative_Dept/blender/drafts/audit_walk_cycle_8frames.png)
- **全4フェーズ代表キーフレーム一覧（6コマ・16:9）**: [`02_Creative_Dept/blender/final_outputs/pair_iich_and_iinet_anim_keyframes.png`](file:///g:/マイドライブ/git/nobuyukitakahashi/02_Creative_Dept/blender/final_outputs/pair_iich_and_iinet_anim_keyframes.png)
- **腕根元400%拡大シームレス監査シート（6ポーズ）**: [`02_Creative_Dept/blender/drafts/audit_arm_seam_closeup.png`](file:///g:/マイドライブ/git/nobuyukitakahashi/02_Creative_Dept/blender/drafts/audit_arm_seam_closeup.png)
- **Blender 5.3 アニメーションプロジェクト（VSE効果音ストリップ統合済み）**: [`02_Creative_Dept/blender/final_outputs/cvn_iich_and_iinet_pair_anim.blend`](file:///g:/マイドライブ/git/nobuyukitakahashi/02_Creative_Dept/blender/final_outputs/cvn_iich_and_iinet_pair_anim.blend)
- **生成・レンダリング統合スクリプト**: [`02_Creative_Dept/blender/drafts/build_pair_animation.py`](file:///g:/マイドライブ/git/nobuyukitakahashi/02_Creative_Dept/blender/drafts/build_pair_animation.py)
- **映像・音声フォーマット**:
  - **尺・フレーム数**: **15.0秒（全450フレーム @ 30fps、`FRAME_START = 1`, `FRAME_END = 450`）**
  - **解像度**: **`1920 × 1080`（Full HD / 16:9 ワイド）**
  - **映像コーデック**: MPEG-4 / H.264（`3.08 Mbps`, 30fps, 450f, `5.99 MB`）
  - **音声コーデック**: AAC ステレオ（48,000 Hz / 2ch, 全4フェーズ完全同期マスコット効果音）
  - **レンダーエンジン**: **Blender 5.3.0** Cycles GPU（OpenImageDenoise, Standard View Transform）

---

## 2. v10 新規改修の技術要点（v9アーカイブは別途そのまま温存）

### A. 2キャラクター「しなやか尻尾物理エンジン」（2次バネ減衰＋S字波動カンチレバー＋地球儀完全真球追従）
1. **300Hz サブステップ 2モード弾性バネ減衰シミュレーション（`precompute_supple_tail_physics`）**:
   - 従来の足首ピボット一本棒回転（`±6〜7°`）を全面刷新し、1次カンチレバーたわみ `(q1_x, q1_y)` と 2次S字波動遅れ `(q2_x, q2_y)` の2連成バネ減衰系を全450フレーム（各フレーム10サブステップ＝300Hz）で物理シミュレーション。
   - **キャラ個性の固有振動数**: いい-ch（軽快・しなやか：`ω1=9.6, ζ1=0.23`）／いい-NETくん（ゆったり優雅：`ω1=8.2, ζ1=0.21`）。
   - **全4フェーズ連動**: 歩行中の軽快な8の字S字スイング、着地ホップ後の弾性バウンス＆減衰余韻（ポヨン・ユラッ）、おじぎ下げ始めの慣性遅れS字＆最下点オーバーシュート＆起き上がり戻り、手振り中のご機嫌な大振幅S字スイングを実現。Frame 195（正面静止）および Frame 450（終了静止）へは正確に `0.000` へ収束。
2. **$C^1$ 根元固定＋厳密弧長保存＋地球儀純粋剛体 `SO(3)` 0.000mm ロック（`apply_supple_tail_and_globe_deform`）**:
   - 背中付け根（`z <= z_root`）は値・1階微分ともに厳密 `0` で固定（浮き・抜けゼロ）。
   - 101点グリッド数値積分による弧長保存の Z 沈み込み $\Delta z(s)$ により、ゴムのように不自然に伸びないリアルな弾性ケーブル曲線を維持。
   - 先端の地球儀（`Globe`）は茎先端（$s=1$）の厳密接線角による純粋剛体 `SO(3)` 回転＋厳密先端変位平行移動を適用し、全450フレームで**完全真球（歪みゼロ）＆茎先端と3D球心の `0.000mm` 一致**を保証。

### B. 目の瞬きの柔和化（若干ゆっくり動作）
- 歩行中および着地ホップ時の瞬き時間を従来の約0.20秒から**約0.35秒**（閉眼 `3.0 f_24` ➔ 閉眼ホールド `1.1 f_24` ➔ やわらかく開眼 `4.2 f_24`）へ延長し、おじぎ・手振り切替の開閉も `4.2 / 5.4 f_24` へ柔和化。視認しやすく愛らしいまばたき動作を実現。
- v9で完成した**腕付け根隙間ゼロ改修**および**いい-ch女の子仕様（細い一定太さ＋まつげ2本＋パステルピンクほっぺ＋笑顔口）・いい-NETくん（やさしいおじぎ弧 `46°`）**はすべて100%継承。

---

## 3. 実MP4動画 視覚監査結果サマリー（v10 合格）
- 完成した v10 実動画 `pair_iich_and_iinet_run_bow_wave.mp4`（`1920×1080`, 30fps, 450f, `5.99 MB`, AAC 48kHz Stereo）から直接12フレームを抽出し、歩行S字スイング・ゆったり瞬き・着地バウンス余韻・正面静止（f=195）・おじぎS字しなり・手振り大スイング・終了静止（f=450）のすべてで破綻ゼロを確認し合格。
