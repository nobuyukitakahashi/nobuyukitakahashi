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

## 2. 実行手順（最適モデル選択・MCP `blender` ＆ Headless CLI ハイブリッド運用）

0. **最適モデル判定 ＆ Swarm動的切替（`Hydrogen` / `Neon` / `Argon`）**:
   - 作業着手前にタスク難易度を判定し、現行モデルと不一致の場合は [`00_COO/AGENTS.md`](../../../00_COO/AGENTS.md) Step 0-A に従って最適モデルを提案または `swarm` で割り当てる：
     - **Tier 1（シーン一覧確認・単体配置・単純移動/回転/リネーム/単色変更）**: `Gemini 4 Hydrogen (Low/Medium)`（`gemini-4-hydrogen-low`）
     - **Tier 2（`bpy`/`bmesh` 造形・ジオメトリ/シェーダーノード・リギング・アニメ・空間計算・デバッグ）**: **`Gemini 4 Neon (High)`**（`gemini-4-neon-high`）
     - **Tier 3（v7/v8級極限幾何・連続エラー再試行時のエスカレーション）**: **`Gemini 4 Neon (XHigh)`**（`gemini-4-neon-xhigh`）
     - **Tier 4（長尺映像参照やGUI視覚照合中心の複合監査）**: `Gemini 4 Argon (Medium/High)` / `Carbon`
   - `swarm` 動的切替モードで `Hydrogen`（または `Neon High`）ワーカーがエラー・破綻を起こした場合は、`swarm(action="model", ...)` で `gemini-4-neon-high` → `gemini-4-neon-xhigh` へ昇格させて修正を実行する。
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
   - **丸胴体・超短足・超短腕マスコット（カービィ／サンリオ型）の3Dアニメーション＆ボディ保護・効果音SE同期鉄則（v7/v8 手足しわ・たるみ完全ゼロ化 ＆ 数式同期SE統合鉄則）**:
     1. 短い腕や足をゴムのように過度に引き伸ばす表現やおじぎで腹部を凹ませる表現は厳禁とし、タマゴ／球体側面の接線曲率中心まわりの `SO(3)` 純粋剛体回転（`det(R)=1`, 伸縮率 `1.000倍`）で短いパドル手をほっぺ横までパタパタ挙上・前後スイングさせること。
     2. **腕（独立開放リム型パドルメッシュ）のしわ・コブ・水かきたるみ・高挙上時の肩上端影スジ防止（v7/v8）**:
        - 上下挙上（Flap）および前後スイング（Swing）の回転ピボットは、離れた頭や目の高さに置いてはならず、必ず**実際の腕付け根断面中心（肩ボールジョイント中心）**に配置すること（離れたピボットだと大角度回転時にレバーアームで根元が胴体から外へ引き抜かれ、コブや長い水かきたるみが発生する）。高い位置で手を振る際は、肩ピボット自体を**タマゴ型胴体表面の水平断面等高線 `R_surf(z)` に厳密追従させながら子午線に沿って滑らかにリフト**させつつ回転させること（胴体表面から外へ浮き上がらせないことで高挙上時の肩上端影スジを完全消滅させる）。
        - 腕パドルの先端〜中間の丸みを潰す原因となる **`dR_from_c` クランプは全面廃止**し、先端側 `m_lock = 0.55` 領域を純粋剛体として保護すること。
        - スカート幅を傾きに応じて拡大する `d_neck_out` のような動的暴走オフセットは禁止し、交差ループすぐ外側のコンパクトなフィレット幅にリムを密着させ、3段つぎはぎ（ベジェ＋カラー＋先端）ではなく**単一 $C^2$ 母線補間＋境界固定2D調和ラプラシアン緩和**で変曲点（ネックのくびれ折れ線）をゼロにすること。
        - カスタム法線ブレンドでは `np.maximum` 等の非微分なクランプ関数を禁止し、リム端（角度差 `0.00°`）から外側へ純粋な $C^2$ `smootherstep` と2Dガウシアンフィルタで遷移させて陰影のリング状スジを防ぐこと。
     3. **超短足の形崩れ・下腹部二重あご段差・股間斜めひきつれしわ防止とボディ本体の完全保護（`w=0.000` ロック・`z_crotch` 基準ドーム変形）（v7/v8）**:
        - 足の前後スイング時は、足幅の途中カットオフや前後非対称クリフを禁止して足キャップ外縁まで均一ウェイト `w=1.000` とし（必要に応じた体積保存つきの微小な軸方向弾性伸縮のみ許容）、**股間分岐高さ `z_crotch` 基準のドーム変形**で股関節リング帯のみ `1.0 -> 0.0` へ滑らかに減衰させ、それより上のボディ本体・お腹・胸ロゴ・顔枠領域は厳密に `w=0.000` にロックしてボディ本体への歪み波及を防止すること。また Phase 1 歩き出しは約 `33°〜36°` の斜め前3/4アングルから正面構図へ回り込み、正面で手を振る区間（Wave）では**両足を対称シルエット（接地・平行）に保持**して片足上げによる股間・下腹部の非対称な歪みを防ぐこと。
        - 足の回転ピボット高さ `z_hip_piv` は必ず変形上限 `z_leg_top` に一致させ、`z < z_leg_top` 全域で `dz = z - z_leg_top <= 0` を単調維持して胸ロゴ直下のS字波打ち（変位符号逆転）を根絶すること。
        - 股間アーチ中央（`x ≈ 0`）には中立減衰マスクを適用して左右逆位相スイングの衝突による斜めひきつれを防ぐとともに、変形後の `Body` メッシュ下部遷移帯に対して、頂点座標 $\mathbf{p}$ ではなく**「初期メッシュからの変位ベクトル場 $\Delta\mathbf{p} = \mathbf{p} - \mathbf{p}_{\text{rest}}$」に対する境界固定ラプラシアン調和緩和**を適用し、静止時の丸み痩せゼロ（誤差 `0.0000mm`）と動作時のしわ・段差ゼロを両立させること。
     4. おじぎ時は足底〜足首下部の回転重みを抑えて短い2本の足を床に踏ん張らせ、足なしボーリング玉化を防ぐこと（毎フレーム足底最下点 `min(z)` で床面接地を厳密ロックする）。
     5. **数式タイムライン完全同期の 48kHz ステレオマスコット効果音（SE）生成 ＆ Blender VSE AAC 音声統合（v8）**:
        - 3Dアニメーション動画（`.mp4`）に効果音（SE）を付与する際は、アニメーション制御スクリプト内の位相・フレーム数式（歩行ステップ接地フレーム、着地バウンス、手振りパタパタ周期、おじぎ・キラキラ演出等）からミリ秒精度で同期した **48kHz 16bit ステレオ WAV サウンドトラック** をプログラム生成し、Blender の Video Sequence Editor（`scene.sequence_editor_create()` ➔ `sequences.new_sound()`）に配置した上で、`scene.render.ffmpeg.audio_codec = 'AAC'`（`audio_bitrate = 192`, `audio_mixrate = 48000`）で映像と完全同期した音声付き MP4 として直接書き出すこと。
3. **視覚監査ループ（Visual Ground Truth）**:
   - 各ステップでレンダリングした `.png`（またはアニメーションのキーフレーム一覧ボード `.png`）を `read_file` で目視監査し、正面・側面・斜め3/4・背面すべての角度で破綻がないか検証・改修する。
4. **中間成果物出力と最終納品**:
   - 完成した `.blend` / `.glb` / `.png` / `.mp4` および制作仕様書 `content_[テーマ名].md` を `02_Creative_Dept/blender/final_outputs/` に保存する。
   - 続けて `04_Delivery_Dept` を通じて `04_Delivery_Dept/outputs/blender/` に最終成果物を格納し、`04_Delivery_Dept/outputs/INDEX.md` を更新する。
