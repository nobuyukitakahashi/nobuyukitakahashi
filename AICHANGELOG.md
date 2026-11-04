# AI変更履歴 (AICHANGELOG)

## 2026-11-05 (v9): 株式会社CVN「いい-NETくん（LILI-net）」3DモデルのRev.4改修（ボディ〜足付け根のへこみ解消・単一強凸曲面化、および頭頂ラインのC∞解析的ドーム曲線化）

### 変更理由
ユーザーからの追加デザイン指示（①ボディと足の付け根が不自然にへこんでいるためもっとなめらかに、②頭のラインがきれいでない）を受け、胴体下部から足先までの変曲点（凹み・くびれ）の根絶と、頭頂ラインのピクセル補間歪みの完全解消を実施するため。

### Before / After
- **Before (Rev.3)**:
  - 胴体底部を一旦閉じてから足領域を局所突出させていたため、脇腹〜太もも外側およびお腹・お尻下の付け根に変曲点（凹み・くびれ）が生じていた。また頭頂ラインに2D画像のピクセルLUT補間とスーパー楕円体（`p = 2.12`）による微細な歪みが残っていた。
- **After (Rev.4)**:
  - **単一強凸曲面＋Taubin平滑化によるへこみゼロの一体造形**: 外側輪郭および前後断面に全区間で二階微分 $f''(u) < 0$ となる単一強凸プロファイルを採用し、股下アーチと足先を $C^2$ 連続エルミート曲線で接続、さらに下半部メッシュに20反復の体積保存型Taubin平滑化を適用することで、脇腹・お腹・お尻から足先まで一切へこみのない滑らかな曲面を実現。
  - **$C^\infty$ 解析的ドーム曲線＋純粋楕円断面による頭頂ラインの完全平滑化**: 上半球を純粋楕円断面（`p = 2.0`）とし、正面頭頂プロファイルを $Z_{\text{top}}(|X|) = Z_{\text{eq}} + (Z_{\text{apex}} - Z_{\text{eq}})(1 - (|X|/W_{\max})^2)^{0.480}$ の解析関数へ刷新。

### 影響範囲
- 更新: [`02_Creative_Dept/drafts/build_iinet_kun.py`](02_Creative_Dept/drafts/build_iinet_kun.py), [`02_Creative_Dept/final_outputs/content_cvn_iinet_3d_modeling.md`](02_Creative_Dept/final_outputs/content_cvn_iinet_3d_modeling.md), [`04_Delivery_Dept/outputs/output_20261104_cvn_iinet_3d_modeling_full.md`](04_Delivery_Dept/outputs/output_20261104_cvn_iinet_3d_modeling_full.md), [`04_Delivery_Dept/outputs/INDEX.md`](04_Delivery_Dept/outputs/INDEX.md) および全レンダリング画像・`.blend` / `.glb` ファイル

---

## 2026-11-05 (v8): 株式会社CVN「いい-NETくん（LILI-net）」3DモデルのRev.3改修（両腕風の丸く尖った足造形・地球儀真下への尻尾接続・TV青枠のスリム化＆微拡大・Cycles 3DCGマット質感レンダリング・全周360度地球儀テクスチャ）

### 変更理由
ユーザーからの追加デザイン指示（①足を完全な足型にせず原画・両腕のように先端が丸く尖った造形のまま多少足らしく延長、②尻尾の先端と地球儀の接続位置を地球儀の真下へ移動、③顔の青枠の枠幅をもう少し細く＆全体サイズをもう少し大きく、④アニメ調ではなく3DCGマット質感でレンダリング、⑤地球儀上の海と大陸を原図にとらわれず全アングルで地球儀らしく描画）をすべて反映するため。

### Before / After
- **Before (Rev.2)**:
  - 平底・足首くびれのある靴型脚、地球儀背面への尻尾接続、Freestyle黒輪郭線＋自己発光によるアニメ調マット表現、正面半球のみの地球儀大陸配置。
- **After (Rev.3)**:
  - **先端が丸く尖った両腕風の足造形**: 靴型を廃止し、原画および両腕と同様に下に向かって丸くすぼまり先端が丸く尖ったパドル／しずく先端形状を維持したまま $Z = -0.110\text{ m}$ まで延長（胴体下部と $C^1$ 連続で接続）。
  - **地球儀真下への尻尾接続**: S字パイプの先端を地球儀の真下（南極中心 $Z = 2.1925\text{ m}$）へ移動し、真下から上向き（$+Z$ 方向）に垂直接続する軌道へ改修。
  - **TV青枠のスリム化＆全体サイズの微拡大**: 青枠・画面の全体スケールを `0.84倍` から `0.905倍` へ拡大し、枠幅係数を `0.74` から `0.54` へスリム化。
  - **Cycles GPU 3DCGマット質感レンダリング**: Freestyle黒輪郭線と自己発光を完全撤廃し、Cyclesパストレーシング＋4灯スタジオソフトボックス照明＋Principled BSDF（`Roughness = 0.94`, `Specular IOR Level = 0.08`）による自然な3DCGマットラバー／クレイフィギュア調陰影へ刷新。
  - **全周360度・世界大陸テクスチャ**: 経度 $-180^\circ \sim +180^\circ$・緯度 $-90^\circ \sim +90^\circ$ 全域に世界の大陸・半島・島列を配置した `2048×1024 px` テクスチャを生成し、全アングルで地球儀として視認可能に改修。

### 影響範囲
- 更新: [`02_Creative_Dept/drafts/build_iinet_kun.py`](02_Creative_Dept/drafts/build_iinet_kun.py), [`02_Creative_Dept/final_outputs/content_cvn_iinet_3d_modeling.md`](02_Creative_Dept/final_outputs/content_cvn_iinet_3d_modeling.md), [`04_Delivery_Dept/outputs/output_20261104_cvn_iinet_3d_modeling_full.md`](04_Delivery_Dept/outputs/output_20261104_cvn_iinet_3d_modeling_full.md), [`04_Delivery_Dept/outputs/INDEX.md`](04_Delivery_Dept/outputs/INDEX.md) および全レンダリング画像・`.blend` / `.glb` ファイル

---

## 2026-11-05 (v7): 株式会社CVN「いい-NETくん（LILI-net）」3DモデルのRev.2改修（2本脚延長・完全無反射マット質感・TV青枠の縮小/スリム化/立体化・目の拡大/立体化・お尻からの尻尾接続・胸元ロゴの3D立体メッシュ化）

### 変更理由
ユーザーからの追加デザイン指示（①足を延ばして足らしい2本脚に、②反射しない無反射マット質感に、③TV画面モチーフの青枠をもう少し立体的に・サイズを小さく、④青枠の太さを若干細く、⑤目をもう少し大きく・立体的に、⑥尻尾がお尻からしっかり出ているように、⑦胸元の `LILI-net` ロゴも立体的に）をすべて反映し、全アングルで破綻のない3Dキャラクターモデルおよびレンダリング成果物を納品するため。

### Before / After
- **Before (v1)**:
  - 5面図に忠実な短い二股突起の足、光沢のあるラバー質感（`Coat Weight = 0.40`）、平面UVテクスチャによる `LILI-net` ロゴ、大きめのTV青枠、浅い尻尾始点。
- **After (Rev.2)**:
  - **2本脚（`Leg.L` / `Leg.R`）の延長と立体造形**: 胴体下部（$Z \approx +0.185\text{ m}$）から接地底面（$Z = -0.275\text{ m}$）まで脚を延長し、「太もも ➔ 足首のくびれ ➔ 前方へぷっくり張り出した丸い足先」を造形。
  - **完全無反射マット質感**: 全マテリアルの `Roughness = 1.0`, `Specular IOR Level = 0.0`, `Coat Weight = 0.0` により鏡面ハイライトを完全排除。
  - **TV青枠・画面・目の立体改修**: 青枠＆画面を `0.84倍` に縮小、枠幅を `0.74倍` にスリム化、青枠の法線方向厚みを `+0.056m` へ増強。目の半径を `0.080m`（約1.28倍）・ドーム厚みを `+0.035m` に拡大。
  - **尻尾の内部貫通接続と `LILI-net` ロゴの3D立体メッシュ化**: 尻尾始点をお尻内部（$Y=0.35\text{ m}, Z=0.49\text{ m}$）から貫通させ、胸元ロゴを独立した3D立体メッシュ（`Logo_LILI_net`、押し出し厚 `+0.023m`）として造形。

### 影響範囲
- 更新: [`02_Creative_Dept/drafts/build_iinet_kun.py`](02_Creative_Dept/drafts/build_iinet_kun.py), [`02_Creative_Dept/final_outputs/content_cvn_iinet_3d_modeling.md`](02_Creative_Dept/final_outputs/content_cvn_iinet_3d_modeling.md), [`04_Delivery_Dept/outputs/output_20261104_cvn_iinet_3d_modeling_full.md`](04_Delivery_Dept/outputs/output_20261104_cvn_iinet_3d_modeling_full.md), [`04_Delivery_Dept/outputs/INDEX.md`](04_Delivery_Dept/outputs/INDEX.md) および全レンダリング画像・`.blend` / `.glb` ファイル

---

## 2026-11-04 (v6): 制作部門（02_Creative_Dept）における Blender 5.2 Headless CLI フォールバック手順と複数面図（5面図）3Dモデリング＆視覚監査ベストプラクティスの標準化

### 変更理由
株式会社CVN公式キャラクター「いい-NETくん（LILI-net）」の5面図からのBlender 3Dモデリング＆レンダリング案件において得られた以下の重要知見を、制作部門（`02_Creative_Dept`）の標準業務ルールおよびスキルに反映し、今後の3D制作の自律完遂力と造形精度を向上させるため：
1. `blender-plugin_blender` MCPサーバーが未起動（タイムアウト）の場合でも、ローカルの `"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" --background --python <script.py>` を用いたヘッドレス `bpy` / `bmesh` スクリプト実行＋生成PNGの `view_file`（`read_file`）視覚監査ループにより、中断することなく高速かつ高精度にキャラクター3Dモデリング・テクスチャ抽出・リギング・マルチアングルレンダリングを完遂できること。
2. 2Dの複数面図（5面図等）に作図上のズレや不整合がある場合、正面・側面の輪郭LUT抽出とコンフォーマル曲面投影（法線オフセット＋局所重み変調）を用いることで、正面・側面・斜めすべての角度で破綻のない立体造形が可能であること。

### Before / After
- **Before**:
  - [`02_Creative_Dept/AGENTS.md`](02_Creative_Dept/AGENTS.md) では、Blender MCP未接続時はレポートに `※Blender未接続` と記録し、`.py` スクリプトのみを出力してエスカレーションする規定となっていた。
  - 2Dの複数面図（5面図等）に作図ズレがある場合の立体整合アルゴリズムや、原画色彩を維持するカラーマネジメント設定に関する明文化がなかった。
- **After**:
  - **Blender MCP未接続時の Headless CLI 自律フォールバック手順の標準化**:
    - MCP未起動・タイムアウト時は直ちに `"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" --background --python <script.py>` によるヘッドレスバッチ実行＋生成PNGの `view_file`（`read_file`）目視監査ループへ自動切り替えし、`.blend` / `.glb` / `.png` の最終出力まで自律完遂する手順を [`02_Creative_Dept/AGENTS.md`](02_Creative_Dept/AGENTS.md) および [`.agents/skills/creative-dept/SKILL.md`](.agents/skills/creative-dept/SKILL.md) に規定。
  - **複数面図（5面図等）からの3Dモデリング＆視覚監査ベストプラクティスの追記**:
    - 正面・側面の輪郭LUT抽出とベース曲面へのコンフォーマル曲面投影（法線オフセット＋局所重み変調）、および `View Transform = Standard` ＋ Principled BSDF ＋ Freestyle アウトラインによる原画色彩・ソフビ/ラバー質感再現ルールを明文化。

### 影響範囲
- 新設: [`05_System_Evolution_Dept/evolution_logs/evolution_20261104.md`](05_System_Evolution_Dept/evolution_logs/evolution_20261104.md)
- 更新: [`02_Creative_Dept/AGENTS.md`](02_Creative_Dept/AGENTS.md), [`.agents/skills/creative-dept/SKILL.md`](.agents/skills/creative-dept/SKILL.md), [`AICHANGELOG.md`](AICHANGELOG.md)

---

## 2026-11-02 (v5): 制作・編集部門（02_Creative_Dept）への Blender MCP 統合プラグインの組み込みとマルチPC環境同期の拡張

### 変更理由
制作部門（`02_Creative_Dept`）がテキスト執筆・編集だけでなく、**Blender MCP（`mcp-for-blender` / MCPサーバー名: `blender`）** を用いたライブ3Dモデリング、アセット検索・インポート（Poly Haven / Sketchfab / Poly Pizza）、AI 3Dモデル生成、カメラ視点・マルチアングル視覚検証（`look`）、およびシーン・画像出力を自律実行できるよう、ワークスペースプラグイン・部門ルール・マルチPC同期スクリプトに組み込むため。

### Before / After
- **Before**:
  - `02_Creative_Dept`（`creative-dept` サブエージェント）は `EnableMCPTools: false` で定義されており、テキスト原稿の作成のみを対象としていた。
  - Windows 用環境同期スクリプト（`sync_pc_env.ps1`）およびワークスペースプラグイン（`.agents/plugins/`）に Blender MCP の定義がなかった。
- **After**:
  - **ワークスペースプラグイン [`.agents/plugins/blender-plugin/`](.agents/plugins/blender-plugin/) の新設**:
    - [`plugin.json`](.agents/plugins/blender-plugin/plugin.json)、[`mcp_config.json`](.agents/plugins/blender-plugin/mcp_config.json)、[`README.md`](.agents/plugins/blender-plugin/README.md) を作成し、`uvx mcp-for-blender`（MCPサーバー名: `blender`）をワークスペースプラグインとして登録。
  - **制作部門 [`02_Creative_Dept/AGENTS.md`](02_Creative_Dept/AGENTS.md) およびスキルの更新**:
    - `creative-dept` サブエージェント定義時に **`EnableMCPTools: true`** を付与（[`coo-orchestrator/SKILL.md`](.agents/skills/coo-orchestrator/SKILL.md) および [`creative-dept/SKILL.md`](.agents/skills/creative-dept/SKILL.md)）。
    - `get_addon_status` ➔ `get_scene_info` ➔ `search_assets` / `import_asset` / `generate_3d` / `execute_blender_code` ➔ `look` によるマルチアングル視覚監査 ➔ `04_Delivery_Dept/outputs/` への最終納品フローを標準化。
  - **Windows 環境同期スクリプト [`sync_pc_env.ps1`](.agents/skills/pc-env-sync/scripts/sync_pc_env.ps1) の拡張**:
    - macOS 版（`sync_mac_env.sh`）と同様に、Windows 版でも `uvx` パスを自動検出して `~/.gemini/config/mcp_config.json` および `~/.gemini/antigravity/mcp_config.json` に `blender`（および `obsidian`）を自動登録するよう更新。

### 影響範囲
- 新設: [`.agents/plugins/blender-plugin/plugin.json`](.agents/plugins/blender-plugin/plugin.json), [`.agents/plugins/blender-plugin/mcp_config.json`](.agents/plugins/blender-plugin/mcp_config.json), [`.agents/plugins/blender-plugin/README.md`](.agents/plugins/blender-plugin/README.md)
- 更新: [`AGENTS.md`](AGENTS.md), [`02_Creative_Dept/AGENTS.md`](02_Creative_Dept/AGENTS.md), [`.agents/skills/creative-dept/SKILL.md`](.agents/skills/creative-dept/SKILL.md), [`.agents/skills/coo-orchestrator/SKILL.md`](.agents/skills/coo-orchestrator/SKILL.md), [`.agents/skills/pc-env-sync/SKILL.md`](.agents/skills/pc-env-sync/SKILL.md), [`.agents/skills/pc-env-sync/scripts/sync_pc_env.ps1`](.agents/skills/pc-env-sync/scripts/sync_pc_env.ps1)

---

## 2026-11-01 (v4): 条件付き・オンデマンド稼働型「法務・コンプライアンス部門（06_Legal_Dept）」の新設

### 変更理由
通常案件におけるパイプラインの処理スピードを維持しつつ、法的リスク（薬機法・景品表示法・ステマ規制・著作権引用・個人情報保護・誹謗中傷リスク等）が含まれる案件や契約書・利用規約等の法務文書案件においてのみ専門的なリーガルスクリーニングと「安全な代替表現」の提示を行うため、条件付き審査ゲート（Conditional Gate）兼オンデマンド専門部署として `06_Legal_Dept` を新設。

### Before / After
- **Before**:
  - 法務・コンプライアンス専門の審査部門が存在せず、広告規制（薬機法・景表法・ステマ規制）や著作権引用要件、個人情報マスキング、契約・規約レビューを専門的に検証・代替案提示する仕組みがなかった。
- **After**:
  - **`06_Legal_Dept`（法務・コンプライアンス部門）と `/legal-dept` スキルの新設**:
    - [`06_Legal_Dept/AGENTS.md`](06_Legal_Dept/AGENTS.md) および [`.agents/skills/legal-dept/SKILL.md`](.agents/skills/legal-dept/SKILL.md) を作成。
    - 通常案件ではスキップし、統括COOが「5大法務リスクトリガー」に該当すると判定した案件（Step 3.5）、またはオーナーから `/legal-dept` で直接指名された案件のみ起動するハイブリッド稼働方式を採用。
    - 審査結果は3段階ステータス（`[APPROVED]` / `[CONDITIONAL_APPROVED]` / `[HOLD]`）で判定し、リスク箇所には「そのまま使える安全な代替表現（修正文案）」と弁護士法第72条配慮の免責注記を付与して `06_Legal_Dept/reviews/review_[テーマ名].md` に出力。
  - **最終出力固定ルール（`04_Delivery_Dept/outputs/`）との完全統合**:
    - `04_Delivery_Dept` が `06_Legal_Dept` の修正指示（安全な代替表現）を反映した上で統合納品パッケージ（Part 4）として `04_Delivery_Dept/outputs/` に格納するフローを確立。

### 影響範囲
- 新設: [`06_Legal_Dept/AGENTS.md`](06_Legal_Dept/AGENTS.md), [`06_Legal_Dept/reviews/.gitkeep`](06_Legal_Dept/reviews/.gitkeep), [`.agents/skills/legal-dept/SKILL.md`](.agents/skills/legal-dept/SKILL.md)
- 更新: [`AGENTS.md`](AGENTS.md), [`.agents/rules/global-policy.md`](.agents/rules/global-policy.md), [`00_COO/AGENTS.md`](00_COO/AGENTS.md), [`04_Delivery_Dept/AGENTS.md`](04_Delivery_Dept/AGENTS.md), [`.agents/skills/coo-orchestrator/SKILL.md`](.agents/skills/coo-orchestrator/SKILL.md)

---

## 2026-11-01 (v3): リサーチ部門（01_Research_Dept）への Google NotebookLM MCP 統合プラグインの組み込み

### 変更理由
リサーチ部門（`01_Research_Dept`）が Web 検索だけでなく、人間オーナーの Google NotebookLM 内のノートブック検索・質問・引用抽出・ソース追加（Ingest）を直接実行できるよう、ワークスペースプラグインとして `notebooklm-mcp` を組み込むため。

### Before / After
- **Before**:
  - `01_Research_Dept` の調査手段は `search_web` とローカルファイルのみだった。
- **After**:
  - **ワークスペースプラグイン [`.agents/plugins/notebooklm-plugin/`](.agents/plugins/notebooklm-plugin/) の新設**:
    - [`plugin.json`](.agents/plugins/notebooklm-plugin/plugin.json) および [`mcp_config.json`](.agents/plugins/notebooklm-plugin/mcp_config.json) を構成し、Windows 環境で確実に起動する `npx.cmd -y notebooklm-mcp@latest`（MCPサーバー名: `notebooklm-research`）を登録。
  - **リサーチ部門 [`01_Research_Dept/AGENTS.md`](01_Research_Dept/AGENTS.md) とスキルの更新**:
    - `research-dept` サブエージェントの定義時に `EnableMCPTools: true` を付与。
    - NotebookLM ナレッジ照会（`[NotebookLM]` タグ）と 2026年最新 Web 調査（`[Web]` タグ）を組み合わせるハイブリッド調査手順および出典記載フォーマットを実装。

---

## 2026-11-01 (v2): 最終出力引き受け専門部門（04_Delivery_Dept）と自律進化部門（05_System_Evolution_Dept）の実装

### 変更理由
1. ユーザーがどのような形式で成果物（Output）を受け取る場合でも、常に単一の固定フォルダ（`04_Delivery_Dept/outputs/`）で受け取れるよう、最終出力を一手に引き受ける専門サブエージェント（`04_Delivery_Dept`）を実装し、全サブエージェントにそのルールを徹底させるため。
2. 人間から都度指示しなくても、常時Antigravityの最新機能・仕様を確認して組織のルールやスキルを自律的にアップデートし続ける専門サブエージェント（`05_System_Evolution_Dept`）を組み込むため。

### Before / After
- **Before**:
  - `01_Research_Dept/reports/`、`02_Creative_Dept/final_outputs/`、`03_Marketing_Dept/promos/` に成果物が分散しており、ユーザーが複数フォルダを見に行く必要があった。またHTMLやCSVなど別形式での出力を一元管理する専門部署がなかった。
  - 組織のルール（`AGENTS.md`）やスキル（`SKILL.md`）の改善は人間からの明示的な指示がある時のみ行われる設計だった。
- **After**:
  - **`04_Delivery_Dept`（納品・出力統合部門）と固定出力フォルダ `04_Delivery_Dept/outputs/` の新設**:
    - `01`〜`03` の各部門フォルダは「中間成果物置き場」と再定義し、全サブエージェントの `AGENTS.md` および `global-policy.md` に「最終成果物はどんな形式であれ必ず `04_Delivery_Dept` が引き受け、`04_Delivery_Dept/outputs/` に格納する」ルールを徹底。
    - `04_Delivery_Dept/outputs/INDEX.md`（納品台帳）により、全成果物を1箇所で一覧・取得可能化。
  - **`05_System_Evolution_Dept`（組織進化・Antigravity最新仕様監査部門）の新設**:
    - パイプライン実行時（および `/system-evolution` 実行時）に、Antigravityの内蔵スキル（`agy-customizations`, `antigravity-guide`）や公式ドキュメント/Changelog、実行ログを自律監査し、人間の指示を待たずに各 `AGENTS.md` や `.agents/skills/` をアップデートする特権部門を実装。

### 影響範囲
- [`.agents/rules/global-policy.md`](.agents/rules/global-policy.md), [`AGENTS.md`](AGENTS.md)
- [`00_COO/AGENTS.md`](00_COO/AGENTS.md) 〜 [`05_System_Evolution_Dept/AGENTS.md`](05_System_Evolution_Dept/AGENTS.md)
- [`.agents/skills/`](.agents/skills/) 配下の全6スキル

---

## 2026-11-01 (v1): Antigravity最新仕様に基づくマルチエージェント組織構造・ルール・スキルの導入

### 変更理由
ユーザーが構想した「フォルダ構造とMDファイルによる仮想サブエージェント分業モデル」を、最新Antigravityの公式カスタマイズ仕様（Hierarchical Rules `AGENTS.md`、On-Demand Skills `.agents/skills/*/SKILL.md`、ネイティブサブエージェント起動ツール `define_subagent` / `invoke_subagent`）に完全適合させ、自律的かつ確実に動作するマルチエージェントパイプラインへ昇華させるため。
