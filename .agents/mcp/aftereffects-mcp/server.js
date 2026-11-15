#!/usr/bin/env node
/**
 * Adobe After Effects Local MCP Server (stdio JSON-RPC 2.0)
 * Zero external npm dependencies (Node.js built-in modules only).
 * Supports both Content-Length header framing and newline-delimited JSON-RPC.
 * Supports Windows (AfterFX.exe -r <jsx> + atomic result file) and macOS (osascript).
 */

const fs = require("fs");
const path = require("path");
const os = require("os");
const { spawn, spawnSync } = require("child_process");

const TASKLIST_EXE = process.env.SystemRoot
  ? path.join(process.env.SystemRoot, "System32", "tasklist.exe")
  : "tasklist.exe";

const BRIDGE_ROOT = path.join(os.tmpdir(), "antigravity-ae-mcp-bridge");
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

function findWindowsAfterEffectsExecutables() {
  const results = [];
  const adobeDirs = ["C:\\Program Files\\Adobe", "C:\\Program Files (x86)\\Adobe"];
  for (const baseDir of adobeDirs) {
    try {
      if (!fs.existsSync(baseDir)) continue;
      const entries = fs.readdirSync(baseDir);
      for (const entry of entries) {
        if (entry.toLowerCase().startsWith("adobe after effects")) {
          const exePath = path.join(baseDir, entry, "Support Files", "AfterFX.exe");
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

function getWindowsAfterEffectsProcess() {
  try {
    const proc = spawnSync(
      TASKLIST_EXE,
      ["/FI", "IMAGENAME eq AfterFX.exe", "/FO", "CSV", "/NH"],
      {
        encoding: "utf8",
        timeout: 5000,
        stdio: ["ignore", "pipe", "pipe"],
        windowsHide: true
      }
    );
    const out = (proc.stdout || "").trim();
    if (!out || out.toLowerCase().includes("no tasks are running") || !out.includes("AfterFX.exe")) {
      return { running: false, processes: [] };
    }
    const lines = out.split(/\r?\n/).filter((l) => l.includes("AfterFX.exe"));
    const processes = lines.map((line) => {
      const cols = line.split('","').map((c) => c.replace(/^"|"$/g, ""));
      return {
        imageName: cols[0] || "AfterFX.exe",
        pid: cols[1] ? Number(cols[1]) : null,
        memory: cols[4] || null
      };
    });
    return { running: processes.length > 0, processes };
  } catch (err) {
    return { running: false, processes: [], error: String(err.message || err) };
  }
}

function sleepSync(ms) {
  const end = Date.now() + ms;
  while (Date.now() < end) {
    // Busy-wait short intervals only when Atomics.wait isn't applicable on main thread
    try {
      Atomics.wait(new Int32Array(new SharedArrayBuffer(4)), 0, 0, Math.min(50, end - Date.now()));
    } catch (_) {
      break;
    }
  }
}

/**
 * Execute ExtendScript (JSX) in Adobe After Effects
 */
function executeAfterEffectsJsx({ script, script_path, wrap_try_catch = true, timeout_ms = 60000 }) {
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

  if (typeof script !== "string" || script.trim().length === 0) {
    if (!script_path) {
      return { ok: false, error: "Either 'script' or 'script_path' must be provided." };
    }
  }

  // Prefer CEP Bridge if active (fast, no "Allow Scripts to Write Files" pref required)
  const hb = getBridgeHeartbeatStatus();
  if (hb.active) {
    ensureBridgeDirs();
    let bridgeJsx = rawCode;
    if (wrap_try_catch) {
      bridgeJsx = `${JSX_JSON_POLYFILL}
(function() {
  var __suppressed = false;
  try {
    try { app.beginSuppressDialogs(); __suppressed = true; } catch(_) {}
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
  } finally {
    if (__suppressed) {
      try { app.endSuppressDialogs(false); } catch(_) {}
    }
  }
})();
`;
    }
    const buid = `${Date.now()}_${process.pid}_${Math.random().toString(36).slice(2, 8)}`;
    const reqPath = path.join(REQ_DIR, `${buid}.json`);
    const tmpReqPath = reqPath + ".tmp";
    const resPath = path.join(RES_DIR, `${buid}.json`);
    fs.writeFileSync(tmpReqPath, JSON.stringify({ id: buid, script: bridgeJsx, createdAt: Date.now() }), "utf8");
    fs.renameSync(tmpReqPath, reqPath);
    try {
      const deadline = Date.now() + Number(timeout_ms || 60000);
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
        return { ok: false, error: `Timed out waiting for After Effects CEP Bridge (${timeout_ms}ms).` };
      }
      const rawText = rawResponse.rawResult;
      if (rawText === "EvalScript error.") {
        return { ok: false, error: "ExtendScript EvalScript error." };
      }
      if (wrap_try_catch) {
        try {
          const parsed = JSON.parse(rawText);
          if (parsed && typeof parsed.result === "string") {
            try { parsed.data = JSON.parse(parsed.result); } catch (_) { parsed.data = parsed.result; }
          }
          return parsed;
        } catch (_) {
          return { ok: true, result: rawText, data: rawText };
        }
      }
      return { ok: true, result: rawText, data: rawText };
    } finally {
      for (const f of [reqPath, tmpReqPath, resPath]) {
        try { if (fs.existsSync(f)) fs.unlinkSync(f); } catch (_) {}
      }
    }
  }

  const uid = `${Date.now()}_${process.pid}_${Math.random().toString(36).slice(2, 8)}`;
  const tmpDir = os.tmpdir();
  const jsxPath = path.join(tmpDir, `ae_mcp_${uid}.jsx`);
  const outPath = path.join(tmpDir, `ae_mcp_res_${uid}.json`);
  const tmpOutPath = outPath + ".tmp";
  const outPathUnix = outPath.replace(/\\/g, "/");
  const tmpOutPathUnix = tmpOutPath.replace(/\\/g, "/");

  let finalJsx = rawCode;
  if (wrap_try_catch) {
    finalJsx = `${JSX_JSON_POLYFILL}
(function() {
  var __outPath = ${toAsciiJsString(outPathUnix)};
  var __tmpOutPath = ${toAsciiJsString(tmpOutPathUnix)};
  function __writeResult(payload) {
    var tf = new File(__tmpOutPath);
    tf.encoding = "UTF-8";
    tf.lineFeed = "Unix";
    if (tf.open("w")) {
      tf.write(payload);
      tf.close();
      var dest = new File(__outPath);
      if (dest.exists) { try { dest.remove(); } catch(_) {} }
      tf.rename(dest.name);
    }
  }
  var __suppressed = false;
  try {
    try { app.beginSuppressDialogs(); __suppressed = true; } catch(_) {}
    var __fn = function() {
${rawCode}
    };
    var __res = __fn();
    var __payload = JSON.stringify({
      ok: true,
      result: typeof __res === "undefined" ? null : (typeof __res === "string" ? __res : JSON.stringify(__res))
    });
    __writeResult(__payload);
    return __payload;
  } catch (e) {
    var __errPayload = JSON.stringify({
      ok: false,
      error: e && e.message ? String(e.message) : String(e),
      line: e && e.line ? Number(e.line) : null,
      fileName: e && e.fileName ? String(e.fileName) : null
    });
    __writeResult(__errPayload);
    return __errPayload;
  } finally {
    if (__suppressed) {
      try { app.endSuppressDialogs(false); } catch(_) {}
    }
  }
})();
`;
  }

  fs.writeFileSync(jsxPath, finalJsx, "utf8");

  try {
    if (process.platform === "win32") {
      const installs = findWindowsAfterEffectsExecutables();
      if (installs.length === 0) {
        return { ok: false, error: "Adobe After Effects executable (AfterFX.exe) not found." };
      }
      const exePath = installs[0].path;
      const child = spawn(exePath, ["-r", jsxPath], {
        detached: true,
        stdio: "ignore",
        windowsHide: true
      });
      child.unref();

      const deadline = Date.now() + Number(timeout_ms || 60000);
      let rawText = "";
      while (Date.now() < deadline) {
        if (fs.existsSync(outPath)) {
          try {
            rawText = fs.readFileSync(outPath, "utf8").replace(/^\uFEFF/, "").trim();
            if (rawText.length > 0) {
              JSON.parse(rawText);
              break;
            }
          } catch (_) {
            rawText = "";
          }
        }
        sleepSync(100);
      }

      if (!rawText) {
        return {
          ok: false,
          error: `Timed out waiting for After Effects response (${timeout_ms}ms). Ensure After Effects is responsive and not blocked by a modal dialog.`
        };
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
    } else if (process.platform === "darwin") {
      const appleScript = `tell application "Adobe After Effects" to DoScriptFile POSIX file ${toAsciiJsString(jsxPath)}`;
      const proc = spawnSync("osascript", ["-e", appleScript], {
        encoding: "utf8",
        timeout: Number(timeout_ms || 60000),
        stdio: ["ignore", "pipe", "pipe"]
      });
      let rawText = "";
      if (fs.existsSync(outPath)) {
        rawText = fs.readFileSync(outPath, "utf8").replace(/^\uFEFF/, "").trim();
      }
      if (!rawText && proc.stdout) {
        rawText = proc.stdout.trim();
      }
      if (!rawText) {
        return {
          ok: false,
          error: proc.stderr ? proc.stderr.trim() : "osascript execution failed",
          exitCode: proc.status
        };
      }
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
    } else {
      return { ok: false, error: `Unsupported platform: ${process.platform}` };
    }
  } finally {
    for (const f of [jsxPath, outPath, tmpOutPath]) {
      try {
        if (fs.existsSync(f)) fs.unlinkSync(f);
      } catch (_) {}
    }
  }
}

function getAfterEffectsStatus() {
  const installs = process.platform === "win32" ? findWindowsAfterEffectsExecutables() : [];
  const procInfo = process.platform === "win32" ? getWindowsAfterEffectsProcess() : { running: false, processes: [] };

  const base = {
    ok: true,
    platform: process.platform,
    installedVersions: installs,
    running: procInfo.running,
    processes: procInfo.processes
  };

  if (!procInfo.running && process.platform === "win32") {
    base.note = "After Effects is not currently running. Calling execute_aftereffects_jsx will launch it automatically.";
    return base;
  }

  const jsx = `
var proj = app.project;
var comps = [];
var itemCount = proj ? proj.numItems : 0;
for (var i = 1; i <= itemCount; i++) {
  var it = proj.item(i);
  if (it instanceof CompItem) {
    comps.push({
      id: it.id,
      name: it.name,
      width: it.width,
      height: it.height,
      frameRate: it.frameRate,
      duration: it.duration,
      numLayers: it.numLayers
    });
  }
}
var activeName = null;
try {
  if (proj && proj.activeItem && proj.activeItem instanceof CompItem) {
    activeName = proj.activeItem.name;
  }
} catch(_) {}
return JSON.stringify({
  version: app.version,
  buildName: app.buildName,
  projectFile: proj && proj.file ? proj.file.fsName : null,
  numItems: itemCount,
  compCount: comps.length,
  activeComp: activeName,
  compositions: comps
});
`;
  const res = executeAfterEffectsJsx({ script: jsx, timeout_ms: 20000 });
  if (!res.ok) {
    return Object.assign(base, {
      jsxConnected: false,
      jsxError: res.error
    });
  }
  return Object.assign(base, {
    jsxConnected: true,
    appInfo: res.data
  });
}

function getProjectSummary({ file_path } = {}) {
  const targetPath = file_path ? path.resolve(file_path).replace(/\\/g, "/") : "";
  const jsx = `
var targetPath = ${toAsciiJsString(targetPath)};
if (targetPath) {
  var f = new File(targetPath);
  if (!f.exists) {
    throw new Error("File not found: " + targetPath);
  }
  app.open(f);
}
var proj = app.project;
if (!proj) {
  throw new Error("No active project.");
}
var items = [];
var comps = [];
for (var i = 1; i <= proj.numItems; i++) {
  var it = proj.item(i);
  var typeName = "Other";
  if (it instanceof CompItem) typeName = "Comp";
  else if (it instanceof FolderItem) typeName = "Folder";
  else if (it instanceof FootageItem) typeName = "Footage";

  var itemInfo = {
    index: i,
    id: it.id,
    name: it.name,
    type: typeName
  };
  if (it instanceof FootageItem && it.mainSource && it.mainSource.file) {
    itemInfo.file = it.mainSource.file.fsName;
  }
  items.push(itemInfo);

  if (it instanceof CompItem) {
    var layers = [];
    for (var l = 1; l <= it.numLayers; l++) {
      var lyr = it.layer(l);
      var lInfo = {
        index: l,
        name: lyr.name,
        enabled: lyr.enabled,
        inPoint: lyr.inPoint,
        outPoint: lyr.outPoint,
        startTime: lyr.startTime
      };
      try {
        if (lyr instanceof TextLayer) {
          lInfo.kind = "Text";
          lInfo.text = String(lyr.property("Source Text").value.text);
        } else if (lyr instanceof ShapeLayer) {
          lInfo.kind = "Shape";
        } else if (lyr instanceof CameraLayer) {
          lInfo.kind = "Camera";
        } else if (lyr instanceof LightLayer) {
          lInfo.kind = "Light";
        } else {
          lInfo.kind = "AV";
        }
      } catch(_) {}
      layers.push(lInfo);
    }
    comps.push({
      id: it.id,
      name: it.name,
      width: it.width,
      height: it.height,
      frameRate: it.frameRate,
      duration: it.duration,
      time: it.time,
      numLayers: it.numLayers,
      layers: layers
    });
  }
}
return JSON.stringify({
  projectFile: proj.file ? proj.file.fsName : null,
  bitsPerChannel: proj.bitsPerChannel,
  numItems: proj.numItems,
  items: items,
  compositions: comps
});
`;
  return executeAfterEffectsJsx({ script: jsx });
}

function exportCompFramePng({ output_path, comp_name, time_seconds } = {}) {
  if (!output_path) {
    return { ok: false, error: "output_path is required." };
  }
  const absOut = path.resolve(output_path);
  const dir = path.dirname(absOut);
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
  const outUnix = absOut.replace(/\\/g, "/");
  const compNameArg = comp_name ? String(comp_name) : "";
  const hasTime = typeof time_seconds === "number" && !isNaN(time_seconds);
  const timeVal = hasTime ? Number(time_seconds) : -1;

  const jsx = `
var proj = app.project;
if (!proj) throw new Error("No active project.");
var compName = ${toAsciiJsString(compNameArg)};
var comp = null;
if (compName) {
  for (var i = 1; i <= proj.numItems; i++) {
    var it = proj.item(i);
    if (it instanceof CompItem && it.name === compName) {
      comp = it;
      break;
    }
  }
  if (!comp) throw new Error("Composition not found: " + compName);
} else if (proj.activeItem && proj.activeItem instanceof CompItem) {
  comp = proj.activeItem;
} else {
  for (var i = 1; i <= proj.numItems; i++) {
    if (proj.item(i) instanceof CompItem) {
      comp = proj.item(i);
      break;
    }
  }
}
if (!comp) throw new Error("No composition found in project.");

var t = ${hasTime ? timeVal : "comp.time"};
if (t < 0) t = 0;
if (t > comp.duration) t = comp.duration;

var outFile = new File(${toAsciiJsString(outUnix)});
if (outFile.exists) outFile.remove();
comp.saveFrameToPng(t, outFile);

return JSON.stringify({
  compName: comp.name,
  time: t,
  width: comp.width,
  height: comp.height,
  outputPath: outFile.fsName,
  exists: outFile.exists
});
`;
  const res = executeAfterEffectsJsx({ script: jsx });
  if (res.ok && fs.existsSync(absOut)) {
    const stat = fs.statSync(absOut);
    res.fileSizeBytes = stat.size;
  }
  return res;
}

function saveAfterEffectsProject({ output_path, render_comp_name, render_output_path } = {}) {
  const outUnix = output_path ? path.resolve(output_path).replace(/\\/g, "/") : "";
  const renderOutUnix = render_output_path ? path.resolve(render_output_path).replace(/\\/g, "/") : "";
  if (output_path) {
    const dir = path.dirname(path.resolve(output_path));
    if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
  }
  if (render_output_path) {
    const dir = path.dirname(path.resolve(render_output_path));
    if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
  }
  const compNameArg = render_comp_name ? String(render_comp_name) : "";

  const jsx = `
var proj = app.project;
if (!proj) throw new Error("No active project.");
var outPath = ${toAsciiJsString(outUnix)};
var renderCompName = ${toAsciiJsString(compNameArg)};
var renderOutPath = ${toAsciiJsString(renderOutUnix)};

var savedFile = null;
if (outPath) {
  var f = new File(outPath);
  proj.save(f);
  savedFile = f.fsName;
} else if (proj.file) {
  proj.save();
  savedFile = proj.file.fsName;
}

var renderInfo = null;
if (renderOutPath) {
  var comp = null;
  if (renderCompName) {
    for (var i = 1; i <= proj.numItems; i++) {
      if (proj.item(i) instanceof CompItem && proj.item(i).name === renderCompName) {
        comp = proj.item(i);
        break;
      }
    }
  } else if (proj.activeItem && proj.activeItem instanceof CompItem) {
    comp = proj.activeItem;
  }
  if (!comp) throw new Error("Target composition for render not found.");
  var rqItem = proj.renderQueue.items.add(comp);
  var om = rqItem.outputModule(1);
  om.file = new File(renderOutPath);
  proj.renderQueue.render();
  renderInfo = {
    compName: comp.name,
    outputPath: om.file.fsName,
    status: rqItem.status
  };
}

return JSON.stringify({
  savedFile: savedFile,
  render: renderInfo
});
`;
  return executeAfterEffectsJsx({ script: jsx, timeout_ms: 180000 });
}

const TOOLS_DEFINITION = [
  {
    name: "get_aftereffects_status",
    description: "Check Adobe After Effects installation, running process status, and active project/compositions.",
    inputSchema: {
      type: "object",
      properties: {},
      additionalProperties: false
    }
  },
  {
    name: "execute_aftereffects_jsx",
    description: "Execute ExtendScript (JSX) inside Adobe After Effects via AfterFX.exe -r and return the JSON/string result.",
    inputSchema: {
      type: "object",
      properties: {
        script: { type: "string", description: "ExtendScript (JSX) code string to execute." },
        script_path: { type: "string", description: "Path to a .jsx script file to execute." },
        wrap_try_catch: { type: "boolean", default: true, description: "Wrap script in try/catch and JSON result writer." },
        timeout_ms: { type: "number", default: 60000, description: "Timeout in milliseconds." }
      },
      additionalProperties: false
    }
  },
  {
    name: "get_project_summary",
    description: "Get summary of the active After Effects project (or open a specified .aep file), listing items, compositions, and layers.",
    inputSchema: {
      type: "object",
      properties: {
        file_path: { type: "string", description: "Optional .aep project file path to open before inspecting." }
      },
      additionalProperties: false
    }
  },
  {
    name: "export_comp_frame_png",
    description: "Save a single frame of an After Effects composition to a PNG file using saveFrameToPng for visual inspection.",
    inputSchema: {
      type: "object",
      properties: {
        output_path: { type: "string", description: "Destination .png file path." },
        comp_name: { type: "string", description: "Target composition name (defaults to active comp or first comp)." },
        time_seconds: { type: "number", description: "Time in seconds to capture (defaults to current comp time)." }
      },
      required: ["output_path"],
      additionalProperties: false
    }
  },
  {
    name: "save_aftereffects_project",
    description: "Save the active After Effects project (.aep) and/or render a composition via the Render Queue.",
    inputSchema: {
      type: "object",
      properties: {
        output_path: { type: "string", description: "Optional .aep save path." },
        render_comp_name: { type: "string", description: "Optional composition name to render." },
        render_output_path: { type: "string", description: "Optional output video/media path to render via Render Queue." }
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
          serverInfo: { name: "aftereffects-mcp", version: "1.0.0" }
        }
      });
      return;
    }

    if (method === "notifications/initialized" || method === "initialized") {
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
      let res;
      try {
        switch (toolName) {
          case "get_aftereffects_status":
            res = getAfterEffectsStatus();
            break;
          case "execute_aftereffects_jsx":
            res = executeAfterEffectsJsx(toolArgs);
            break;
          case "get_project_summary":
            res = getProjectSummary(toolArgs);
            break;
          case "export_comp_frame_png":
            res = exportCompFramePng(toolArgs);
            break;
          case "save_aftereffects_project":
            res = saveAfterEffectsProject(toolArgs);
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
  getAfterEffectsStatus,
  executeAfterEffectsJsx,
  getProjectSummary,
  exportCompFramePng,
  saveAfterEffectsProject,
  TOOLS_DEFINITION
};
