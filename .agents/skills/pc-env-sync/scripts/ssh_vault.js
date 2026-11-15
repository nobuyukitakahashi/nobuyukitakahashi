#!/usr/bin/env node
"use strict";

const fs = require("fs");
const path = require("path");
const os = require("os");
const zlib = require("zlib");
const crypto = require("crypto");
const { execFileSync } = require("child_process");

const VAULT_MAGIC = "AGY-SSH-VAULT-V1";
const SCRYPT_PARAMS = { N: 16384, r: 8, p: 1, maxmem: 64 * 1024 * 1024 };

function parseArgs(argv) {
  const args = argv.slice(2);
  const cmd = args[0] && !args[0].startsWith("-") ? args[0] : "";
  const opts = {
    vault: "",
    sshDir: path.join(os.homedir(), ".ssh"),
    workspace: "",
    noHistory: false,
    help: false
  };
  for (let i = cmd ? 1 : 0; i < args.length; i++) {
    const a = args[i];
    if (a === "--vault" && args[i + 1]) {
      opts.vault = args[++i];
    } else if (a === "--ssh-dir" && args[i + 1]) {
      opts.sshDir = args[++i];
    } else if (a === "--workspace" && args[i + 1]) {
      opts.workspace = args[++i];
    } else if (a === "--no-history") {
      opts.noHistory = true;
    } else if (a === "-h" || a === "--help") {
      opts.help = true;
    }
  }
  return { cmd, opts };
}

function isAgyWorkspace(dirPath) {
  if (!dirPath) return false;
  return fs.existsSync(path.join(dirPath, ".agents", "skills", "pc-env-sync", "SKILL.md"));
}

function resolveWorkspaceRoot(explicitPath) {
  if (explicitPath && isAgyWorkspace(explicitPath)) {
    return path.resolve(explicitPath);
  }
  if (process.env.AGY_WORKSPACE_ROOT && isAgyWorkspace(process.env.AGY_WORKSPACE_ROOT)) {
    return path.resolve(process.env.AGY_WORKSPACE_ROOT);
  }

  const scriptCandidate = path.resolve(__dirname, "..", "..", "..", "..");
  if (isAgyWorkspace(scriptCandidate) && fs.existsSync(path.join(scriptCandidate, ".git"))) {
    return scriptCandidate;
  }

  let cur = process.cwd();
  while (cur) {
    if (isAgyWorkspace(cur)) return cur;
    const parent = path.dirname(cur);
    if (!parent || parent === cur) break;
    cur = parent;
  }

  const cfgFiles = [
    path.join(os.homedir(), ".gemini", "antigravity", "mcp_config.json"),
    path.join(os.homedir(), ".gemini", "config", "mcp_config.json")
  ];
  for (const cfg of cfgFiles) {
    if (!fs.existsSync(cfg)) continue;
    try {
      const json = JSON.parse(fs.readFileSync(cfg, "utf8"));
      for (const server of Object.values(json.mcpServers || {})) {
        for (const arg of server.args || []) {
          if (typeof arg !== "string") continue;
          const m = arg.match(/^(.+?)[\\/]\.agents[\\/]mcp[\\/]/);
          if (m && isAgyWorkspace(m[1])) {
            return path.resolve(m[1]);
          }
        }
      }
    } catch (_) {
      // Ignore malformed config
    }
  }

  const searchBases = [];
  if (process.platform === "win32") {
    searchBases.push(os.homedir());
    for (let code = 67; code <= 90; code++) {
      const drv = `${String.fromCharCode(code)}:\\`;
      if (fs.existsSync(drv)) searchBases.push(drv);
    }
  } else {
    searchBases.push(os.homedir());
    const cloudDir = path.join(os.homedir(), "Library", "CloudStorage");
    if (fs.existsSync(cloudDir)) {
      try {
        for (const entry of fs.readdirSync(cloudDir, { withFileTypes: true })) {
          if (entry.isDirectory() && entry.name.startsWith("GoogleDrive-")) {
            searchBases.push(path.join(cloudDir, entry.name));
          }
        }
      } catch (_) {}
    }
    if (fs.existsSync("/Volumes")) {
      try {
        for (const entry of fs.readdirSync("/Volumes", { withFileTypes: true })) {
          if (entry.isDirectory()) searchBases.push(path.join("/Volumes", entry.name));
        }
      } catch (_) {}
    }
  }

  for (const base of searchBases) {
    for (const rel of [path.join("git", "nobuyukitakahashi"), "nobuyukitakahashi"]) {
      const cand = path.join(base, rel);
      if (isAgyWorkspace(cand)) return path.resolve(cand);
    }
    try {
      for (const entry of fs.readdirSync(base, { withFileTypes: true })) {
        if (!entry.isDirectory()) continue;
        for (const rel of [path.join("git", "nobuyukitakahashi"), "nobuyukitakahashi"]) {
          const cand = path.join(base, entry.name, rel);
          if (isAgyWorkspace(cand)) return path.resolve(cand);
        }
      }
    } catch (_) {
      // Ignore permission errors
    }
  }
  return "";
}

function resolveDefaultVaultPath(explicitWorkspace) {
  const ws = resolveWorkspaceRoot(explicitWorkspace);
  if (!ws) {
    throw new Error("Could not detect Google Drive / nobuyukitakahashi workspace. Pass --vault <path> or --workspace <path>.");
  }
  const driveRoot = path.dirname(path.dirname(ws));
  return path.join(driveRoot, "_private_backup", "ssh", "ssh_keys_latest.agyvault");
}

function readHiddenPassword(promptText) {
  return new Promise((resolve, reject) => {
    if (!process.stdin.isTTY) {
      if (process.env.AGY_SSH_VAULT_PASSWORD) {
        resolve(process.env.AGY_SSH_VAULT_PASSWORD);
        return;
      }
      reject(new Error("Interactive terminal (TTY) is required for password entry."));
      return;
    }

    process.stdout.write(promptText);
    const stdin = process.stdin;
    const wasRaw = stdin.isRaw;
    stdin.setRawMode(true);
    stdin.resume();

    let chars = [];
    const onData = (buf) => {
      const str = buf.toString("utf8");
      for (let i = 0; i < str.length; i++) {
        const ch = str[i];
        if (ch === "\r" || ch === "\n") {
          stdin.setRawMode(Boolean(wasRaw));
          stdin.pause();
          stdin.removeListener("data", onData);
          process.stdout.write("\n");
          resolve(chars.join(""));
          return;
        }
        if (ch === "\u0003") {
          stdin.setRawMode(Boolean(wasRaw));
          stdin.pause();
          stdin.removeListener("data", onData);
          process.stdout.write("\n");
          reject(new Error("Cancelled by user."));
          return;
        }
        if (ch === "\u007f" || ch === "\b") {
          if (chars.length > 0) chars.pop();
        } else if (ch >= " ") {
          chars.push(ch);
        }
      }
    };
    stdin.on("data", onData);
  });
}

function formatTimestamp(date) {
  const p = (n) => String(n).padStart(2, "0");
  return (
    date.getFullYear() +
    p(date.getMonth() + 1) +
    p(date.getDate()) +
    "_" +
    p(date.getHours()) +
    p(date.getMinutes()) +
    p(date.getSeconds())
  );
}

function encryptPayload(plainObj, password) {
  const compressed = zlib.gzipSync(Buffer.from(JSON.stringify(plainObj), "utf8"));
  const salt = crypto.randomBytes(16);
  const iv = crypto.randomBytes(12);
  const key = crypto.scryptSync(password, salt, 32, SCRYPT_PARAMS);
  const cipher = crypto.createCipheriv("aes-256-gcm", key, iv);
  const encrypted = Buffer.concat([cipher.update(compressed), cipher.final()]);
  const tag = cipher.getAuthTag();
  key.fill(0);

  return {
    magic: VAULT_MAGIC,
    kdf: "scrypt",
    scrypt: { N: SCRYPT_PARAMS.N, r: SCRYPT_PARAMS.r, p: SCRYPT_PARAMS.p },
    cipher: "aes-256-gcm",
    createdAt: new Date().toISOString(),
    sourceHost: os.hostname(),
    salt: salt.toString("base64"),
    iv: iv.toString("base64"),
    tag: tag.toString("base64"),
    data: encrypted.toString("base64")
  };
}

function decryptVault(vaultObj, password) {
  if (!vaultObj || vaultObj.magic !== VAULT_MAGIC) {
    throw new Error("Invalid vault file format.");
  }
  const salt = Buffer.from(vaultObj.salt, "base64");
  const iv = Buffer.from(vaultObj.iv, "base64");
  const tag = Buffer.from(vaultObj.tag, "base64");
  const encrypted = Buffer.from(vaultObj.data, "base64");
  const params = vaultObj.scrypt
    ? { N: vaultObj.scrypt.N, r: vaultObj.scrypt.r, p: vaultObj.scrypt.p, maxmem: 64 * 1024 * 1024 }
    : SCRYPT_PARAMS;

  const key = crypto.scryptSync(password, salt, 32, params);
  try {
    const decipher = crypto.createDecipheriv("aes-256-gcm", key, iv);
    decipher.setAuthTag(tag);
    const compressed = Buffer.concat([decipher.update(encrypted), decipher.final()]);
    const jsonBuf = zlib.gunzipSync(compressed);
    return JSON.parse(jsonBuf.toString("utf8"));
  } catch (err) {
    throw new Error("Decryption failed (wrong password or corrupted vault file).");
  } finally {
    key.fill(0);
  }
}

function applyStrictPermissions(targetPath, isPublicOrKnown) {
  if (process.platform === "win32") {
    if (isPublicOrKnown) return;
    try {
      const whoami = execFileSync("whoami", [], { encoding: "utf8" }).trim();
      execFileSync("icacls", [targetPath, "/inheritance:r", "/grant:r", `${whoami}:F`], {
        stdio: "ignore"
      });
    } catch (err) {
      console.warn(`  [WARN] Could not apply strict ACL on ${targetPath}: ${err.message}`);
    }
  } else {
    fs.chmodSync(targetPath, isPublicOrKnown ? 0o644 : 0o600);
  }
}

async function runBackup(opts) {
  if (!fs.existsSync(opts.sshDir)) {
    throw new Error(`SSH directory not found: ${opts.sshDir}`);
  }

  const vaultPath = opts.vault ? path.resolve(opts.vault) : resolveDefaultVaultPath(opts.workspace);
  const entries = fs.readdirSync(opts.sshDir, { withFileTypes: true });
  const files = [];

  for (const entry of entries) {
    if (!entry.isFile()) continue;
    if (entry.name.endsWith(".old") || entry.name === ".DS_Store" || entry.name === "Thumbs.db") {
      continue;
    }
    const fullPath = path.join(opts.sshDir, entry.name);
    const stat = fs.statSync(fullPath);
    const content = fs.readFileSync(fullPath);
    const isPublic = entry.name.endsWith(".pub") || entry.name === "known_hosts";
    files.push({
      name: entry.name,
      mode: isPublic ? 0o644 : 0o600,
      mtime: stat.mtime.toISOString(),
      size: stat.size,
      contentBase64: content.toString("base64")
    });
  }

  if (files.length === 0) {
    throw new Error(`No files found to back up in ${opts.sshDir}`);
  }

  console.log(`Target SSH Dir : ${opts.sshDir} (${files.length} files)`);
  console.log(`Vault Output   : ${vaultPath}`);

  const pw1 = await readHiddenPassword("Enter backup encryption password: ");
  if (pw1.length < 8) {
    throw new Error("Password must be at least 8 characters.");
  }
  if (process.stdin.isTTY) {
    const pw2 = await readHiddenPassword("Confirm backup encryption password: ");
    if (pw1 !== pw2) {
      throw new Error("Passwords do not match.");
    }
  }

  const payload = {
    version: 1,
    createdAt: new Date().toISOString(),
    sourceHost: os.hostname(),
    sourcePlatform: process.platform,
    files
  };
  const encryptedEnvelope = encryptPayload(payload, pw1);
  const serialized = JSON.stringify(encryptedEnvelope, null, 2) + "\n";

  const outDir = path.dirname(vaultPath);
  fs.mkdirSync(outDir, { recursive: true });
  fs.writeFileSync(vaultPath, serialized, { encoding: "utf8", mode: 0o600 });
  console.log(`[OK] Encrypted SSH backup saved: ${vaultPath}`);

  if (!opts.noHistory) {
    const stamp = formatTimestamp(new Date());
    const baseName = path.basename(vaultPath, path.extname(vaultPath)).replace(/_latest$/, "");
    const historyPath = path.join(outDir, `${baseName}_${stamp}.agyvault`);
    fs.writeFileSync(historyPath, serialized, { encoding: "utf8", mode: 0o600 });
    console.log(`[OK] Snapshot history saved   : ${historyPath}`);
  }
}

async function runVerifyOrRestore(opts, shouldWrite) {
  const vaultPath = opts.vault ? path.resolve(opts.vault) : resolveDefaultVaultPath(opts.workspace);
  if (!fs.existsSync(vaultPath)) {
    throw new Error(`Vault file not found: ${vaultPath}`);
  }

  console.log(`Vault Input    : ${vaultPath}`);
  const vaultObj = JSON.parse(fs.readFileSync(vaultPath, "utf8"));
  const pw = await readHiddenPassword("Enter vault password: ");
  const payload = decryptVault(vaultObj, pw);

  if (!payload || !Array.isArray(payload.files)) {
    throw new Error("Decrypted payload is invalid.");
  }

  console.log(`[OK] Vault verified (${payload.files.length} files, created ${payload.createdAt} on ${payload.sourceHost})`);
  if (!shouldWrite) {
    for (const f of payload.files) {
      console.log(`  - ${f.name} (${f.size} bytes)`);
    }
    return;
  }

  fs.mkdirSync(opts.sshDir, { recursive: true });
  if (process.platform !== "win32") {
    fs.chmodSync(opts.sshDir, 0o700);
  }

  const stamp = formatTimestamp(new Date());
  let backupDir = "";
  for (const f of payload.files) {
    const safeName = path.basename(f.name);
    if (safeName !== f.name) {
      throw new Error(`Unsafe filename in vault: ${f.name}`);
    }
    const destPath = path.join(opts.sshDir, safeName);
    if (fs.existsSync(destPath)) {
      if (!backupDir) {
        backupDir = `${opts.sshDir}_pre_restore_${stamp}`;
        fs.mkdirSync(backupDir, { recursive: true });
      }
      fs.copyFileSync(destPath, path.join(backupDir, safeName));
    }
    const buf = Buffer.from(f.contentBase64, "base64");
    const isPublic = safeName.endsWith(".pub") || safeName === "known_hosts";
    fs.writeFileSync(destPath, buf, { mode: isPublic ? 0o644 : 0o600 });
    applyStrictPermissions(destPath, isPublic);
    console.log(`  [RESTORED] ${safeName} (${buf.length} bytes)`);
  }

  if (backupDir) {
    console.log(`[INFO] Existing files were backed up before overwrite to: ${backupDir}`);
  }
  console.log(`[OK] SSH keys restored to ${opts.sshDir} with strict permissions.`);
}

async function main() {
  const { cmd, opts } = parseArgs(process.argv);
  if (opts.help || !["backup", "restore", "verify"].includes(cmd)) {
    console.log(
      [
        "Usage:",
        "  node ssh_vault.js backup  [--vault <file>] [--ssh-dir <dir>] [--workspace <dir>] [--no-history]",
        "  node ssh_vault.js restore [--vault <file>] [--ssh-dir <dir>] [--workspace <dir>]",
        "  node ssh_vault.js verify  [--vault <file>] [--workspace <dir>]"
      ].join("\n")
    );
    process.exit(opts.help ? 0 : 1);
  }

  if (cmd === "backup") {
    await runBackup(opts);
  } else if (cmd === "verify") {
    await runVerifyOrRestore(opts, false);
  } else if (cmd === "restore") {
    await runVerifyOrRestore(opts, true);
  }
}

main().catch((err) => {
  console.error(`[ERROR] ${err.message}`);
  process.exit(1);
});
