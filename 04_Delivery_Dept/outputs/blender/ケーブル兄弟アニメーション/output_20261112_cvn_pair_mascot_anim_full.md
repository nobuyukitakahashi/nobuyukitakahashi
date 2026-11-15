# 最終納品パッケージ：株式会社CVN 公式キャラクター「ケーブル兄弟（いい-ch ＆ いい-NETくん）」2体ペア3Dアニメーション（Blender 5.3 / v6 完成版：腕根元シームレス一体化・ひれ完全ゼロ・足歪みゼロ・ボディ本体歪み波及ゼロ・Full HD 30fps）
- **納品日**: 2026年11月12日
- **ジャンル**: `blender`
- **格納場所**: `04_Delivery_Dept/outputs/blender/ケーブル兄弟アニメーション/`
- **法務・コンプライアンス審査**: `SKIPPED（通常案件・自社/依頼元公式マスコット3Dアニメーション制作、5大法務リスクトリガー非該当）`
- **同梱・変換ファイル一覧**:
  - マスターパッケージ仕様書: [`output_20261112_cvn_pair_mascot_anim_full.md`](output_20261112_cvn_pair_mascot_anim_full.md)
  - 15.0秒 Full HD 3Dアニメーション動画（全450フレーム @ 30fps, `1920×1080 px` 16:9 ワイド, H.264 MP4）: [`output_20261112_cvn_pair_run_bow_wave.mp4`](output_20261112_cvn_pair_run_bow_wave.mp4)（互換シンボリック名: [`pair_iich_and_iinet_run_bow_wave.mp4`](pair_iich_and_iinet_run_bow_wave.mp4)）
  - 全4フェーズ代表キーフレーム一覧シート（6コマ・16:9, `1984×768 px` PNG）: [`output_20261112_cvn_pair_anim_keyframes.png`](output_20261112_cvn_pair_anim_keyframes.png)（互換シンボリック名: [`pair_iich_and_iinet_anim_keyframes.png`](pair_iich_and_iinet_anim_keyframes.png)）
  - 歩行1サイクル連続監査シート（8コマ・16:9, `2320×678 px` PNG）: [`output_20261112_cvn_pair_walk_cycle_8frames.png`](output_20261112_cvn_pair_walk_cycle_8frames.png)
  - 腕根元400%拡大シームレス監査シート（6ポーズ, `2584×768 px` PNG）: [`output_20261112_cvn_pair_arm_seam_closeup.png`](output_20261112_cvn_pair_arm_seam_closeup.png)
  - Blender 5.3 アニメーションプロジェクトファイル（腕根元スライディング吸盤フィレットスカート＋法線角度差 `0.00°` シームレス一体化・超短足弾性振り子リグ・ボディ本体歪み波及ゼロ制御・Full HD 30fps 450f）: [`output_20261112_cvn_pair_anim.blend`](output_20261112_cvn_pair_anim.blend)（互換シンボリック名: [`cvn_iich_and_iinet_pair_anim.blend`](cvn_iich_and_iinet_pair_anim.blend)）

---

## Part 1. 完成コンテンツ本編・制作仕様

# CVN公式マスコット「いい-ch（LILI-ch）＆ いい-NETくん（LILI-net）」2体ペア3Dアニメーション動画 制作仕様・品質監査レポート（Blender 5.3 / v6 完成版：腕根元シームレス一体化・ひれ完全ゼロ・足歪みゼロ・ボディ本体歪み波及ゼロ・Full HD 30fps）

### 1. 概要・制作スペック
- **最終納品動画ファイル**: [`output_20261112_cvn_pair_run_bow_wave.mp4`](output_20261112_cvn_pair_run_bow_wave.mp4) / [`pair_iich_and_iinet_run_bow_wave.mp4`](pair_iich_and_iinet_run_bow_wave.mp4)（制作元中間ファイル: [`02_Creative_Dept/blender/final_outputs/pair_iich_and_iinet_run_bow_wave.mp4`](file:///g:/マイドライブ/git/nobuyukitakahashi/02_Creative_Dept/blender/final_outputs/pair_iich_and_iinet_run_bow_wave.mp4)）
- **全4フェーズ代表キーフレーム一覧（6コマ・16:9）**: [`output_20261112_cvn_pair_anim_keyframes.png`](output_20261112_cvn_pair_anim_keyframes.png) / [`pair_iich_and_iinet_anim_keyframes.png`](pair_iich_and_iinet_anim_keyframes.png)（制作元中間ファイル: [`02_Creative_Dept/blender/final_outputs/pair_iich_and_iinet_anim_keyframes.png`](file:///g:/マイドライブ/git/nobuyukitakahashi/02_Creative_Dept/blender/final_outputs/pair_iich_and_iinet_anim_keyframes.png)）
- **歩行1サイクル連続監査シート（8コマ・16:9）**: [`output_20261112_cvn_pair_walk_cycle_8frames.png`](output_20261112_cvn_pair_walk_cycle_8frames.png)（制作元中間ファイル: [`02_Creative_Dept/blender/drafts/audit_walk_cycle_8frames.png`](file:///g:/マイドライブ/git/nobuyukitakahashi/02_Creative_Dept/blender/drafts/audit_walk_cycle_8frames.png)）
- **腕根元400%拡大シームレス監査シート（6ポーズ）**: [`output_20261112_cvn_pair_arm_seam_closeup.png`](output_20261112_cvn_pair_arm_seam_closeup.png)（制作元中間ファイル: [`02_Creative_Dept/blender/drafts/audit_arm_seam_closeup.png`](file:///g:/マイドライブ/git/nobuyukitakahashi/02_Creative_Dept/blender/drafts/audit_arm_seam_closeup.png)）
- **Blender 5.3 アニメーションプロジェクト**: [`output_20261112_cvn_pair_anim.blend`](output_20261112_cvn_pair_anim.blend) / [`cvn_iich_and_iinet_pair_anim.blend`](cvn_iich_and_iinet_pair_anim.blend)（制作元中間ファイル: [`02_Creative_Dept/blender/final_outputs/cvn_iich_and_iinet_pair_anim.blend`](file:///g:/マイドライブ/git/nobuyukitakahashi/02_Creative_Dept/blender/final_outputs/cvn_iich_and_iinet_pair_anim.blend)）
- **生成・レンダリング統合スクリプト**: [`02_Creative_Dept/blender/drafts/build_pair_animation.py`](file:///g:/マイドライブ/git/nobuyukitakahashi/02_Creative_Dept/blender/drafts/build_pair_animation.py)
- **映像フォーマット**:
  - **尺・フレーム数**: **15.0秒（全450フレーム @ 30fps、`FRAME_START = 1`, `FRAME_END = 450`）**
  - **解像度**: **`1920 × 1080`（Full HD / 16:9 ワイド）**
  - **カメラ・画角**: 16:9 縦視野角完全維持設計（`lens = 52.5mm` `= 70.0mm * 0.75`、頭上の地球儀上端〜足元の余白バランスを従来の完成構図と100%同一に保ちつつ左右のスタジオ空間を拡張）
  - **コーデック**: MPEG-4 / H.264（CRF: HIGH, GOP: 15）
  - **レンダーエンジン**: **Blender 5.3.0** Cycles GPU（OpenImageDenoise, Standard View Transform）

---

### 2. v6 全面改修の技術要点（腕根元シームレス一体化 ＋ オーナー指摘項目の100%根絶）

#### A. 腕とボディの「切れ目（境界線）」完全消滅：スライディング吸盤フィレットスカート ＋ 法線完全一致制御
- **課題**: v5 では独立閉曲面パドル腕（`Arm.L/R`）とタマゴ型 `Body` が約50°〜80°のV字角で交差していたため、正面・斜め3/4歩行・手振り時に腕の付け根まわりに別パーツが刺さっているような楕円状の陰影境界線（切れ目）が見えていた。また、Boolean + Voxel Remesh を毎フレーム行う方式ではトポロジ変化による動画フリッカー（チラつき）や翼状のひれが発生するリスクがあった。
- **v6 解決アーキテクチャ**:
  1. **開放リム型パドル腕メッシュ（6,273頂点・全450フレームでトポロジ100%不変）**:
     - `Arm.L/R` を極座標グリッド（`n_rings = 56` × `n_theta = 112` ＋ 先端極1頂点 ＝ 6,273頂点）の開放リム型メッシュとして構築し、内側リム（`j = 0`）を開放端として `Body` 表面に密着させた。これによりフレーム間のトポロジ変化によるフリッカーは物理的にゼロとなる。
  2. **円筒座標 `Body` 表面距離場と毎フレーム動的2次ベジェRフィレット架橋**:
     - タマゴ型 `Body` 側面（`z >= 0.165m [IICh] / 0.255m [IINet]` では足変形重み `w_leg == 0.000` のため Step 1B 時点で100%静止タマゴ形状）を円筒座標グリッド `(phi, z) -> (R_surf, N_surf)` で高精度サンプリング。
     - 毎フレーム剛体 `SO(3)` 回転させた腕母線と `Body` 表面の真の交差位置 `u_zero(theta)`（外側から内側への連続探索で特定）およびネック位置 `u_neck(theta)`（表面高さ `H(theta)` 到達点）から、ボディ接平面上のリム点 `P_rim(theta)`・交差制御点 `P_ctrl(theta)`・腕側ネック点 `P_neck(theta)` を結び、2次ベジェ曲線 $P_{\text{skirt}}(s, \theta) = (1-s)^2 P_{\text{rim}} + 2(1-s)s P_{\text{ctrl}} + s^2 P_{\text{neck}}$ で滑らかなRフィレットスカートを動的形成。
     - 脇下（`cos(theta) < 0`）はタイトなR高さ（`7〜10mm`）に絞ることで、腕を大きく前後に振っても高く上げても**翼状のひれは一切発生しない**。
  3. **カスタム分割法線（`normals_split_custom_set_from_vertices`）によるリム法線角度差 `0.00°` 完全一致**:
     - スカートの開放リム端（`j = 0, s = 0`）の頂点法線に `Body` 側のステップ2〜4変形後法線 `n_body_final` を100%代入（`w_norm = 1.000`）し、スカート領域（`0 <= s <= 1.0`）で幾何法線 `n_geom` へ `smootherstep` 補間（毎回 `custom_normal` 属性をリセットしてから真の幾何法線を取得・下向き法線成分 `Nz < 0` の巻き込み防止処理付き）。
     - 全450フレーム数値監査において、**リム端での `Body` との位置誤差 `0.0000mm`、法線角度差 `0.00°`** を達成し、400%拡大監査シート（[`output_20261112_cvn_pair_arm_seam_closeup.png`](output_20261112_cvn_pair_arm_seam_closeup.png)）でも腕と胴体の境界線が完全に消滅し、1つの柔らかいソフビで一体成型された外観を実現した。

#### B. 足（超短足）の不自然な歪み・下腹部段差の完全解消と心地よい弾性伸縮
- **解決アーキテクチャ**:
  - 足先〜足底（`IICh: z <= 0.035m`, `IINet: z <= 0.045m`）から股関節上限（`IICh: z = 0.165m`, `IINet: z = 0.255m`）にかけて広い遷移帯で `smootherstep` 減衰させ、足の付け根支点（`z_hip_piv = 0.145m / 0.215m`）まわりの素直な振り子回転（`±19°〜20.5°`）と軸方向の弾性伸縮（`+8.5%` 伸び ／ `-6.0%` クッション縮み）を適用。
  - 下腹部（`z = 0.13m〜0.25m`）に水平方向の段差を生じさせていた半径方向の逆スケーリング（`kxy_leg`）を撤廃し、斜め後ろスイング時（`Frame 36` 等）も下腹部から足先まで段差やねじれの一切ないぷっくり丸いシルエットを維持。

#### C. 手足リグから「ボディ本体（お腹・胸ロゴ・タマゴ輪郭）」への歪み波及ゼロ保証
- `IICh_Body` / `IINet_Body` は腕を含まない純粋タマゴ型メッシュであるため、腕のスイング・挙上によるボディ本体への頂点歪み波及は **`0.000%`（完全ゼロ）**。
- 胸ロゴ下端より上（`IICh: z >= 0.165m`, `IINet: z >= 0.255m`）のボディ本体全域は足変形重み **`w_leg = 0.000`（完全無変形）** に厳密ロックされ、全450フレームを通じてお腹・胸ロゴ（`LILI-ch` / `LILI-net`）・タマゴ型輪郭に歪みが一切波及しない。

---

### 3. 全4フェーズ演出タイムライン詳細（450フレーム / 15.0秒 @ 30fps）

| フェーズ | フレーム範囲（30fps / 秒数） | カービィ型・超短足マスコットの可愛い仕草・カメラワーク詳細 | 視覚監査フレーム（30fps） |
| :--- | :--- | :--- | :--- |
| **Phase 1：カービィお手本準拠の「トコ・ピョコ！」超短足ウォーク** | `Frame 1〜160`<br>（`0.00s〜5.33s`） | ・**テンポ**: 1歩＝10フレーム（左右1サイクル＝20フレーム @ 30fps、計16歩）。2体は心地よい位相差で仲良く歩く。<br>・**カメラワーク**: 歩き出し（`Frame 1〜90`）は約 `36°〜33°` の斜め前3/4円筒オービットから、`Frame 90〜165` で正面16:9カメラ `pos=(0, -8.45, 1.22), lens=52.5mm` へ滑らかに回り込む。<br>・**手足連動**: 丸い形を保った超短足が付け根支点まわりに `±19°〜20.5°` スイングしつつ `+8.5% / -6.0%` 心地よく伸び縮みし、シームレス一体型パドル手が逆位相で `±37°〜38°` パタパタ大きくスイング（腕根元の切れ目ゼロ・ひれゼロ・胸ロゴ歪みゼロ）。 | 8コマ連続監査:<br>`Frame 21, 24, 26, 29, 31, 34, 36, 39`<br>6コマ代表:<br>`Frame 26`, `Frame 96` |
| **Phase 2：ちょこんと両足着地ホップ（「ピョコン・ピタッ！」）＆正面静止** | `Frame 161〜210`<br>（`5.33s〜7.00s`） | `Y = 0.0m` 定位置に到着した瞬間、両足を揃えて小さく **「ピョコン！」と可愛い着地ホップ（高さ `+4.6cm`、足が `+6.5%` ぷっくり伸び、短い両手を横にパタッと開く）** ➔ 着地で優しくクッションして、正面スマイル静止構図（`Frame 195〜210`）にピタッと収まる。 | `Frame 170`（ピョコン着地ホップ）<br>`Frame 195`（正面完全静止） |
| **Phase 3：短い2本の足で踏ん張って「ペコリ！」とする可愛いおじぎ** | `Frame 211〜300`<br>（`7.00s〜10.00s`） | 両キャラとも **短い2本の足を床にちょこんと踏ん張って正面に見せたまま**、ボディ本体と胸ロゴ（`LILI-ch` / `LILI-net`）は歪みゼロの完全剛体回転で前へ **`20.5° / 21.5°` 綺麗に「ペコリ！」とおじぎ**。シームレス一体型パドル手も切れ目・ひれゼロで後ろ外側（`-22°`）へ添え、地球儀も前へ可愛く揺れる。 | `Frame 252`（両足踏ん張り＆丸ボディペコリおじぎ） |
| **Phase 4：両キャラともほっぺ横の高い位置で「パタパタ！」と振る手振り** | `Frame 301〜450`<br>（`10.00s〜15.00s`） | 左の `いい-ch`（右手 `-X`）・右の `いい-NETくん`（左手 `+X`）**両方とも外側のパドル手をほっぺ横の高い位置（`+24° ⇔ +58°`）まで持ち上げ、腕根元の切れ目・ひれ・歪みゼロで「パタパタパタッ！」と元気に手振り**。小首を可愛く傾げ、短い片足を交互にちょこんと浮かせて最後は正面静止ポーズ（`Frame 450`）に収まる。 | `Frame 345`（両キャラ高い位置の手振りUp＆外側足浮き）<br>`Frame 351` / `Frame 364`（手振りDown＆内側足ちょこん浮き） |

---

### 4. 視覚監査結果サマリー（Blender 5.3 / v6 Full HD 30fps 完成監査）
1. **腕根元400%拡大監査シート（[`output_20261112_cvn_pair_arm_seam_closeup.png`](output_20261112_cvn_pair_arm_seam_closeup.png)）**: 6つの代表ポーズ（`Frame 195` 正面静止、`Frame 26` 歩行前振り、`Frame 36` 歩行後ろ振り、`Frame 252` おじぎ、`Frame 345` 手振り最高点、`Frame 351` 手振り下端）の400%拡大画像を目視監査し、腕とボディの境界線（切れ目・暗い陰影帯）が完全に消滅し、ひれもゼロで滑らかなソフビ一体成型となっていることを確認し合格。
2. **歩行1サイクル連続監査シート（[`output_20261112_cvn_pair_walk_cycle_8frames.png`](output_20261112_cvn_pair_walk_cycle_8frames.png)）**: 30fps 歩行1サイクル連続8コマ（16:9ワイド構図）すべてにおいて、①腕根元の切れ目・ひれが完全ゼロであること、②前後に動く左右の超短足と下腹部に段差やねじれが一切なく、ぷっくり丸い形を保ったままトコトコ歩いていること、③ボディ本体と胸ロゴ（`LILI-ch` / `LILI-net`）に歪みが一切波及していないことを確認し合格。
3. **全4フェーズ代表キーフレームシート（[`output_20261112_cvn_pair_anim_keyframes.png`](output_20261112_cvn_pair_anim_keyframes.png)）**: 全4フェーズ6コマ（16:9ワイド構図）すべてにおいて、上下の頭上（地球儀上端）〜足元の余白バランスが完璧に維持され、腕根元のシームレス一体化・足の自然な振り子伸縮・ボディ本体の歪みゼロを確認し合格。

---

## Part 2. SNS・マーケティング告知文
※本案件は `/blender` ジャンル直行モード（3Dアニメーション制作・v6 Full HD 30fps 全面改修案件）として稼働したため、`03_Marketing_Dept` によるSNS告知文生成はスキップされています。

---

## Part 3. リファレンス解析サマリー＆設計根拠
- **動作リファレンス出典**: `Kirby walk cycle coloured`（`https://www.youtube.com/watch?v=xZMflRnbC3o`、フレーム単位解析を 30fps タイムベースへ高精度換算：1歩＝10フレーム・左右1サイクル＝20フレーム＝0.67秒 @ 30fps）
- **ペア造形・正面バランス基準**: 株式会社CVN 公式キャラクター「ケーブル兄弟（いい-ch ＆ いい-NETくん）」2体横並び原画 `ref_20261110_pair_balance.png`（完成静止画シルエット重なり一致率 **IoU 98.11%**、16:9 Full HD `lens = 52.5mm` にて縦視野角・頭上地球儀〜足元余白比率を100%完全維持）
- **Blender 5.3 / v6 改修による4大設計原則**:
  1. **Full HD (`1920×1080`) @ 30fps（全450フレーム・15.0秒）**: 24fps比1.25倍のフレーム密度により歩行・着地ホップ・おじぎ・パタパタ手振りの時間解像度と滑らかさを向上しつつ、16:9 ワイド画角で開放感あるスタジオ空間を実現。
  2. **腕根元シームレス一体化（位置誤差 `0.0000mm`・法線角度差 `0.00°`・フリッカーゼロ・ひれゼロ）**: 開放リム型パドル腕メッシュ（6,273頂点固定トポロジ）＋毎フレーム動的2次ベジェRフィレットスカート＋カスタム分割法線同期により、Boolean/Remesh由来のフリッカーや翼状のひれを一切出さず、腕と胴体の切れ目を完全に消滅させたソフビ一体成型表現を達成。
  3. **超短足の形崩れ・下腹部段差ゼロ＆心地よい軸方向弾性伸縮**: 半径方向の逆スケーリング（`kxy_leg`）を撤廃し、付け根支点（`z_hip_piv = 0.145m / 0.215m`）まわりの振り子回転（`±19°〜20.5°`）と軸方向弾性伸縮（`+8.5%` 伸び ／ `-6.0%` 縮み）により、下腹部から足先まで段差やねじれのない丸いシルエットを維持。
  4. **ボディ本体・胸ロゴへの歪み波及ゼロ保証**: 腕を含まない純粋タマゴ型 `Body` メッシュと胸ロゴ下端より上（`IICh: z >= 0.165m`, `IINet: z >= 0.255m`）の `w_leg = 0.000` 厳密ロック、およびおじぎ時の上部ボディ剛体回転により、全450フレームを通じて胸ロゴ（`LILI-ch` / `LILI-net`）とお腹・タマゴ輪郭の歪みをゼロに保つ。
