#!/usr/bin/env python3
"""Google Colab の GPU をホスト型 API（HTTPS + SSE）経由で実行する CLI（Python 標準機能のみ）。

WebSocket がブロックされる環境でも、`colab exec` の代わりに HTTPS 通信だけで
ランタイムの作成・ファイルの受け渡し・Python スクリプト実行・自動削除を行えます。

事前に、公式の Colab CLI（例: `uv tool install --with keyrings.alt google-colab-cli`
＋ `colab usage` でのログイン）と、ご自身の Google Cloud プロジェクト ID の設定が必要です。

設定方法（どれか 1 つ）:
  python3 colab_api.py config --project <あなたのGCPプロジェクトID>
  または環境変数 COLAB_QUOTA_PROJECT=<あなたのGCPプロジェクトID>
  またはコマンド引数 --project <あなたのGCPプロジェクトID>

主なコマンド:
  python3 colab_api.py status
  python3 colab_api.py specs
  python3 colab_api.py run job.py --gpu T4 --in input.txt::content/job/input.txt --out content/job/out.json::./out.json
  python3 colab_api.py exec --gpu T4 "import torch; print(torch.cuda.is_available())"
  python3 colab_api.py release [runtimes/...]
"""
import argparse
import base64
import configparser
import datetime as dt
import http.client
import json
import os
import shutil
import ssl
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from pathlib import Path

HOME_CFG = Path(os.path.expanduser(os.environ.get("COLAB_API_HOME", "~/.config/colab-api")))
CONFIG_PATH = HOME_CFG / "config.json"
TOKEN_CACHE_PATH = HOME_CFG / "token_cache.json"
LEDGER_PATH = HOME_CFG / "ledger.json"

DEFAULT_KEYRING_PATH = Path(
    os.path.expanduser(os.environ.get("COLAB_KEYRING_PATH", "~/.local/share/python_keyring/keyring_pass.cfg"))
)
MCP_URL = "https://colaboratory.googleapis.com/mcp"
CHUNK_BYTES = 30 * 1024 * 1024  # Runtime Proxy PUT 上限（50MB 未満）に合わせた 30MB チャンク

GPU_MAP = {
    "CPU": ("VARIANT_CPU", "NONE"),
    "T4": ("VARIANT_GPU", "T4"),
    "L4": ("VARIANT_GPU", "L4"),
    "G4": ("VARIANT_GPU", "G4"),
    "A100": ("VARIANT_GPU", "A100"),
}

BLOCKED_NAMES = (
    ".env",
    "token.json",
    "token_cache.json",
    "keyring_pass.cfg",
    "client_secret",
    ".clasprc.json",
    "credentials",
    "application_default_credentials",
    "pkce_state.json",
)
BLOCKED_PARTS = (".secrets", ".ssh", ".config/gemini-notebook-api", ".config/colab-api")


class ColabApiError(Exception):
    pass


def ssl_context():
    cafile = os.environ.get("SSL_CERT_FILE")
    if cafile and os.path.exists(cafile):
        return ssl.create_default_context(cafile=cafile)
    return ssl.create_default_context()


def ensure_cfg_dir():
    HOME_CFG.mkdir(parents=True, exist_ok=True)
    try:
        os.chmod(HOME_CFG, 0o700)
    except OSError:
        pass


def write_secure_json(path: Path, data):
    ensure_cfg_dir()
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    try:
        os.chmod(tmp, 0o600)
    except OSError:
        pass
    os.replace(tmp, path)
    try:
        os.chmod(path, 0o600)
    except OSError:
        pass


def load_json_or(path: Path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def now_iso():
    return dt.datetime.now().astimezone().isoformat(timespec="seconds")


def resolve_quota_project(cli_project=None):
    if cli_project:
        return cli_project.strip()
    env_p = os.environ.get("COLAB_QUOTA_PROJECT", "").strip()
    if env_p:
        return env_p
    cfg = load_json_or(CONFIG_PATH, {})
    cfg_p = str(cfg.get("quota_project", "")).strip()
    if cfg_p:
        return cfg_p
    upload_dir = Path(os.environ.get("ANTIGRAVITY_UPLOAD_DIR", "/home/antigravity/upload"))
    for cand in (upload_dir / "colab-config.json",):
        u_cfg = load_json_or(cand, {})
        u_p = str(u_cfg.get("quota_project", "")).strip()
        if u_p:
            return u_p
    raise ColabApiError(
        "Google Cloud のプロジェクト ID（x-goog-user-project）が未設定です。\n"
        "次のいずれかで、ご自身のプロジェクト ID を指定してください：\n"
        "  python3 colab_api.py config --project <あなたのGCPプロジェクトID>\n"
        "  または環境変数 COLAB_QUOTA_PROJECT=<あなたのGCPプロジェクトID>\n"
        "  または --project <あなたのGCPプロジェクトID>"
    )


# ---------- 認証（google-colab-cli のキーリングを読み取り専用で参照） ----------

def _decode_keyring_value(raw_val: str):
    val = raw_val.strip()
    if (val.startswith("b'") and val.endswith("'")) or (val.startswith('b"') and val.endswith('"')):
        val = val[2:-1]
    for decoder in (base64.b64decode, base64.urlsafe_b64decode):
        try:
            padded = val + "=" * (-len(val) % 4)
            decoded = decoder(padded)
            txt = decoded.decode("utf-8")
            return json.loads(txt)
        except Exception:
            continue
    try:
        return json.loads(val)
    except Exception as e:
        raise ColabApiError(f"キーリング内の認証 JSON を読み取れませんでした: {e}") from e


def _read_os_keyring_fallback():
    """Windows Credential Manager / macOS Keychain fallback when keyring_pass.cfg is absent."""
    try:
        import keyring  # type: ignore
        raw_val = keyring.get_password("google-colab-cli", "oauth_token")
        if raw_val:
            return _decode_keyring_value(raw_val)
    except Exception:
        pass

    # Fallback via uv's google-colab-cli tool venv Python (reads OS keyring without printing secrets to user)
    py_candidates = []
    if sys.platform == "win32":
        appdata = os.environ.get("APPDATA", "")
        if appdata:
            py_candidates.append(Path(appdata) / "uv" / "tools" / "google-colab-cli" / "Scripts" / "python.exe")
    else:
        py_candidates.append(Path(os.path.expanduser("~/.local/share/uv/tools/google-colab-cli/bin/python")))
    colab_exe = shutil.which("colab")
    if colab_exe:
        p = Path(colab_exe).resolve()
        for rel in ("python.exe", "python", "python3"):
            cand = p.parent / rel
            if cand.exists():
                py_candidates.append(cand)

    probe_code = (
        "import keyring, sys; "
        "v = keyring.get_password('google-colab-cli', 'oauth_token'); "
        "sys.stdout.write(v if v else '')"
    )
    for py_bin in py_candidates:
        if not py_bin.exists():
            continue
        try:
            proc = subprocess.run(
                [str(py_bin), "-c", probe_code],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if proc.returncode == 0 and proc.stdout.strip():
                return _decode_keyring_value(proc.stdout.strip())
        except Exception:
            continue
    return None


def read_keyring_creds():
    upload_dir = Path(os.environ.get("ANTIGRAVITY_UPLOAD_DIR", "/home/antigravity/upload"))
    keyring_candidates = [
        DEFAULT_KEYRING_PATH,
        upload_dir / "colab-keyring.cfg",
        upload_dir / "keyring_pass.cfg",
    ]
    keyring_path = next((p for p in keyring_candidates if p.exists() and p.is_file()), None)
    if keyring_path is None:
        creds = _read_os_keyring_fallback()
        if creds and (creds.get("refresh_token") or creds.get("token")):
            return creds
        raise ColabApiError(
            f"Colab CLI の認証情報が見つかりません: {DEFAULT_KEYRING_PATH}\n"
            "先に `uv tool install --with keyrings.alt google-colab-cli` を入れ、"
            "`colab usage` で個人の Google アカウントにログインしてください。"
        )
    cp = configparser.RawConfigParser()
    cp.read(keyring_path, encoding="utf-8")
    candidates = [("google_2Dcolab_2Dcli", "oauth_5ftoken")]
    for sec in cp.sections():
        for opt in cp.options(sec):
            if "colab" in sec.lower() and "oauth" in opt.lower():
                candidates.append((sec, opt))
    raw_val = None
    for sec, opt in candidates:
        if cp.has_option(sec, opt):
            raw_val = cp.get(sec, opt)
            break
    if not raw_val:
        raise ColabApiError(
            f"キーリングファイル内に google-colab-cli のトークン項目が見つかりません: {keyring_path}"
        )
    creds = _decode_keyring_value(raw_val)
    if not creds.get("refresh_token") and not creds.get("token"):
        raise ColabApiError("キーリング内の認証情報にトークン項目が含まれていません。`colab usage` で再ログインしてください。")
    return creds


def _parse_expiry_epoch(expiry_val):
    if isinstance(expiry_val, (int, float)):
        return float(expiry_val)
    if isinstance(expiry_val, str) and expiry_val.strip():
        try:
            s = expiry_val.strip().replace("Z", "+00:00")
            return dt.datetime.fromisoformat(s).timestamp()
        except Exception:
            return 0.0
    return 0.0


def refresh_access_token(creds):
    token_uri = creds.get("token_uri") or "https://oauth2.googleapis.com/token"
    if not creds.get("refresh_token") or not creds.get("client_id"):
        raise ColabApiError("キーリング内にリフレッシュ用の情報が不足しています。`colab usage` を再実行してください。")
    form = {
        "client_id": creds["client_id"],
        "refresh_token": creds["refresh_token"],
        "grant_type": "refresh_token",
    }
    if creds.get("client_secret"):
        form["client_secret"] = creds["client_secret"]
    req = urllib.request.Request(token_uri, data=urllib.parse.urlencode(form).encode(), method="POST")
    try:
        with urllib.request.urlopen(req, context=ssl_context(), timeout=30) as r:
            res = json.load(r)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")
        if "invalid_grant" in body:
            raise ColabApiError("Colab 認証の期限が切れています。`colab usage` で再ログインしてください。") from e
        raise ColabApiError(f"アクセストークンの更新に失敗しました（HTTP {e.code}）") from e
    token = res.get("access_token")
    if not token:
        raise ColabApiError("トークン更新の応答にアクセストークンが含まれませんでした。")
    exp = time.time() + int(res.get("expires_in", 3600)) - 120
    write_secure_json(TOKEN_CACHE_PATH, {"access_token": token, "expiry": exp, "updated_at": now_iso()})
    return token


def get_access_token(force_refresh=False):
    if not force_refresh:
        cached = load_json_or(TOKEN_CACHE_PATH, {})
        if cached.get("access_token") and float(cached.get("expiry", 0)) > time.time() + 60:
            return cached["access_token"]
    creds = read_keyring_creds()
    if not force_refresh and creds.get("token"):
        exp = _parse_expiry_epoch(creds.get("expiry"))
        if exp > time.time() + 120:
            return creds["token"]
    return refresh_access_token(creds)


# ---------- Hosted MCP 呼び出し ----------

def mcp_call(tool: str, arguments: dict, quota_project: str, timeout=660):
    payload = json.dumps(
        {"jsonrpc": "2.0", "id": str(uuid.uuid4()), "method": "tools/call", "params": {"name": tool, "arguments": arguments}}
    ).encode()
    refreshed = False
    raw = ""
    for attempt in range(5):
        token = get_access_token(force_refresh=refreshed)
        hdrs = {
            "Authorization": "Bearer " + token,
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
            "x-goog-user-project": quota_project,
        }
        try:
            req = urllib.request.Request(MCP_URL, data=payload, headers=hdrs, method="POST")
            with urllib.request.urlopen(req, context=ssl_context(), timeout=timeout) as r:
                raw = r.read().decode("utf-8", "replace")
            break
        except urllib.error.HTTPError as e:
            msg = e.read().decode("utf-8", "replace")[:600]
            if e.code == 401 and not refreshed:
                refreshed = True
                continue
            if e.code in (429, 503) and attempt < 4:
                time.sleep(2 ** attempt * 3)
                continue
            raise ColabApiError(f"{tool}: HTTP {e.code} {msg}") from e
    if raw.lstrip().startswith("event:") or "\ndata:" in raw:
        datas = [l[5:].strip() for l in raw.splitlines() if l.startswith("data:")]
        msgs = []
        for d in datas:
            if not d:
                continue
            try:
                msgs.append(json.loads(d))
            except json.JSONDecodeError:
                continue
        finals = [m for m in msgs if isinstance(m, dict) and ("result" in m or "error" in m)]
        if not finals:
            raise ColabApiError(f"{tool}: SSE 応答を解釈できませんでした")
        final = finals[-1]
    else:
        final = json.loads(raw)
    if "error" in final:
        raise ColabApiError(f"{tool}: {final['error']}")
    res = final.get("result", {})
    if res.get("isError"):
        raise ColabApiError(f"{tool}: " + " ".join(c.get("text", "") for c in res.get("content", [])))
    if "structuredContent" in res:
        return res["structuredContent"]
    txt = "".join(c.get("text", "") for c in res.get("content", []))
    try:
        return json.loads(txt)
    except json.JSONDecodeError:
        return {"text": txt}


# ---------- 台帳と安全チェック ----------

def load_ledger():
    return load_json_or(LEDGER_PATH, {})


def save_ledger(led):
    write_secure_json(LEDGER_PATH, led)


def mark_ledger(name, **kw):
    led = load_ledger()
    led.setdefault(name, {}).update(kw)
    save_ledger(led)


def pid_alive(pid):
    if not pid:
        return False
    try:
        os.kill(int(pid), 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    except OSError:
        return False


def check_safe_local_path(path_str: str, allow_private=False):
    if allow_private:
        return
    p = str(Path(path_str).resolve())
    low = p.lower().replace("\\", "/")
    fname = Path(p).name.lower()
    if any(part in low for part in BLOCKED_PARTS) or any(b in fname for b in BLOCKED_NAMES):
        raise ColabApiError(
            f"秘密情報や認証ファイルの送信を防ぐため停止しました: {p}\n"
            "本当に送信したい場合のみ --allow-private を付けて実行してください。"
        )


# ---------- ランタイム操作 ----------

def alive_runtimes(quota_project: str):
    res = mcp_call("list_runtimes", {}, quota_project)
    return {r["name"]: r for r in res.get("runtimes", [])}


def ensure_runtime(gpu: str, highmem: bool, quota_project: str, reuse=True):
    variant, accel = GPU_MAP[gpu]
    shape = "SHAPE_HIGHMEM" if (highmem and gpu in ("CPU", "T4", "A100")) else "SHAPE_STANDARD"
    want = (variant, accel, shape)
    led = load_ledger()
    live = alive_runtimes(quota_project)
    if reuse:
        for name, entry in led.items():
            if name not in live or entry.get("state") == "released":
                continue
            spec = live[name].get("runtimeSpec", {})
            busy_elsewhere = (
                entry.get("state") in ("busy", "creating")
                and entry.get("pid") != os.getpid()
                and pid_alive(entry.get("pid"))
            )
            if not busy_elsewhere and (spec.get("variant"), spec.get("accelerator"), spec.get("shape")) == want:
                mark_ledger(name, state="busy", pid=os.getpid(), last_used=now_iso())
                print(f"再利用: {name}", file=sys.stderr)
                return name
    rid = f"colab-api-{uuid.uuid4().hex[:12]}"
    name = f"runtimes/{rid}"
    mark_ledger(name, state="creating", gpu=gpu, shape=shape, created=now_iso(), pid=os.getpid())
    t0 = time.time()
    req_id = str(uuid.uuid4())
    for attempt in range(4):
        try:
            mcp_call(
                "create_runtime",
                {
                    "requestId": req_id,
                    "runtimeId": rid,
                    "runtime": {"runtimeSpec": {"variant": variant, "accelerator": accel, "shape": shape}},
                },
                quota_project,
            )
            break
        except ColabApiError as e:
            if "DEADLINE_EXCEEDED" in str(e) and attempt < 3:
                continue
            mark_ledger(name, state="released", note=f"作成失敗: {str(e)[:200]}")
            raise
    mark_ledger(name, state="busy", ready_sec=round(time.time() - t0, 1))
    print(f"作成: {name}（{gpu} / {shape}・{time.time() - t0:.1f}秒）", file=sys.stderr)
    return name


def release_runtime(name: str, quota_project: str):
    mcp_call("delete_runtime", {"name": name, "allowMissing": True}, quota_project)
    led = load_ledger()
    entry = led.get(name, {})
    mins = ""
    if entry.get("created"):
        try:
            mins = round((dt.datetime.now().astimezone() - dt.datetime.fromisoformat(entry["created"])).total_seconds() / 60, 1)
        except Exception:
            mins = ""
    mark_ledger(name, state="released", released=now_iso(), minutes=mins, pid=None)
    print(f"削除: {name}", file=sys.stderr)


# ---------- Runtime Proxy（ファイル転送） ----------

class RuntimeProxy:
    def __init__(self, name: str, quota_project: str):
        self.name = name
        self.quota_project = quota_project
        self.url = ""
        self.tok = ""
        self.exp = 0.0
        self.refresh()

    def refresh(self):
        ci = mcp_call("get_runtime", {"name": self.name}, self.quota_project)["connectionInfo"]
        self.url = ci["url"].rstrip("/")
        self.tok = ci["token"]
        self.exp = time.time() + 50 * 60

    def req(self, method: str, path: str, body=None, ctype=None):
        if time.time() > self.exp:
            self.refresh()
        hdrs = {"X-Colab-Runtime-Proxy-Token": self.tok}
        if ctype:
            hdrs["Content-Type"] = ctype
        for attempt in range(2):
            try:
                r_obj = urllib.request.Request(self.url + path, data=body, headers=hdrs, method=method)
                with urllib.request.urlopen(r_obj, context=ssl_context(), timeout=600) as r:
                    return r.read()
            except urllib.error.HTTPError as e:
                if e.code == 404 and attempt == 0 and method == "PUT":
                    self.refresh()
                    hdrs["X-Colab-Runtime-Proxy-Token"] = self.tok
                    continue
                raise ColabApiError(f"{method} {path}: HTTP {e.code} {e.read().decode('utf-8', 'replace')[:300]}") from e

    def mkdirs(self, remote_dir: str):
        parts = [p for p in remote_dir.strip("/").split("/") if p]
        for i in range(1, len(parts) + 1):
            try:
                self.req(
                    "PUT",
                    "/api/contents/" + "/".join(parts[:i]),
                    json.dumps({"type": "directory"}).encode(),
                    "application/json",
                )
            except ColabApiError as e:
                if "HTTP 409" not in str(e):
                    raise

    def upload(self, local_path: str, remote_path: str):
        data = Path(local_path).read_bytes()
        remote = remote_path.lstrip("/")
        if "/" in remote:
            self.mkdirs(remote.rsplit("/", 1)[0])
        if len(data) <= CHUNK_BYTES:
            body = {"type": "file", "format": "base64", "content": base64.b64encode(data).decode()}
            self.req("PUT", "/api/contents/" + remote, json.dumps(body).encode(), "application/json")
            return
        chunk_idx = 0
        for i in range(0, len(data), CHUNK_BYTES):
            chunk_idx += 1
            last = i + CHUNK_BYTES >= len(data)
            body = {
                "type": "file",
                "format": "base64",
                "content": base64.b64encode(data[i : i + CHUNK_BYTES]).decode(),
                "chunk": -1 if last else chunk_idx,
            }
            self.req("PUT", "/api/contents/" + remote, json.dumps(body).encode(), "application/json")

    def download(self, remote_path: str, local_path: str):
        out = Path(local_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(self.req("GET", "/files/" + remote_path.lstrip("/")))


# ---------- コード実行 ----------

def execute_cell(name: str, code: str, quota_project: str, session_tag=None):
    session = f"{name}/sessions/{session_tag or 'job-' + uuid.uuid4().hex[:8]}"
    return mcp_call(
        "execute_code",
        {"session": session, "executionId": str(uuid.uuid4()), "code": code},
        quota_project,
        timeout=300,
    )


def launch_and_wait(px: RuntimeProxy, name: str, script_name: str, pip_pkgs: str, max_min: int, quota_project: str):
    pip_part = f"pip install -q {pip_pkgs} && " if pip_pkgs else ""
    shell = f"cd /content/job && rm -f .exit job.log && ( ( {pip_part}python -u {script_name} ) > job.log 2>&1; echo $? > .exit ) &"
    execute_cell(name, "import subprocess; subprocess.Popen(" + repr(shell) + ", shell=True, start_new_session=True); 'started'", quota_project)
    t0, last_keepalive = time.time(), 0.0
    while True:
        try:
            exit_code = int(px.req("GET", "/files/content/job/.exit").decode().strip() or "1")
            break
        except ColabApiError as e:
            if "HTTP 404" not in str(e):
                raise
        except (http.client.HTTPException, urllib.error.URLError, ConnectionError, TimeoutError):
            pass
        el = time.time() - t0
        if el > max_min * 60:
            raise ColabApiError(f"{max_min} 分以内に終了しませんでした（--max-min で延長可能）")
        if el - last_keepalive >= 120:
            last_keepalive = el
            try:
                execute_cell(name, "1", quota_project, session_tag="keepalive")
            except Exception:
                pass
        mark_ledger(name, last_used=now_iso())
        time.sleep(5)
    try:
        log_txt = px.req("GET", "/files/content/job/job.log").decode("utf-8", "replace")
    except ColabApiError:
        log_txt = ""
    return exit_code, log_txt


# ---------- サブコマンド ----------

def cmd_config(a):
    cfg = load_json_or(CONFIG_PATH, {})
    cfg["quota_project"] = a.project.strip()
    write_secure_json(CONFIG_PATH, cfg)
    print(f"設定を保存しました: {CONFIG_PATH} (quota_project={cfg['quota_project']})")


def cmd_status(a):
    qp = resolve_quota_project(a.project)
    sub = mcp_call("get_subscription", {}, qp)
    live = alive_runtimes(qp)
    led = load_ledger()
    active_ledger = sum(1 for k, v in led.items() if k in live and v.get("state") != "released")
    print("Subscription:", json.dumps(sub, ensure_ascii=False))
    print(f"Active runtimes: {len(live)}")
    for rname, r in live.items():
        spec = r.get("runtimeSpec", {})
        tag = "ledger" if rname in led else "external"
        print(f" - {rname} ({spec.get('accelerator')} / {spec.get('shape')} / {tag})")
    print(f"Ledger tracked active ({LEDGER_PATH}): {active_ledger}")


def cmd_specs(a):
    qp = resolve_quota_project(a.project)
    res = mcp_call("list_runtime_specs", {}, qp)
    print(json.dumps(res, ensure_ascii=False, indent=2))


def cmd_run(a):
    qp = resolve_quota_project(a.project)
    script = Path(a.script)
    if not script.is_file():
        raise ColabApiError(f"実行スクリプトが見つかりません: {script}")
    check_safe_local_path(str(script), allow_private=a.allow_private)
    for item in a.inputs:
        check_safe_local_path(item.split("::")[0], allow_private=a.allow_private)
    t0 = time.time()
    name = ensure_runtime(a.gpu, a.highmem, qp, reuse=not a.fresh)
    ok = False
    try:
        px = RuntimeProxy(name, qp)
        px.mkdirs("content/job")
        for item in a.inputs:
            local, _, remote = item.partition("::")
            remote = remote or f"content/job/{Path(local).name}"
            px.upload(local, remote)
        px.upload(str(script), "content/job/" + script.name)
        code, log_txt = launch_and_wait(px, name, script.name, a.pip, a.max_min, qp)
        lines = [l.rsplit("\r", 1)[-1] for l in log_txt.split("\n")]
        print("\n".join(lines)[-6000:])
        if a.log:
            Path(a.log).write_text(log_txt, encoding="utf-8")
        missing = []
        for item in a.outputs:
            remote, _, local = item.partition("::")
            try:
                px.download(remote.lstrip("/"), local or Path(remote).name)
            except ColabApiError as e:
                missing.append(remote)
                print(f"ダウンロード失敗: {remote} ({str(e)[:120]})", file=sys.stderr)
        ok = code == 0 and not missing
        print(f"終了コード {code}（所要 {time.time() - t0:.1f} 秒）", file=sys.stderr)
    finally:
        if a.keep:
            mark_ledger(name, state="kept", pid=None, last_used=now_iso())
            print(f"維持: {name}（不要になったら release で削除してください）", file=sys.stderr)
        else:
            release_runtime(name, qp)
    sys.exit(0 if ok else 1)


def cmd_exec(a):
    qp = resolve_quota_project(a.project)
    name = ensure_runtime(a.gpu, a.highmem, qp, reuse=not a.fresh)
    try:
        if a.shell:
            code = "import subprocess, sys; r = subprocess.run(" + repr(a.code) + ", shell=True, text=True); sys.exit(r.returncode)"
        else:
            code = a.code
        res = execute_cell(name, code, qp)
        print(json.dumps(res, ensure_ascii=False, indent=2))
    finally:
        if a.keep:
            mark_ledger(name, state="kept", pid=None, last_used=now_iso())
        else:
            release_runtime(name, qp)


def cmd_release(a):
    qp = resolve_quota_project(a.project)
    led = load_ledger()
    live = alive_runtimes(qp)
    targets = [a.name] if a.name else [n for n, e in led.items() if e.get("state") != "released"]
    released = 0
    for n in targets:
        if n not in led:
            raise ColabApiError(f"停止しました: {n} はこのツールが作成したランタイム（台帳）にありません。")
        if n in live:
            release_runtime(n, qp)
            released += 1
        else:
            mark_ledger(n, state="released", released=now_iso(), note="既に終了", pid=None)
    if released == 0:
        print("返却対象のランタイムはありませんでした。")


def main():
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except Exception:
            pass
    p = argparse.ArgumentParser(description="Google Colab API 経由 GPU 実行 CLI（HTTPS + SSE）")
    p.add_argument("--project", default=None, help="Google Cloud プロジェクト ID（未指定時は COLAB_QUOTA_PROJECT か config.json）")
    sp = p.add_subparsers(dest="cmd", required=True)

    c = sp.add_parser("config", help="使用する Google Cloud プロジェクト ID を保存")
    c.add_argument("--project", required=True, dest="project")
    c.set_defaults(f=cmd_config)

    st = sp.add_parser("status", help="プラン・起動中ランタイム・台帳を確認（ランタイムは作成しません）")
    st.set_defaults(f=cmd_status)

    spcs = sp.add_parser("specs", help="利用可能な CPU/GPU/TPU 一覧を取得（ランタイムは作成しません）")
    spcs.set_defaults(f=cmd_specs)

    r = sp.add_parser("run", help="Python スクリプトをアップロードして実行し、結果を回収後に自動削除")
    r.add_argument("script")
    r.add_argument("--gpu", default="T4", choices=list(GPU_MAP))
    r.add_argument("--highmem", action="store_true")
    r.add_argument("--in", dest="inputs", action="append", default=[], help="手元のパス[::Colab側パス]")
    r.add_argument("--out", dest="outputs", action="append", default=[], help="Colab側パス::手元のパス")
    r.add_argument("--pip", default="")
    r.add_argument("--keep", action="store_true")
    r.add_argument("--fresh", action="store_true")
    r.add_argument("--allow-private", action="store_true")
    r.add_argument("--max-min", type=int, default=180)
    r.add_argument("--log", default="")
    r.set_defaults(f=cmd_run)

    ex = sp.add_parser("exec", help="短い Python コード（または --shell でシェルコマンド）を単発実行")
    ex.add_argument("code")
    ex.add_argument("--gpu", default="T4", choices=list(GPU_MAP))
    ex.add_argument("--highmem", action="store_true")
    ex.add_argument("--shell", action="store_true")
    ex.add_argument("--keep", action="store_true")
    ex.add_argument("--fresh", action="store_true")
    ex.set_defaults(f=cmd_exec)

    rl = sp.add_parser("release", help="このツールが作成して台帳に残っているランタイムだけを終了する")
    rl.add_argument("name", nargs="?")
    rl.set_defaults(f=cmd_release)

    a = p.parse_args()
    try:
        a.f(a)
    except ColabApiError as e:
        print(e, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
