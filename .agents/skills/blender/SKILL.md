---
name: blender
description: >-
  Blender 5.3 / 5.2（MCPサーバー blender および Headless CLI）を用いた3Dモデリング、キャラクター造形、
  ロゴ3DベベルCG、マテリアル・ライティング、3Dアニメーション制作を専任で実行し、
  中間成果物を 02_Creative_Dept/blender/ に、最終成果物を 04_Delivery_Dept/outputs/blender/ に格納するスキル。
  ユーザーが /blender を指定した際、またはジャンル選択で「Blender（3Dモデリング・CG・3Dアニメ）」を選択した際に使用する。
---

# 🎨 Blender 3Dモデリング・CG・アニメーション専任スキル (`/blender`)

## 1. ジャンル別ディレクトリ規約（厳守）
- **試作・スクリプト・テクスチャ・参照画像置き場**:
  - [`02_Creative_Dept/blender/drafts/`](../../../02_Creative_Dept/blender/drafts/)
- **制作部門の完成中間成果物置き場**:
  - [`02_Creative_Dept/blender/final_outputs/`](../../../02_Creative_Dept/blender/final_outputs/)
- **最終納品フォルダ（`04_Delivery_Dept` による格納先）**:
  - [`04_Delivery_Dept/outputs/blender/`](../../../04_Delivery_Dept/outputs/blender/)
  - ※納品台帳 [`04_Delivery_Dept/outputs/INDEX.md`](../../../04_Delivery_Dept/outputs/INDEX.md) の「`## 🎨 1. Blender`」セクションにリンク（`blender/ファイル名`）を追記する。

---

## 2. 実行手順（MCP `blender` ＆ Headless CLI ハイブリッド運用）

1. **要件確認と接続チェック（Blender 5.3 優先・5.2 互換）**:
   - [`02_Creative_Dept/AGENTS.md`](../../../02_Creative_Dept/AGENTS.md) の「B. Blender 3D / CG制作手順」に従う。
   - Blender Lab 公式 MCPサーバー `blender`（`blender-mcp.exe` ⇄ `bl_ext.user_default.mcp` `localhost:9876`）の `get_objects_summary` / `execute_blender_code`（戻り値は必ず `result = {...}` の dict 形式）を確認する。GUI未接続時は `execute_blender_code_for_cli` またはローカルの Blender CLI（`C:\Program Files\Blender Foundation\Blender 5.3\blender.exe` を最優先検出し、未導入環境では `Blender 5.2\blender.exe` へ互換フォールバック：`--background --python 02_Creative_Dept/blender/drafts/<script.py>`）を実行する。
2. **`bpy` / `bmesh` 構築と鉄則の適用**:
   - シェーダーノードは名前ではなく `type`（`"BSDF_PRINCIPLED"` 等）で検索する。
   - 原画色彩の忠実再現時は `scene.view_settings.view_transform = 'Standard'` を設定する。
   - **Blender 5.2 / 5.3 動画出力（MP4 / FFmpeg）の必須設定順序と 16:9 アスペクト変更時の縦切れ防止**:
     - Blender 5.2以降では先に `scene.render.image_settings.media_type = 'VIDEO'` を設定してから `scene.render.image_settings.file_format = 'FFMPEG'` を指定すること（逆順または未設定だと `Enum 'FFMPEG' not found` エラーとなる）。
     - `4:3` から `16:9`（`1920×1080` Full HD）へアスペクト変更する際、水平センサー基準のまま解像度だけ変えると上下（頭上の地球儀・足元）がクロップされるため、必ず焦点距離を `lens_16_9 = lens_4_3 * 0.75`（または `sensor_fit = 'VERTICAL'`）に補正し、広角化に合わせてスタジオ背景の横幅も拡張すること。
   - 複数面図（5面図等）からの造形時は正面・側面輪郭LUT抽出＋コンフォーマル曲面投影を用いる。
   - **静止画とアニメーションでの同色パーツ（胴体と腕等）構造の使い分け**:
     - **静止画単体造形時**: `BOOLEAN (UNION)` ＋ 高解像度 `REMESH (VOXEL)` ＋ 正面2D外周シルエットロック付き2段階調和スムージング（`Smooth_Seam_3D` + `Smooth_Seam_Y`）で境界筋を完全除去する。
     - **アニメーション時（独立腕メッシュの完全シームレス一体化：開放リム型スライディング2次ベジェフィレットスカート ＋ カスタム法線 `0.00°` 一致）**:
       静止画用の単一溶接メッシュを局所ウェイトで大角度回転させると「翼の骨格・ひれ状のシワ」が発生し、逆に閉曲面同士の単純交差では境界にV字角の陰影線（別パーツ感）が残る。一体成型マスコットのアニメーションでは、**①ボディ本体（`Body`）は腕なしの純粋滑らかメッシュとして無変形保護（胴体ひれ0%）し、②腕を開放リム型構造化メッシュ（全フレームでトポロジ固定＝フリッカーゼロ）として先端〜中間は純粋剛体 `SO(3)` 回転させつつ、③根元スカート部のみを毎フレームのボディ表面へ2次ベジェ曲線（$\mathbf{B}_0 \to \mathbf{B}_1 \to \mathbf{B}_2$）で滑らかにR架橋（脇下はタイトにしてひれを防止）し、④`normals_split_custom_set_from_vertices` でリム端法線をボディ変形後法線と角度差 `0.00°` で完全一致（＋同一マテリアル・`visible_shadow=False`）**させる。
   - 空間曲線パーツ（アンテナ・尻尾等）と球体（地球儀等）は必ず3D球心へ直接貫入接続させる。
   - **丸胴体・超短足・超短腕マスコット（カービィ／サンリオ型）の3Dアニメーション＆ボディ保護鉄則**:
     1. 短い腕や足をゴムのように過度に引き伸ばす表現やおじぎで腹部を凹ませる表現は厳禁とし、タマゴ／球体側面の接線曲率中心まわりの `SO(3)` 純粋剛体回転（`det(R)=1`, 伸縮率 `1.000倍`）で短いパドル手をほっぺ横までパタパタ挙上・前後スイングさせること。
     2. **超短足の形崩れ防止とボディ本体の完全保護（`w=0.000` ロック）**: 足の前後スイング時は、足幅の途中カットオフや前後非対称クリフを禁止して足キャップ外縁まで均一ウェイト `w=1.000` とし（必要に応じた体積保存つきの微小な軸方向弾性伸縮のみ許容）、股関節リング帯のみで `1.0 -> 0.0` へ滑らかに減衰させ、それより上のボディ本体・お腹・胸ロゴ・顔枠領域は厳密に `w=0.000` にロックしてボディ本体への歪み波及を防止すること。また Phase 1 歩き出しは約 `33°〜36°` の斜め前3/4アングルから正面構図へ回り込むこと。
     3. おじぎ時は足底〜足首下部の回転重みを抑えて短い2本の足を床に踏ん張らせ、足なしボーリング玉化を防ぐこと（毎フレーム足底最下点 `min(z)` で床面接地を厳密ロックする）。
3. **視覚監査ループ（Visual Ground Truth）**:
   - 各ステップでレンダリングした `.png`（またはアニメーションのキーフレーム一覧ボード `.png`）を `read_file` で目視監査し、正面・側面・斜め3/4・背面すべての角度で破綻がないか検証・改修する。
4. **中間成果物出力と最終納品**:
   - 完成した `.blend` / `.glb` / `.png` / `.mp4` および制作仕様書 `content_[テーマ名].md` を `02_Creative_Dept/blender/final_outputs/` に保存する。
   - 続けて `04_Delivery_Dept` を通じて `04_Delivery_Dept/outputs/blender/` に最終成果物を格納し、`04_Delivery_Dept/outputs/INDEX.md` を更新する。
