#!/usr/bin/env node
/**
 * Adobe Premiere Pro Local MCP Server (stdio JSON-RPC 2.0)
 * Zero external npm dependencies (Node.js built-in modules only).
 * Communicates with Premiere Pro via a lightweight CEP Bridge Panel
 * using an atomic file queue under os.tmpdir()/antigravity-premiere-mcp-bridge.
 */

const fs = require("fs");
const path = require("path");
const os = require("os");
const { spawnSync } = require("child_process");

const TASKLIST_EXE = process.env.SystemRoot
  ? path.join(process.env.SystemRoot, "System32", "tasklist.exe")
  : "tasklist.exe";

const BRIDGE_ROOT = path.join(os.tmpdir(), "antigravity-premiere-mcp-bridge");
const REQ_DIR = path.join(BRIDGE_ROOT, "requests");
const RES_DIR = path.join(BRIDGE_ROOT, "responses");
const HEARTBEAT_PATH = path.join(BRIDGE_ROOT, "heartbeat.json");

function ensureBridgeDirs() {
  for (const d of [BRIDGE_ROOT, REQ_DIR, RES_DIR]) {
    if (!fs.existsSync(d)) {
      fs.mkdirSync(d, { recursive: true });
    }
  }
}

function toAsciiJsString(str) {
  const s = String(str == null ? "" : str);
  let out = '"';
  for (let i = 0; i < s.length; i++) {
    const code = s.charCodeAt(i);
    if (code === 0x22) out += '\\"';
    else if (code === 0x5c) out += "\\\\";
    else if (code === 0x0a) out += "\\n";
    else if (code === 0x0d) out += "\\r";
    else if (code === 0x09) out += "\\t";
    else if (code < 0x20 || code > 0x7e) {
      out += "\\u" + code.toString(16).padStart(4, "0");
    } else {
      out += s.charAt(i);
    }
  }
  out += '"';
  return out;
}

const JSX_JSON_POLYFILL = `
if (typeof JSON === "undefined") {
  JSON = {};
}
if (typeof JSON.stringify !== "function") {
  JSON.stringify = function(obj) {
    var t = typeof obj;
    if (obj === null || t === "undefined") return "null";
    if (t === "number") return isFinite(obj) ? String(obj) : "null";
    if (t === "boolean") return String(obj);
    if (t === "string") {
      return '"' + obj.replace(/\\\\/g, "\\\\\\\\")
                      .replace(/"/g, '\\\\"')
                      .replace(/\\r/g, "\\\\r")
                      .replace(/\\n/g, "\\\\n")
                      .replace(/\\t/g, "\\\\t") + '"';
    }
    if (obj instanceof Array) {
      var arr = [];
      for (var i = 0; i < obj.length; i++) {
        arr.push(JSON.stringify(obj[i]));
      }
      return "[" + arr.join(",") + "]";
    }
    if (t === "object") {
      var pairs = [];
      for (var k in obj) {
        if (obj.hasOwnProperty(k) && typeof obj[k] !== "function" && typeof obj[k] !== "undefined") {
          pairs.push(JSON.stringify(String(k)) + ":" + JSON.stringify(obj[k]));
        }
      }
      return "{" + pairs.join(",") + "}";
    }
    return '""';
  };
}
`;

function findWindowsPremiereExecutables() {
  const results = [];
  const adobeDirs = ["C:\\Program Files\\Adobe", "C:\\Program Files (x86)\\Adobe"];
  for (const baseDir of adobeDirs) {
    try {
      if (!fs.existsSync(baseDir)) continue;
      const entries = fs.readdirSync(baseDir);
      for (const entry of entries) {
        if (entry.toLowerCase().startsWith("adobe premiere pro")) {
          const exePath = path.join(baseDir, entry, "Adobe Premiere Pro.exe");
          if (fs.existsSync(exePath)) {
            const yearMatch = entry.match(/20\d{2}/);
            results.push({
              name: entry,
              path: exePath,
              releaseYear: yearMatch ? yearMatch[0] : null
            });
          }
        }
      }
    } catch (_) {}
  }
  results.sort((a, b) => (Number(b.releaseYear || 0) - Number(a.releaseYear || 0)));
  return results;
}

function getWindowsPremiereProcess() {
  try {
    const proc = spawnSync(
      TASKLIST_EXE,
      ["/FI", "IMAGENAME eq Adobe Premiere Pro.exe", "/FO", "CSV", "/NH"],
      {
        encoding: "utf8",
        timeout: 5000,
        stdio: ["ignore", "pipe", "pipe"],
        windowsHide: true
      }
    );
    const out = (proc.stdout || "").trim();
    if (!out || out.toLowerCase().includes("no tasks are running") || !out.includes("Adobe Premiere Pro.exe")) {
      return { running: false, processes: [] };
    }
    const lines = out.split(/\r?\n/).filter((l) => l.includes("Adobe Premiere Pro.exe"));
    const processes = lines.map((line) => {
      const cols = line.split('","').map((c) => c.replace(/^"|"$/g, ""));
      return {
        imageName: cols[0] || "Adobe Premiere Pro.exe",
        pid: cols[1] ? Number(cols[1]) : null,
        memory: cols[4] || null
      };
    });
    return { running: processes.length > 0, processes };
  } catch (err) {
    return { running: false, processes: [], error: String(err.message || err) };
  }
}

function getBridgeHeartbeatStatus() {
  try {
    if (!fs.existsSync(HEARTBEAT_PATH)) {
      return { active: false, reason: "Heartbeat file not found." };
    }
    const raw = fs.readFileSync(HEARTBEAT_PATH, "utf8");
    const data = JSON.parse(raw);
    const ageMs = Date.now() - Number(data.updatedAt || 0);
    return {
      active: ageMs >= 0 && ageMs < 8000,
      ageMs,
      isoTime: data.isoTime || null,
      extensionId: data.extensionId || null
    };
  } catch (err) {
    return { active: false, reason: String(err.message || err) };
  }
}

function sleepSync(ms) {
  const end = Date.now() + ms;
  while (Date.now() < end) {
    try {
      Atomics.wait(new Int32Array(new SharedArrayBuffer(4)), 0, 0, Math.min(50, end - Date.now()));
    } catch (_) {
      break;
    }
  }
}

function executePremiereJsx({ script, script_path, wrap_try_catch = true, timeout_ms = 30000 }) {
  let rawCode = "";
  if (script_path) {
    const absPath = path.resolve(script_path);
    if (!fs.existsSync(absPath)) {
      return { ok: false, error: `Script file not found: ${absPath}` };
    }
    rawCode = fs.readFileSync(absPath, "utf8").replace(/^\uFEFF/, "");
  } else if (typeof script === "string" && script.trim().length > 0) {
    rawCode = script;
  } else {
    return { ok: false, error: "Either 'script' or 'script_path' must be provided." };
  }

  ensureBridgeDirs();
  const hb = getBridgeHeartbeatStatus();
  if (!hb.active) {
    return {
      ok: false,
      error: "Premiere Pro CEP Bridge is not active. Launch Adobe Premiere Pro and open Window > Extensions > Antigravity MCP Bridge."
    };
  }

  let finalJsx = rawCode;
  if (wrap_try_catch) {
    finalJsx = `${JSX_JSON_POLYFILL}
(function() {
  try {
    var __fn = function() {
${rawCode}
    };
    var __res = __fn();
    return JSON.stringify({
      ok: true,
      result: typeof __res === "undefined" ? null : (typeof __res === "string" ? __res : JSON.stringify(__res))
    });
  } catch (e) {
    return JSON.stringify({
      ok: false,
      error: e && e.message ? String(e.message) : String(e),
      line: e && e.line ? Number(e.line) : null
    });
  }
})();
`;
  }

  const uid = `${Date.now()}_${process.pid}_${Math.random().toString(36).slice(2, 8)}`;
  const reqPath = path.join(REQ_DIR, `${uid}.json`);
  const tmpReqPath = reqPath + ".tmp";
  const resPath = path.join(RES_DIR, `${uid}.json`);

  fs.writeFileSync(tmpReqPath, JSON.stringify({ id: uid, script: finalJsx, createdAt: Date.now() }), "utf8");
  fs.renameSync(tmpReqPath, reqPath);

  try {
    const deadline = Date.now() + Number(timeout_ms || 30000);
    let rawResponse = null;
    while (Date.now() < deadline) {
      if (fs.existsSync(resPath)) {
        try {
          rawResponse = JSON.parse(fs.readFileSync(resPath, "utf8"));
          break;
        } catch (_) {
          rawResponse = null;
        }
      }
      sleepSync(60);
    }

    if (!rawResponse) {
      return {
        ok: false,
        error: `Timed out waiting for Premiere Pro CEP Bridge (${timeout_ms}ms).`
      };
    }

    const rawText = rawResponse.rawResult;
    if (rawText === "EvalScript error.") {
      return { ok: false, error: "ExtendScript EvalScript error (syntax or runtime error)." };
    }

    if (wrap_try_catch) {
      try {
        const parsed = JSON.parse(rawText);
        if (parsed && typeof parsed.result === "string") {
          try {
            parsed.data = JSON.parse(parsed.result);
          } catch (_) {
            parsed.data = parsed.result;
          }
        }
        return parsed;
      } catch (_) {
        return { ok: true, result: rawText, data: rawText };
      }
    }
    return { ok: true, result: rawText, data: rawText };
  } finally {
    for (const f of [reqPath, tmpReqPath, resPath]) {
      try {
        if (fs.existsSync(f)) fs.unlinkSync(f);
      } catch (_) {}
    }
  }
}

function getPremiereStatus() {
  const installs = process.platform === "win32" ? findWindowsPremiereExecutables() : [];
  const procInfo = process.platform === "win32" ? getWindowsPremiereProcess() : { running: false, processes: [] };
  const bridgeInfo = getBridgeHeartbeatStatus();

  const base = {
    ok: true,
    platform: process.platform,
    installedVersions: installs,
    running: procInfo.running,
    processes: procInfo.processes,
    cepBridge: bridgeInfo
  };

  if (!procInfo.running || !bridgeInfo.active) {
    base.note = !procInfo.running
      ? "Premiere Pro is not running."
      : "Premiere Pro is running, but CEP Bridge is not active. Open Window > Extensions > Antigravity MCP Bridge in Premiere Pro.";
    return base;
  }

  const jsx = `
var proj = app.project;
var seq = proj ? proj.activeSequence : null;
return JSON.stringify({
  version: app.version,
  build: app.build,
  projectName: proj ? proj.name : null,
  projectPath: proj ? proj.path : null,
  sequenceCount: proj && proj.sequences ? proj.sequences.numSequences : 0,
  activeSequence: seq ? {
    name: seq.name,
    width: seq.frameSizeHorizontal,
    height: seq.frameSizeVertical,
    videoTracks: seq.videoTracks ? seq.videoTracks.numTracks : 0,
    audioTracks: seq.audioTracks ? seq.audioTracks.numTracks : 0
  } : null
});
`;
  const res = executePremiereJsx({ script: jsx, timeout_ms: 10000 });
  if (!res.ok) {
    return Object.assign(base, { jsxConnected: false, jsxError: res.error });
  }
  return Object.assign(base, { jsxConnected: true, appInfo: res.data });
}

function getProjectSummary() {
  const jsx = `
var proj = app.project;
if (!proj) throw new Error("No active Premiere Pro project.");
var sequences = [];
for (var s = 0; s < proj.sequences.numSequences; s++) {
  var seq = proj.sequences[s];
  var vTracks = [];
  for (var vt = 0; vt < seq.videoTracks.numTracks; vt++) {
    var track = seq.videoTracks[vt];
    var clips = [];
    for (var c = 0; c < track.clips.numItems; c++) {
      var clip = track.clips[c];
      clips.push({
        name: clip.name,
        startSeconds: clip.start ? clip.start.seconds : null,
        endSeconds: clip.end ? clip.end.seconds : null,
        durationSeconds: clip.duration ? clip.duration.seconds : null
      });
    }
    vTracks.push({ index: vt, name: track.name, clipCount: clips.length, clips: clips });
  }
  var aTracks = [];
  for (var at = 0; at < seq.audioTracks.numTracks; at++) {
    var atrack = seq.audioTracks[at];
    aTracks.push({ index: at, name: atrack.name, clipCount: atrack.clips.numItems });
  }
  sequences.push({
    name: seq.name,
    id: seq.sequenceID,
    width: seq.frameSizeHorizontal,
    height: seq.frameSizeVertical,
    timebase: seq.timebase,
    endSeconds: seq.end ? Number(seq.end) / 254016000000 : null,
    videoTracks: vTracks,
    audioTracks: aTracks
  });
}
var rootItems = [];
if (proj.rootItem && proj.rootItem.children) {
  for (var i = 0; i < proj.rootItem.children.numItems; i++) {
    var item = proj.rootItem.children[i];
    rootItems.push({
      name: item.name,
      type: item.type,
      mediaPath: typeof item.getMediaPath === "function" ? item.getMediaPath() : null
    });
  }
}
return JSON.stringify({
  projectName: proj.name,
  projectPath: proj.path,
  activeSequenceName: proj.activeSequence ? proj.activeSequence.name : null,
  rootItemCount: rootItems.length,
  rootItems: rootItems,
  sequences: sequences
});
`;
  return executePremiereJsx({ script: jsx });
}

function exportFramePng({ output_path, time_seconds } = {}) {
  if (!output_path) {
    return { ok: false, error: "output_path is required." };
  }
  const absOut = path.resolve(output_path);
  const dir = path.dirname(absOut);
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
  const hasTime = typeof time_seconds === "number" && !isNaN(time_seconds);
  const timeVal = hasTime ? Number(time_seconds) : -1;

  const jsx = `
var proj = app.project;
if (!proj || !proj.activeSequence) throw new Error("No active sequence in Premiere Pro.");
var seq = proj.activeSequence;
var t = seq.getPlayerPosition();
if (${hasTime ? "true" : "false"}) {
  t = new Time();
  t.seconds = ${timeVal};
}
var outPath = ${toAsciiJsString(absOut)};
var f = new File(outPath);
if (f.exists) f.remove();
var ok = seq.exportFramePNG(t, outPath);
return JSON.stringify({
  sequenceName: seq.name,
  timeSeconds: t.seconds,
  outputPath: outPath,
  exported: Boolean(ok)
});
`;
  const res = executePremiereJsx({ script: jsx });
  if (res.ok && fs.existsSync(absOut)) {
    res.fileSizeBytes = fs.statSync(absOut).size;
  }
  return res;
}

function saveOrExportPremiere({ save_project = false, save_as_path, export_media_path, export_preset_path, work_area_type = 0 } = {}) {
  if (save_as_path) {
    const dir = path.dirname(path.resolve(save_as_path));
    if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
  }
  if (export_media_path) {
    const dir = path.dirname(path.resolve(export_media_path));
    if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
  }

  const jsx = `
var proj = app.project;
if (!proj) throw new Error("No active Premiere Pro project.");
var saved = null;
var saveAsPath = ${toAsciiJsString(save_as_path ? path.resolve(save_as_path) : "")};
if (saveAsPath) {
  proj.saveAs(saveAsPath);
  saved = saveAsPath;
} else if (${save_project ? "true" : "false"}) {
  proj.save();
  saved = proj.path;
}

var exported = null;
var exportPath = ${toAsciiJsString(export_media_path ? path.resolve(export_media_path) : "")};
var presetPath = ${toAsciiJsString(export_preset_path ? path.resolve(export_preset_path) : "")};
if (exportPath) {
  if (!proj.activeSequence) throw new Error("No active sequence to export.");
  if (!presetPath) throw new Error("export_preset_path (.epr) is required for exportAsMediaDirect.");
  var ok = proj.activeSequence.exportAsMediaDirect(exportPath, presetPath, ${Number(work_area_type || 0)});
  exported = { outputPath: exportPath, presetPath: presetPath, result: ok };
}

return JSON.stringify({ saved: saved, exported: exported });
`;
  return executePremiereJsx({ script: jsx, timeout_ms: 180000 });
}

const TOOLS_DEFINITION = [
  {
    name: "get_premiere_status",
    description: "Check Adobe Premiere Pro installation, running process, CEP Bridge status, and active project/sequence info.",
    inputSchema: { type: "object", properties: {}, additionalProperties: false }
  },
  {
    name: "execute_premiere_jsx",
    description: "Execute ExtendScript (JSX) inside Adobe Premiere Pro via the CEP Bridge and return the JSON/string result.",
    inputSchema: {
      type: "object",
      properties: {
        script: { type: "string", description: "ExtendScript (JSX) code string to execute." },
        script_path: { type: "string", description: "Path to a .jsx script file to execute." },
        wrap_try_catch: { type: "boolean", default: true, description: "Wrap script in try/catch and JSON wrapper." },
        timeout_ms: { type: "number", default: 30000, description: "Timeout in milliseconds." }
      },
      additionalProperties: false
    }
  },
  {
    name: "get_project_summary",
    description: "Get summary of the active Premiere Pro project, root items, sequences, tracks, and clips.",
    inputSchema: { type: "object", properties: {}, additionalProperties: false }
  },
  {
    name: "export_frame_png",
    description: "Export a single frame of the active Premiere Pro sequence as PNG for visual inspection.",
    inputSchema: {
      type: "object",
      properties: {
        output_path: { type: "string", description: "Destination .png file path." },
        time_seconds: { type: "number", description: "Optional time in seconds (defaults to current player position)." }
      },
      required: ["output_path"],
      additionalProperties: false
    }
  },
  {
    name: "save_or_export_premiere",
    description: "Save the active Premiere Pro project (.prproj) and/or export the active sequence via exportAsMediaDirect.",
    inputSchema: {
      type: "object",
      properties: {
        save_project: { type: "boolean", default: false },
        save_as_path: { type: "string" },
        export_media_path: { type: "string" },
        export_preset_path: { type: "string" },
        work_area_type: { type: "number", default: 0 }
      },
      additionalProperties: false
    }
  }
];

function startMcpServer() {
  let buffer = Buffer.alloc(0);
  let framingMode = "newline";

  function sendResponse(obj) {
    const jsonStr = JSON.stringify(obj);
    if (framingMode === "content-length") {
      const byteLen = Buffer.byteLength(jsonStr, "utf8");
      process.stdout.write(`Content-Length: ${byteLen}\r\n\r\n${jsonStr}`);
    } else {
      process.stdout.write(jsonStr + "\n");
    }
  }

  function handleRpcMessage(msg) {
    if (!msg || typeof msg !== "object") return;
    const { id, method, params } = msg;

    if (method === "initialize") {
      sendResponse({
        jsonrpc: "2.0",
        id,
        result: {
          protocolVersion: (params && params.protocolVersion) || "2024-11-05",
          capabilities: { tools: {} },
          serverInfo: { name: "premiere-mcp", version: "1.0.0" }
        }
      });
      return;
    }

    if (method === "notifications/initialized" || method === "initialized") return;
    if (method === "ping") {
      sendResponse({ jsonrpc: "2.0", id, result: {} });
      return;
    }
    if (method === "tools/list") {
      sendResponse({ jsonrpc: "2.0", id, result: { tools: TOOLS_DEFINITION } });
      return;
    }

    if (method === "tools/call") {
      const toolName = params && params.name;
      const toolArgs = (params && params.arguments) || {};
      let res;
      try {
        switch (toolName) {
          case "get_premiere_status":
            res = getPremiereStatus();
            break;
          case "execute_premiere_jsx":
            res = executePremiereJsx(toolArgs);
            break;
          case "get_project_summary":
            res = getProjectSummary();
            break;
          case "export_frame_png":
            res = exportFramePng(toolArgs);
            break;
          case "save_or_export_premiere":
            res = saveOrExportPremiere(toolArgs);
            break;
          default:
            res = { ok: false, error: `Unknown tool: ${toolName}` };
        }
        sendResponse({
          jsonrpc: "2.0",
          id,
          result: {
            content: [{ type: "text", text: JSON.stringify(res, null, 2) }],
            isError: res.ok === false
          }
        });
      } catch (err) {
        sendResponse({
          jsonrpc: "2.0",
          id,
          result: {
            content: [{ type: "text", text: JSON.stringify({ ok: false, error: String(err.message || err) }, null, 2) }],
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
        error: { code: -32601, message: `Method not found: ${method}` }
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
      const leadingWsBytes = Buffer.byteLength(preview.slice(0, preview.length - trimmedPreview.length), "utf8");
      if (leadingWsBytes > 0) buffer = buffer.slice(leadingWsBytes);

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
          handleRpcMessage(JSON.parse(bodyText));
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
              handleRpcMessage(msg);
              return;
            } catch (_) {}
          }
          return;
        }
        const line = buffer.slice(0, nlIdx).toString("utf8").trim();
        buffer = buffer.slice(nlIdx + 1);
        if (line.length > 0) {
          try {
            handleRpcMessage(JSON.parse(line));
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
  getPremiereStatus,
  executePremiereJsx,
  getProjectSummary,
  exportFramePng,
  saveOrExportPremiere,
  TOOLS_DEFINITION
};
