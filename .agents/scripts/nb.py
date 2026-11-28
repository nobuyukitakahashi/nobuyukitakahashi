#!/usr/bin/env python3
"""Gemini Notebook API を使うための小さな道具（Python の標準機能だけで動く）。

ローカル PC でも、Gemini タスクの専用パソコン（ヘッドレス環境）でも動きます。

  python3 nb.py login                 ローカルのブラウザでログインする（ローカル PC 向け）
  python3 nb.py login-start           認可 URL を出す（ヘッドレス VM 向け・Step 1）
  python3 nb.py login-finish <URL>    リダイレクト先 URL からトークンを保存する（Step 2）
  python3 nb.py check                 つながっているか確かめる（ノートブックを 3 冊だけ表示）
  python3 nb.py list                  ノートブックの一覧
  python3 nb.py create "名前"         ノートブックを作る（明示された時だけ）
  python3 nb.py add-text <ID> "名前" "本文"      テキストを入れる
  python3 nb.py add-url  <ID> <URL> ["名前"]     Web ページ・YouTube を入れる
  python3 nb.py upload   <ID> <ファイル> ["名前"] PDF・Word・画像・音声などを入れる
  python3 nb.py sources  <ID>         ソースの一覧
  python3 nb.py mcp                   MCP の中継役（stdio JSON-RPC）

<ID> は notebooks/xxxx でも xxxx だけでもよい。
ソースを入れる命令は、Notebook 側の処理が終わる（ACTIVE か FAILED になる）まで待ってから結果を出す。

置き場（既定: ~/.config/gemini-notebook-api/、環境変数 NOTEBOOK_API_HOME で変更可）:
  client_secret.json  Google Cloud で作った「デスクトップ アプリ」の OAuth クライアント
  pkce_state.json     ヘッドレス認証の一時状態（login-finish 後に自動削除）
  token.json          ログイン情報（0600・外部に出さない）
"""
import base64
import hashlib
import http.server
import json
import mimetypes
import os
import secrets
import ssl
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
import webbrowser

HOME = os.path.normpath(os.path.expanduser(os.environ.get("NOTEBOOK_API_HOME", "~/.config/gemini-notebook-api")))
CLIENT = os.path.join(HOME, "client_secret.json")
TOKEN = os.path.join(HOME, "token.json")
PKCE_STATE = os.path.join(HOME, "pkce_state.json")
BASE = "https://notebook.googleapis.com"
SCOPE = "https://www.googleapis.com/auth/notebook"
EXTRA_TYPES = {
    ".md": "text/markdown",
    ".m4a": "audio/mp4",
    ".csv": "text/csv",
    ".txt": "text/plain",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
}


class NbError(Exception):
    pass


def die(msg):
    raise NbError(msg)


def ssl_context():
    cafile = os.environ.get("SSL_CERT_FILE")
    if cafile and os.path.exists(cafile):
        return ssl.create_default_context(cafile=cafile)
    return ssl.create_default_context()


def ensure_home():
    os.makedirs(HOME, exist_ok=True)
    try:
        os.chmod(HOME, 0o700)
    except OSError:
        pass


def load_client():
    if not os.path.exists(CLIENT):
        die(
            f"OAuth クライアントの JSON がありません: {CLIENT}\n"
            "Google Cloud でダウンロードした「デスクトップ アプリ」の client_secret_….json を、"
            "このパスに配置してください。"
        )
    with open(CLIENT, encoding="utf-8") as f:
        c = json.load(f)
    c = c.get("installed") or c.get("web")
    if not c:
        die("client_secret.json の形が違います。種類「デスクトップ アプリ」で作った JSON を置いてください。")
    return c


def save_json(path, data):
    ensure_home()
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)
    try:
        os.chmod(tmp, 0o600)
    except OSError:
        pass
    os.replace(tmp, path)
    try:
        os.chmod(path, 0o600)
    except OSError:
        pass


def urlopen_json(req, timeout=60):
    with urllib.request.urlopen(req, context=ssl_context(), timeout=timeout) as r:
        return json.load(r)


def exchange_code(c, code, redirect_uri, verifier):
    data = urllib.parse.urlencode(
        {
            "code": code,
            "client_id": c["client_id"],
            "client_secret": c.get("client_secret", ""),
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
            "code_verifier": verifier,
        }
    ).encode()
    req = urllib.request.Request(c.get("token_uri", "https://oauth2.googleapis.com/token"), data=data, method="POST")
    try:
        tok = urlopen_json(req)
    except urllib.error.HTTPError as e:
        die("トークンを受け取れませんでした: " + e.read().decode("utf-8", "replace")[:300])
    if "refresh_token" not in tok:
        die("更新用のトークンが返ってきませんでした。Google 側の権限画面でアクセス許可を再実行してください。")
    if SCOPE not in tok.get("scope", ""):
        die("Notebook の権限にチェックが入っていませんでした。許可画面でチェックを入れてやり直してください。")
    save_json(
        TOKEN,
        {
            "refresh_token": tok["refresh_token"],
            "access_token": tok["access_token"],
            "expiry": time.time() + tok.get("expires_in", 3600) - 60,
            "scope": tok.get("scope"),
        },
    )
    print("ログインできました。トークンを保存しました:", TOKEN)


# ---------- ログイン（ローカルブラウザ版 / ヘッドレス VM 版） ----------

def make_pkce():
    verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).rstrip(b"=").decode()
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()
    state = secrets.token_urlsafe(16)
    return verifier, challenge, state


def login(argv):
    c = load_client()
    hint = argv[0] if argv else ""
    verifier, challenge, state = make_pkce()
    got = {}

    class H(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            if "code" in q or "error" in q:
                body = (
                    "許可を受け取りました。このタブは閉じて戻ってください。"
                    if "code" in q
                    else "許可されませんでした: " + q["error"][0]
                )
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(f"<meta charset=utf-8><p style='font:16px sans-serif'>{body}</p>".encode())
                self.wfile.flush()
                got.update({k: v[0] for k, v in q.items()})
            else:
                self.send_response(404)
                self.end_headers()

        def log_message(self, *a):
            pass

    H.timeout = 10
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), H)
    srv.daemon_threads = True
    redirect = f"http://127.0.0.1:{srv.server_port}/"
    params = {
        "client_id": c["client_id"],
        "redirect_uri": redirect,
        "response_type": "code",
        "scope": SCOPE,
        "access_type": "offline",
        "prompt": "consent",
        "code_challenge": challenge,
        "code_challenge_method": "S256",
        "state": state,
    }
    if hint:
        params["login_hint"] = hint
    url = c.get("auth_uri", "https://accounts.google.com/o/oauth2/auth") + "?" + urllib.parse.urlencode(params)
    print("ブラウザで次のページを開いて、Notebook の権限を許可してください。")
    print(url, flush=True)
    if os.environ.get("NB_NO_BROWSER") != "1":
        webbrowser.open(url)
    t = threading.Thread(target=srv.serve_forever, daemon=True)
    t.start()
    t0 = time.time()
    while "code" not in got and "error" not in got and time.time() - t0 < 600:
        time.sleep(0.5)
    srv.shutdown()
    srv.server_close()
    if "code" not in got:
        die("許可を受け取れませんでした（時間切れか拒否）。もう一度 login してください。")
    if got.get("state") != state:
        die("state が一致しません。もう一度 login してください。")
    exchange_code(c, got["code"], redirect, verifier)


def login_start(argv):
    """ヘッドレス環境用（Step 1）：PKCE URL を出して一時状態を保存する（既定は login_hint なし）。"""
    c = load_client()
    verifier, challenge, state = make_pkce()
    redirect = "http://127.0.0.1:8765/"
    params = {
        "client_id": c["client_id"],
        "redirect_uri": redirect,
        "response_type": "code",
        "scope": SCOPE,
        "access_type": "offline",
        "prompt": "consent",
        "code_challenge": challenge,
        "code_challenge_method": "S256",
        "state": state,
    }
    if argv:
        params["login_hint"] = argv[0]
    save_json(
        PKCE_STATE,
        {
            "verifier": verifier,
            "state": state,
            "redirect_uri": redirect,
            "created_at": time.time(),
        },
    )
    url = c.get("auth_uri", "https://accounts.google.com/o/oauth2/auth") + "?" + urllib.parse.urlencode(params)
    print("下の URL を個人の Google アカウント側のブラウザで開いて許可してください。")
    print("許可後、アドレスバーに表示された http://127.0.0.1:8765/?state=... URL 全体をコピーして")
    print("  python3 nb.py login-finish \"<URL>\"")
    print("へ渡してください（画面に『接続できません』と出ても URL 自体はコピーできます）。\n")
    print(url)


def login_finish(argv):
    """ヘッドレス環境用（Step 2）：リダイレクト先 URL から token.json を保存する。"""
    if not argv:
        die('使い方: python3 nb.py login-finish "http://127.0.0.1:8765/?state=...&code=..."')
    if not os.path.exists(PKCE_STATE):
        die("login-start の記録がありません。先に python3 nb.py login-start を実行してください。")
    with open(PKCE_STATE, encoding="utf-8") as f:
        st = json.load(f)
    parsed = urllib.parse.urlparse(argv[0].strip())
    q = urllib.parse.parse_qs(parsed.query)
    if "error" in q:
        die("認可が拒否されました: " + q["error"][0])
    if "code" not in q:
        die("URL の中に code= が見つかりませんでした。リダイレクト先 URL 全体を渡してください。")
    if q.get("state", [""])[0] != st.get("state"):
        die("state が一致しません。もう一度 login-start からやり直してください。")
    c = load_client()
    exchange_code(c, q["code"][0], st["redirect_uri"], st["verifier"])
    try:
        os.remove(PKCE_STATE)
    except OSError:
        pass


def access_token():
    if not os.path.exists(TOKEN):
        die("まだログインしていません。先に python3 nb.py login-start / login-finish を実行してください。")
    with open(TOKEN, encoding="utf-8") as f:
        t = json.load(f)
    if t.get("access_token") and t.get("expiry", 0) > time.time():
        return t["access_token"]
    c = load_client()
    data = urllib.parse.urlencode(
        {
            "client_id": c["client_id"],
            "client_secret": c.get("client_secret", ""),
            "refresh_token": t["refresh_token"],
            "grant_type": "refresh_token",
        }
    ).encode()
    req = urllib.request.Request(c.get("token_uri", "https://oauth2.googleapis.com/token"), data=data, method="POST")
    try:
        new = urlopen_json(req)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")
        if "invalid_grant" in body:
            die("ログインの期限が切れています（テスト公開のアプリは 7 日で失効する場合があります）。再度ログインしてください。")
        die("トークンの更新に失敗しました: " + body[:300])
    t.update(access_token=new["access_token"], expiry=time.time() + new.get("expires_in", 3600) - 60)
    save_json(TOKEN, t)
    return t["access_token"]


# ---------- REST ----------

def call(method, path, body=None, raw=None, ctype="application/json", headers=None):
    h = {"Authorization": "Bearer " + access_token()}
    data = None
    if body is not None:
        data, h["Content-Type"] = json.dumps(body).encode(), ctype
    elif raw is not None:
        data, h["Content-Type"] = raw, ctype
    h.update(headers or {})
    req = urllib.request.Request(path if path.startswith("http") else BASE + path, data=data, method=method, headers=h)
    try:
        with urllib.request.urlopen(req, context=ssl_context(), timeout=120) as r:
            txt = r.read().decode("utf-8", "replace")
            return r.status, (json.loads(txt) if txt.strip() else {}), r.headers
    except urllib.error.HTTPError as e:
        txt = e.read().decode("utf-8", "replace")
        try:
            return e.code, json.loads(txt), e.headers
        except ValueError:
            return e.code, {"raw": txt[:500]}, e.headers


def nb(x):
    return x if x.startswith("notebooks/") else "notebooks/" + x


def mime_of(p):
    ext = os.path.splitext(p)[1].lower()
    return EXTRA_TYPES.get(ext) or mimetypes.guess_type(p)[0] or "application/octet-stream"


def wait_ready(name, timeout=300):
    t0 = time.time()
    while True:
        st, b, _ = call("GET", "/v1/" + name)
        if st != 200 or b.get("state") in ("ACTIVE", "FAILED") or time.time() - t0 > timeout:
            return st, b
        time.sleep(3)


def show(st, b):
    print(st)
    print(json.dumps(b, ensure_ascii=False, indent=2))
    if st >= 400:
        sys.exit(1)


def rest(cmd, a):
    if cmd in ("check", "list"):
        size = "3" if cmd == "check" else "100"
        st, b, _ = call("GET", "/v1/notebooks?pageSize=" + size)
        if cmd == "check" and st == 200:
            print("つながりました。ノートブック（最近見た順に 3 冊）:")
            for n in b.get("notebooks", []):
                print(" -", n.get("displayName"), "|", n["name"])
            return
        return show(st, b)
    if cmd == "create":
        if not a:
            die('使い方: python3 nb.py create "ノートブック名"')
        st, b, _ = call("POST", "/v1/notebooks", {"displayName": a[0]})
        return show(st, b)
    if cmd == "add-text":
        if len(a) < 3:
            die('使い方: python3 nb.py add-text <ノートブックID> "題名" "本文"')
        st, b, _ = call("POST", f"/v1/{nb(a[0])}/sources", {"displayName": a[1], "textContent": {"content": a[2]}})
    elif cmd == "add-url":
        if len(a) < 2:
            die('使い方: python3 nb.py add-url <ノートブックID> <URL> ["題名"]')
        st, b, _ = call(
            "POST",
            f"/v1/{nb(a[0])}/sources",
            {"displayName": a[2] if len(a) > 2 else a[1], "webContent": {"url": a[1]}},
        )
    elif cmd == "upload":
        if len(a) < 2:
            die('使い方: python3 nb.py upload <ノートブックID> <ファイルパス> ["題名"]')
        with open(a[1], "rb") as f:
            raw_bytes = f.read()
        q = {"uploadType": "media", "source.displayName": a[2] if len(a) > 2 else os.path.basename(a[1])}
        st, b, _ = call(
            "POST",
            f"/upload/v1/{nb(a[0])}/sources:upload?" + urllib.parse.urlencode(q),
            raw=raw_bytes,
            ctype=mime_of(a[1]),
        )
    elif cmd == "sources":
        if not a:
            die("使い方: python3 nb.py sources <ノートブックID>")
        st, b, _ = call("GET", f"/v1/{nb(a[0])}/sources?pageSize=100")
        return show(st, b)
    else:
        print(__doc__)
        return
    if st == 200:
        st, b = wait_ready(b.get("source", b)["name"])
    show(st, b)


# ---------- MCP の中継役 ----------

def mcp():
    url = BASE + "/mcp"
    version = "2026-07-28"
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except ValueError:
            continue
        if "id" not in msg:
            continue
        if msg.get("method") == "initialize":
            version = msg.get("params", {}).get("protocolVersion") or version
        try:
            token = access_token()
        except Exception as e:
            sys.stdout.write(
                json.dumps({"jsonrpc": "2.0", "id": msg["id"], "error": {"code": -32000, "message": str(e)}}, ensure_ascii=False)
                + "\n"
            )
            sys.stdout.flush()
            continue
        h = {
            "Authorization": "Bearer " + token,
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
            "MCP-Protocol-Version": version,
            "Mcp-Method": msg.get("method", ""),
        }
        req = urllib.request.Request(url, data=json.dumps(msg).encode(), method="POST", headers=h)
        try:
            with urllib.request.urlopen(req, context=ssl_context(), timeout=120) as r:
                txt = r.read().decode("utf-8", "replace")
                if "text/event-stream" in r.headers.get("Content-Type", ""):
                    txt = "\n".join(l[5:].strip() for l in txt.splitlines() if l.startswith("data:"))
                out = json.loads(txt)
        except urllib.error.HTTPError as e:
            out = {"jsonrpc": "2.0", "id": msg["id"], "error": {"code": -32000, "message": f"HTTP {e.code}: {e.read().decode('utf-8', 'replace')[:300]}"}}
        except Exception as e:
            out = {"jsonrpc": "2.0", "id": msg["id"], "error": {"code": -32000, "message": str(e)[:300]}}
        sys.stdout.write(json.dumps(out, ensure_ascii=False) + "\n")
        sys.stdout.flush()


def main():
    for stream in (sys.stdin, sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except Exception:
            pass
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print(__doc__)
        return
    cmd, a = sys.argv[1], sys.argv[2:]
    try:
        if cmd == "login":
            login(a)
        elif cmd == "login-start":
            login_start(a)
        elif cmd == "login-finish":
            login_finish(a)
        elif cmd == "mcp":
            mcp()
        else:
            rest(cmd, a)
    except NbError as e:
        print(e, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
