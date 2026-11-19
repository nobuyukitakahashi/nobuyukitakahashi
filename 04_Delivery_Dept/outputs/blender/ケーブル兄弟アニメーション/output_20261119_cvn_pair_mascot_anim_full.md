# CVN公式マスコット「いい-ch（LILI-ch）＆ いい-NETくん（LILI-net）」2体ペア3Dアニメーション動画 制作仕様・品質監査レポート（Blender 5.3 / v9 完成版：腕付け根の隙間・切れ目完全ゼロ化 ＋ 目の表情アニメーション〔案A：王道マスコット系・いい-ch女の子仕様〕＋ 完全同期効果音SE付き Full HD 30fps）

## 1. 概要・制作スペック
- **完成動画ファイル（効果音SE統合・音声付きMP4）**: [`02_Creative_Dept/blender/final_outputs/pair_iich_and_iinet_run_bow_wave.mp4`](file:///g:/マイドライブ/git/nobuyukitakahashi/02_Creative_Dept/blender/final_outputs/pair_iich_and_iinet_run_bow_wave.mp4)
- **完全同期マスコット効果音（SE）トラック（48kHz / 16-bit ステレオWAV）**: [`02_Creative_Dept/blender/final_outputs/pair_iich_and_iinet_sfx.wav`](file:///g:/マイドライブ/git/nobuyukitakahashi/02_Creative_Dept/blender/final_outputs/pair_iich_and_iinet_sfx.wav)
- **全4フェーズ代表キーフレーム一覧（6コマ・16:9）**: [`02_Creative_Dept/blender/final_outputs/pair_iich_and_iinet_anim_keyframes.png`](file:///g:/マイドライブ/git/nobuyukitakahashi/02_Creative_Dept/blender/final_outputs/pair_iich_and_iinet_anim_keyframes.png)
- **2キャラクター目の表情クローズアップ監査シート（6ポーズ）**: [`02_Creative_Dept/blender/drafts/audit_eye_expressions.png`](file:///g:/マイドライブ/git/nobuyukitakahashi/02_Creative_Dept/blender/drafts/audit_eye_expressions.png)
- **歩行1サイクル連続監査シート（8コマ・16:9）**: [`02_Creative_Dept/blender/drafts/audit_walk_cycle_8frames.png`](file:///g:/マイドライブ/git/nobuyukitakahashi/02_Creative_Dept/blender/drafts/audit_walk_cycle_8frames.png)
- **腕根元＆両足・下腹部・股間 400%拡大シームレス監査シート（6ポーズ）**: [`02_Creative_Dept/blender/drafts/audit_arm_seam_closeup.png`](file:///g:/マイドライブ/git/nobuyukitakahashi/02_Creative_Dept/blender/drafts/audit_arm_seam_closeup.png)
- **Blender 5.3 アニメーションプロジェクト（VSE効果音ストリップ統合済み）**: [`02_Creative_Dept/blender/final_outputs/cvn_iich_and_iinet_pair_anim.blend`](file:///g:/マイドライブ/git/nobuyukitakahashi/02_Creative_Dept/blender/final_outputs/cvn_iich_and_iinet_pair_anim.blend)
- **生成・レンダリング統合スクリプト**: [`02_Creative_Dept/blender/drafts/build_pair_animation.py`](file:///g:/マイドライブ/git/nobuyukitakahashi/02_Creative_Dept/blender/drafts/build_pair_animation.py)
- **映像・音声フォーマット**:
  - **尺・フレーム数**: **15.0秒（全450フレーム @ 30fps、`FRAME_START = 1`, `FRAME_END = 450`）**
  - **解像度**: **`1920 × 1080`（Full HD / 16:9 ワイド）**
  - **映像コーデック**: MPEG-4 / H.264（`3.05 Mbps`, 30fps, 450f）
  - **音声コーデック**: AAC ステレオ（48,000 Hz / 2ch, 全4フェーズ完全同期マスコット効果音）
  - **レンダーエンジン**: **Blender 5.3.0** Cycles GPU（OpenImageDenoise, Standard View Transform）

---

## 2. v9 改修の技術要点

### A. いい-NETくん（およびいい-ch）腕付け根の隙間・黒い切れ目スジの完全ゼロ化
1. **リム端（`j=0`）のボディ内部微小噛み込み（`-0.35mm`）＆ `j=0, 1` 法線 `0.00°` 完全一致ロック**:
   - v8でいい-NETくん側のみリム全周が `+0.02〜+0.12mm` 外側へ浮いていた現象を解消し、`delta_rim = -0.00035m` で全周をボディ内部へ確実に噛み込ませ、表面通過直後の `j=1` までボディ法線と角度差 `0.00°` でロックすることで物理的浮き・隙間を完全ゼロ化。
2. **前面フィレット拡張・肩ピボット適正化・おじぎ後ろ引き角適正化（ボディ輪郭裏回り込みの根絶）**:
   - いい-NETくんの肩ピボット `y_sh` を `0.046m -> 0.026m` に適正化、おじぎ時の後ろ振り角を `-22° -> -10°`、カメラ前面側・脇下前縁のフィレット幅 `W_front` を拡張（`0.050m` / いい-ch `0.040m`）し、胴体正面輪郭の裏側へ腕付け根が回り込んで暗い影スジ（隙間見え）を生む現象を100%消滅。
3. **動的 `m_lock_k` による高挙上時（Frame 345）の `j=27` 折れ込み完全解消**:
   - 方位角ごとに `m_lock_k = max(m_lock, m_zero + 18.0)` を動的保証し、手振り頂点で発生していた `min_cos_bend = -0.916` の折れ返りおよび脇下の縦スジを完全解消。

### B. 2キャラクターの目の表情アニメーション（案A：王道マスコット系 ＋ いい-ch女の子仕様）
- **コンフォーマル曲面投影による影ゼロ・浮きゼロ表現**: `Face_Screen` の BVHTree 重心補間プロジェクタ上で、真円弧・完全一定太さ・真円半円キャップのコンフォーマルリボンとして生成。
- **いい-ch（女の子仕様）**:
  - いい-NETくん（`r_tube = 0.0300m`）より繊細で細い一定太さ（`r_tube = 0.0205m`）のライン。
  - **閉じ目（まばたき・おじぎ）**: 優雅な真円弧（`52°`）の目尻に外向きに跳ねる**可愛い曲線まつげ2本**を追加＋おじぎ時は**パステルピンクのほっぺチーク**を表示。
  - **笑顔目（手振り）**: 通常目上端の高さまで明るく笑い上がる弧（`76°`）＋**上向きまつげ2本**＋**パステルピンクのほっぺチーク**＋少し広くにっこりした**可愛い笑顔口**で、満面の笑顔の女の子表情を実現。
- **いい-NETくん（男の子仕様）**:
  - しっかりした一定太さ（`r_tube = 0.0300m`）の親しみやすいライン。
  - **おじぎ閉じ目**: 強すぎないやさしく自然な真円弧（`46°`）。
  - **手振り笑顔目**: 元気いっぱいの明るい真円弧（`68°`）。
- **フェーズ別タイムライン**:
  - **Phase 1（歩き）**: 2体ずらしの自然なまばたき各2回（いい-ch: f=45, 120 / いい-NETくん: f=60, 135）。
  - **Phase 2（着地ホップ）**: ホップ頂点で1回まばたき ➔ Frame 195 正面静止で100%公式通常目へ復帰。
  - **Phase 3（おじぎ）**: まばたき連動でシームレスに閉じ目（`︶ ︶`）へ切替 ➔ 起き上がりで開眼。
  - **Phase 4（手振り）**: まばたき連動で笑顔目（`◠ ◠`）へ切替 ➔ Frame 450 終了時は100%公式通常目へ復帰。

---

## 3. 実MP4動画 視覚監査結果サマリー（v9 合格）
- 完成した `pair_iich_and_iinet_run_bow_wave.mp4`（Full HD 1920×1080, 30fps, 450f, AAC 48kHz Stereo）から直接フレームを抽出し、**おじぎ連続9コマ800%拡大・手振り連続9コマ800%拡大・全フェーズ代表8コマ**を目視検証。腕付け根の隙間・切れ目ゼロ、および全フェーズの目の表情・まつげ・チーク・音声多重化の完全品質を確認し合格。
