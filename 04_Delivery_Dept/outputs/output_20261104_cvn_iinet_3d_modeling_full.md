# 最終納品パッケージ：株式会社CVN 公式キャラクター「いい-NETくん（LILI-net）」3Dモデリング＆レンダリング制作（Rev.3 改修完了版）

- **納品日**: 2026年11月05日（Rev.3 改修版）
- **格納場所**: `04_Delivery_Dept/outputs/`
- **法務・コンプライアンス審査**: `SKIPPED（通常案件・自社公式キャラクター3D制作）`
- **同梱・変換ファイル一覧**:
  - **マスターパッケージ（本書・Rev.3）**: [`output_20261104_cvn_iinet_3d_modeling_full.md`](output_20261104_cvn_iinet_3d_modeling_full.md)
  - **斜め3/4 ヒーローレンダリング（1400×1680 px・Cycles 3DCGマット質感・Rev.3）**: [`output_20261104_cvn_iinet_hero_3quarter.png`](output_20261104_cvn_iinet_hero_3quarter.png)（別名コピー: [`iinet_kun_hero_3quarter.png`](iinet_kun_hero_3quarter.png)）
  - **正面・側面・斜め・背面 4面比較ボード（3320×1008 px・Rev.3）**: [`output_20261104_cvn_iinet_front_and_side.png`](output_20261104_cvn_iinet_front_and_side.png)（別名コピー: [`iinet_kun_front_and_side.png`](iinet_kun_front_and_side.png)）
  - **全6アングル統合シート（5面図＋斜め / 2496×1992 px・Rev.3）**: [`output_20261104_cvn_iinet_5views_sheet.png`](output_20261104_cvn_iinet_5views_sheet.png)（別名コピー: [`iinet_kun_5views_sheet.png`](iinet_kun_5views_sheet.png)）
  - **Blender 5.2 マスターファイル（全11メッシュパーツ・リグ・3DCGマットマテリアル・Cyclesスタジオライト設定済・Rev.3）**: [`output_20261104_cvn_iinet_kun.blend`](output_20261104_cvn_iinet_kun.blend)
  - **Web / AR / 汎用3Dエンジン用 glTF 2.0 Binary（11パーツ＋アーマチュア同梱・Rev.3）**: [`output_20261104_cvn_iinet_kun.glb`](output_20261104_cvn_iinet_kun.glb)

---

## エグゼクティブサマリー（Rev.3 全5項目改修・Cycles 3DCGマット質感・ボーン構成・プレビュー）

### 1. レンダリング画像プレビュー一覧（Rev.3 改修完了版）

#### (1) 斜め3/4 ヒーローカット（広告チラシ・メインビジュアル用）
- ファイル: [`output_20261104_cvn_iinet_hero_3quarter.png`](output_20261104_cvn_iinet_hero_3quarter.png) / [`iinet_kun_hero_3quarter.png`](iinet_kun_hero_3quarter.png)
![斜め3/4 ヒーローカット（Rev.3）](output_20261104_cvn_iinet_hero_3quarter.png)

#### (2) 正面・左側面・斜め3/4・背面 4面比較ボード
- ファイル: [`output_20261104_cvn_iinet_front_and_side.png`](output_20261104_cvn_iinet_front_and_side.png) / [`iinet_kun_front_and_side.png`](iinet_kun_front_and_side.png)
![正面・側面・斜め・背面 4面比較ボード（Rev.3）](output_20261104_cvn_iinet_front_and_side.png)

#### (3) 全6アングル統合シート（正面・左側面・背面・上面・底面・斜め3/4）
- ファイル: [`output_20261104_cvn_iinet_5views_sheet.png`](output_20261104_cvn_iinet_5views_sheet.png) / [`iinet_kun_5views_sheet.png`](iinet_kun_5views_sheet.png)
![全6アングル統合シート（Rev.3）](output_20261104_cvn_iinet_5views_sheet.png)

---

### 2. Rev.3 ユーザー改修要件（全5項目）および累積改修仕様サマリー

| 項目 | Rev.3 改修要件・課題 | 3Dモデリング・マテリアル・レンダリングにおける実装仕様 |
| :--- | :--- | :--- |
| **① 足の形状（先端が丸く尖った両腕風の2本足造形）** | Rev.2の靴型／平底造形を廃止し、原画（`05_front.png`）の「先端が丸く尖っている」形状を維持したまま、両腕のようなパドル／ティアドロップ形状で足らしく延長する。 | 原画のシルエットおよび両腕（`Arm.L` / `Arm.R`）と同じく、**下に向かってぷっくり丸みを帯びながらすぼまり、先端が丸く尖った（ティアドロップ／パドル先端状）造形**を維持したまま、接地底面 $Z = -0.110\text{ m}$（股下アーチ頂点 $Z \approx +0.175\text{ m}$、左右中心 $X = \pm 0.258\text{ m}, Y = 0.0\text{ m}$）まで延長。胴体下部曲面へ $C^1$ 連続（段差・折れ目ゼロ）で接続しつつ、先端に向かって半径が $s^{0.50}(0.68 + 0.32s)$ でぷっくり丸く収束する解析的プロファイルを採用。 |
| **② 尻尾先端と地球儀の接続位置（地球儀の真下へ接続）** | 尻尾（`Antenna`）の先端が地球儀の横／後ろではなく、**地球儀の真下（南極点）** に繋がるようにする。 | 地球儀の中心を $(X, Y, Z) = (0.0, 1.190, 2.3725)\text{ m}$（半径 $R = 0.180\text{ m}$、南極点 $(0.0, 1.190, 2.1925)\text{ m}$）に配置。お尻内部 $(Y=0.350\text{ m}, Z=0.490\text{ m})$ から表面を貫通し、背中下部の最大後方突出点 $(Z=1.060\text{ m})$ ➔ 背中上部の谷部 $(Z=1.640\text{ m}, Y=0.975\text{ m})$ ➔ 地球儀真下の直前 $(Z=2.155\text{ m}, Y=1.190\text{ m})$ を2段階の解析的余弦曲線（$C^1/C^2$ 連続）で滑らかに繋ぎ、そこから **$+Z$ 方向（真上）へ垂直に立ち上がって地球儀の真下（南極中心 $Z=2.1925\text{ m}$）へ接続**。 |
| **③ 顔のTV青枠（`Face_Frame`）のスリム化＆全体サイズ微拡大** | 顔の青枠の太さをもっと細くし、青枠全体のサイズを少し大きくする。 | TV青枠および画面（`Face_Screen`）の外径スケールを Rev.2 の `0.84倍` から **`0.905倍`（顔中心 $Z_c = 1.2645\text{ m}$）へひと回り拡大**。同時に青枠の枠幅係数（`thickness_slim`）を Rev.2 の `0.74` から **`0.54`（従来の約半分強のシャープな細枠）** にスリム化し、法線方向へ $+0.038\text{ m}$ 立体隆起。胸元の3D立体ロゴ（`Logo_LILI_net`）も $Z$ 方向へ $-0.014\text{ m}$ 微調整して美しい余白を確保。 |
| **④ アニメ調を排した本格3DCGマット質感レンダリング（Cycles GPU）** | アニメ調（黒フチ線やフラットな発光塗り）をやめ、立体感のある3Dモデルらしいマット（つや消し）質感でレンダリングする。 | Freestyle（黒い輪郭線）を完全廃止（`use_freestyle = False`）し、全マテリアルの自己発光をゼロ化（`Emission Strength = 0.0`）。`Roughness = 0.94`, `Specular IOR Level = 0.08`, `Coat Weight = 0.0` の落ち着いたつや消しラバー／クレイフィギュア質感に統一。レンダリングエンジンを **Cycles GPU（OpenImageDenoise, 64 samples）** に切り替え、カメラ連動の4灯大型エリアライト＋`StudioWorld` 環境光により、全パーツの丸みと立体造形が柔らかな3D陰影で浮かび上がる本格3DCGレンダリングへ刷新。 |
| **⑤ 地球儀（`Globe`）の全周360度・世界大陸テクスチャ化** | 正面以外の角度（横・後ろ・上・下）から見ても地球儀だと一目でわかるように、全周に海と大陸を配置する。 | 経度 $-180^\circ \sim +180^\circ$・緯度 $-90^\circ \sim +90^\circ$ の全周360度にわたり世界の大陸・半島・島列（ユーラシア、日本列島、東南アジア、豪州、NZ、アフリカ、マダガスカル、欧州、スカンジナビア、英国、グリーンランド、北米、中米、カリブ諸島、南米、太平洋諸島）を配置した高解像度正距円筒図法マップ（`2048 × 1024 px`）を生成。UVシーム補正を実装し、全6アングルすべてでシームレスな「水色の海＋緑の大陸」を表現。 |
| **（Rev.2 継承）目・口の立体化＆胸元 `LILI-net` 3D立体メッシュ** | パッチリ大きな立体目・立体口、および胸元の `LILI-net` 3D立体文字メッシュ。 | 目（`Eye.L/R`）は半径 $0.080\text{ m}$・ドーム厚 $+0.035\text{ m}$、口（`Mouth`）は $+0.022\text{ m}$ 立体チューブ、胸元ロゴ（`Logo_LILI_net`）は12反復Taubin境界スムージング＋法線方向 $+0.023\text{ m}$ 立体押し出しメッシュとして造形。 |

---

### 3. アニメーション用アーマチュア（`IINet_Armature`）ボーン構成（全11メッシュパーツ対応）

```text
IINet_Armature
└── Root (0, 0, -0.105) -> (0, 0, 0.18)
    └── Body (0, 0, 0.18) -> (0, 0, 1.90)
        │   [追従メッシュ: Body, Face_Screen, Face_Frame, Eye.L, Eye.R, Mouth, Logo_LILI_net]
        ├── Leg.L (+0.275, 0.0, 0.18) -> (+0.258, 0.0, -0.105)  [先端が丸く尖った左足スイング制御]
        ├── Leg.R (-0.275, 0.0, 0.18) -> (-0.258, 0.0, -0.105)  [先端が丸く尖った右足スイング制御]
        ├── Arm.L (+0.72, 0.0, 0.68)  -> (+0.96, 0.0, 0.32)     [左アーム パタパタ・曲げ制御]
        ├── Arm.R (-0.72, 0.0, 0.68)  -> (-0.96, 0.0, 0.32)     [右アーム パタパタ・曲げ制御]
        └── Antenna_1 -> Antenna_2 -> Antenna_3 -> Globe        [お尻貫通〜地球儀真下接続S字尻尾＆地球儀制御]
```

---

## Part 1. 完成コンテンツ本編（3Dモデリング＆レンダリング制作仕様書 Rev.3）

- **制作年月**: 2026年11月
- **制作担当**: Creative部門（`02_Creative_Dept`）
- **使用環境**: Blender 5.2.3 LTS（Python API `bpy` / `bmesh` による完全プロシージャル構築・Cycles GPU レンダリング）

### 1. 成果物ファイル一覧

#### (1) 最終納品ファイル（`04_Delivery_Dept/outputs/` 格納済）
| 種別 | 納品ファイルパス | 仕様・解像度 |
| :--- | :--- | :--- |
| **Blenderマスターファイル** | [`04_Delivery_Dept/outputs/output_20261104_cvn_iinet_kun.blend`](output_20261104_cvn_iinet_kun.blend) | Blender 5.2形式（全11メッシュパーツ＋リグ＋3Dマットマテリアル＋Cyclesスタジオライト設定済） |
| **Web / AR用 3Dモデル** | [`04_Delivery_Dept/outputs/output_20261104_cvn_iinet_kun.glb`](output_20261104_cvn_iinet_kun.glb) | glTF 2.0 Binary形式（11パーツ＋アーマチュア同梱） |
| **斜め3/4 ヒーローレンダリング** | [`04_Delivery_Dept/outputs/output_20261104_cvn_iinet_hero_3quarter.png`](output_20261104_cvn_iinet_hero_3quarter.png)<br>（同内容コピー: [`iinet_kun_hero_3quarter.png`](iinet_kun_hero_3quarter.png)） | `1400 × 1680 px`（Cycles 3Dマット陰影・透過合成スタジオカード背景・接地シャドウ付） |
| **正面・側面・斜め・背面 4面比較ボード** | [`04_Delivery_Dept/outputs/output_20261104_cvn_iinet_front_and_side.png`](output_20261104_cvn_iinet_front_and_side.png)<br>（同内容コピー: [`iinet_kun_front_and_side.png`](iinet_kun_front_and_side.png)） | `3320 × 1008 px`（4パネル並列高解像度ボード） |
| **全6アングル統合シート（5面図＋斜め）** | [`04_Delivery_Dept/outputs/output_20261104_cvn_iinet_5views_sheet.png`](output_20261104_cvn_iinet_5views_sheet.png)<br>（同内容コピー: [`iinet_kun_5views_sheet.png`](iinet_kun_5views_sheet.png)） | `2496 × 1992 px`（正面・側面・背面・上面・底面・斜め3/4） |

#### (2) 構築スクリプト・中間アセット（`02_Creative_Dept/drafts/`）
| 種別 | ファイルパス | 内容 |
| :--- | :--- | :--- |
| **3D一括構築Pythonスクリプト** | `02_Creative_Dept/drafts/build_iinet_kun.py` | 輪郭LUT抽出・Rev.3全5項目3Dメッシュ生成・リギング・Cyclesマットレンダリング自動化 |
| **モデリング設計ドラフト** | `02_Creative_Dept/drafts/draft_cvn_iinet_3d_modeling.md` | 座標変換定義・Rev.3改修設計メモ |
| **全周360度地球儀テクスチャ** | `02_Creative_Dept/drafts/globe_texture.png` | `2048 × 1024 px` 正距円筒図法（Equirectangular）全周360度世界大陸テクスチャ |

### 2. Rev.3 ユーザー改修要件（全5項目）の実装仕様詳細

#### ① 足の形状：原画の「先端が丸く尖った造形」を維持し、両腕のようなパドル／ティアドロップ形状で足らしく延長（`Body` 下部 `Leg.L` / `Leg.R`）
- Rev.2で導入していた「足首のくびれ＋前方に張り出した平底の靴／ブーツ型」を全面廃止。
- 原画（`05_front.png` / `01_back.png`）のシルエットおよび両腕（`Arm.L` / `Arm.R`）の先端と同じく、**下に向かってぷっくりと丸みを帯びながらすぼまり、先端が丸く尖っている（ティアドロップ／パドル先端状）造形**を維持したまま、接地底面 $Z = -0.110\text{ m}$（股下アーチ頂点 $Z \approx +0.175\text{ m}$、左右中心 $X = \pm 0.258\text{ m}, Y = 0.0\text{ m}$）まで下方向へ適度に延長。
- 胴体下部曲面 $(X_{\text{torso}}, Y_{\text{torso}}, Z_{\text{torso}})$ に対して付け根（$s=1$）で勾配ゼロ（$C^1$ 連続）で接続しつつ、先端（$s \to 0$）に向かって半径が $s^{0.50}(0.68 + 0.32s)$ でぷっくり丸く収束する解析的プロファイルを採用。胴体との段差や折れ目を完全にゼロに抑え、正面・側面・背面・底面・斜め3/4のどの角度から見ても「両腕と同じ系統の丸く尖った可愛い2本の足」に見える造形を実現した。

#### ② 尻尾（`Antenna`）の先端と地球儀（`Globe`）の接続位置を「地球儀の真下（南極点）」へ移動
- 従来は尻尾の上端が地球儀の後方／側面（赤道付近）から刺さっていた軌道を改修し、地球儀の中心を $(X, Y, Z) = (0.0, 1.190, 2.3725)\text{ m}$（半径 $R = 0.180\text{ m}$、南極点 $(0.0, 1.190, 2.1925)\text{ m}$）に配置。
- お尻内部 $(Y=0.350\text{ m}, Z=0.490\text{ m})$ からお尻表面を貫通し、背中下部の最大後方突出点 $(Z=1.060\text{ m}, dY/dZ=0)$ ➔ 背中上部の谷部 $(Z=1.640\text{ m}, Y=0.975\text{ m}, dY/dZ=0)$ ➔ 地球儀真下の直前 $(Z=2.155\text{ m}, Y=1.190\text{ m}, dY/dZ=0)$ を2段階の解析的余弦曲線（$C^1/C^2$ 連続）で滑らかに繋ぎ、そこから **$+Z$ 方向（真上）へ垂直に立ち上がって地球儀の真下（南極中心 $Z=2.1925\text{ m}$）へ接続** する構造とした。

#### ③ 顔の青枠（`Face_Frame`）の枠幅スリム化＆全体サイズの微拡大
- TV画面モチーフの青枠および画面（`Face_Screen`）の外径スケールを Rev.2 の `0.84倍` から **`0.905倍`（顔中心 $Z_c = 1.2645\text{ m}$）へひと回り拡大** し、キャラクターらしい愛嬌のある画面サイズを確保。
- 同時に青枠の枠幅係数（`thickness_slim`）を Rev.2 の `0.74` から **`0.54`（従来の約半分強のシャープで洗練された細枠）** にスリム化し、ボディ表面から法線方向へ $+0.038\text{ m}$ 立体的に隆起させた。
- 合わせて胸元の3D立体ロゴ（`Logo_LILI_net`）を $Z$ 方向へ $-0.014\text{ m}$ 微調整し、大きくなった青枠下端との間に美しい余白を確保した。

#### ④ アニメ調レンダリングの廃止 ➔ 本格3DCGマット質感（Cycles GPU）レンダリングへの全面刷新
- **Freestyle（黒いアニメ輪郭線）の完全廃止**: `scene.render.use_freestyle = False` および `view_layer.use_freestyle = False` により2Dイラスト風の黒フチ線を完全撤廃。
- **自己発光（Emission）の完全ゼロ化とマットシェーディング**: 全マテリアルの `Emission Strength = 0.0` とし、フラットな塗りつぶしを廃止。`Roughness = 0.94`, `Specular IOR Level = 0.08`, `Coat Weight = 0.0` のしっとり落ち着いたつや消しラバー／クレイフィギュア質感に統一。
- **Cycles GPU パストレーシング＆スタジオ4灯ソフトボックス照明**: レンダリングエンジンを `CYCLES`（GPU + OpenImageDenoise, 64 samples）に切り替え、カメラ連動の4灯大型エリアライト（`Key_Cam` のみ大判ソフトシャドウ有効、`Fill_Cam` / `Rim_Cam` / `Bounce_Cam`＋`StudioWorld` 環境光）によって、ボディの丸み・青枠の厚み・ぷっくりした目と口・胸元の3D立体ロゴ `LILI-net` が柔らかい立体陰影で浮かび上がる本格3Dレンダリングを実現した。

#### ⑤ 地球儀（`Globe`）の全周360度・世界大陸テクスチャ化（全アングル対応）
- 正面図からの切り抜きに依存していた従来の半球テクスチャを廃止し、経度 $-180^\circ \sim +180^\circ$・緯度 $-90^\circ \sim +90^\circ$ の全周360度にわたり世界の大陸・半島・島列（ユーラシア大陸、日本列島、東南アジア諸島、オーストラリア、ニュージーランド、アフリカ大陸、マダガスカル、ヨーロッパ、スカンジナビア、イギリス、グリーンランド、北アメリカ大陸、中央アメリカ、カリブ諸島、南アメリカ大陸、太平洋諸島）をバランスよく配置した高解像度正距円筒図法マップ（`2048 × 1024 px`）をプロシージャル生成。
- 3D単位球面上の周期三角関数摂動による自然な海岸線の凹凸（岬・湾・半島）とアンチエイリアス処理に加え、経度 $\pm 180^\circ$ 境界および極点でのUVシーム補正を実装し、**正面・側面・背面・上面・底面・斜め3/4のどの角度から見ても一目で「地球儀」とわかる鮮やかな水色の海と緑の大陸**を表現した。

### 3. 視覚監査（Visual Audit）結果

再生成された3種のレンダリング画像（`output_20261104_cvn_iinet_hero_3quarter.png`, `output_20261104_cvn_iinet_front_and_side.png`, `output_20261104_cvn_iinet_5views_sheet.png`）を目視監査し、Rev.3の全5項目が最高品質で達成されていることを確認した。

1. **足の造形（原画準拠・両腕風の丸く尖った2本足）**: 正面・背面・側面・底面・斜め3/4のすべてのビューにおいて、胴体から段差ゼロで滑らかに伸び、両腕と同じように先端がぷっくり丸く尖った可愛い2本足として造形されている。
2. **尻尾先端と地球儀真下の接続**: 側面・背面・上面・底面・斜め3/4のすべてで、お尻から出た青いS字パイプが折れ目なく滑らかに地球儀の下へ回り込み、地球儀の真下（南極中心）へ垂直に接続している。
3. **顔の青枠・目・口・胸元3Dロゴ**: ひと回り大きく、かつ細くシャープになった立体青枠（外径 `0.905倍`、幅 `0.54倍`、厚み `+0.038 m`）の中に、大きめのぷっくりした丸目（半径 `0.080 m`）と口が収まり、その下に3D立体文字の `LILI-net` ロゴが干渉なく配置されている。
4. **3DCGマット質感レンダリング**: 黒い輪郭線やアニメ調のベタ塗りが完全に消え、Cyclesパストレーシングによる柔らかな3D陰影と上品なマット質感で全パーツの立体感が自然に表現されている。
5. **全周360度地球儀テクスチャ**: 正面（ユーラシア・アフリカ・インド・日本・豪州）、側面（北米・南米・グリーンランド・欧州・アフリカ）、背面（北米・南米・東アジア・カムチャツカ・豪州・NZ）、上面（北半球大陸群）、底面（南半球大陸群）、斜め3/4の全アングルにおいて、シーム（継ぎ目）のない美しい海と大陸が描画されている。

---

## Part 2. 設計要件＆参照5面図仕様サマリー（`01_Research_Dept/inputs/task_20261104_cvn_iinet_3d_modeling.md` 準拠）

- **対象キャラクター**: 株式会社CVN キャラクター「いい-NETくん」（胸ロゴ：`LILI-net` ※「いい」を `LI` `LI` で表現したデザイン）
- **用途**: 広告チラシ用ビジュアル、およびアニメーション用3Dモデル
- **質感・トーン（Rev.3）**: アニメ調を排した本格3DCGマット（つや消しラバー／クレイフィギュア）質感（Cycles GPU パストレーシング）
- **参照5面図アセット**:
  - `02_Creative_Dept/drafts/ref_images/05_front.png`（正面図）
  - `02_Creative_Dept/drafts/ref_images/03_side.png`（左側面図）
  - `02_Creative_Dept/drafts/ref_images/01_back.png`（背面図）
  - `02_Creative_Dept/drafts/ref_images/04_top.png`（上面図）
  - `02_Creative_Dept/drafts/ref_images/02_bottom.png`（底面図）
