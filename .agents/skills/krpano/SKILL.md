---
name: krpano
description: >-
  krpano 1.24（krpanotools CLI・XML/Action/JS API・Testing Server）による360°VRツアー・WebXR・ThreeJS・3DGS制作とHTML5書き出しスキル。
  /krpano 指定時、または krpano 制作・XML編集依頼時に使用。
---

# 🥽 krpano 1.24 VRコンテンツ制作・自動化専任スキル (`/krpano`)

## 1. ディレクトリ規約
- 試作・`.config`・仮出力：`02_Creative_Dept/krpano/drafts/<案件サブフォルダ>/`
- 中間成果物（`tour.xml` / スキン / カスタムJS）：`02_Creative_Dept/krpano/final_outputs/<案件サブフォルダ>/`
- 最終納品先（HTML5 VRツアー本番一式）：`04_Delivery_Dept/outputs/krpano/<案件サブフォルダ>/`（[`INDEX.md`](../../../04_Delivery_Dept/outputs/INDEX.md) の `krpano 1.24` 更新）

## 2. ローカル SDK ＆ 一次ドキュメント
- **SDK / CLI**: `g:\マイドライブ\git\krpano\krpano-1.24\krpanotools.exe`（`makepano`, `maketiles`, `convert`, `makepreview`, `spheretocube`, `cubetosphere`, `protect`, `encrypt`, `testserver`, `register`）
- **一次資料**: `docu/`（`xml.html`, `actions.html`, `js_api.html`, `tools/krpanotools.html`, `plugins/`）、`templates/`（`vtour-multires.config`, `vtour-vr.config`, `vtour-normal.config` 等）、`viewer/examples/`（`3d-gaussian-splatting/`, `threejs/`, `depthmap/`, `webvr/` 等）。特殊機能は必ず実例確認してから実装。

## 3. 実行手順
1. **環境確認**: 必要時 `krpanotools.exe register show` でライセンス確認。
2. **CLI ビルド**:
   ```powershell
   & "g:\マイドライブ\git\krpano\krpano-1.24\krpanotools.exe" makepano `
     -config="g:\マイドライブ\git\krpano\krpano-1.24\templates\vtour-multires.config" `
     -output="02_Creative_Dept/krpano/drafts/<案件サブフォルダ>" "<入力画像1>" "<入力画像2>"
   ```
   （※VR軽量併用時は `vtour-vr.config`、カスタム設定は UTF-8 BOMなし `.config` または `-setting=value`）
3. **XML / JS 編集 ＆ ブラウザ実機監査【必須】**:
   - `tour.xml` / `skin/vtourskin.xml` / `tour.html` を UTF-8（BOMなし）で編集。
   - `IsDaemon: true` で `krpanotools.exe testserver -root="<draftsフルパス>" -port=8890 -open=no -nocache=all -q` を起動（HTTPS必要時は `-s`）。
   - `browser` サブエージェントで `http://127.0.0.1:8890/tour.html` を開き、表示・XML/コンソールエラー・遷移・UI崩れをスクショ監査後、`manage_task(kill)` で `testserver` を必ず停止。
4. **保護・納品**: 要望時は `encrypt` / `protect` を適用し、`qa-verifier` 合格後にクリーンな本番一式を `04_Delivery_Dept/outputs/krpano/<案件サブフォルダ>/` へ格納・`INDEX.md` 更新。
