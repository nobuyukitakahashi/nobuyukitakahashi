# 最終納品パッケージ：株式会社CVN 公式キャラクター「ケーブル兄弟（いい-ch ＆ いい-NETくん）」2体ペア3Dアニメーション動画（15.0秒 / 全360フレーム @ 24fps：全身3Dラバー弾性変形仕様 — ゴム弾性ウォーク ➔ 正面静止 ➔ 顔の下からクニュッと折れ曲がる深いおじぎ ➔ ビヨーンと伸びて大きく振る手振り）
- **納品日**: 2026年11月10日
- **格納場所**: `04_Delivery_Dept/outputs/`
- **法務・コンプライアンス審査**: `SKIPPED（通常案件・自社公式マスコット3Dアニメーション制作）`
- **同梱・変換ファイル一覧**:
  - マスターパッケージ仕様書: [`output_20261110_cvn_pair_animation_full.md`](output_20261110_cvn_pair_animation_full.md)
  - 15.0秒 3Dアニメーション動画（360フレーム @ 24fps, `1280×960 px`, H.264 MP4）: [`output_20261110_cvn_pair_run_bow_wave.mp4`](output_20261110_cvn_pair_run_bow_wave.mp4)（[`pair_iich_and_iinet_run_bow_wave.mp4`](pair_iich_and_iinet_run_bow_wave.mp4)）
  - 6フェーズ代表キーフレーム一覧ボード（`1920×960 px`）: [`output_20261110_cvn_pair_anim_keyframes.png`](output_20261110_cvn_pair_anim_keyframes.png)（[`pair_iich_and_iinet_anim_keyframes.png`](pair_iich_and_iinet_anim_keyframes.png)）
  - Blender 5.2 アニメーションプロジェクトファイル（全360fラバー変形・微細グレイン質感・ソフビ一体成型ボディ付）: [`output_20261110_cvn_pair_anim.blend`](output_20261110_cvn_pair_anim.blend)（[`cvn_iich_and_iinet_pair_anim.blend`](cvn_iich_and_iinet_pair_anim.blend)）

---

## Part 1. 完成コンテンツ本編（3Dアニメーション制作仕様・品質監査レポート：全身3Dラバー弾性変形仕様）

### 1. 概要・制作スペック
- **動画ファイル**: [`output_20261110_cvn_pair_run_bow_wave.mp4`](output_20261110_cvn_pair_run_bow_wave.mp4)（[`pair_iich_and_iinet_run_bow_wave.mp4`](pair_iich_and_iinet_run_bow_wave.mp4)）
- **キーフレーム一覧ボード**: [`output_20261110_cvn_pair_anim_keyframes.png`](output_20261110_cvn_pair_anim_keyframes.png)（[`pair_iich_and_iinet_anim_keyframes.png`](pair_iich_and_iinet_anim_keyframes.png)）
- **Blender 5.2 アニメーションプロジェクト**: [`output_20261110_cvn_pair_anim.blend`](output_20261110_cvn_pair_anim.blend)（[`cvn_iich_and_iinet_pair_anim.blend`](cvn_iich_and_iinet_pair_anim.blend)）
- **映像フォーマット**:
  - **尺・フレーム数**: **15.0秒（全360フレーム @ 24fps）**
  - **解像度**: `1280 × 960`（4:3 フル高精細）
  - **コーデック**: MPEG-4 / H.264（CRF: HIGH）
  - **レンダーエンジン**: Blender 5.2 Cycles GPU（OpenImageDenoise）

---

### 2. オーナーフィードバック反映：全身3Dラバー（ゴム弾性）変形エンジンの実装

単なる剛体ボーン回転では正面カメラから丸いボディの立体的な動きが伝わりにくいという課題を解決するため、キャラクター全メッシュ（`Body`, `Face_Screen`, `Face_Frame`, `Eye.L`, `Eye.R`, `Mouth`, `Logo_LILI_*`, `Antenna`, `Globe`）に対して連続的な **3Dラバー（ゴム弾性）空間ワープ＆直交Frenet腕伸縮エンジン** を構築・適用しました。

| フェーズ | フレーム範囲（秒数） | 3Dラバー（ゴム弾性）演出・アクション詳細 | 代表監査フレーム |
| :--- | :--- | :--- | :--- |
| **Phase 1：間（ま）をおいた、ぴょこぴょこ左右傾き歩き＋ゴム弾性の足元** | `Frame 1〜132`<br>（`0.0秒〜5.5秒`） | 細かすぎる小走りではなく、**1歩＝14フレーム（左右1サイクル＝28フレーム、5.5秒間で約9.4歩）** の間（ま）をおいたテンポで奥（`Y = +11.5m`）から手前（`Y = 0.0m`）へ歩いてくる。<br>・**着地タメ（前半38%）**: 体重が乗った側のゴムの足元が床に押し付けられて縦に `-24%` ムニュッと潰れ（接地スクワッシュ）、一拍の間（ま）をつくる。<br>・**ぴょこっ！ホップ（後半62%）**: 床を蹴る足がゴムのように `+28%` ビヨッと伸び（ストレッチ）、胴体全体を左右へ **`±11.8°`** 大きく傾けながらぴょこぴょこ歩いてくる。 | `Frame 25`（遠景ラバーウォーク）<br>`Frame 89`（中景ラバーウォーク） |
| **Phase 2：ゴム弾性着地＆正面静止構図** | `Frame 133〜168`<br>（`5.5秒〜7.0秒`） | 定位置（`Y = 0.0m`）に到着して「ぴょこん ➔ ムニュッ（着地スクワッシュ）➔ ポヨン（弾性復帰）」とゴムの弾力で収まり（`Frame 133〜154`）、完成静止画と完全一致する正面構図でピタッと静止する（`Frame 155〜168`）。 | `Frame 156`（正面静止） |
| **Phase 3：顔から下がゴムのようにクニュッと内側にへこんで折れ曲がる深いおじぎ** | `Frame 169〜240`<br>（`7.0秒〜10.0秒`） | 中空の柔らかいゴム人形のお腹が押されたように、**顔枠の下〜股上の腹部エリアが内側（`+Y` 奥方向へ `+0.20〜0.23m`、左右幅 `-26%`）へクニュッと深くへこんで内側に折れ曲がり**、顔・頭部全体が手前下方向へ **`37° / 35°`** 深く前傾しておじぎする。<br>・正面から見ても顔が大きく下へ沈み込み、頭頂部の丸いグリーン／ピンクの頭と前傾した地球儀が正面に大きく現れる。<br>・全メッシュに同一の連続3D空間ワープを適用しているため、顔枠や胸ロゴ（`LILI-ch` / `LILI-net`）の浮き・剥がれはゼロ。 | `Frame 202`（深いゴム折りおじぎ） |
| **Phase 4：丸みを保ったままゴムのようにビヨーンと伸びて大きく振る手振り** | `Frame 241〜360`<br>（`10.0秒〜15.0秒`） | 直交Frenet座標系（腕軸方向 `ell` × 断面厚み方向 `tau`）によるゴム腕伸縮変形により、**先端のぷっくり丸いパドル形状を100%保ったまま腕が通常の約1.75〜1.85倍にビヨーンと伸び**、斜め上の高い位置（`Frame 276`）から横ワイドな位置（`Frame 300`）まで大きなストローク（周期16フレーム）で元気よくブンブン手を振る。<br>・手振りに合わせてゴムの胴体と足元も上下にビヨーン・ムニュッと弾み、最後の約1秒（`Frame 336〜360`）で元の長さと正面静止構図へ滑らかに収まる。 | `Frame 276`（高位置バンザイ手振り）<br>`Frame 300`（ワイド振り下ろし） |
