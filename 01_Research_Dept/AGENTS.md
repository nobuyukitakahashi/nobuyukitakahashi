# 役割定義：Research & Knowledge部門（`01_Research_Dept`：調査・クライアントカルテ・ナレッジ統合）

Lane B 案件の事前調査（NotebookLM / Gemini Notebook × 2026年基準 Web調査）に加え、継続クライアントの統括カルテ（`projects/`）、音声議事録（`audio-meeting-minutes`）、Obsidian ナレッジ連携を一元管理する。

## 1. 管轄領域
1. **ハイブリッド調査（`inputs/` ➔ `reports/`）**:
   - `01_Research_Dept/inputs/task_[YYYYMMDD]_[テーマ名].md` に基づき調査。
   - ノート一覧・作成・高速ソース投入は認証済みなら `gemini-notebook` を優先、照会・引用抽出・音声生成は `notebooklm-research` を使用（未認証時は `※NotebookLM未認証（Web検索のみで実施）` と明記しWeb調査へ進む）。
   - `search_web` で 2026年基準の一次情報・出典URLを収集し、`01_Research_Dept/reports/report_[テーマ名].md` を保存、タスク先頭へ `[完了]` 追記。
2. **継続クライアント統括カルテ（`projects/<client_id>/`）**:
   - 複数ジャンルを横断する継続顧客の `PROJECT_MASTER.md`（基本情報・ブランド規定・NotebookLM ID・意思決定ログ・関連成果物一覧）と参照原本（`sources/`）を管理する。
3. **音声議事録・Obsidian連携**:
   - 会議録音は `.agents/skills/audio-meeting-minutes/SKILL.md`、Obsidian Vault 連携は `obsidian-*` スキル群に準拠する。

## 2. レポート出力フォーマット（厳守）
```markdown
# 調査レポート：[テーマ名]
- **調査日**: 2026年XX月XX日
- **対応タスク**: `01_Research_Dept/inputs/task_[YYYYMMDD]_[テーマ名].md`
- **参照ソース区分**: NotebookLM（[ノートブック名 / なし]） ＋ Web検索（2026年最新）
- **概要**: （結論を3行以内）

### 1. 主要な事実と背景
- （NotebookLM由来は `[NotebookLM]`、Web由来は `[Web]` を付記）

### 2. メリットと強み / デメリットとリスク
- **メリット**: / **デメリット・課題**:

### 3. 具体的な実例・ケーススタディ
- （導入事例・比較データ・2026年トレンド）

### 4. 情報源・出典一覧
- **NotebookLM 参照ソース**: / **Web 出典URL**: `[タイトル](URL)`

### 5. 次工程（Creative / Delivery）への引き継ぎ事項
- 推奨ターゲット層 / 構成・切り口案 / 出力フォーマット留意点 / 注意点
```

## 3. 禁止事項
- 推測・虚偽の記載禁止（未裏付けは `※ソース不明（要人間確認）` と明記）。
- `04_Delivery_Dept/outputs/` へ直接書き込まない（`global-policy.md` 遵守）。
