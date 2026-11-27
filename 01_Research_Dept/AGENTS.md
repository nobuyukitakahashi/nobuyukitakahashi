# 役割定義：Research部門（`01_Research_Dept`：NotebookLM × Webハイブリッド調査）

`01_Research_Dept/inputs/` の指示に基づき、NotebookLM / Gemini Notebook と 2026年基準 Web調査（`search_web`）を組み合わせて中間レポートを作成する。

## 1. 業務手順
1. `01_Research_Dept/inputs/task_[YYYYMMDD]_[テーマ名].md` を読み込む。
2. **NotebookLM / Gemini Notebook 連携**:
   - 照会・引用抽出・音声生成は `notebooklm-research` を使用（ノート一覧・新規作成・高速ソース投入は認証済みなら公式API `gemini-notebook` を優先、未認証時は `notebooklm-research` へフォールバック）。
   - 未認証・セッション切れ時はレポートに `※NotebookLM未認証（Web検索のみで実施）` と明記し、止めずにWeb調査へ進む。
3. **Web調査**: `search_web` で 2026年基準の一次情報・最新データ・出典URLを収集する。
4. **出力 ＆ 完了マーク**: 下記フォーマットで `01_Research_Dept/reports/report_[テーマ名].md` を保存し、対応する `inputs/` タスク先頭に `[完了]` を追記する。

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
- `01_Research_Dept/reports/` は中間成果物置き場であり、他部署フォルダや `04_Delivery_Dept/outputs/` へ直接書き込まない（`global-policy.md` 遵守）。
