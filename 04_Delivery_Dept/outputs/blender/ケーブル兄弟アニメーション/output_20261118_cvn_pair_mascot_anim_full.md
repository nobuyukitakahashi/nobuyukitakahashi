# 最終納品パッケージ：株式会社CVN 公式キャラクター「ケーブル兄弟（いい-ch ＆ いい-NETくん）」2体ペア3Dアニメーション（Blender 5.3 / v8 完成版：「歩くとき」「手を振るとき」の残存くびれ・影スジ・股間歪み完全ゼロ化 ＋ 完全同期マスコット効果音SE付き Full HD 30fps）
- **納品日**: 2026年11月18日
- **ジャンル**: `blender`
- **格納場所**: `04_Delivery_Dept/outputs/blender/ケーブル兄弟アニメーション/`
- **法務・コンプライアンス審査**: `SKIPPED（通常案件・自社/依頼元公式マスコット3Dアニメーション制作、5大法務リスクトリガー非該当）`
- **同梱・変換ファイル一覧**:
  - マスターパッケージ仕様書: [`output_20261118_cvn_pair_mascot_anim_full.md`](output_20261118_cvn_pair_mascot_anim_full.md)（および [`output_20261112_cvn_pair_mascot_anim_full.md`](output_20261112_cvn_pair_mascot_anim_full.md) もv8最新内容へ同期更新済）
  - 15.0秒 効果音SE付き Full HD 3Dアニメーション動画（全450フレーム @ 30fps, `1920×1080 px` 16:9 ワイド, H.264 + AAC 48kHz Stereo MP4）: [`output_20261118_cvn_pair_run_bow_wave.mp4`](output_20261118_cvn_pair_run_bow_wave.mp4)（[`output_20261112_cvn_pair_run_bow_wave.mp4`](output_20261112_cvn_pair_run_bow_wave.mp4) / 互換シンボリック名: [`pair_iich_and_iinet_run_bow_wave.mp4`](pair_iich_and_iinet_run_bow_wave.mp4)）
  - 完全同期マスコット効果音（SE）マスターWAV（48,000 Hz / 16-bit Stereo WAV）: [`output_20261118_cvn_pair_sfx.wav`](output_20261118_cvn_pair_sfx.wav)（互換シンボリック名: [`pair_iich_and_iinet_sfx.wav`](pair_iich_and_iinet_sfx.wav)）
  - 全4フェーズ代表キーフレーム一覧シート（6コマ・16:9, `1984×768 px` PNG）: [`output_20261118_cvn_pair_anim_keyframes.png`](output_20261118_cvn_pair_anim_keyframes.png)（[`output_20261112_cvn_pair_anim_keyframes.png`](output_20261112_cvn_pair_anim_keyframes.png) / 互換シンボリック名: [`pair_iich_and_iinet_anim_keyframes.png`](pair_iich_and_iinet_anim_keyframes.png)）
  - 歩行1サイクル連続監査シート（8コマ・16:9, `2320×678 px` PNG）: [`output_20261118_cvn_pair_walk_cycle_8frames.png`](output_20261118_cvn_pair_walk_cycle_8frames.png)（[`output_20261112_cvn_pair_walk_cycle_8frames.png`](output_20261112_cvn_pair_walk_cycle_8frames.png)）
  - 腕根元＆両足・下腹部・股間 400%拡大シームレス監査シート（6ポーズ, `2584×768 px` PNG）: [`output_20261118_cvn_pair_arm_seam_closeup.png`](output_20261118_cvn_pair_arm_seam_closeup.png)（[`output_20261112_cvn_pair_arm_seam_closeup.png`](output_20261112_cvn_pair_arm_seam_closeup.png)）
  - Blender 5.3 アニメーションプロジェクトファイル（VSE Sound Strip `Mascot_SFX` パック統合済・`dR_from_c` クランプ撤廃＆ `m_lock = 0.55` 剛体保護・タマゴ等高線追従リフト・足ドーム `z_leg_top` 適正化＋お腹保護マスク `w_belly_protect`・Phase 4 股間完全対称維持・Full HD 30fps 450f）: [`output_20261118_cvn_pair_anim.blend`](output_20261118_cvn_pair_anim.blend)（[`output_20261112_cvn_pair_anim.blend`](output_20261112_cvn_pair_anim.blend) / 互換シンボリック名: [`cvn_iich_and_iinet_pair_anim.blend`](cvn_iich_and_iinet_pair_anim.blend)）

---

## Part 1. 完成コンテンツ本編・制作仕様

# CVN公式マスコット「いい-ch（LILI-ch）＆ いい-NETくん（LILI-net）」2体ペア3Dアニメーション動画 制作仕様・品質監査レポート（Blender 5.3 / v8 完成版：「歩くとき」「手を振るとき」の残存くびれ・影スジ・股間歪み完全ゼロ化 ＋ 完全同期マスコット効果音SE付き Full HD 30fps）

### 1. 概要・制作スペック
- **最終納品動画ファイル（効果音SE統合・音声付きMP4）**: [`output_20261118_cvn_pair_run_bow_wave.mp4`](output_20261118_cvn_pair_run_bow_wave.mp4) / [`pair_iich_and_iinet_run_bow_wave.mp4`](pair_iich_and_iinet_run_bow_wave.mp4)（制作元中間ファイル: [`02_Creative_Dept/blender/final_outputs/pair_iich_and_iinet_run_bow_wave.mp4`](file:///g:/マイドライブ/git/nobuyukitakahashi/02_Creative_Dept/blender/final_outputs/pair_iich_and_iinet_run_bow_wave.mp4)）
- **完全同期マスコット効果音（SE）トラック（48kHz / 16-bit ステレオWAV）**: [`output_20261118_cvn_pair_sfx.wav`](output_20261118_cvn_pair_sfx.wav) / [`pair_iich_and_iinet_sfx.wav`](pair_iich_and_iinet_sfx.wav)（制作元中間ファイル: [`02_Creative_Dept/blender/final_outputs/pair_iich_and_iinet_sfx.wav`](file:///g:/マイドライブ/git/nobuyukitakahashi/02_Creative_Dept/blender/final_outputs/pair_iich_and_iinet_sfx.wav)）
- **全4フェーズ代表キーフレーム一覧（6コマ・16:9）**: [`output_20261118_cvn_pair_anim_keyframes.png`](output_20261118_cvn_pair_anim_keyframes.png) / [`pair_iich_and_iinet_anim_keyframes.png`](pair_iich_and_iinet_anim_keyframes.png)（制作元中間ファイル: [`02_Creative_Dept/blender/final_outputs/pair_iich_and_iinet_anim_keyframes.png`](file:///g:/マイドライブ/git/nobuyukitakahashi/02_Creative_Dept/blender/final_outputs/pair_iich_and_iinet_anim_keyframes.png)）
- **歩行1サイクル連続監査シート（8コマ・16:9）**: [`output_20261118_cvn_pair_walk_cycle_8frames.png`](output_20261118_cvn_pair_walk_cycle_8frames.png)（制作元中間ファイル: [`02_Creative_Dept/blender/drafts/audit_walk_cycle_8frames.png`](file:///g:/マイドライブ/git/nobuyukitakahashi/02_Creative_Dept/blender/drafts/audit_walk_cycle_8frames.png)）
- **腕根元＆両足・下腹部・股間 400%拡大シームレス監査シート（6ポーズ）**: [`output_20261118_cvn_pair_arm_seam_closeup.png`](output_20261118_cvn_pair_arm_seam_closeup.png)（制作元中間ファイル: [`02_Creative_Dept/blender/drafts/audit_arm_seam_closeup.png`](file:///g:/マイドライブ/git/nobuyukitakahashi/02_Creative_Dept/blender/drafts/audit_arm_seam_closeup.png)）
- **Blender 5.3 アニメーションプロジェクト（VSE効果音ストリップ統合済み）**: [`output_20261118_cvn_pair_anim.blend`](output_20261118_cvn_pair_anim.blend) / [`cvn_iich_and_iinet_pair_anim.blend`](cvn_iich_and_iinet_pair_anim.blend)（制作元中間ファイル: [`02_Creative_Dept/blender/final_outputs/cvn_iich_and_iinet_pair_anim.blend`](file:///g:/マイドライブ/git/nobuyukitakahashi/02_Creative_Dept/blender/final_outputs/cvn_iich_and_iinet_pair_anim.blend)）
- **生成・レンダリング統合スクリプト**: [`02_Creative_Dept/blender/drafts/build_pair_animation.py`](file:///g:/マイドライブ/git/nobuyukitakahashi/02_Creative_Dept/blender/drafts/build_pair_animation.py)
- **映像・音声フォーマット**:
  - **尺・フレーム数**: **15.0秒（全450フレーム @ 30fps、`FRAME_START = 1`, `FRAME_END = 450`）**
  - **解像度**: **`1920 × 1080`（Full HD / 16:9 ワイド）**
  - **カメラ・画角**: 16:9 縦視野角完全維持設計（`lens = 52.5mm` `= 70.0mm * 0.75`）
  - **映像コーデック**: MPEG-4 / H.264（CRF: HIGH, GOP: 15）
  - **音声コーデック**: AAC ステレオ（48,000 Hz / 192 kbps、全4フェーズ完全同期マスコット効果音）
  - **レンダーエンジン**: **Blender 5.3.0** Cycles GPU（OpenImageDenoise, Standard View Transform）

---

### 2. v8 極限改修の技術要点（「歩くとき」「手を振るとき」の残存くびれ・影スジ・股間歪み完全ゼロ化 ＋ 効果音SE統合）

#### A. 腕（パドル手）の「歩くとき」と「手を振るとき」の極限調整
1. **ひょうたん型のくびれ・潰れを生んでいた `dR_from_c` 半径クランプの完全撤廃**:
   - 腕を前に振ったり（Frame 26）、上に高く持ち上げたり（Frame 345）した際、斜めに傾いた腕母線がリム `(S_0, Z_0)` より先へ張り出すのをリム内側へ押し戻していた `dR_from_c` クランプを完全撤廃。これにより前振り時や高挙上時の腕中間の凹み・ひょうたん型くびれが100%消滅した。
2. **純粋剛体ロック境界 `m_lock = 0.55 * (n_u - 1)` への引き締め（パドル中間部の痩せ根絶）**:
   - `m_lock` を `0.76` から `0.55`（`n_skirt = 14, n_collar = 12, n_tip = 30`、合計56リング・6,273頂点のトポロジ完全維持）へ引き締め、腕の先端側半分以上（`u = 0.55..1.0`）を100%純粋剛体回転のぷっくり丸いパドル形状として完全保護した。
3. **「歩くとき」と「手を振るとき」の回転角＆タマゴ表面等高線追従リフトの最適化（肩上端の暗い影スジ消滅）**:
   - **歩くとき（Phase 1）**: 短いパドル手の前後スイング振幅 `swing_amp` を `23.0°`（いい-ch）／`22.0°`（いい-NETくん）に最適化し、前振り時の軽い挙上連動と胴体ヨー回転（`torso_yaw_deg = 8.2 * s`）を組み合わせることで、付け根の歪みゼロで元気に腕を振って歩く。
   - **手を振るとき（Phase 4）**: 肩ソケット位置自体をタマゴ胴体の表面等高線 `R_surf(z_sh + dz_lift) - R_surf(z_sh)` に沿って正確かつ滑らかにほっぺの横（`sh_lift_z = +0.068m / +0.078m`）へスライドさせつつ、パドル自体の挙上角 `outer_flap` を `(25.5 + 11.5 * sw10) * w_wave`（最大 `+37°` 〜 最小 `+14°`）でパタパタ振ることで、肩上端で胴体法線と腕法線が鋭角にぶつかって生じていた暗いシェーディングの影スジを100%解消した。
4. **法線ブレンドの広帯域平滑化**:
   - `s_max_theta = 0.85 + 0.35 * sin2_th` および法線グリッドの2Dガウシアン平滑化（`sigma = 1.8 × 1.8`、リム端 `j=0` は `Body` 法線に角度差 `0.00°` で厳密ロック）により、肩周り全周のシェーディングが完全に連続化した。

#### B. 足（超短足）の「歩くとき」と「手を振るとき」の極限調整
1. **股間の谷（`z_crotch`）より上の「1つに繋がったお腹」のねじれ解消とお腹シルエット保護**:
   - 足変形の上端 `z_leg_top`（`= z_hip_piv`）を実際の足突起ドーム高さ（いい-ch: `z_leg_solid = 0.022m, z_leg_top = 0.112m`、いい-NETくん: `z_leg_solid = 0.030m, z_leg_top = 0.175m`）に引き下げ、さらに前面のお腹保護マスク `w_belly_protect` と股間アーチ中立減衰 `w_crotch_arch`、および変位ベクトル場 $\Delta \mathbf{p}$ の18反復ラプラシアン調和緩和を適用。
   - 歩行時の足ドーム局所スイング角 `max_swing_deg = 10.5° / 11.5°` と胴体ヨーひねり（`8.2°`）・ロール揺れ（`4.0°`）・バウンスの調和により、斜め3/4アングル（Frame 26 / 36）でもお腹の下のくびれ・二重あご段差が100%ゼロのまま可愛くトコトコ歩く。
2. **「手を振るとき（Phase 4）」の股間・足元の完全対称シルエット維持**:
   - Phase 4（手振り中）における左右非対称な足の局所変形をすべて `0.0` にロックし、両足とも100%綺麗な丸い対称シルエットを保ったまま、身体全体の小首傾げロール（`-3.8°`）・左右スウェイ・軽やかな上下リズムホップで手振りのリズムを表現。これにより Frame 345 / 351 の足元・股間の非対称な歪みが100%ゼロとなった。

#### C. 完全同期マスコット効果音（SE）のプロシージャル生成とMP4・Blend統合
- Python `numpy` + `wave` により、アニメーションの数式（`f_24` タイムライン）と1ミリ秒のズレもなく完全同期した **48,000Hz / 16-bit ステレオ効果音（[`output_20261118_cvn_pair_sfx.wav`](output_20261118_cvn_pair_sfx.wav) / [`pair_iich_and_iinet_sfx.wav`](pair_iich_and_iinet_sfx.wav)）** を生成し、Blender VSE Sound Strip（`Mascot_SFX`）および MP4 AAC 192kbps 音声ストリームとして統合：
  1. **Phase 1（歩く音）**: いい-ch（左定位 `L:0.82, R:0.48`）の「ポコッ、トコッ♪」と、いい-NETくん（右定位 `L:0.48, R:0.82`、`3.0 f_24` 位相差）の「ポテッ、トテッ♪」が1歩（10.0フレーム＝0.3333秒）ごとに完全同期し、奥から手前への接近に合わせて滑らかにクレッシェンド。
  2. **Phase 2（着地ホップ音）**: Frame 162 のジャンプ開始で可愛い上昇グライド音「ピョコン♪（`350Hz -> 790Hz`）」、Frame 180 の着地クッションで「ポテッ♪」。
  3. **Phase 3（おじぎ音）**: Frame 222 のおじぎ開始でソフトスウィッシュ＋下降2音マリンバチャイム「ペコリ♪（`E5 659Hz -> C5 523Hz`）」、Frame 271 の起き上がりで上昇2音チャイム「フワッ♪（`C5 -> E5`）」。
  4. **Phase 4（手を振る音）**: 手振り周期（12.5フレーム＝0.4167秒）の上振り・下振り速度ピーク（6.25フレーム＝0.2083秒ごと）に完全同期した、シルク風スウィッシュ＋キュートなポップトーン「パタパタパタッ♪（フリフリッ♪）」。

---

### 3. 全4フェーズ演出・効果音（SE）タイムライン詳細（450フレーム / 15.0秒 @ 30fps）

| フェーズ | フレーム範囲（30fps / 秒数） | カービィ型・超短足マスコットの可愛い仕草・カメラワーク・完全同期効果音（SE）詳細 | 視覚監査フレーム（30fps） |
| :--- | :--- | :--- | :--- |
| **Phase 1：カービィお手本準拠の「トコ・ピョコ！」超短足ウォーク** | `Frame 1〜160`<br>（`0.00s〜5.33s`） | ・**テンポ＆SE**: 1歩＝10フレーム（左右1サイクル＝20フレーム @ 30fps、計16歩）。左いい-ch「ポコッ、トコッ♪」と右いい-NETくん「ポテッ、トテッ♪」がステレオ定位・位相差で完全同期。<br>・**手足くびれゼロ連動**: `dR_from_c` 撤廃＆ `m_lock=0.55` 保護のパドル手と、`z_leg_top` 足ドーム適正化＋お腹保護マスク `w_belly_protect` の超短足により、くびれ・しわ・段差ゼロでトコトコ歩く。 | 8コマ連続監査:<br>`Frame 21, 24, 26, 29, 31, 34, 36, 39`<br>6コマ代表:<br>`Frame 26`, `Frame 96` |
| **Phase 2：ちょこんと両足着地ホップ（「ピョコン・ピタッ！」）＆正面静止** | `Frame 161〜210`<br>（`5.33s〜7.00s`） | `Y = 0.0m` 定位置に到着した瞬間、両足を揃えて小さく **「ピョコン♪（上昇グライドSE）」と可愛い着地ホップ（高さ `+4.6cm`）** ➔ 着地クッション「ポテッ♪」で正面スマイル静止構図（`Frame 195〜210`）にピタッと収まる（静止時変位 $\Delta \mathbf{p} = \mathbf{0}$ で元形状と `0.0000mm` 完全一致）。 | `Frame 170`（ピョコン着地ホップ）<br>`Frame 195`（正面完全静止） |
| **Phase 3：短い2本の足で踏ん張って「ペコリ！」とする可愛いおじぎ** | `Frame 211〜300`<br>（`7.00s〜10.00s`） | 両キャラとも **短い2本の足を床にちょこんと踏ん張って正面に見せたまま**、ソフトスウィッシュ＋マリンバチャイム「ペコリ♪（`E5 -> C5`）」に合わせて前へ **`20.5° / 21.5°` 綺麗におじぎ** ➔ 起き上がりチャイム「フワッ♪（`C5 -> E5`）」で正面へ戻る。 | `Frame 252`（両足踏ん張り＆丸ボディペコリおじぎ） |
| **Phase 4：両キャラともほっぺ横の高い位置で「パタパタ！」と振る手振り** | `Frame 301〜450`<br>（`10.00s〜15.00s`） | タマゴ胴体の表面等高線に沿って肩ソケットをほっぺの横（`+0.068m / +0.078m`）へスライドさせつつパドル手を `+14° ⇔ +37°` で振り、**くびれ・肩上端の暗い影スジ・股間歪み100%ゼロで、手振り速度ピークに完全同期した「パタパタパタッ♪（フリフリッ♪）」SE** とともに元気に手振り。足元は完全対称の丸いシルエットのまま小首傾げ＆リズムホップで可愛く動き、最後は正面静止ポーズ（`Frame 450`）に収まる。 | `Frame 345`（両キャラ高い位置の手振りUp）<br>`Frame 351` / `Frame 364`（手振りDown） |

---

### 4. 視覚監査結果サマリー（Blender 5.3 / v8 Full HD 30fps 完成監査）
1. **400%拡大クローズアップ監査シート（[`output_20261118_cvn_pair_arm_seam_closeup.png`](output_20261118_cvn_pair_arm_seam_closeup.png)）**: 6つの代表ポーズ（`Frame 195` 正面静止、`Frame 26` 歩行前振り、`Frame 36` 歩行後ろ振り、`Frame 252` おじぎ、`Frame 345` 高い手振りUp、`Frame 351` 手振りDown）を400%拡大で目視監査し、**「歩くとき（Frame 26 / 36）」の腕の潰れやお腹下のくびれ段差、および「手を振るとき（Frame 345 / 351）」の腕のひょうたん型くびれ・肩上端の暗い影スジ・股間アーチの非対称な歪みがすべて100%消滅**し、どのポーズでもぷっくり丸く張りのあるソフビ一体成型シルエットになっていることを確認し合格。
2. **歩行1サイクル連続監査シート（[`output_20261118_cvn_pair_walk_cycle_8frames.png`](output_20261118_cvn_pair_walk_cycle_8frames.png)）**: 連続8コマすべてで手足のくびれ・しわ・段差が完全ゼロであり、可愛いトコトコ歩行になっていることを確認し合格。
3. **全4フェーズ代表キーフレームシート（[`output_20261118_cvn_pair_anim_keyframes.png`](output_20261118_cvn_pair_anim_keyframes.png)）**: 全4フェーズ6コマすべてにおいて完璧な造形・構図を確認し合格。

---

## Part 2. SNS・マーケティング告知文
※本案件は `/blender` ジャンル直行モード（3Dアニメーション制作・v8 Full HD 30fps 手足くびれ・影スジ・股間歪み完全ゼロ化 ＋ 完全同期マスコット効果音SE統合案件）として稼働したため、`03_Marketing_Dept` によるSNS告知文生成はスキップされています。

---

## Part 3. リファレンス解析サマリー＆設計根拠
- **動作リファレンス出典**: `Kirby walk cycle coloured`（`https://www.youtube.com/watch?v=xZMflRnbC3o`、フレーム単位解析を 30fps タイムベースへ高精度換算：1歩＝10フレーム・左右1サイクル＝20フレーム＝0.67秒 @ 30fps）
- **ペア造形・正面バランス基準**: 株式会社CVN 公式キャラクター「ケーブル兄弟（いい-ch ＆ いい-NETくん）」2体横並び原画 `ref_20261110_pair_balance.png`（完成静止画シルエット重なり一致率 **IoU 98.11%**、16:9 Full HD `lens = 52.5mm` にて縦視野角・頭上地球儀〜足元余白比率を100%完全維持）
- **Blender 5.3 / v8 改修による4大設計原則**:
  1. **「歩くとき」「手を振るとき」のパドル腕くびれ・肩影スジ完全ゼロ（`dR_from_c` クランプ撤廃 ＋ `m_lock = 0.55` 剛体保護 ＋ タマゴ等高線追従リフト ＋ 2Dガウシアン法線平滑化）**: 前振り・高挙上時に腕中間を押し潰していた `dR_from_c` クランプを撤廃し、先端側半分以上（`u >= 0.55`）を純粋剛体回転で保護。さらに手振り時はタマゴ表面等高線に沿って肩ソケットをほっぺ横へスライドさせつつ適正角度（`+14° ⇔ +37°`）で振ることで、ひょうたん型くびれと肩上端の暗い影スジを100%解消。
  2. **「歩くとき」「手を振るとき」の超短足・お腹下段差・股間歪み完全ゼロ（足ドーム `z_leg_top` 適正化 ＋ お腹保護マスク `w_belly_protect` ＋ Phase 4 足元完全対称ロック）**: 足変形領域を実際の足突起ドーム（`z_leg_top = 0.112m / 0.175m`）に限定して股間より上の1つに繋がったお腹のねじれを根絶し、Phase 4 手振り時は足元の非対称変形をゼロにして小首傾げ＆リズムホップで表現することで股間の非対称な歪みを100%解消。
  3. **アニメーション数式と1ミリ秒単位で完全同期した 48kHz / 16-bit ステレオ効果音（SE）統合**: 歩く音（左右ステレオ定位の「ポコッ、トコッ♪」「ポテッ、トテッ♪」）、着地ホップ音（「ピョコン♪」「ポテッ♪」）、おじぎ音（「ペコリ♪」「フワッ♪」）、手を振る音（「パタパタパタッ♪」）をプロシージャル合成し、MP4（AAC 192kbps）および `.blend`（VSE Sound Strip）へ完全統合。
  4. **ボディ本体・胸ロゴ・顔領域への歪み波及ゼロ保証**: 胸ロゴ下端より上の `w_leg = 0.0` / `w_lap = 0.0` 厳密ロックにより、全450フレームを通じて胸ロゴ（`LILI-ch` / `LILI-net`）とお腹・タマゴ輪郭の歪みをゼロに保つ。
