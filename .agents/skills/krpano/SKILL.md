---
name: krpano
description: >-
  krpano 1.24（ローカルCLI "g:\マイドライブ\git\krpano\krpano-1.24\krpanotools.exe"、XML/Action/JS API、
  および内蔵 Testing Server ＋ ブラウザ視覚監査）を用いた 360°VRパノラマツアー、WebXR、ThreeJS連携、
  3D Gaussian Splatting、Depthmap 等の制作・カスタマイズ・暗号化・HTML5書き出しを実行し、
  中間成果物を 02_Creative_Dept/krpano/ に、最終成果物を 04_Delivery_Dept/outputs/krpano/ に格納するスキル。
  ユーザーが /krpano を指定した際、または krpano でのVRコンテンツ制作・XML編集・テスト実行を指示した際に使用する。
---

# 🥽 krpano 1.24 VRコンテンツ制作・自動化専任スキル (`/krpano`)

## 1. ディレクトリ規約（案件別サブフォルダ分離）

本スキルは既存の5大ジャンル（`blender` / `illustrator` / `photoshop` / `davinci` / `writing`）および `/pano2vr` とフォルダを完全に分離して運用する単体操作スキルです。

- **試作・`.config`・XML検証・仮出力置き場**:
  - [`02_Creative_Dept/krpano/drafts/`](../../../02_Creative_Dept/krpano/drafts/)（案件単位で `<案件サブフォルダ>/` を切って分離）
- **制作部門の完成中間成果物置き場（編集済み `tour.xml` / スキン / カスタムJS・プラグイン一式）**:
  - [`02_Creative_Dept/krpano/final_outputs/`](../../../02_Creative_Dept/krpano/final_outputs/)（`<案件サブフォルダ>/` で分離）
- **最終納品フォルダ（HTML5 VRツアー一式 / 保護・暗号化済み出力パッケージ）**:
  - [`04_Delivery_Dept/outputs/krpano/`](../../../04_Delivery_Dept/outputs/krpano/)（`<案件サブフォルダ>/` で分離）
  - 納品時は必ず [`04_Delivery_Dept/outputs/INDEX.md`](../../../04_Delivery_Dept/outputs/INDEX.md) の `krpano 1.24` セクションへ追記する。

---

## 2. ローカル SDK・CLI・一次ドキュメント参照先

- **SDK ルート**: `g:\マイドライブ\git\krpano\krpano-1.24`
- **CLI 実行バイナリ**: `g:\マイドライブ\git\krpano\krpano-1.24\krpanotools.exe`
  - サブコマンド: `makepano` / `maketiles` / `convert` / `makepreview` / `spheretocube` / `cubetosphere` / `protect` / `encrypt` / `testserver` / `register`
- **ローカル公式ドキュメント（一次情報・1.24準拠）**:
  - XML / 構文: `docu/xml.html`, `docu/xml_syntax.html`, `docu/coordinates.html`, `docu/embedpano.html`
  - スクリプト / API: `docu/actions.html`, `docu/js_api.html`
  - CLI / 設定 / サーバー: `docu/tools/krpanotools.html`, `docu/tools/config.html`, `docu/tools/testingserver.html`
  - プラグイン: `docu/plugins/`（`webvr.html`, `threejs.html`, `krpanomaps.html`, `soundinterface.html`, `videoplayer.html`, `postprocessing.html`, `gyro2.html`, `radar.html`, `combobox.html`, `scrollarea.html` 等）
  - ライセンス: `license.html`
- **テンプレート ＆ サンプル**:
  - `.config` テンプレート: `templates/vtour-multires.config`, `templates/vtour-vr.config`, `templates/vtour-normal.config`, `templates/flat.config`, `templates/multiframe.config` 等
  - XML / HTML テンプレート: `templates/xml/`, `templates/html/embedpano.html`
  - 実装サンプル: `viewer/examples/`（`3d-gaussian-splatting/`, `threejs/`, `depthmap/`, `webvr/`, `webvr-controllers/`, `compare-panos/`, `videopano/`, `javascript-interface/` 等）

---

## 3. 実行手順（CLIビルド × XML/JS編集 × ブラウザ視覚監査）

### フェーズ1：環境・ライセンス・仕様確認
1. **ライセンス状態確認（必要時）**:
   ```powershell
   & "g:\マイドライブ\git\krpano\krpano-1.24\krpanotools.exe" register show
   ```
   - `krpano License` が有効であることを確認する（`Branding Free License` が未登録の場合は、通常ライセンス条件および `license.html` の範囲に準拠する）。
2. **仕様・サンプルの参照**:
   - 特殊なプラグイン（ThreeJS、3D Gaussian Splatting、Depthmap、WebVR等）を使う場合は、推測で記述せず必ず上記のローカル `docu/` または `viewer/examples/` 内の実例を確認する。

### フェーズ2：CLI によるツアー・タイル自動生成
1. **出力先準備**:
   - 案件名を決めて `02_Creative_Dept/krpano/drafts/<案件サブフォルダ>/` を作成する。
2. **`makepano` 実行（例：マルチレゾリューションVRツアー）**:
   ```powershell
   & "g:\マイドライブ\git\krpano\krpano-1.24\krpanotools.exe" makepano `
     -config="g:\マイドライブ\git\krpano\krpano-1.24\templates\vtour-multires.config" `
     -output="02_Creative_Dept/krpano/drafts/<案件サブフォルダ>" `
     "<入力画像1>" "<入力画像2>"
   ```
   - VRヘッドセット向け軽量イメージも同時生成する場合は `vtour-vr.config` を使用する。
   - WebP / JPEG XL 等の1.24対応フォーマットや品質設定を変える場合は、`drafts/<案件サブフォルダ>/` 内にカスタム `.config`（`include` 活用・UTF-8 BOMなし）を作成して `-config=` に渡すか、`-setting=value` で上書きする。

### フェーズ3：XML / Action / JS カスタマイズ ＆ ブラウザ視覚監査
1. **XML / スキン / JS の編集**:
   - 生成された `tour.xml`、`skin/vtourskin.xml`、`tour.html` 等を編集し、シーン初期視点（`<view hlookat="..." vlookat="..." fov="..." />`）、ホットスポット（`<hotspot ath="..." atv="..." />`）、UIレイヤー、カスタム `<action>`、ThreeJS や WebVR 設定を組み込む。
   - すべてのテキストファイルは **UTF-8（BOMなし）** で保存する。
2. **Testing Server のバックグラウンド起動**:
   - `IsDaemon: true`（または終了時に必ず停止管理）で `testserver` を起動する：
     ```powershell
     & "g:\マイドライブ\git\krpano\krpano-1.24\krpanotools.exe" testserver `
       -root="g:\マイドライブ\git\nobuyukitakahashi\02_Creative_Dept\krpano\drafts\<案件サブフォルダ>" `
       -port=8890 -open=no -nocache=all -q
     ```
   - WebXR / ジャイロ等 HTTPS が必要なテストでは `-s` を付与する（自己署名証明書警告あり）。
3. **ブラウザ実機監査（`browser` サブエージェント）**:
   - `browser` サブエージェントで `http://127.0.0.1:8890/tour.html` を開き、画面表示・XMLパースエラーやコンソールエラーの有無・シーン遷移・ホットスポットやUIの崩れをスクリーンショット付きで確認する。
   - 確認完了後、起動していた `testserver` タスクは必ず `manage_task`（`kill`）で終了する。

### フェーズ4：保護・暗号化（任意）と最終納品
1. **中間成果物の整理**:
   - 完成版のソース設定・XML・カスタムJS・作業メモを `02_Creative_Dept/krpano/final_outputs/<案件サブフォルダ>/` へ保存する。
2. **保護・暗号化（ユーザー要望時）**:
   - 必要に応じて `krpanotools.exe encrypt`（XML/JS暗号化）や `krpanotools.exe protect`（ドメイン制限等）を適用する。
3. **最終納品格納と台帳更新**:
   - そのままWebサーバーやホスティングへ公開できるクリーンな本番一式（`tour.html`, `tour.js`, `tour.xml`, `panos/`, `skin/`, `plugins/` 等。不要なテスト用 `.exe` や一時 `.config` は除外可否を確認して整理）を `04_Delivery_Dept/outputs/krpano/<案件サブフォルダ>/` へ格納する。
   - [`04_Delivery_Dept/outputs/INDEX.md`](../../../04_Delivery_Dept/outputs/INDEX.md) の `krpano 1.24` セクションを更新し、ユーザーへ最終成果物パスを報告する。
