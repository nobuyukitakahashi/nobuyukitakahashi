---
name: colab-api-gpu
description: Google Colab API（colab_api.py / colab CLI）でプラン・残コンピューティングユニット確認や T4/L4/G4/A100 GPU での Python/CUDA 実行・自動ランタイム削除を行うスキル。ローカルPCおよび Remote Agents 共通。
---

# Google Colab GPU 実行（`colab_api.py`）ルール (`/colab-api-gpu`)

WebSocket がブロックされるリモート環境でも HTTPS + SSE と Runtime Proxy 経由で GPU 実行できる [`colab_api.py`](../../scripts/colab_api.py)（同期先 `~/.local/bin/colab_api.py`）を使用します。ローカルPCでは公式 `colab` CLI（`uv tool install --with keyrings.alt google-colab-cli`）と併用可能です。

## 1. 事前設定と認証前提
1. **認証元**: `google-colab-cli` のログイン（`colab usage`）が前提。`colab_api.py` は Linux の `~/.local/share/python_keyring/keyring_pass.cfg`、Remote Agents の `/home/antigravity/upload/colab-keyring.cfg`（または `keyring_pass.cfg`）、さらに Windows/macOS の OS キーリングを**読み取り専用**で参照し、更新キャッシュのみ `~/.config/colab-api/token_cache.json`（`0600`）へ保存する。
2. **クォータプロジェクト（`x-goog-user-project`）**:
   - 設定コマンド：`python ~/.local/bin/colab_api.py config --project <GCPプロジェクトID>`（または環境変数 `COLAB_QUOTA_PROJECT`）。既定候補は既存プロジェクト `gemini-notebook-mcp-515611`。
   - `HTTP 403` で Colab API が未有効の場合は、以下の URL を ` ```text ` コードブロックで案内して有効化してもらう：
     `https://console.cloud.google.com/apis/library/colaboratory.googleapis.com?project=<ID>`
3. **Remote Agents 環境**: 未導入時は `bash .agents/scripts/bootstrap_remote_3kit.sh` を実行する。

## 2. 実行・片付けの厳守事項
1. **秘密情報の非出力**: `keyring_pass.cfg` / `token_cache.json` / トークン・鍵の中身を絶対に `cat` や `print` しない。認証ファイル（`.env`, `token.json`, `client_secret*.json`, `.clasprc.json`, `keyring_pass.cfg` 等）は Colab へ送信しない（ツール側でも自動ブロック）。
2. **読み取り専用チェックでランタイムを作らない**:
   - プラン・起動中ランタイム確認：`python ~/.local/bin/colab_api.py status`
   - 利用可能 GPU 種別確認：`python ~/.local/bin/colab_api.py specs`
   - コンピューティングユニット残高詳細：`colab usage`
   - GPU ランタイムの作成（`run` / `exec`）はユーザーが依頼した時のみ行う。
3. **使い終わったら必ずランタイム削除**:
   - `colab_api.py run <script.py>` / `colab_api.py exec` は完了後に自動で `delete_runtime` を呼ぶ。
   - `--keep` を使った場合も作業完了後に `colab_api.py release` を実行し、`colab_api.py status` で起動中ランタイムが `0` に戻ったことを確認する。
   - `release` は自前台帳（`~/.config/colab-api/ledger.json`）に載っているランタイムのみを対象とし、他人のランタイム・ノートを消さない。
4. **ファイル受け渡しの書式**:
   - `colab_api.py run` は Colab 側の `/content/job` で実行される。
   - 入力：`--in 手元のパス::content/job/ファイル名`、出力：`--out content/job/出力ファイル::手元のパス`（Colab 側パスは先頭の `/` を付けない）。スクリプト側は `/content/job/` へ出力する。
5. **URL 提示ルール**: 承認 URL や Google Cloud Console URL は Markdown リンクにせず、` ```text ` コードブロックに 1 行で出す。

## 3. GitHub モデル等を Colab で動かす際の注意
1. Colab に最初から入っている PyTorch・CUDA は入れ直さない。依存導入時は torch 系を除き、`pyproject.toml` / `requirements.txt` の `git+` 依存を先に入れる。
2. 既導入パッケージを古い版で上書きしない（`pip install --upgrade-strategy only-if-needed` を使用）。
3. `--no-deps` 使用時はモデル読み込み前に主要モジュールを import 確認し、不足分を入れてから本番処理に進む。
4. **T4 は bf16 非対応**：推論 CLI を `--help` で確認し、fp16 非対応なら fp32 を指定する。
