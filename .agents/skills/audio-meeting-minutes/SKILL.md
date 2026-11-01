---
name: audio-meeting-minutes
description: |
  音声・動画の録音ファイル（MP3, WAV, M4A, AAC, MP4, WebM 等）から高精度な文字起こしを実行し、
  決定事項、アクションアイテム（担当者・期日）、重要論点、発言タイムラインを網羅した詳細な議事録（Markdown）を自動生成するスキル。
  Whisper（ローカル/API）およびGoogle GeminiマルチモーダルAPIによる音声解析、長尺音声の自動分割処理、GitHub/Jira連携用タスク抽出に対応。
---

# Audio Meeting Minutes Generator (audio-meeting-minutes)

音声・動画録音ファイルから、**「音声認識・文字起こし（audio-transcriber）」** と **「構造化議事録・アクションアイテム生成（meeting-minutes）」** を統合してワンストップで実行する専門スキルです。

---

## 1. 概要と機能

1. **音声・動画ファイルの文字起こし (Transcription)**
   - MP3, WAV, M4A, AAC, FLAC, OGG, MP4, WebM 等に対応。
   - `google-genai` / `google-generativeai`（Geminiのネイティブ音声認識）または `openai-whisper`（ローカル）を活用。
   - 発言の文脈、専門用語、フィラー（「えーと」「あー」）の自動除去・整形。
2. **詳細議事録の構造化 (Structured Minutes)**
   - 会議基本情報（タイトル、日時、参加者、アジェンダ）
   - **エグゼクティブサマリー（3行要約）**
   - **決定事項（Decisions）**
   - **ToDo・ネクストアクション（Action Items: 担当者・期限・タスク内容）**
   - **議題別の詳細議論と論点（Discussion Points）**
   - **発言タイムライン / 話者別要点**
3. **タスク管理ツール連携**
   - GitHub Issues や Jira にそのままコピー・連携可能なチェックリスト形式で出力。

---

## 2. 議事録の標準出力フォーマット

出力する議事録は以下の構造に従います：

```markdown
# 📋 [会議名 / テーマ] 議事録

- **日時**: YYYY年MM月DD日 HH:MM - HH:MM
- **参加者**: [参加者名、役職など]
- **音声ファイル**: `[対象ファイル名]`
- **記録・要約**: Antigravity (audio-meeting-minutes)

---

## 📌 エグゼクティブサマリー (要約)
1. 
2. 
3. 

---

## 🎯 決定事項 (Decisions)
- [決議内容1]
- [決議内容2]

---

## ✅ アクションアイテム (ToDo / Next Actions)
- [ ] **[担当者]** タスク内容 (期日: YYYY/MM/DD)
- [ ] **[担当者]** タスク内容 (期日: YYYY/MM/DD)

---

## 💬 議題別 詳細議事 (Discussions)

### 議題 1: [アジェンダ名]
- **論点・背景**: 
- **主な意見・発言**:
  - **A氏**: 
  - **B氏**: 
- **結論 / 次のステップ**: 

### 議題 2: [アジェンダ名]
...

---

## ⏱️ 発言タイムライン / 話者ハイライト (任意)
- **[00:02:15]**: 〇〇に関する課題提起
- **[00:15:30]**: 予算方針の確定
```

---

## 3. 実行手順・処理フロー

エージェントが音声ファイルから議事録を作成する際は、以下のステップで進めます。

### ステップ 1: 音声ファイルの確認とメタデータ収集
- ユーザーから渡されたファイルのパス、形式、サイズを確認します。
- 判明している場合は、会議のタイトル・参加者名・前提知識をヒアリングまたは把握します。

### ステップ 2: 文字起こし実行 (Transcription)
以下のいずれかの方法で音声をテキスト化します：

#### 方法 A: Gemini API (マルチモーダル) を利用する場合 (推奨・高速)
Gemini 2.5/3.0系モデルは音声を直接読み取って要約・議事録化が可能です。
```python
# scripts/transcribe_gemini.py を利用
# GEMINI_API_KEY または Vertex AI ADC を使用して直接解析
```

#### 方法 B: Whisper (ローカル実行) を利用する場合
オフライン環境やローカル完結を求める場合：
```bash
python -m whisper "path/to/audio.mp3" --model medium --language ja --output_format txt
```

### ステップ 3: 議事録の整形と保存
- 文字起こしテキストをもとに、上記の「標準出力フォーマット」に当てはめてMarkdown文書を生成。
- 生成した議事録は、対象音声ファイルと同じディレクトリ、または `docs/minutes/YYYY-MM-DD_title.md` に保存します。
