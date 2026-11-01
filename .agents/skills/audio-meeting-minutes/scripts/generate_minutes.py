"""
Audio Transcriber & Meeting Minutes CLI Helper
Gemini API / Local Whisper を活用した音声ファイル文字起こし＆議事録生成ヘルパースクリプト
"""

import sys
import os
import argparse
from pathlib import Path

def generate_meeting_minutes_prompt(transcript_text: str, title: str = "", attendees: str = "") -> str:
    prompt = f"""
以下は会議の音声から書き起こされたテキストです。
この内容を分析し、抜け漏れのない詳細で実用的な議事録を日本語のMarkdown形式で作成してください。

# 前提情報
- 会議名/テーマ: {title if title else "未指定"}
- 参加者: {attendees if attendees else "未指定（発言内容から推定してください）"}

# 必須フォーマット
# 📋 [会議名] 議事録

- **日時**: (文脈から推定、または空欄)
- **参加者**: (特定できた参加者)

---

## 📌 エグゼクティブサマリー (3行要約)
1. 
2. 
3. 

---

## 🎯 決定事項 (Decisions)
- [決まったこと・承認されたこと]

---

## ✅ アクションアイテム (ToDo / Next Actions)
- [ ] **[担当者]** タスク内容 (期日: YYYY/MM/DD)

---

## 💬 議題別 詳細議事 (Discussions)
### 議題名
- **論点**: 
- **主な意見・発言**: 
- **結論**: 

---

## 📝 文字起こしテキスト:
{transcript_text}
"""
    return prompt.strip()

def main():
    parser = argparse.ArgumentParser(description="Audio Meeting Minutes Helper")
    parser.add_argument("audio_path", help="Path to the audio/video file or transcript text file")
    parser.add_argument("--title", help="Meeting title", default="")
    parser.add_argument("--attendees", help="Attendees list", default="")
    parser.add_argument("--output", help="Output markdown path", default="")
    args = parser.parse_args()

    audio_file = Path(args.audio_path)
    if not audio_file.exists():
        print(f"Error: File not found: {args.audio_path}", file=sys.stderr)
        sys.exit(1)

    print(f"Target file: {audio_file.name}")
    print(f"Title: {args.title}")
    print(f"Attendees: {args.attendees}")

if __name__ == "__main__":
    main()
