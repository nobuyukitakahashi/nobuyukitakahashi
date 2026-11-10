---
name: auto-git-sync
description: |
  Mandatory automated Git & GitHub synchronization workflow for cross-device maintenance.
  Ensures that before starting tasks, 'git pull origin main' is executed to fetch updates from other devices,
  and after completing tasks, all changes are automatically committed and pushed via 'git push origin main'
  without waiting for explicit user instructions.
---

# Auto Git Sync Workflow

複数端末でプロジェクトを並行・交代で開発・運用する際の、完全自動Git/GitHub同期プロトコルです。

---

## ワークフロー規則（自律実行原則）

ユーザーから「git pushして」「git pullして」と言われなくても、**自律的に常時実行**します。

### フェーズ 1: 着手前チェック（Pre-Execution Check & Pull）
1. **ステータス確認**:
   ```bash
   git status
   ```
2. **最新変更の自動取り込み**:
   ```bash
   git pull origin main
   ```
   - 他の端末での更新がある場合は自動マージされ、常に最新のコードベース上で作業を開始します。
   - コンフリクトが発生した場合は即座に差分を分析し、ユーザーに状況を報告した上で安全に解決します。

### フェーズ 2: 作業完了時自動コミット＆プッシュ（Post-Execution Commit & Push）
タスクのコード変更、スクリプト作成、ドキュメント更新が完了したら、回答を出力する前に以下を必ず実行します：

1. **未コミット・未追跡ファイルの確認**:
   ```bash
   git status -s
   ```
2. **一時ファイルの整理**:
   作業用の一時ファイル（`temp_*`, `test.*` 等）が残っている場合は削除、または `.gitignore` で除外。
3. **ステージング＆コミット**:
   ```bash
   git add <対象ファイル>
   git commit -m "<タスク内容に応じたプレフィックス付きメッセージ (feat/fix/chore/docs): 変更内容>"
   ```
4. **GitHubへのプッシュ**:
   ```bash
   git push origin main
   ```
5. **完了報告**:
   最終応答にてコミットメッセージとGitHub同期が完了したことをユーザーに明記する。
