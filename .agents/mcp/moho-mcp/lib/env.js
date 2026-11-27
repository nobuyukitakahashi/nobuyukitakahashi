"use strict";

const fs = require("fs");
const path = require("path");
const os = require("os");
const { spawnSync } = require("child_process");

const IS_WIN = process.platform === "win32";
const IS_MAC = process.platform === "darwin";

const TASKLIST_EXE = IS_WIN && process.env.SystemRoot
  ? path.join(process.env.SystemRoot, "System32", "tasklist.exe")
  : "tasklist.exe";

const BRIDGE_DIR = process.env.MOHO_BRIDGE_DIR || path.join(os.tmpdir(), "agy-moho-bridge");

/**
 * Parse Moho Pro14.user.settings key-value file ("Key"\t"Value").
 */
function readMohoUserSettings(settingsPath) {
  const result = {};
  if (!settingsPath || !fs.existsSync(settingsPath)) return result;
  try {
    const raw = fs.readFileSync(settingsPath, "utf8");
    const lines = raw.split(/\r?\n/);
    for (const line of lines) {
      const m = line.match(/^"([^"]+)"\t"(.*)"$/);
      if (m) {
        const key = m[1];
        const val = m[2].replace(/\\\\/g, "\\").replace(/\\"/g, '"');
        result[key] = val;
      }
    }
  } catch (_) {}
  return result;
}

/**
 * Find Moho Pro 14.x settings file path.
 */
function findUserSettingsPath() {
  if (IS_WIN) {
    const appData = process.env.APPDATA || path.join(os.homedir(), "AppData", "Roaming");
    const candidates = [
      path.join(appData, "Lost Marble", "Moho Pro", "14", "Moho Pro14.user.settings"),
      path.join(appData, "Lost Marble", "Moho Debut", "14", "Moho Debut14.user.settings"),
      path.join(appData, "Lost Marble", "Moho Pro", "13.5", "Moho Pro13.5.user.settings")
    ];
    for (const p of candidates) {
      if (fs.existsSync(p)) return p;
    }
  } else if (IS_MAC) {
    const candidates = [
      path.join(os.homedir(), "Library", "Application Support", "Lost Marble", "Moho Pro", "14", "Moho Pro14.user.settings")
    ];
    for (const p of candidates) {
      if (fs.existsSync(p)) return p;
    }
  }
  return null;
}

/**
 * Fast detection of running Moho process(es).
 */
function getRunningMohoProcesses() {
  const procs = [];
  if (IS_WIN) {
    try {
      const res = spawnSync(
        TASKLIST_EXE,
        ["/FI", "IMAGENAME eq Moho.exe", "/FO", "CSV", "/NH"],
        { encoding: "utf8", timeout: 5000, stdio: ["ignore", "pipe", "pipe"], windowsHide: true }
      );
      const lines = (res.stdout || "").trim().split(/\r?\n/);
      for (const line of lines) {
        if (!line.toLowerCase().includes("moho.exe")) continue;
        const cols = line.split('","').map((s) => s.replace(/^"|"$/g, ""));
        const pid = parseInt(cols[1], 10);
        if (!isNaN(pid)) {
          procs.push({
            name: cols[0],
            pid,
            sessionName: cols[2] || "",
            memUsage: cols[4] || ""
          });
        }
      }
    } catch (_) {}
  } else if (IS_MAC) {
    try {
      const res = spawnSync("pgrep", ["-fl", "Moho"], { encoding: "utf8", timeout: 4000 });
      const lines = (res.stdout || "").trim().split(/\r?\n/).filter(Boolean);
      for (const line of lines) {
        const m = line.match(/^(\d+)\s+(.*)$/);
        if (m) procs.push({ name: "Moho", pid: parseInt(m[1], 10), command: m[2] });
      }
    } catch (_) {}
  }
  return procs;
}

/**
 * Read live Lua bridge heartbeat if present.
 */
function readBridgeHeartbeat(bridgeDir = BRIDGE_DIR) {
  const hbPath = path.join(bridgeDir, "heartbeat.json");
  if (!fs.existsSync(hbPath)) {
    return { alive: false, reason: "no_heartbeat_file", heartbeatPath: hbPath };
  }
  try {
    const raw = fs.readFileSync(hbPath, "utf8").replace(/^\uFEFF/, "").trim();
    const data = JSON.parse(raw);
    const stat = fs.statSync(hbPath);
    const ageMs = Date.now() - stat.mtimeMs;
    return {
      alive: ageMs < 60000,
      fresh: ageMs < 5000,
      ageMs: Math.round(ageMs),
      heartbeatPath: hbPath,
      data
    };
  } catch (err) {
    return { alive: false, reason: `parse_error: ${err.message}`, heartbeatPath: hbPath };
  }
}

/**
 * Detect complete Moho installation, Custom Content Folder, scripts, and live bridge status.
 */
function detectMohoEnvironment() {
  const exeCandidates = IS_WIN
    ? [
        process.env.MOHO_PATH,
        "C:\\Program Files\\Moho 14\\Moho.exe",
        "C:\\Program Files\\Lost Marble\\Moho 14\\Moho.exe",
        "C:\\Program Files (x86)\\Moho 14\\Moho.exe"
      ].filter(Boolean)
    : IS_MAC
    ? [
        process.env.MOHO_PATH,
        "/Applications/Moho 14.app/Contents/MacOS/Moho",
        "/Applications/Moho.app/Contents/MacOS/Moho"
      ].filter(Boolean)
    : [process.env.MOHO_PATH].filter(Boolean);

  let mohoExe = null;
  for (const cand of exeCandidates) {
    if (cand && fs.existsSync(cand)) {
      mohoExe = cand;
      break;
    }
  }

  const settingsPath = findUserSettingsPath();
  const settings = readMohoUserSettings(settingsPath);

  const fallbackContentCandidates = [
    path.resolve(__dirname, "..", "..", "..", "..", "..", "antigravity", "moho", "Moho Pro"),
    path.join(os.homedir(), "Documents", "Moho Pro"),
    path.join(os.homedir(), "Documents", "Lost Marble", "Moho Pro")
  ];
  let editableFilesDir = null;
  if (process.env.MOHO_CONTENT_DIR && fs.existsSync(process.env.MOHO_CONTENT_DIR)) {
    editableFilesDir = process.env.MOHO_CONTENT_DIR;
  } else if (settings.EditableFilesDir && fs.existsSync(settings.EditableFilesDir)) {
    editableFilesDir = settings.EditableFilesDir;
  } else {
    for (const cand of fallbackContentCandidates) {
      if (cand && fs.existsSync(cand)) {
        editableFilesDir = cand;
        break;
      }
    }
  }

  let version = null;
  for (const key of Object.keys(settings)) {
    const m = key.match(/^UserFolderUpdatedForVersion_(.+)$/);
    if (m) {
      version = m[1];
      break;
    }
  }
  if (!version && mohoExe) version = "14.x";

  const scriptsDir = editableFilesDir ? path.join(editableFilesDir, "Scripts") : null;
  const bridgeToolPath = scriptsDir ? path.join(scriptsDir, "Tool", "agy_moho_bridge.lua") : null;
  const bridgeUtilPath = scriptsDir ? path.join(scriptsDir, "Utility", "agy_json.lua") : null;
  const bridgeMenuPath = scriptsDir ? path.join(scriptsDir, "Menu", "Antigravity", "agy_moho_bridge_panel.lua") : null;

  const bridgeInstalled = Boolean(
    bridgeToolPath && fs.existsSync(bridgeToolPath) &&
    bridgeUtilPath && fs.existsSync(bridgeUtilPath)
  );

  const processes = getRunningMohoProcesses();
  const heartbeat = readBridgeHeartbeat(BRIDGE_DIR);

  return {
    installed: Boolean(mohoExe),
    platform: process.platform,
    version,
    mohoExe,
    settingsPath,
    editableFilesDir,
    scriptsDir,
    bridgeDir: BRIDGE_DIR,
    bridgeInstalled,
    bridgeFiles: {
      tool: bridgeToolPath,
      utility: bridgeUtilPath,
      menu: bridgeMenuPath
    },
    isRunning: processes.length > 0,
    processes,
    liveBridge: heartbeat,
    preferredExportFormat: settings.PreferredExportFormat || null
  };
}

module.exports = {
  IS_WIN,
  IS_MAC,
  BRIDGE_DIR,
  detectMohoEnvironment,
  getRunningMohoProcesses,
  readBridgeHeartbeat,
  readMohoUserSettings,
  findUserSettingsPath
};
