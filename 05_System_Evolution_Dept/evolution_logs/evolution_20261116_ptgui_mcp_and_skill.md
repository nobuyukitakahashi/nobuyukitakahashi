# System Evolution Log: PTGui Pro 13 ローカルMCPサーバー（`ptgui`）＆専任スキル（`/ptgui`）新設

- **実施日**: 2026-11-16
- **対象**: `.agents/mcp/ptgui-mcp/`, `.agents/skills/ptgui/SKILL.md`, `02_Creative_Dept/ptgui/`, `04_Delivery_Dept/outputs/ptgui/`, `pc-env-sync`

## アップデート概要
1. **360°VRパノラマ制作パイプラインの上流工程（スティッチ・HDR合成）の自動化**:
   - 既存の `/pano2vr`（Pano2VR 8）および `/krpano`（krpano 1.24）の上流工程にあたる、分割撮影画像・RAW/HDRブラケット画像からの 360° Equirectangular パノラマ生成を担う **PTGui Pro 13 専任スキル（`/ptgui`）** および **ローカルMCPサーバー（`ptgui`）** を新設。
2. **別フォルダ分離運用の徹底**:
   - 既存5大ジャンルおよび `pano2vr` / `krpano` と混在しないよう、`02_Creative_Dept/ptgui/{drafts,final_outputs}/` および `04_Delivery_Dept/outputs/ptgui/` を独立配置。
3. **クロスプラットフォーム環境同期対応**:
   - `sync_pc_env.ps1`（Windows）および `sync_mac_env.sh`（macOS）の双方で `ptgui` スキルと `ptgui` MCPサーバーが自動登録されるよう更新完了。
