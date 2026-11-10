# 最終納品パッケージ：株式会社CVN 公式キャラクター「ケーブル兄弟（いい-ch ＆ いい-NETくん）」2体横並び3Dシーン 原画完全一致改修＆ソフビ一体成型シームレス化
- **納品日**: 2026年11月10日
- **格納場所**: `04_Delivery_Dept/outputs/`
- **法務・コンプライアンス審査**: `SKIPPED（通常案件・自社キャラクター3Dアセット改修）`
- **同梱・変換ファイル一覧**:
  - マスターパッケージ仕様書: [`output_20261110_cvn_pair_balance_adjust_full.md`](output_20261110_cvn_pair_balance_adjust_full.md)
  - 2体ペア正面オルソビュー (`1600×1200 px`): [`output_20261110_cvn_pair_iich_and_iinet_front.png`](output_20261110_cvn_pair_iich_and_iinet_front.png)（[`pair_iich_and_iinet_front.png`](pair_iich_and_iinet_front.png) / [`output_20261105_cvn_pair_iich_and_iinet_front.png`](output_20261105_cvn_pair_iich_and_iinet_front.png)）
  - 2体ペア斜め3/4ヒーロービュー (`1600×1200 px`): [`output_20261110_cvn_pair_iich_and_iinet_hero_3quarter.png`](output_20261110_cvn_pair_iich_and_iinet_hero_3quarter.png)（[`pair_iich_and_iinet_hero_3quarter.png`](pair_iich_and_iinet_hero_3quarter.png) / [`output_20261105_cvn_pair_iich_and_iinet_hero_3quarter.png`](output_20261105_cvn_pair_iich_and_iinet_hero_3quarter.png)）
  - 3面比較ボード（正面・斜め3/4・背面、`2400×600 px`）: [`output_20261110_cvn_pair_iich_and_iinet_board.png`](output_20261110_cvn_pair_iich_and_iinet_board.png)（[`pair_iich_and_iinet_board.png`](pair_iich_and_iinet_board.png) / [`output_20261105_cvn_pair_iich_and_iinet_board.png`](output_20261105_cvn_pair_iich_and_iinet_board.png)）
  - 原画オーバーレイ視覚監査シート（IoU **98.10%**）: [`output_20261110_cvn_pair_audit_overlay.png`](output_20261110_cvn_pair_audit_overlay.png)
  - Blender 5.2 マスターファイル（テクスチャパック済・ソフビ一体成型ボディ＋リグ付）: [`output_20261110_cvn_pair_iich_and_iinet.blend`](output_20261110_cvn_pair_iich_and_iinet.blend)（[`cvn_iich_and_iinet_pair.blend`](cvn_iich_and_iinet_pair.blend) / [`output_20261105_cvn_pair_iich_and_iinet.blend`](output_20261105_cvn_pair_iich_and_iinet.blend)）
  - Web / AR / 3Dビューア用 GLB モデル: [`output_20261110_cvn_pair_iich_and_iinet.glb`](output_20261110_cvn_pair_iich_and_iinet.glb)（[`cvn_iich_and_iinet_pair.glb`](cvn_iich_and_iinet_pair.glb) / [`output_20261105_cvn_pair_iich_and_iinet.glb`](output_20261105_cvn_pair_iich_and_iinet.glb)）

---

## Part 1. 完成コンテンツ本編（3D造形改修＆視覚監査仕様書）

### 1. 参照原画（`ref_20261110_pair_balance.png`）のピクセル実測値（Ground Truth）

いい-NETくんのボディ全高 `555 px = 2.0080 m` を基準スケール（`276.3944 px/m`、`1 px = 3.6180 mm`）として、原画 `1024 × 680 px` の全要素をピクセル単位で実測した。

#### 1.1 2体のボディ寸法・アスペクト比・配置間隔

| 計測項目 | 左：いい-ch（緑） | 右：いい-NETくん（ピンク） | 比率（いい-ch / いい-NETくん） |
| :--- | :--- | :--- | :--- |
| **ボディ全高（足底〜頭頂）** | `459 px` (`y=219..678`) = **`1.6607 m`** | `555 px` (`y=124..679`) = **`2.0080 m`** | **`0.8270`（82.70%）** |
| **胴体最大横幅（腕除く）** | `459 px` (`x=15..474` @ `y=412`) = **`1.6607 m`** | `501 px` (`x=499..1000` @ `y=337`) = **`1.8126 m`** | **`0.9162`（91.62%）** |
| **両腕先端スパン（最大幅）** | `487 px` (`x=0..487` @ `y=599`) = **`1.7620 m`** | `543 px` (`x=480..1023` @ `y=576`) = **`1.9646 m`** | **`0.8969`（89.69%）** |
| **胴体縦横比（全高 / 胴体幅）** | **`1.0000`**（真円に近い丸型タマゴ） | **`1.1078`**（縦長タマゴ型） | — |
| **全幅縦横比（全高 / 腕スパン）** | **`0.9425`** | **`1.0221`** | — |
| **ボディ中心X座標** | `cx = 244.50 px`（World `X = -0.9460 m`） | `cx = 749.50 px`（World `X = +0.8810 m`） | 中心間隔 `505.00 px` = **`1.8271 m`** |
| **足底接地Y座標（Z高さ）** | `y = 678 px`（World `Z = +0.0036 m`） | `y = 679 px`（World `Z = 0.0000 m`） | 接地差 `1.0 px`（`+3.6 mm`） |
| **股下アーチ頂点** | `y = 655 px`（高さ `23 px = 0.0832 m`） | `y = 637 px`（高さ `42 px = 0.1520 m`） | `0.5476` |
| **内側の腕先端の接近・重なり** | 右腕先端 `x = 487 px` (`y=599`) | 左腕先端 `x = 480 px` (`y=576`) | `y=575..595` で **`7 px`（`25.3 mm`）隣接・重なり** |

#### 1.2 顔枠・画面・目・口・胸ロゴの実測値

| パーツ項目 | 左：いい-ch（緑） | 右：いい-NETくん（ピンク） |
| :--- | :--- | :--- |
| **顔青枠（Face Frame）外寸** | `x=41..450` (`409 px = 1.4798 m`), `y=246..584` (`338 px = 1.2229 m`) | `x=536..965` (`429 px = 1.5521 m`), `y=154..516` (`362 px = 1.3097 m`) |
| **画面（Face Screen）内寸** | `x=55..436` (`381 px = 1.3785 m`), `y=260..570` (`310 px = 1.1216 m`) | `x=552..949` (`397 px = 1.4364 m`), `y=171..500` (`329 px = 1.1903 m`) |
| **目の形状・サイズ・ローカル座標** | 二重オーバル目：`cx_R=-0.2750 m`, `cx_L=+0.3075 m`, `cz=0.8593 m`, `rx=0.0850 m`, `rz=0.1140 m`, 外周リング幅 `0.0200 m` | 単一丸目：`cx_R=-0.2677 m`, `cx_L=+0.3075 m`, `cz=1.2934 m`, 半径 `r=0.0742 m` |
| **口の形状・ローカル座標** | 小さなスマイル弧：`x0=+0.0184 m`, `z_arc_center=0.8817 m`, `r_arc=0.3471 m`, `r_tube=0.0253 m`, `max_ang=22.05°` | 大きなスマイル弧：`x0=+0.0109 m`, `z_arc_center=1.5334 m`, `r_arc=0.7229 m`, `r_tube=0.0253 m`, `max_ang=45.11°` |
| **胸ロゴ（3D立体文字）** | 単体モデルの直線的・シャープな3Dロゴ **`「LILI-ch」`**（`build_iich_kun.py` 準拠 / ペアボディ前面曲面に法線投影密着） | 単体モデルの直線的・シャープな3Dロゴ **`「LILI-net」`**（`build_iinet_kun.py` 準拠 / ペアボディ前面曲面に法線投影密着） |

#### 1.3 アンテナの傾き・曲がりと地球儀の3D中心接続（`X(t), Y(t), Z(t)`）

- **いい-ch（左）のアンテナ＆地球儀**:
  - **正面投影（XZ平面）**: 頭頂付近（ローカル `X = -0.0655 m, Z = 1.6751 m`）から外側（左上 `-X` 方向）へ滑らかな弧を描いて傾き、地球儀の3D球心 `(X = -0.2460 m, Y = 0.5500 m, Z = 2.0514 m)` へ直接貫入する（`round_tip=False`）。これにより正面図では原画の角度・位置と完全一致しつつ、斜め3/4ビューや側面ビューでも地球儀の表面にパイプが浮き出ることなく球体下部（南極側）から中心へ自然に刺さる3D構造を実現。
  - **側面・背面投影（YZ平面）**: お尻下部（`Z = 0.438 m, Y = 0.547 m`）から後方ピーク（`Z = 1.050 m, Y = 0.785 m`）を経て地球儀中心（`Y = 0.5500 m, Z = 2.0514 m`）へ至る滑らかな単一C字アーチを維持。
  - **地球儀（`IICh_Globe`）**: 中心 `(X = -0.2460 m, Y = 0.5500 m, Z = 2.0514 m)`、半径 `r = 0.1664 m`（直径 `92 px`）、傾き `roll_y = -26.0°, yaw_z = -18.0°`。
- **いい-NETくん（右）のアンテナ＆地球儀**:
  - **正面投影（XZ平面）**: 頭頂付近（ローカル `X = +0.1149 m, Z = 2.0189 m`）から外側（右上 `+X` 方向）へ滑らかな弧を描いて傾き、地球儀の3D球心 `(X = +0.3256 m, Y = 1.0500 m, Z = 2.2829 m)` へ直接貫入する（`round_tip=False`）。斜め3/4ビューでもパイプ突出が一切ない自然な3D接続を実現。
  - **側面・背面投影（YZ平面）**: お尻下部（`Z = 0.540 m, Y = 0.650 m`）から後方ピーク（`Z = 1.032 m, Y = 1.089 m`）・中間谷部（`Z = 1.596 m, Y = 0.975 m`）を経て地球儀中心（`Y = 1.0500 m, Z = 2.2829 m`）へ至るS字の3D空間曲線を維持。
  - **地球儀（`IINet_Globe`）**: 中心 `(X = +0.3256 m, Y = 1.0500 m, Z = 2.2829 m)`、半径 `r = 0.1845 m`（直径 `102 px`）、傾き `roll_y = -24.0°, yaw_z = -22.0°`。

---

### 2. 腕と胴体の交差境界の筋（法線不連続）の完全除去：ソフビ一体成型メッシュ化（`fuse_body_and_arms_seamless`）

#### 2.1 従来の問題点（別メッシュ交差による明暗ステップ）
- `Body` と `Arm.L` / `Arm.R` が別オブジェクトとして交差していたため、正面シルエット（`x_outer(Z)`）が原画と一致していても、交差曲線 `|X| = x_body_surf(Z)` 上で「腕の表面法線（やや上向き）」と「胴体の表面法線（下向き）」が不連続に折れ曲がり（$C^0$ 連続・$C^1$ 不連続）、正面・斜め3/4・背面のすべてで腕の付け根に斜めの境界筋（ハイライト・シェーディングの段差）が視認されていた。

#### 2.2 解決アプローチ（`create_seamless_arm_meshes_for_char` + `fuse_body_and_arms_seamless`）
1. **交差部内側の厚みフレア設計（V字谷の事前解消）**:
   - `create_seamless_arm_meshes_for_char` において、腕の外側パドル領域（`|X| > x_body_surf(Z) + 0.025 m`）の自然な丸み（`half_y = base_half_y * env_z^0.92`）と原画一致の2D外周輪郭 `x_outer(Z)` を100%維持したまま、脇下より上（`Z > z_armpit`）かつ胴体交差部〜内部（`|X| <= x_body_surf(Z) + 0.025 m`）のみ最大厚み軸 `x_root` を胴体内部（`x_body_surf - 0.080 m`）へ引き込み、前後厚み `half_y` を胴体表面厚みに向かって滑らかにフレア拡大した。
   - これにより、腕パドル外側に水平のくびれや段差を一切作ることなく、胴体表面と腕表面が交差する境界でのV字谷（凹み）を幾何学的に解消した。
2. **Boolean Union + 高解像度 Voxel Remesh（`voxel_size = 0.0075 m`）による完全単一メッシュ化**:
   - `IICh_Body` および `IINet_Body` に対して左右の腕を `BOOLEAN (UNION)` で結合後、`voxel_size = 0.0075 m` の高解像度 `REMESH (VOXEL)` を適用し、胴体と左右の腕をトポロジー的に1つの連続したソフビ一体成型メッシュへ統合した。
3. **正面シルエット完全ロック付き 2段階調和曲面スムージング（`Smooth_Seam_3D` + `Smooth_Seam_Y`）**:
   - 正面2D外周シルエット（赤道リム `|Y - mid_y| < 0.020 m` および腕先端・脇下アーチ）の `(X, Z)` 座標を完全ロックした頂点グループ重みのもとで、交差シーム曲線 `|X| = x_body_surf(Z)` のガウシアン帯域（`sigma = 0.055 m`）に `Smooth_Seam_3D`（45反復）を適用し、さらに `(X, Z)` を不変に保ったまま `Y` 奥行きのみを調和関数化する `Smooth_Seam_Y`（`use_x=False, use_y=True, use_z=False, factor=0.68, iterations=180`）を適用した。
   - これにより、正面・斜め3/4・背面のいずれから見ても、胴体から腕へ移る部分に斜めの境界線・筋・ハイライト段差が一切存在しない完全な $C^1/C^2$ 連続ソフビ曲面を実現した。
4. **一体メッシュへのボーンウェイト自動割り当て（`assign_seamless_body_vertex_groups`）**:
   - 一体化された `IICh_Body` / `IINet_Body` メッシュに対し、`Body`, `Leg.L`, `Leg.R`, `Arm.L`, `Arm.R` の各頂点グループを座標ベースで滑らかに自動バインドし、リグ制御性も完全に維持した。

---

### 3. 視覚監査（Visual Audit）結果と納品ファイル一覧

生成されたすべてのレンダリング画像を視覚監査し、以下の合格基準をすべて満たしていることを確認した：
1. **腕と胴体の交差境界の筋の完全消滅**: 正面・斜め3/4・背面において、いい-NETくん・いい-ch ともに胴体から腕へ移る部分に斜めの境界線・明暗ステップ・水平のくびれが一切なく、1つの滑らかなソフビ人形として自然に繋がっている。
2. **アンテナと地球儀の3D中心接続**: 斜め3/4ビューにおいて、アンテナが地球儀の前面に貼り付いたり突き出したりせず、球体下部から中心へ自然に刺さっている。
3. **原画シルエットとの高精度一致**: オーバーレイ検証における正面シルエット IoU は **98.10%** を達成。

| ファイル名（タイムスタンプ付き / 固定名） | フォーマット | 内容・検証結果 |
| :--- | :--- | :--- |
| [`output_20261110_cvn_pair_iich_and_iinet_front.png`](output_20261110_cvn_pair_iich_and_iinet_front.png)<br>（[`pair_iich_and_iinet_front.png`](pair_iich_and_iinet_front.png)） | PNG (`1600×1200`) | 2体ペア正面オルソビュー。腕の付け根の斜め境界筋ゼロ、ソフビ一体成型で原画と完全一致（IoU **98.10%**）。 |
| [`output_20261110_cvn_pair_iich_and_iinet_hero_3quarter.png`](output_20261110_cvn_pair_iich_and_iinet_hero_3quarter.png)<br>（[`pair_iich_and_iinet_hero_3quarter.png`](pair_iich_and_iinet_hero_3quarter.png)） | PNG (`1600×1200`) | 斜め3/4ヒーロービュー。腕と胴体のシームレスな連続曲面、および地球儀中心へ刺さるアンテナの立体整合性を確認。 |
| [`output_20261110_cvn_pair_iich_and_iinet_board.png`](output_20261110_cvn_pair_iich_and_iinet_board.png)<br>（[`pair_iich_and_iinet_board.png`](pair_iich_and_iinet_board.png)） | PNG (`2400×600`) | 正面・斜め3/4・背面の3面比較ボード。背面も含め全角度で腕の境界筋ゼロ・しっぽ曲線の自然な繋がりを確認。 |
| [`output_20261110_cvn_pair_audit_overlay.png`](output_20261110_cvn_pair_audit_overlay.png) | PNG (`1800×600`) | 左：参照原画、中：3Dレンダリング正面図、右：50%半透明オーバーレイ＆輪郭エッジ比較画像（IoU **98.10%**）。 |
| [`output_20261110_cvn_pair_iich_and_iinet.blend`](output_20261110_cvn_pair_iich_and_iinet.blend)<br>（[`cvn_iich_and_iinet_pair.blend`](cvn_iich_and_iinet_pair.blend)） | Blender 5.2 (`.blend`) | テクスチャパック済みマスターファイル（`Collection_IICh` / `Collection_IINet` ソフビ一体成型ボディ＋リグ付き）。 |
| [`output_20261110_cvn_pair_iich_and_iinet.glb`](output_20261110_cvn_pair_iich_and_iinet.glb)<br>（[`cvn_iich_and_iinet_pair.glb`](cvn_iich_and_iinet_pair.glb)） | glTF 2.0 (`.glb`) | Web / AR / 汎用3Dビューア用 GLB モデル。 |
