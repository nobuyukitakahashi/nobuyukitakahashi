---
name: clasp-gas-deploy
description: clasp 3系で Google Apps Script（GAS）プロジェクトの作成・取得（pull）・反映（push）・デプロイ（deploy）・一覧確認を行う手順と安全ルール。ローカルPCおよび Remote Agents 共通。
---

# clasp（GAS）プロジェクト作成・push / pull・deploy (`/clasp-gas-deploy`)

## 1. 環境別コマンド前提
- **Windows ローカルPC**: PowerShell の ExecutionPolicy 制約を避けるため `clasp.cmd` を使用（Node 22+、`npm.cmd install -g @google/clasp@3` で導入済み）。
- **macOS / Linux / Remote Agents**: `clasp` を使用。Remote Agents（クラウド Linux VM）では未導入なら `bash .agents/scripts/bootstrap_remote_3kit.sh` で自動導入（`/home/antigravity/upload/clasprc.json` があれば `~/.clasprc.json` へ自動シード）。
- **前提**: Google Apps Script API（`https://script.google.com/home/usersettings`）がオンであること。

## 2. 運用・安全ルール（厳守）
1. **新規 GAS はユーザー依頼時のみ作成**: テスト確認だけで勝手に `clasp create` を実行しない。
2. **秘密情報の非出力**: `~/.clasprc.json` のトークン文字列は stdout やログへ絶対に出力せず、Git へも絶対に含めない。
3. **初回ログイン手順**:
   - **ローカルPC**: `clasp.cmd login`（または `clasp login`）でブラウザ認可。
   - **Remote Agents（ヘッドレス）**: `clasp login --no-localhost` を待機させ、承認 URL を下記のコードブロック形式で案内し、認可後のリダイレクト先 URL 全体を貼り戻してもらう（承認後の「接続が拒否されました」は正常）。
   - 期限切れ時は `clasp list` を1回実行して自動更新を試し、それでも `invalid_grant` なら再ログインを案内する。
4. **作成・反映・公開の手順**:
   - 新規作成：`clasp create` は **`.clasp.json` が無い新しい空のフォルダ** で実行する（古い `.clasp.json` が残っていると失敗する）。
   - `clasp create` は `appsscript.json` を既定内容で上書きするため、用意した `appsscript.json` は **`create` の後に置き直してから `clasp push --force` → `clasp deploy`** の順で進める。
   - 既存取り込みは `clasp clone <scriptId>`、取得は `clasp pull`、反映は `clasp push`、公開/版更新は `clasp deploy`、一覧は `clasp list`。
5. **公開範囲の既定は `MYSELF`（自分だけ）**: `appsscript.json` の `webapp.access` は明示されない限り `"MYSELF"` を使う。`"ANYONE_ANONYMOUS"` はユーザーが「誰でもログインなしで開けるように」と明示した時のみ使用する。
6. **URL 提示ルール**: 承認 URL・Google Apps Script 設定 URL・デプロイ後の `/exec` URL・スプレッドシート URL は Markdown リンクにせず、1 URL につき 1 つの ` ```text ` コードブロックで 1 行そのまま提示する。
