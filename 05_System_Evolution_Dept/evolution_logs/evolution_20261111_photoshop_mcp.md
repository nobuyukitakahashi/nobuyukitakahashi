# 組織自律進化・監査レポート（20261111_photoshop_mcp）
- **監査対象**: Adobe Photoshop 2027 (v28.0) 自動制御用ローカルMCPサーバー（`photoshop`）＆専用スキル（`/photoshop`, `adobe-photoshop`）の構築・グローバル登録・実機検証、および制作体制の **5大ジャンル（`blender` / `illustrator` / `photoshop` / `davinci` / `writing`）** への拡張
- **判定ステータス**: `[UPDATED: 改善実施]`

### 1. Antigravity最新機能・仕様のチェック結果
- 外部npmパッケージ依存ゼロ（Node.js標準モジュールのみ）で動作する **Adobe Photoshop 2027 (v28.0) ローカルMCPサーバー（[`.agents/mcp/photoshop-mcp/server.js`](../../.agents/mcp/photoshop-mcp/server.js)）** および **即時実行CLIブリッジ（[`.agents/mcp/photoshop-mcp/cli.js`](../../.agents/mcp/photoshop-mcp/cli.js)）** を新設。
- 以下の全5種のツールを実装し、stdio JSON-RPC 2.0（`Content-Length` ヘッダおよび Newline-delimited JSON 両対応）での高速応答（未起動時 `316 ms`）を確認：
  1. `get_photoshop_status`: Node.js `fs.readdirSync` + `tasklist.exe` による Photoshop 2027 実行ファイル・COM ProgID (`Photoshop.Application`)・プロセス起動状態・開いているドキュメント一覧の高速取得
  2. `execute_photoshop_jsx`: ExtendScript（DOM / ActionManager）文字列または `.jsx` ファイルの UTF-8 BOM 完全保護＆`try/catch` エラー行番号付き実行
  3. `get_document_summary`: アクティブドキュメント（または指定 `.psd`/`.psb`/`.png`/`.jpg`/`.tiff`）の寸法・解像度・カラーモード・ビット深度・全レイヤー階層ツリー（`LayerSet` / `ArtLayer`、`kind`、`boundsPx`、`textInfo`）のJSON取得
  4. `export_canvas_png`: 複製ドキュメント上でのRGB変換・スケール調整による視覚監査（`read_file`）用PNG書き出し
  5. `save_photoshop_document`: `.psd` / `.png` / `.jpg` / `.tiff` 保存（複製上でのテキスト一括ラスタライズ `rasterize_text`、CMYK変換 `cmyk_convert`、統合 `flatten` 対応）
- **Windows DCOM `/Automation -Embedding` クラスファクトリ維持機構と 300dpi フォントサイズDPI補正の実装**:
  - Windows 環境で `New-Object -ComObject Photoshop.Application` を単発プロセスから呼び出した際、プロセス終了時に参照カウントが `0` となって Photoshop が `CoRevokeClassObject` を呼び出し、2回目以降の接続で `0x80080005 (CO_E_SERVER_EXEC_FAILURE)` が発生する問題を WMI デタッチド COM ホルダー（`agy_ps_com_holder.ps1`）の自動維持機構で解決。
  - `300 dpi` ドキュメントにおける `textItem.size` のポイント換算拡大（`300 / 72 = 4.1667倍`）を `new UnitValue(sizePx * (72.0 / doc.resolution), "pt")` で補正する鉄則を確立し、[`.agents/skills/adobe-photoshop/SKILL.md`](../../.agents/skills/adobe-photoshop/SKILL.md) に明文化。

### 2. パイプライン稼働監査（00_COO 〜 04_Delivery_Dept）
- **5大ジャンル体制への拡張と固定出力ルール遵守状況**: OK
- **更新・新設したルール・スキル・設定ファイル一覧**:
  1. **MCPサーバー＆CLIブリッジ**:
     - [`.agents/mcp/photoshop-mcp/server.js`](../../.agents/mcp/photoshop-mcp/server.js)
     - [`.agents/mcp/photoshop-mcp/cli.js`](../../.agents/mcp/photoshop-mcp/cli.js)
  2. **専用スキル（ワークスペース＆グローバル同期済）**:
     - [`.agents/skills/photoshop/SKILL.md`](../../.agents/skills/photoshop/SKILL.md)
     - [`.agents/skills/adobe-photoshop/SKILL.md`](../../.agents/skills/adobe-photoshop/SKILL.md)
     - [`.agents/skills/pc-env-sync/SKILL.md`](../../.agents/skills/pc-env-sync/SKILL.md) / [`sync_pc_env.ps1`](../../.agents/skills/pc-env-sync/scripts/sync_pc_env.ps1) / [`sync_mac_env.sh`](../../.agents/skills/pc-env-sync/scripts/sync_mac_env.sh)
  3. **グローバル `mcp_config.json`（全3箇所）**:
     - `C:\Users\nobuy\.gemini\antigravity\mcp_config.json`
     - `C:\Users\nobuy\.gemini\config\mcp_config.json`
     - `C:\Users\nobuy\.gemini\antigravity-obsidian\mcp_config.json`
  4. **5大ジャンル対応の組織ルール＆オーケストレーションスキル**:
     - [`AGENTS.md`](../../AGENTS.md)
     - [`00_COO/AGENTS.md`](../../00_COO/AGENTS.md)
     - [`02_Creative_Dept/AGENTS.md`](../../02_Creative_Dept/AGENTS.md)
     - [`04_Delivery_Dept/AGENTS.md`](../../04_Delivery_Dept/AGENTS.md)
     - [`.agents/skills/coo-orchestrator/SKILL.md`](../../.agents/skills/coo-orchestrator/SKILL.md)
     - [`.agents/skills/creative-dept/SKILL.md`](../../.agents/skills/creative-dept/SKILL.md)
     - [`.agents/skills/delivery-dept/SKILL.md`](../../.agents/skills/delivery-dept/SKILL.md)
  5. **Adobe Photoshop 2027 (`v28.0.0`) 実機検証成果物と納品台帳**:
     - [`02_Creative_Dept/photoshop/drafts/test_photoshop_mcp_build.jsx`](../../02_Creative_Dept/photoshop/drafts/test_photoshop_mcp_build.jsx)
     - [`02_Creative_Dept/photoshop/final_outputs/test_photoshop_mcp_verify.psd`](../../02_Creative_Dept/photoshop/final_outputs/test_photoshop_mcp_verify.psd)
     - [`02_Creative_Dept/photoshop/final_outputs/test_photoshop_mcp_verify.png`](../../02_Creative_Dept/photoshop/final_outputs/test_photoshop_mcp_verify.png)
     - [`02_Creative_Dept/photoshop/final_outputs/content_photoshop_mcp_setup.md`](../../02_Creative_Dept/photoshop/final_outputs/content_photoshop_mcp_setup.md)
     - [`04_Delivery_Dept/outputs/photoshop/output_20261111_photoshop_mcp_setup_full.md`](../../04_Delivery_Dept/outputs/photoshop/output_20261111_photoshop_mcp_setup_full.md)
     - [`04_Delivery_Dept/outputs/photoshop/output_20261111_photoshop_mcp_verify.psd`](../../04_Delivery_Dept/outputs/photoshop/output_20261111_photoshop_mcp_verify.psd)
     - [`04_Delivery_Dept/outputs/photoshop/output_20261111_photoshop_mcp_verify.png`](../../04_Delivery_Dept/outputs/photoshop/output_20261111_photoshop_mcp_verify.png)
     - [`04_Delivery_Dept/outputs/INDEX.md`](../../04_Delivery_Dept/outputs/INDEX.md)
