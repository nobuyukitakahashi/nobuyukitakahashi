#!/usr/bin/env node
/**
 * Gemini Notebook Official API Local MCP Server (stdio JSON-RPC 2.0)
 *
 * Bridges Antigravity / MCP clients to Google's official Gemini Notebook REST API
 * (https://notebook.googleapis.com/v1 & /upload/v1) with automatic OAuth 2.0
 * refresh-token rotation so tokens never need manual hourly pasting.
 *
 * Zero external npm dependencies (Node.js 18+ built-in fetch/http/crypto/fs only).
 * Supports both Content-Length header framing and newline-delimited JSON-RPC.
 * Supports Windows, macOS, and Linux.
 *
 * Hybrid architecture note:
 * - Official Gemini Notebook API (Public Preview) covers notebook CRUD/rename and
 *   fast/reliable source ingestion (Web URL, YouTube, inline Text/Markdown, local
 *   file upload up to 200 MiB) + source state inspection.
 * - Q&A / RAG querying and Audio Overview generation are not yet exposed in the
 *   Public Preview API; keep `notebooklm-research` MCP alongside this server for those.
 */

const fs = require("fs");
const path = require("path");
const os = require("os");
const http = require("http");
const crypto = require("crypto");
const { spawnSync, spawn } = require("child_process");

const IS_WIN = process.platform === "win32";
const IS_MAC = process.platform === "darwin";

const API_BASE = "https://notebook.googleapis.com/v1";
const UPLOAD_BASE = "https://notebook.googleapis.com/upload/v1";
const OAUTH_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth";
const OAUTH_TOKEN_URL = "https://oauth2.googleapis.com/token";
const DEFAULT_SCOPES = [
  "https://www.googleapis.com/auth/notebook"
];
const MAX_UPLOAD_BYTES = 200 * 1024 * 1024; // 200 MiB per official API limit
const TOKEN_REFRESH_MARGIN_MS = 5 * 60 * 1000; // refresh 5 minutes before expiry

// In-memory cache for refreshed ADC / env / read-only OAuth tokens
let cachedAdcToken = null;
let cachedEnvOAuthToken = null;
let cachedFallbackOAuthToken = null;

/**
 * Resolve local OS config directory (strictly outside Git repository).
 */
function getConfigDir() {
  if (process.env.GEMINI_NOTEBOOK_CONFIG_DIR) {
    return path.resolve(process.env.GEMINI_NOTEBOOK_CONFIG_DIR);
  }
  if (IS_WIN) {
    const base = process.env.LOCALAPPDATA || path.join(os.homedir(), "AppData", "Local");
    return path.join(base, "gemini-notebook-mcp");
  }
  if (IS_MAC) {
    return path.join(os.homedir(), "Library", "Application Support", "gemini-notebook-mcp");
  }
  const base = process.env.XDG_CONFIG_HOME || path.join(os.homedir(), ".config");
  return path.join(base, "gemini-notebook-mcp");
}

function getConfigPaths() {
  const dir = getConfigDir();
  return {
    dir,
    configFile: path.join(dir, "config.json"),
    tokensFile: path.join(dir, "tokens.json")
  };
}

function getUploadDirs() {
  const dirs = [];
  if (process.env.ANTIGRAVITY_UPLOAD_DIR) {
    dirs.push(path.resolve(process.env.ANTIGRAVITY_UPLOAD_DIR));
  }
  if (!IS_WIN) {
    dirs.push("/home/antigravity/upload");
  }
  return dirs.filter((d, idx) => d && dirs.indexOf(d) === idx && fs.existsSync(d));
}

function findUploadedSeedFiles() {
  const uploadDirs = getUploadDirs();
  let configSeed = null;
  let tokensSeed = null;

  for (const dir of uploadDirs) {
    if (!configSeed) {
      for (const name of ["gemini-notebook-config.json", "config.json"]) {
        const cand = path.join(dir, name);
        const parsed = readJsonIfExists(cand);
        if (parsed && typeof parsed.clientId === "string" && parsed.clientId && typeof parsed.projectId === "string" && parsed.projectId) {
          configSeed = { path: cand, data: parsed };
          break;
        }
      }
    }
    if (!tokensSeed) {
      for (const name of ["gemini-notebook-tokens.json", "tokens.json"]) {
        const cand = path.join(dir, name);
        const parsed = readJsonIfExists(cand);
        if (parsed && (typeof parsed.refresh_token === "string" || typeof parsed.access_token === "string")) {
          tokensSeed = { path: cand, data: parsed };
          break;
        }
      }
    }
  }
  return { uploadDirs, configSeed, tokensSeed };
}

function seedFromUploadDirIfNeeded(paths) {
  const existingCfg = readJsonIfExists(paths.configFile);
  const existingTokens = readJsonIfExists(paths.tokensFile);
  if (existingCfg && existingCfg.clientId && existingTokens && (existingTokens.refresh_token || existingTokens.access_token)) {
    return { cfg: existingCfg, tokens: existingTokens, seededConfig: null, seededTokens: null };
  }

  const { configSeed, tokensSeed } = findUploadedSeedFiles();
  let resolvedCfg = existingCfg;
  let resolvedTokens = existingTokens;
  let seededConfig = null;
  let seededTokens = null;

  if ((!resolvedCfg || !resolvedCfg.clientId) && configSeed) {
    resolvedCfg = configSeed.data;
    seededConfig = configSeed.path;
    try {
      writePrivateJson(paths.configFile, resolvedCfg);
    } catch (_) {}
  }
  if ((!resolvedTokens || (!resolvedTokens.refresh_token && !resolvedTokens.access_token)) && tokensSeed) {
    resolvedTokens = tokensSeed.data;
    seededTokens = tokensSeed.path;
    try {
      writePrivateJson(paths.tokensFile, resolvedTokens);
    } catch (_) {}
  }

  return { cfg: resolvedCfg, tokens: resolvedTokens, seededConfig, seededTokens };
}

function ensurePrivateDir(dirPath) {
  if (!fs.existsSync(dirPath)) {
    fs.mkdirSync(dirPath, { recursive: true, mode: 0o700 });
  }
}

function writePrivateJson(filePath, data) {
  ensurePrivateDir(path.dirname(filePath));
  const payload = JSON.stringify(data, null, 2) + "\n";
  fs.writeFileSync(filePath, payload, { encoding: "utf8", mode: 0o600 });
  if (!IS_WIN) {
    try {
      fs.chmodSync(filePath, 0o600);
    } catch (_) {}
  }
}

function readJsonIfExists(filePath) {
  if (!filePath || !fs.existsSync(filePath)) return null;
  try {
    const raw = fs.readFileSync(filePath, "utf8");
    if (!raw || !raw.trim()) return null;
    return JSON.parse(raw);
  } catch (_) {
    return null;
  }
}

/**
 * Locate gcloud Application Default Credentials JSON if present.
 */
function findAdcFile() {
  const candidates = [];
  if (process.env.GOOGLE_APPLICATION_CREDENTIALS) {
    candidates.push(process.env.GOOGLE_APPLICATION_CREDENTIALS);
  }
  if (IS_WIN && process.env.APPDATA) {
    candidates.push(path.join(process.env.APPDATA, "gcloud", "application_default_credentials.json"));
  }
  candidates.push(path.join(os.homedir(), ".config", "gcloud", "application_default_credentials.json"));

  for (const cand of candidates) {
    if (cand && fs.existsSync(cand)) {
      return cand;
    }
  }
  return null;
}

function runGcloud(args, timeout = 10000) {
  if (IS_WIN) {
    return spawnSync("cmd.exe", ["/d", "/s", "/c", "gcloud.cmd", ...args], {
      encoding: "utf8",
      timeout,
      windowsHide: true
    });
  }
  return spawnSync("gcloud", args, {
    encoding: "utf8",
    timeout
  });
}

function detectGcloudCommand() {
  const res = runGcloud(["--version"], 5000);
  if (!res.error && res.status === 0) {
    const firstLine = (res.stdout || "").split(/\r?\n/)[0] || "";
    return { installed: true, command: IS_WIN ? "gcloud.cmd" : "gcloud", version: firstLine.trim() };
  }
  return { installed: false, command: null, version: null };
}

/**
 * Save OAuth Desktop Client credentials (from Google Cloud Console client_secret_*.json)
 * and GCP project ID into local OS private config directory.
 */
function saveOAuthClientConfig({ client_secret_path, client_id, client_secret, project_id }) {
  const paths = getConfigPaths();
  const existing = readJsonIfExists(paths.configFile) || {};

  let resolvedClientId = client_id || existing.clientId || null;
  let resolvedClientSecret = client_secret || existing.clientSecret || null;
  let resolvedProjectId = project_id || existing.projectId || null;

  if (client_secret_path) {
    const absPath = path.resolve(client_secret_path);
    if (!fs.existsSync(absPath)) {
      return { ok: false, error: `client_secret file not found: ${absPath}` };
    }
    const parsed = readJsonIfExists(absPath);
    if (!parsed) {
      return { ok: false, error: `Failed to parse JSON from: ${absPath}` };
    }
    const block = parsed.installed || parsed.web || parsed;
    if (!block.client_id) {
      return { ok: false, error: "JSON does not contain 'installed.client_id' or 'client_id'." };
    }
    resolvedClientId = block.client_id;
    resolvedClientSecret = block.client_secret || "";
    if (!resolvedProjectId && block.project_id) {
      resolvedProjectId = block.project_id;
    }
  }

  if (!resolvedClientId) {
    return {
      ok: false,
      error: "client_id is required (pass --client-secret <client_secret.json> or --client-id <id>)."
    };
  }
  if (!resolvedProjectId) {
    return {
      ok: false,
      error: "project_id is required (pass --project <GCP_PROJECT_ID>)."
    };
  }

  const nextConfig = {
    projectId: String(resolvedProjectId).trim(),
    clientId: String(resolvedClientId).trim(),
    clientSecret: String(resolvedClientSecret || "").trim(),
    updatedAt: new Date().toISOString()
  };

  writePrivateJson(paths.configFile, nextConfig);

  return {
    ok: true,
    config_file: paths.configFile,
    project_id: nextConfig.projectId,
    client_id_masked: maskSecret(nextConfig.clientId),
    has_client_secret: Boolean(nextConfig.clientSecret)
  };
}

function maskSecret(val) {
  if (!val || typeof val !== "string") return null;
  if (val.length <= 10) return "***";
  return `${val.slice(0, 6)}...${val.slice(-4)}`;
}

function escapeHtml(str) {
  return String(str || "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

/**
 * Exchange OAuth 2.0 refresh_token for a fresh access_token.
 */
async function refreshAccessToken({ clientId, clientSecret, refreshToken }) {
  const params = new URLSearchParams({
    client_id: clientId,
    refresh_token: refreshToken,
    grant_type: "refresh_token"
  });
  if (clientSecret) {
    params.set("client_secret", clientSecret);
  }

  const resp = await fetch(OAUTH_TOKEN_URL, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: params.toString()
  });

  const text = await resp.text();
  let data = null;
  try {
    data = JSON.parse(text);
  } catch (_) {}

  if (!resp.ok || !data || !data.access_token) {
    const errDesc = (data && (data.error_description || data.error)) || `HTTP ${resp.status}`;
    throw new Error(`OAuth token refresh failed: ${errDesc}`);
  }

  const expiresInSec = Number(data.expires_in || 3600);
  return {
    access_token: data.access_token,
    refresh_token: data.refresh_token || refreshToken,
    token_type: data.token_type || "Bearer",
    scope: data.scope || DEFAULT_SCOPES.join(" "),
    expiry_date: Date.now() + expiresInSec * 1000
  };
}

/**
 * Resolve active OAuth Bearer token and GCP Project ID.
 * Priority:
 * 1. Explicit env var GEMINI_NOTEBOOK_ACCESS_TOKEN
 * 2. Local OAuth Desktop Client config.json + tokens.json (auto-seeded from Remote Agents /home/antigravity/upload if needed)
 * 3. Env OAuth Desktop Client refresh_token (GEMINI_NOTEBOOK_CLIENT_ID + GEMINI_NOTEBOOK_REFRESH_TOKEN)
 * 4. gcloud ADC authorized_user JSON (direct Node.js auto-refresh, no gcloud binary required)
 * 5. gcloud CLI print-access-token fallback
 */
async function resolveAuthContext({ forceRefresh = false } = {}) {
  const paths = getConfigPaths();
  const seeded = seedFromUploadDirIfNeeded(paths);
  const localCfg = seeded.cfg;
  const envProjectId =
    process.env.GEMINI_NOTEBOOK_PROJECT_ID ||
    process.env.GOOGLE_CLOUD_PROJECT ||
    process.env.GCLOUD_PROJECT ||
    null;

  // 1. Direct env access token
  if (process.env.GEMINI_NOTEBOOK_ACCESS_TOKEN && !forceRefresh) {
    const projectId = envProjectId || (localCfg && localCfg.projectId) || null;
    return {
      source: "env_access_token",
      accessToken: process.env.GEMINI_NOTEBOOK_ACCESS_TOKEN.trim(),
      projectId,
      expiryDate: null
    };
  }

  // 2. Local OAuth 2.0 Desktop Client + tokens.json (or Remote Agents upload-seeded config)
  const localTokens = seeded.tokens;
  if (localCfg && localCfg.clientId && localTokens) {
    const projectId = envProjectId || localCfg.projectId || null;
    const now = Date.now();
    if (
      !forceRefresh &&
      cachedFallbackOAuthToken &&
      cachedFallbackOAuthToken.clientId === localCfg.clientId &&
      cachedFallbackOAuthToken.expiryDate - now > TOKEN_REFRESH_MARGIN_MS
    ) {
      return {
        source: "oauth_desktop_memory_cached",
        accessToken: cachedFallbackOAuthToken.accessToken,
        projectId,
        expiryDate: cachedFallbackOAuthToken.expiryDate
      };
    }

    const isValid =
      !forceRefresh &&
      localTokens.access_token &&
      typeof localTokens.expiry_date === "number" &&
      localTokens.expiry_date - now > TOKEN_REFRESH_MARGIN_MS;

    if (isValid) {
      return {
        source: seeded.seededTokens ? "oauth_upload_seeded_cached" : "oauth_desktop_cached",
        accessToken: localTokens.access_token,
        projectId,
        expiryDate: localTokens.expiry_date
      };
    }

    if (localTokens.refresh_token) {
      const refreshed = await refreshAccessToken({
        clientId: localCfg.clientId,
        clientSecret: localCfg.clientSecret || "",
        refreshToken: localTokens.refresh_token
      });
      cachedFallbackOAuthToken = {
        clientId: localCfg.clientId,
        accessToken: refreshed.access_token,
        expiryDate: refreshed.expiry_date
      };
      try {
        writePrivateJson(paths.tokensFile, {
          ...localTokens,
          ...refreshed,
          updatedAt: new Date().toISOString()
        });
      } catch (_) {}
      return {
        source: seeded.seededTokens ? "oauth_upload_seeded_refreshed" : "oauth_desktop_refreshed",
        accessToken: refreshed.access_token,
        projectId,
        expiryDate: refreshed.expiry_date
      };
    }
  }

  // 3. Env OAuth 2.0 Desktop Client refresh_token (useful for Remote Agents / CI without local files)
  if (process.env.GEMINI_NOTEBOOK_CLIENT_ID && process.env.GEMINI_NOTEBOOK_REFRESH_TOKEN) {
    const clientId = process.env.GEMINI_NOTEBOOK_CLIENT_ID.trim();
    const clientSecret = (process.env.GEMINI_NOTEBOOK_CLIENT_SECRET || "").trim();
    const refreshToken = process.env.GEMINI_NOTEBOOK_REFRESH_TOKEN.trim();
    const projectId = envProjectId || (localCfg && localCfg.projectId) || null;
    const now = Date.now();
    if (
      !forceRefresh &&
      cachedEnvOAuthToken &&
      cachedEnvOAuthToken.clientId === clientId &&
      cachedEnvOAuthToken.expiryDate - now > TOKEN_REFRESH_MARGIN_MS
    ) {
      return {
        source: "env_oauth_cached",
        accessToken: cachedEnvOAuthToken.accessToken,
        projectId,
        expiryDate: cachedEnvOAuthToken.expiryDate
      };
    }
    const refreshed = await refreshAccessToken({ clientId, clientSecret, refreshToken });
    cachedEnvOAuthToken = {
      clientId,
      accessToken: refreshed.access_token,
      expiryDate: refreshed.expiry_date
    };
    return {
      source: "env_oauth_refreshed",
      accessToken: refreshed.access_token,
      projectId,
      expiryDate: refreshed.expiry_date
    };
  }

  // 4. gcloud ADC authorized_user JSON (direct refresh without gcloud binary)
  const adcFile = findAdcFile();
  if (adcFile) {
    const adc = readJsonIfExists(adcFile);
    if (adc && adc.type === "authorized_user" && adc.client_id && adc.refresh_token) {
      const projectId = envProjectId || adc.quota_project_id || (localCfg && localCfg.projectId) || null;
      const now = Date.now();
      if (
        !forceRefresh &&
        cachedAdcToken &&
        cachedAdcToken.adcFile === adcFile &&
        cachedAdcToken.expiryDate - now > TOKEN_REFRESH_MARGIN_MS
      ) {
        return {
          source: "gcloud_adc_cached",
          accessToken: cachedAdcToken.accessToken,
          projectId,
          expiryDate: cachedAdcToken.expiryDate
        };
      }
      const refreshed = await refreshAccessToken({
        clientId: adc.client_id,
        clientSecret: adc.client_secret || "",
        refreshToken: adc.refresh_token
      });
      cachedAdcToken = {
        adcFile,
        accessToken: refreshed.access_token,
        expiryDate: refreshed.expiry_date
      };
      return {
        source: "gcloud_adc_refreshed",
        accessToken: refreshed.access_token,
        projectId,
        expiryDate: refreshed.expiry_date
      };
    }
  }

  // 4. gcloud CLI fallback
  const gcloud = detectGcloudCommand();
  if (gcloud.installed) {
    const tokRes = runGcloud(["auth", "application-default", "print-access-token"], 15000);
    if (!tokRes.error && tokRes.status === 0 && tokRes.stdout && tokRes.stdout.trim()) {
      let projectId = envProjectId || (localCfg && localCfg.projectId) || null;
      if (!projectId) {
        const projRes = runGcloud(["config", "get-value", "project"], 10000);
        if (!projRes.error && projRes.status === 0 && projRes.stdout) {
          const val = projRes.stdout.trim();
          if (val && val !== "(unset)") projectId = val;
        }
      }
      return {
        source: "gcloud_cli",
        accessToken: tokRes.stdout.trim(),
        projectId,
        expiryDate: null
      };
    }
  }

  throw new Error(
    "Gemini Notebook OAuth credentials not configured. Run:\n" +
      "  1) node .agents/mcp/gemini-notebook-mcp/cli.js auth-setup --client-secret <path/to/client_secret.json> --project <GCP_PROJECT_ID>\n" +
      "  2) node .agents/mcp/gemini-notebook-mcp/cli.js login\n" +
      "Or configure gcloud ADC with scope https://www.googleapis.com/auth/notebook."
  );
}

/**
 * Interactive local loopback OAuth 2.0 login flow with PKCE (S256).
 * Intended to be triggered via `cli.js login`.
 */
async function runOAuthLoginFlow({ project_id, port = 0, open_browser = true, timeout_ms = 180000 } = {}) {
  const paths = getConfigPaths();
  const cfg = readJsonIfExists(paths.configFile);
  if (!cfg || !cfg.clientId) {
    return {
      ok: false,
      error: `OAuth client config not found at ${paths.configFile}. Run 'auth-setup' first.`
    };
  }

  const effectiveProjectId = project_id || cfg.projectId;
  if (project_id && project_id !== cfg.projectId) {
    writePrivateJson(paths.configFile, {
      ...cfg,
      projectId: String(project_id).trim(),
      updatedAt: new Date().toISOString()
    });
  }

  const state = crypto.randomBytes(24).toString("hex");
  const codeVerifier = crypto.randomBytes(32).toString("base64url");
  const codeChallenge = crypto.createHash("sha256").update(codeVerifier).digest("base64url");

  return new Promise((resolve) => {
    let settled = false;
    let timer = null;

    const server = http.createServer(async (req, res) => {
      try {
        const reqUrl = new URL(req.url, `http://127.0.0.1:${server.address().port}`);
        if (reqUrl.pathname !== "/callback") {
          res.writeHead(404, { "Content-Type": "text/plain; charset=utf-8" });
          res.end("Not found");
          return;
        }

        const errParam = reqUrl.searchParams.get("error");
        const returnedState = reqUrl.searchParams.get("state");
        const code = reqUrl.searchParams.get("code");

        if (errParam) {
          res.writeHead(400, { "Content-Type": "text/html; charset=utf-8" });
          res.end("<h1>Authentication Cancelled / Failed</h1><p>You may close this tab.</p>");
          finish({ ok: false, error: `OAuth authorization error: ${errParam}` });
          return;
        }
        if (returnedState !== state || !code) {
          res.writeHead(400, { "Content-Type": "text/html; charset=utf-8" });
          res.end("<h1>Invalid OAuth callback</h1><p>State mismatch or missing code.</p>");
          finish({ ok: false, error: "Invalid OAuth callback (state mismatch or missing code)." });
          return;
        }

        const redirectUri = `http://127.0.0.1:${server.address().port}/callback`;
        const bodyParams = new URLSearchParams({
          code,
          client_id: cfg.clientId,
          redirect_uri: redirectUri,
          grant_type: "authorization_code",
          code_verifier: codeVerifier
        });
        if (cfg.clientSecret) {
          bodyParams.set("client_secret", cfg.clientSecret);
        }

        const tokenResp = await fetch(OAUTH_TOKEN_URL, {
          method: "POST",
          headers: { "Content-Type": "application/x-www-form-urlencoded" },
          body: bodyParams.toString()
        });
        const tokenData = await tokenResp.json().catch(() => null);
        if (!tokenResp.ok || !tokenData || !tokenData.access_token) {
          const msg = (tokenData && (tokenData.error_description || tokenData.error)) || `HTTP ${tokenResp.status}`;
          res.writeHead(500, { "Content-Type": "text/html; charset=utf-8" });
          res.end(`<h1>Token exchange failed</h1><p>${escapeHtml(msg)}</p>`);
          finish({ ok: false, error: `Token exchange failed: ${msg}` });
          return;
        }

        const existingTokens = readJsonIfExists(paths.tokensFile) || {};
        const expiresIn = Number(tokenData.expires_in || 3600);
        const saved = {
          access_token: tokenData.access_token,
          refresh_token: tokenData.refresh_token || existingTokens.refresh_token || null,
          token_type: tokenData.token_type || "Bearer",
          scope: tokenData.scope || DEFAULT_SCOPES.join(" "),
          expiry_date: Date.now() + expiresIn * 1000,
          updatedAt: new Date().toISOString()
        };
        writePrivateJson(paths.tokensFile, saved);

        res.writeHead(200, { "Content-Type": "text/html; charset=utf-8" });
        res.end(
          "<html><body style='font-family:sans-serif;padding:2rem;'>" +
            "<h1>Gemini Notebook API Authentication Successful</h1>" +
            "<p>Tokens saved locally with auto-refresh enabled. You may close this browser tab.</p>" +
            "</body></html>"
        );

        finish({
          ok: true,
          tokens_file: paths.tokensFile,
          project_id: effectiveProjectId,
          has_refresh_token: Boolean(saved.refresh_token),
          scope: saved.scope,
          expiry_iso: new Date(saved.expiry_date).toISOString()
        });
      } catch (e) {
        res.writeHead(500, { "Content-Type": "text/plain; charset=utf-8" });
        res.end("Internal error during OAuth callback.");
        finish({ ok: false, error: String(e.message || e) });
      }
    });

    function finish(result) {
      if (settled) return;
      settled = true;
      if (timer) clearTimeout(timer);
      try {
        server.close();
      } catch (_) {}
      resolve(result);
    }

    server.on("error", (err) => {
      finish({ ok: false, error: `Failed to start local OAuth callback server: ${err.message}` });
    });

    server.listen(Number(port) || 0, "127.0.0.1", () => {
      const boundPort = server.address().port;
      const redirectUri = `http://127.0.0.1:${boundPort}/callback`;
      const authParams = new URLSearchParams({
        client_id: cfg.clientId,
        redirect_uri: redirectUri,
        response_type: "code",
        scope: DEFAULT_SCOPES.join(" "),
        access_type: "offline",
        prompt: "consent",
        state,
        code_challenge: codeChallenge,
        code_challenge_method: "S256"
      });
      const authUrl = `${OAUTH_AUTH_URL}?${authParams.toString()}`;

      console.error("\n[Gemini Notebook OAuth] Open this URL in your browser to authorize:");
      console.error(authUrl + "\n");

      if (open_browser) {
        try {
          if (IS_WIN) {
            spawn("rundll32.exe", ["url.dll,FileProtocolHandler", authUrl], {
              detached: true,
              stdio: "ignore",
              windowsHide: true
            }).unref();
          } else if (IS_MAC) {
            spawn("open", [authUrl], { detached: true, stdio: "ignore" }).unref();
          } else {
            spawn("xdg-open", [authUrl], { detached: true, stdio: "ignore" }).unref();
          }
        } catch (_) {}
      }

      timer = setTimeout(() => {
        finish({ ok: false, error: `OAuth login timed out after ${Math.round(timeout_ms / 1000)}s.` });
      }, timeout_ms);
    });
  });
}

/**
 * Normalize resource names.
 */
function normalizeNotebookName(input) {
  if (!input || typeof input !== "string") {
    throw new Error("notebook_name is required (e.g. 'notebooks/<id>' or '<id>').");
  }
  const trimmed = input.trim().replace(/^\/+/, "");
  if (!trimmed) throw new Error("notebook_name cannot be empty.");
  return trimmed.startsWith("notebooks/") ? trimmed : `notebooks/${trimmed}`;
}

function normalizeSourceName(sourceName, notebookName) {
  if (!sourceName || typeof sourceName !== "string") {
    throw new Error("source_name is required (e.g. 'notebooks/<nb_id>/sources/<src_id>').");
  }
  const trimmed = sourceName.trim().replace(/^\/+/, "");
  if (trimmed.includes("/sources/")) {
    return trimmed.startsWith("notebooks/") ? trimmed : `notebooks/${trimmed}`;
  }
  if (!notebookName) {
    throw new Error("Pass full source_name ('notebooks/<nb_id>/sources/<src_id>') or provide notebook_name as well.");
  }
  const nb = normalizeNotebookName(notebookName);
  const srcId = trimmed.startsWith("sources/") ? trimmed.slice("sources/".length) : trimmed;
  return `${nb}/sources/${srcId}`;
}

/**
 * Generic authenticated REST call to Gemini Notebook API with single automatic 401 retry.
 */
async function apiRequest({
  method = "GET",
  url,
  headers = {},
  body = undefined,
  isBinary = false,
  retryOn401 = true
}) {
  let auth = await resolveAuthContext({ forceRefresh: false });

  async function execOnce(authCtx) {
    const reqHeaders = {
      Authorization: `Bearer ${authCtx.accessToken}`,
      ...headers
    };
    if (authCtx.projectId) {
      reqHeaders["x-goog-user-project"] = authCtx.projectId;
    }
    if (!isBinary && body !== undefined && !reqHeaders["Content-Type"]) {
      reqHeaders["Content-Type"] = "application/json";
    }

    const resp = await fetch(url, {
      method,
      headers: reqHeaders,
      body: body === undefined ? undefined : isBinary ? body : JSON.stringify(body)
    });

    const rawText = await resp.text();
    let json = null;
    if (rawText) {
      try {
        json = JSON.parse(rawText);
      } catch (_) {}
    }

    return { resp, json, rawText, authCtx };
  }

  let attempt = await execOnce(auth);
  if (attempt.resp.status === 401 && retryOn401 && auth.source !== "env_access_token") {
    auth = await resolveAuthContext({ forceRefresh: true });
    attempt = await execOnce(auth);
  }

  if (!attempt.resp.ok) {
    const apiErr = (attempt.json && attempt.json.error) || null;
    const message =
      (apiErr && apiErr.message) ||
      (attempt.rawText ? attempt.rawText.slice(0, 500) : `HTTP ${attempt.resp.status}`);
    const statusText = (apiErr && apiErr.status) || attempt.resp.statusText || String(attempt.resp.status);

    let hint = null;
    if (message.includes("WORKSPACE_ACCOUNT_NOT_SUPPORTED")) {
      hint = "Gemini Notebook Public Preview API currently supports personal Google Accounts (@gmail.com) only, not Google Workspace accounts.";
    } else if (attempt.resp.status === 404 && method === "POST" && url.endsWith("/notebooks")) {
      hint = "Sign in to https://notebook.google.com at least once in a browser with this Google account before calling the API.";
    } else if (attempt.resp.status === 403 && !auth.projectId) {
      hint = "Set your GCP Project ID (x-goog-user-project) and enable notebook.googleapis.com in Google Cloud Console.";
    } else if (attempt.resp.status === 403) {
      hint = "Verify that 'notebook.googleapis.com' is enabled on your GCP project and your OAuth token has the 'https://www.googleapis.com/auth/notebook' scope.";
    }

    return {
      ok: false,
      http_status: attempt.resp.status,
      api_status: statusText,
      error: message,
      hint,
      auth_source: attempt.authCtx.source,
      project_id: attempt.authCtx.projectId
    };
  }

  return {
    ok: true,
    http_status: attempt.resp.status,
    data: attempt.json !== null ? attempt.json : attempt.rawText,
    auth_source: attempt.authCtx.source,
    project_id: attempt.authCtx.projectId
  };
}

/**
 * Infer MIME type from file extension for upload_file_source.
 */
function inferMimeType(filePath) {
  const ext = path.extname(filePath || "").toLowerCase();
  const map = {
    ".pdf": "application/pdf",
    ".txt": "text/plain",
    ".md": "text/markdown",
    ".markdown": "text/markdown",
    ".csv": "text/csv",
    ".html": "text/html",
    ".htm": "text/html",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ".mp3": "audio/mpeg",
    ".wav": "audio/wav",
    ".m4a": "audio/mp4",
    ".aac": "audio/aac",
    ".ogg": "audio/ogg",
    ".flac": "audio/flac",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp",
    ".gif": "image/gif"
  };
  return map[ext] || "application/octet-stream";
}

async function pollSourceUntilDone(sourceName, { timeout_seconds = 60, poll_interval_ms = 2000 } = {}) {
  const deadline = Date.now() + Math.max(5, Number(timeout_seconds) || 60) * 1000;
  let lastResult = null;
  while (Date.now() < deadline) {
    lastResult = await getSource({ source_name: sourceName });
    if (!lastResult.ok) return lastResult;
    const state = lastResult.source && lastResult.source.state;
    if (state === "ACTIVE" || state === "FAILED" || state === "DELETING") {
      return lastResult;
    }
    await new Promise((r) => setTimeout(r, Math.max(500, poll_interval_ms)));
  }
  return {
    ...(lastResult || { ok: true }),
    warning: `Timed out waiting for source to become ACTIVE (last state: ${lastResult && lastResult.source ? lastResult.source.state : "UNKNOWN"}).`
  };
}

// ============================================================================
// Tool Implementations
// ============================================================================

async function getGeminiNotebookStatus(args = {}) {
  const paths = getConfigPaths();
  const seeded = seedFromUploadDirIfNeeded(paths);
  const uploadCheck = findUploadedSeedFiles();
  const localCfg = seeded.cfg;
  const localTokens = seeded.tokens;
  const adcFile = findAdcFile();
  const adcData = adcFile ? readJsonIfExists(adcFile) : null;
  const gcloud = detectGcloudCommand();

  const status = {
    ok: true,
    api_base: API_BASE,
    upload_base: UPLOAD_BASE,
    config_dir: paths.dir,
    oauth_desktop: {
      configured: Boolean(localCfg && localCfg.clientId),
      project_id: (localCfg && localCfg.projectId) || null,
      client_id_masked: localCfg ? maskSecret(localCfg.clientId) : null,
      has_tokens: Boolean(localTokens && (localTokens.access_token || localTokens.refresh_token)),
      has_refresh_token: Boolean(localTokens && localTokens.refresh_token),
      token_expiry_iso:
        localTokens && typeof localTokens.expiry_date === "number"
          ? new Date(localTokens.expiry_date).toISOString()
          : null,
      scope: (localTokens && localTokens.scope) || null
    },
    remote_upload_seed: {
      upload_dirs_detected: uploadCheck.uploadDirs,
      config_seed_found: Boolean(uploadCheck.configSeed),
      tokens_seed_found: Boolean(uploadCheck.tokensSeed)
    },
    gcloud_adc: {
      adc_file_exists: Boolean(adcFile),
      adc_file: adcFile || null,
      adc_type: (adcData && adcData.type) || null,
      quota_project_id: (adcData && adcData.quota_project_id) || null,
      gcloud_cli_installed: gcloud.installed,
      gcloud_cli_version: gcloud.version
    },
    env_override: {
      has_access_token: Boolean(process.env.GEMINI_NOTEBOOK_ACCESS_TOKEN),
      has_refresh_token: Boolean(process.env.GEMINI_NOTEBOOK_CLIENT_ID && process.env.GEMINI_NOTEBOOK_REFRESH_TOKEN),
      project_id:
        process.env.GEMINI_NOTEBOOK_PROJECT_ID ||
        process.env.GOOGLE_CLOUD_PROJECT ||
        process.env.GCLOUD_PROJECT ||
        null
    },
    ready_for_api: Boolean(
      process.env.GEMINI_NOTEBOOK_ACCESS_TOKEN ||
        (process.env.GEMINI_NOTEBOOK_CLIENT_ID && process.env.GEMINI_NOTEBOOK_REFRESH_TOKEN) ||
        (localCfg && localCfg.clientId && localTokens && (localTokens.refresh_token || localTokens.access_token)) ||
        (adcData && adcData.type === "authorized_user" && adcData.refresh_token) ||
        gcloud.installed
    ),
    api_capabilities_note:
      "Official Public Preview API supports notebooks (list/get/create/rename) and sources (list/get/add_web/add_text/upload_file up to 200 MiB). For Q&A/RAG queries or Audio Overviews, use the companion 'notebooklm-research' MCP."
  };

  if (args.live_check) {
    try {
      const probe = await apiRequest({
        method: "GET",
        url: `${API_BASE}/notebooks?pageSize=1`
      });
      status.live_check = probe.ok
        ? {
            ok: true,
            auth_source: probe.auth_source,
            project_id: probe.project_id,
            sample_count: Array.isArray(probe.data && probe.data.notebooks) ? probe.data.notebooks.length : 0
          }
        : {
            ok: false,
            http_status: probe.http_status,
            api_status: probe.api_status,
            error: probe.error,
            hint: probe.hint
          };
      if (!probe.ok) {
        status.ok = false;
      }
    } catch (err) {
      status.live_check = { ok: false, error: String(err.message || err) };
      status.ok = false;
    }
  }

  return status;
}

async function listNotebooks(args = {}) {
  const pageSize = Math.min(100, Math.max(1, Number(args.page_size) || 50));
  const fetchAll = Boolean(args.fetch_all);
  let pageToken = args.page_token ? String(args.page_token) : "";
  const allNotebooks = [];
  let nextPageToken = null;
  let lastMeta = null;

  do {
    const qs = new URLSearchParams({ pageSize: String(pageSize) });
    if (pageToken) qs.set("pageToken", pageToken);
    const res = await apiRequest({
      method: "GET",
      url: `${API_BASE}/notebooks?${qs.toString()}`
    });
    if (!res.ok) return res;
    lastMeta = res;
    const batch = Array.isArray(res.data && res.data.notebooks) ? res.data.notebooks : [];
    allNotebooks.push(...batch);
    nextPageToken = (res.data && res.data.nextPageToken) || null;
    pageToken = nextPageToken || "";
  } while (fetchAll && nextPageToken);

  return {
    ok: true,
    count: allNotebooks.length,
    notebooks: allNotebooks,
    next_page_token: nextPageToken,
    auth_source: lastMeta && lastMeta.auth_source,
    project_id: lastMeta && lastMeta.project_id
  };
}

async function getNotebook(args = {}) {
  const name = normalizeNotebookName(args.notebook_name || args.name);
  const res = await apiRequest({
    method: "GET",
    url: `${API_BASE}/${name}`
  });
  if (!res.ok) return res;
  return {
    ok: true,
    notebook: res.data,
    auth_source: res.auth_source,
    project_id: res.project_id
  };
}

async function createNotebook(args = {}) {
  const displayName = args.display_name || args.title || args.name;
  if (!displayName || typeof displayName !== "string" || !displayName.trim()) {
    return { ok: false, error: "display_name is required." };
  }
  const res = await apiRequest({
    method: "POST",
    url: `${API_BASE}/notebooks`,
    body: { displayName: displayName.trim() }
  });
  if (!res.ok) return res;
  return {
    ok: true,
    notebook: res.data,
    auth_source: res.auth_source,
    project_id: res.project_id
  };
}

async function renameNotebook(args = {}) {
  const name = normalizeNotebookName(args.notebook_name || args.name);
  const displayName = args.display_name || args.new_name || args.title;
  if (!displayName || typeof displayName !== "string" || !displayName.trim()) {
    return { ok: false, error: "display_name is required." };
  }
  const res = await apiRequest({
    method: "PATCH",
    url: `${API_BASE}/${name}?updateMask=displayName`,
    body: { displayName: displayName.trim() }
  });
  if (!res.ok) return res;
  return {
    ok: true,
    notebook: res.data,
    auth_source: res.auth_source,
    project_id: res.project_id
  };
}

async function listSources(args = {}) {
  const parent = normalizeNotebookName(args.notebook_name || args.parent);
  const pageSize = Math.min(100, Math.max(1, Number(args.page_size) || 50));
  const fetchAll = Boolean(args.fetch_all);
  let pageToken = args.page_token ? String(args.page_token) : "";
  const allSources = [];
  let nextPageToken = null;
  let lastMeta = null;

  do {
    const qs = new URLSearchParams({ pageSize: String(pageSize) });
    if (pageToken) qs.set("pageToken", pageToken);
    const res = await apiRequest({
      method: "GET",
      url: `${API_BASE}/${parent}/sources?${qs.toString()}`
    });
    if (!res.ok) return res;
    lastMeta = res;
    const batch = Array.isArray(res.data && res.data.sources) ? res.data.sources : [];
    allSources.push(...batch);
    nextPageToken = (res.data && res.data.nextPageToken) || null;
    pageToken = nextPageToken || "";
  } while (fetchAll && nextPageToken);

  return {
    ok: true,
    notebook_name: parent,
    count: allSources.length,
    sources: allSources,
    next_page_token: nextPageToken,
    auth_source: lastMeta && lastMeta.auth_source,
    project_id: lastMeta && lastMeta.project_id
  };
}

async function getSource(args = {}) {
  const fullName = normalizeSourceName(args.source_name || args.name, args.notebook_name);
  const res = await apiRequest({
    method: "GET",
    url: `${API_BASE}/${fullName}`
  });
  if (!res.ok) return res;
  return {
    ok: true,
    source: res.data,
    auth_source: res.auth_source,
    project_id: res.project_id
  };
}

async function addWebSource(args = {}) {
  const parent = normalizeNotebookName(args.notebook_name || args.parent);
  const url = args.url;
  if (!url || typeof url !== "string" || !/^https?:\/\//i.test(url.trim())) {
    return { ok: false, error: "Valid http:// or https:// url is required." };
  }
  const payload = {
    webContent: { url: url.trim() }
  };
  if (args.display_name && String(args.display_name).trim()) {
    payload.displayName = String(args.display_name).trim();
  }

  const res = await apiRequest({
    method: "POST",
    url: `${API_BASE}/${parent}/sources`,
    body: payload
  });
  if (!res.ok) return res;

  if (args.wait_until_active && res.data && res.data.name) {
    return pollSourceUntilDone(res.data.name, { timeout_seconds: args.timeout_seconds });
  }
  return {
    ok: true,
    source: res.data,
    auth_source: res.auth_source,
    project_id: res.project_id
  };
}

async function addTextSource(args = {}) {
  const parent = normalizeNotebookName(args.notebook_name || args.parent);
  let content = args.content;
  let displayName = args.display_name;
  let mimeType = args.mime_type || "text/markdown";

  if (!content && args.file_path) {
    const absPath = path.resolve(args.file_path);
    if (!fs.existsSync(absPath)) {
      return { ok: false, error: `Text file not found: ${absPath}` };
    }
    content = fs.readFileSync(absPath, "utf8");
    if (!displayName) {
      displayName = path.basename(absPath);
    }
    if (!args.mime_type) {
      mimeType = absPath.toLowerCase().endsWith(".md") ? "text/markdown" : "text/plain";
    }
  }

  if (!content || typeof content !== "string" || !content.trim()) {
    return { ok: false, error: "content (or readable file_path) is required." };
  }
  if (!displayName || !String(displayName).trim()) {
    return { ok: false, error: "display_name is required." };
  }
  if (mimeType !== "text/plain" && mimeType !== "text/markdown") {
    return { ok: false, error: "mime_type for add_text_source must be 'text/plain' or 'text/markdown'." };
  }

  const payload = {
    displayName: String(displayName).trim(),
    mimeType,
    textContent: { content }
  };

  const res = await apiRequest({
    method: "POST",
    url: `${API_BASE}/${parent}/sources`,
    body: payload
  });
  if (!res.ok) return res;

  if (args.wait_until_active && res.data && res.data.name) {
    return pollSourceUntilDone(res.data.name, { timeout_seconds: args.timeout_seconds });
  }
  return {
    ok: true,
    source: res.data,
    auth_source: res.auth_source,
    project_id: res.project_id
  };
}

async function uploadFileSource(args = {}) {
  const parent = normalizeNotebookName(args.notebook_name || args.parent);
  if (!args.file_path || typeof args.file_path !== "string") {
    return { ok: false, error: "file_path is required." };
  }
  const absPath = path.resolve(args.file_path);
  if (!fs.existsSync(absPath)) {
    return { ok: false, error: `File not found: ${absPath}` };
  }
  const stat = fs.statSync(absPath);
  if (!stat.isFile()) {
    return { ok: false, error: `Path is not a file: ${absPath}` };
  }
  if (stat.size === 0) {
    return { ok: false, error: `File is empty (0 bytes): ${absPath}` };
  }
  if (stat.size > MAX_UPLOAD_BYTES) {
    return {
      ok: false,
      error: `File exceeds the 200 MiB official API limit (${stat.size} bytes): ${absPath}`
    };
  }

  const displayName = (args.display_name && String(args.display_name).trim()) || path.basename(absPath);
  const mimeType = (args.mime_type && String(args.mime_type).trim()) || inferMimeType(absPath);
  const fileBuffer = fs.readFileSync(absPath);

  const qs = new URLSearchParams({
    uploadType: "media",
    "source.displayName": displayName
  });

  const res = await apiRequest({
    method: "POST",
    url: `${UPLOAD_BASE}/${parent}/sources:upload?${qs.toString()}`,
    headers: {
      "Content-Type": mimeType
    },
    body: fileBuffer,
    isBinary: true
  });
  if (!res.ok) return res;

  if (args.wait_until_active && res.data && res.data.name) {
    return pollSourceUntilDone(res.data.name, { timeout_seconds: args.timeout_seconds });
  }
  return {
    ok: true,
    uploaded_bytes: stat.size,
    mime_type: mimeType,
    source: res.data,
    auth_source: res.auth_source,
    project_id: res.project_id
  };
}

// ============================================================================
// MCP Tools Schema
// ============================================================================

const TOOLS_DEFINITION = [
  {
    name: "get_gemini_notebook_status",
    description:
      "Check official Gemini Notebook API (notebook.googleapis.com/v1) authentication status, OAuth Desktop / gcloud ADC readiness, token expiry, and optional live API connectivity probe.",
    inputSchema: {
      type: "object",
      properties: {
        live_check: {
          type: "boolean",
          description: "If true, executes a live GET /v1/notebooks?pageSize=1 call to verify real API connectivity."
        }
      }
    }
  },
  {
    name: "list_notebooks",
    description:
      "List notebooks accessible to the authenticated personal Google Account via the official Gemini Notebook API (GET /v1/notebooks).",
    inputSchema: {
      type: "object",
      properties: {
        page_size: { type: "integer", description: "Max notebooks per page (1-100, default 50)." },
        page_token: { type: "string", description: "Pagination token from a previous list_notebooks call." },
        fetch_all: { type: "boolean", description: "If true, automatically follows nextPageToken to fetch all notebooks." }
      }
    }
  },
  {
    name: "get_notebook",
    description: "Get metadata for a single notebook by resource name (GET /v1/notebooks/{id}).",
    inputSchema: {
      type: "object",
      properties: {
        notebook_name: { type: "string", description: "Notebook resource name ('notebooks/<id>' or '<id>')." }
      },
      required: ["notebook_name"]
    }
  },
  {
    name: "create_notebook",
    description: "Create a new persistent notebook via the official Gemini Notebook API (POST /v1/notebooks).",
    inputSchema: {
      type: "object",
      properties: {
        display_name: { type: "string", description: "Human-readable title for the new notebook." }
      },
      required: ["display_name"]
    }
  },
  {
    name: "rename_notebook",
    description: "Rename an existing notebook's displayName (PATCH /v1/notebooks/{id}?updateMask=displayName).",
    inputSchema: {
      type: "object",
      properties: {
        notebook_name: { type: "string", description: "Notebook resource name ('notebooks/<id>' or '<id>')." },
        display_name: { type: "string", description: "New display title for the notebook." }
      },
      required: ["notebook_name", "display_name"]
    }
  },
  {
    name: "list_sources",
    description: "List all sources inside a notebook along with their processing state (PROCESSING / ACTIVE / FAILED).",
    inputSchema: {
      type: "object",
      properties: {
        notebook_name: { type: "string", description: "Notebook resource name ('notebooks/<id>' or '<id>')." },
        page_size: { type: "integer", description: "Max sources per page (1-100, default 50)." },
        page_token: { type: "string", description: "Pagination token from a previous list_sources call." },
        fetch_all: { type: "boolean", description: "If true, fetches all pages automatically." }
      },
      required: ["notebook_name"]
    }
  },
  {
    name: "get_source",
    description: "Get details and current processing state of a single source (GET /v1/notebooks/{nb}/sources/{src}).",
    inputSchema: {
      type: "object",
      properties: {
        source_name: { type: "string", description: "Full source resource name ('notebooks/<nb>/sources/<src>') or source ID if notebook_name is provided." },
        notebook_name: { type: "string", description: "Optional notebook resource name when passing only a source ID." }
      },
      required: ["source_name"]
    }
  },
  {
    name: "add_web_source",
    description: "Add a public Web page URL or YouTube video URL to a notebook via official Gemini Notebook API.",
    inputSchema: {
      type: "object",
      properties: {
        notebook_name: { type: "string", description: "Target notebook resource name ('notebooks/<id>' or '<id>')." },
        url: { type: "string", description: "Public http(s) Web page or YouTube video URL." },
        display_name: { type: "string", description: "Optional display title for the source." },
        wait_until_active: { type: "boolean", description: "If true, polls until state becomes ACTIVE or FAILED." },
        timeout_seconds: { type: "integer", description: "Max wait time in seconds when wait_until_active is true (default 60)." }
      },
      required: ["notebook_name", "url"]
    }
  },
  {
    name: "add_text_source",
    description: "Add inline plain text or Markdown content (or read from a local .md/.txt file) as a notebook source.",
    inputSchema: {
      type: "object",
      properties: {
        notebook_name: { type: "string", description: "Target notebook resource name ('notebooks/<id>' or '<id>')." },
        display_name: { type: "string", description: "Display title for the text source (defaults to filename if file_path is given)." },
        content: { type: "string", description: "Inline UTF-8 text or Markdown content." },
        file_path: { type: "string", description: "Optional local UTF-8 text/Markdown file path to read content from." },
        mime_type: {
          type: "string",
          enum: ["text/markdown", "text/plain"],
          description: "MIME type ('text/markdown' or 'text/plain', default 'text/markdown')."
        },
        wait_until_active: { type: "boolean", description: "If true, polls until state becomes ACTIVE or FAILED." },
        timeout_seconds: { type: "integer", description: "Max wait time in seconds when wait_until_active is true (default 60)." }
      },
      required: ["notebook_name"]
    }
  },
  {
    name: "upload_file_source",
    description:
      "Upload a local file (PDF, DOCX, audio, image, CSV, Markdown, etc., up to 200 MiB) directly into a notebook via POST /upload/v1/{parent}/sources:upload?uploadType=media.",
    inputSchema: {
      type: "object",
      properties: {
        notebook_name: { type: "string", description: "Target notebook resource name ('notebooks/<id>' or '<id>')." },
        file_path: { type: "string", description: "Absolute or relative local path to the file to upload." },
        display_name: { type: "string", description: "Optional display title (defaults to file basename)." },
        mime_type: { type: "string", description: "Optional MIME type override (auto-inferred from extension if omitted)." },
        wait_until_active: { type: "boolean", description: "If true, polls until state becomes ACTIVE or FAILED." },
        timeout_seconds: { type: "integer", description: "Max wait time in seconds when wait_until_active is true (default 60)." }
      },
      required: ["notebook_name", "file_path"]
    }
  }
];

async function handleToolCall(toolName, toolArgs) {
  switch (toolName) {
    case "get_gemini_notebook_status":
      return getGeminiNotebookStatus(toolArgs);
    case "list_notebooks":
      return listNotebooks(toolArgs);
    case "get_notebook":
      return getNotebook(toolArgs);
    case "create_notebook":
      return createNotebook(toolArgs);
    case "rename_notebook":
      return renameNotebook(toolArgs);
    case "list_sources":
      return listSources(toolArgs);
    case "get_source":
      return getSource(toolArgs);
    case "add_web_source":
      return addWebSource(toolArgs);
    case "add_text_source":
      return addTextSource(toolArgs);
    case "upload_file_source":
      return uploadFileSource(toolArgs);
    default:
      return { ok: false, error: `Unknown tool: ${toolName}` };
  }
}

// ============================================================================
// Stdio JSON-RPC 2.0 MCP Server
// ============================================================================

function startMcpServer() {
  let framingMode = "newline";
  let buffer = Buffer.alloc(0);

  function sendResponse(obj) {
    const jsonStr = JSON.stringify(obj);
    if (framingMode === "content-length") {
      const len = Buffer.byteLength(jsonStr, "utf8");
      process.stdout.write(`Content-Length: ${len}\r\n\r\n${jsonStr}`);
    } else {
      process.stdout.write(jsonStr + "\n");
    }
  }

  async function handleRpcMessage(msg) {
    if (!msg || typeof msg !== "object") return;
    const { id, method, params } = msg;

    if (method === "initialize") {
      const clientProto = (params && params.protocolVersion) || "2024-11-05";
      sendResponse({
        jsonrpc: "2.0",
        id,
        result: {
          protocolVersion: clientProto,
          capabilities: { tools: {} },
          serverInfo: {
            name: "gemini-notebook-mcp",
            version: "1.0.0"
          }
        }
      });
      return;
    }

    if (method === "notifications/initialized" || method === "notifications/cancelled") {
      return;
    }

    if (method === "ping") {
      sendResponse({ jsonrpc: "2.0", id, result: {} });
      return;
    }

    if (method === "tools/list") {
      sendResponse({
        jsonrpc: "2.0",
        id,
        result: { tools: TOOLS_DEFINITION }
      });
      return;
    }

    if (method === "tools/call") {
      const toolName = params && params.name;
      const toolArgs = (params && params.arguments) || {};
      try {
        const res = await handleToolCall(toolName, toolArgs);
        sendResponse({
          jsonrpc: "2.0",
          id,
          result: {
            content: [
              {
                type: "text",
                text: JSON.stringify(res, null, 2)
              }
            ],
            isError: res.ok === false
          }
        });
      } catch (err) {
        sendResponse({
          jsonrpc: "2.0",
          id,
          result: {
            content: [
              {
                type: "text",
                text: JSON.stringify({ ok: false, error: String(err.message || err) }, null, 2)
              }
            ],
            isError: true
          }
        });
      }
      return;
    }

    if (typeof id !== "undefined") {
      sendResponse({
        jsonrpc: "2.0",
        id,
        error: {
          code: -32601,
          message: `Method not found: ${method}`
        }
      });
    }
  }

  function processBuffer() {
    while (buffer.length > 0) {
      const preview = buffer.slice(0, Math.min(buffer.length, 64)).toString("utf8");
      const trimmedPreview = preview.replace(/^[\r\n\s]+/, "");
      if (trimmedPreview.length === 0) {
        buffer = Buffer.alloc(0);
        return;
      }
      const leadingWsBytes = Buffer.byteLength(
        preview.slice(0, preview.length - trimmedPreview.length),
        "utf8"
      );
      if (leadingWsBytes > 0) {
        buffer = buffer.slice(leadingWsBytes);
      }

      const headStr = buffer.slice(0, Math.min(buffer.length, 32)).toString("utf8");
      if (/^Content-Length:/i.test(headStr)) {
        framingMode = "content-length";
        const sepIdx = buffer.indexOf("\r\n\r\n");
        const sepIdxLf = buffer.indexOf("\n\n");
        let headerEnd = -1;
        let sepLen = 4;
        if (sepIdx !== -1 && (sepIdxLf === -1 || sepIdx < sepIdxLf)) {
          headerEnd = sepIdx;
          sepLen = 4;
        } else if (sepIdxLf !== -1) {
          headerEnd = sepIdxLf;
          sepLen = 2;
        }
        if (headerEnd === -1) return;

        const headerText = buffer.slice(0, headerEnd).toString("utf8");
        const match = headerText.match(/Content-Length:\s*(\d+)/i);
        if (!match) {
          buffer = buffer.slice(headerEnd + sepLen);
          continue;
        }
        const contentLen = parseInt(match[1], 10);
        const totalNeeded = headerEnd + sepLen + contentLen;
        if (buffer.length < totalNeeded) return;

        const bodyText = buffer.slice(headerEnd + sepLen, totalNeeded).toString("utf8");
        buffer = buffer.slice(totalNeeded);
        try {
          const msg = JSON.parse(bodyText);
          handleRpcMessage(msg).catch(() => {});
        } catch (_) {}
      } else {
        framingMode = "newline";
        const nlIdx = buffer.indexOf("\n");
        if (nlIdx === -1) {
          const candidate = buffer.toString("utf8").trim();
          if (candidate.startsWith("{") && candidate.endsWith("}")) {
            try {
              const msg = JSON.parse(candidate);
              buffer = Buffer.alloc(0);
              handleRpcMessage(msg).catch(() => {});
              return;
            } catch (_) {}
          }
          return;
        }
        const line = buffer.slice(0, nlIdx).toString("utf8").trim();
        buffer = buffer.slice(nlIdx + 1);
        if (line.length > 0) {
          try {
            const msg = JSON.parse(line);
            handleRpcMessage(msg).catch(() => {});
          } catch (_) {}
        }
      }
    }
  }

  process.stdin.on("data", (chunk) => {
    buffer = Buffer.concat([buffer, chunk]);
    processBuffer();
  });
}

if (require.main === module) {
  startMcpServer();
}

module.exports = {
  getConfigDir,
  getConfigPaths,
  saveOAuthClientConfig,
  runOAuthLoginFlow,
  resolveAuthContext,
  getGeminiNotebookStatus,
  listNotebooks,
  getNotebook,
  createNotebook,
  renameNotebook,
  listSources,
  getSource,
  addWebSource,
  addTextSource,
  uploadFileSource,
  inferMimeType,
  normalizeNotebookName,
  normalizeSourceName,
  TOOLS_DEFINITION
};
