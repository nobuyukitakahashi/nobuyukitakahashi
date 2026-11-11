#!/usr/bin/env node
/**
 * Adobe Photoshop Local MCP Server (stdio JSON-RPC 2.0)
 * Zero external npm dependencies (Node.js built-in modules only).
 * Supports both Content-Length header framing and newline-delimited JSON-RPC.
 * Supports Windows (COM Photoshop.Application via PowerShell) and macOS (osascript).
 */

const fs = require("fs");
const path = require("path");
const os = require("os");
const { spawnSync } = require("child_process");

const PS_EXE = process.env.SystemRoot
  ? path.join(process.env.SystemRoot, "System32", "WindowsPowerShell", "v1.0", "powershell.exe")
  : "powershell.exe";

const TASKLIST_EXE = process.env.SystemRoot
  ? path.join(process.env.SystemRoot, "System32", "tasklist.exe")
  : "tasklist.exe";

// Helper: Escape any string into pure ASCII JS literal with \uXXXX escapes for non-ASCII
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

/**
 * Fast Node.js native detection of Adobe Photoshop executables on Windows
 */
function findWindowsPhotoshopExecutables() {
  const results = [];
  const adobeDirs = ["C:\\Program Files\\Adobe", "C:\\Program Files (x86)\\Adobe"];
  for (const baseDir of adobeDirs) {
    try {
      if (!fs.existsSync(baseDir)) continue;
      const entries = fs.readdirSync(baseDir);
      for (const entry of entries) {
        if (entry.toLowerCase().startsWith("adobe photoshop")) {
          const exePath = path.join(baseDir, entry, "Photoshop.exe");
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
  return results;
}

/**
 * Fast process check via tasklist.exe (no PowerShell cold-start overhead)
 */
function getWindowsPhotoshopProcess() {
  try {
    const proc = spawnSync(
      TASKLIST_EXE,
      ["/FI", "IMAGENAME eq Photoshop.exe", "/FO", "CSV", "/NH"],
      {
        encoding: "utf8",
        timeout: 5000,
        stdio: ["ignore", "pipe", "pipe"],
        windowsHide: true
      }
    );
    const out = (proc.stdout || "").trim();
    const lines = out.split(/\r?\n/).filter((l) => l.toLowerCase().includes("photoshop.exe"));
    if (lines.length > 0) {
      const cols = lines[0].split('","').map((s) => s.replace(/^"|"$/g, ""));
      const pid = parseInt(cols[1], 10);
      return { isRunning: true, processId: isNaN(pid) ? null : pid };
    }
  } catch (_) {}
  return { isRunning: false, processId: null };
}

/**
 * Execute ExtendScript (JSX) in Adobe Photoshop and return parsed result.
 */
function runExtendScript(jsxCode, options = {}) {
  const wrapTryCatch = options.wrap_try_catch !== false;
  const timeoutMs = options.timeout_ms || 120000;

  const tmpId = `agy_ps_${ process.pid }_${ Date.now() }_${ Math.random().toString(36).slice(2, 8) }`;
  const tmpDir = os.tmpdir();
  const jsxPath = path.join(tmpDir, `${ tmpId }.jsx`);
  const outPath = path.join(tmpDir, `${ tmpId }_out.txt`);
  const ps1Path = path.join(tmpDir, `${ tmpId }.ps1`);

  const escapedOutPath = toAsciiJsString(outPath.replace(/\\/g, "/"));

  const finalJsx = wrapTryCatch
    ? `${ JSX_JSON_POLYFILL }
(function() {
  var __resPayload = "";
  var __origUnits = null;
  var __origDialogs = null;
  try {
    try {
      __origDialogs = app.displayDialogs;
      app.displayDialogs = DialogModes.NO;
    } catch (_d) {}
    try {
      __origUnits = app.preferences.rulerUnits;
      app.preferences.rulerUnits = Units.PIXELS;
    } catch (_u) {}
    var __userFn = function() {
${ jsxCode }
    };
    var __val = __userFn();
    var __valStr = (typeof __val === "undefined") ? "null" : (typeof __val === "string" ? __val : JSON.stringify(__val));
    __resPayload = JSON.stringify({ ok: true, result: __valStr });
  } catch (e) {
    __resPayload = JSON.stringify({
      ok: false,
      error: String(e.message || e),
      name: String(e.name || "ExtendScriptError"),
      line: (typeof e.line !== "undefined") ? e.line : null,
      fileName: (typeof e.fileName !== "undefined") ? String(e.fileName) : null
    });
  }
  try {
    var __f = new File(${ escapedOutPath });
    __f.encoding = "UTF-8";
    if (__f.open("w")) {
      __f.write(__resPayload);
      __f.close();
    }
  } catch (fe) {}
  return __resPayload;
})();
`
    : jsxCode;

  // Write JSX with UTF-8 BOM (\uFEFF) so ExtendScript engine always parses UTF-8 accurately
  fs.writeFileSync(jsxPath, "\uFEFF" + finalJsx, "utf8");

  try {
    if (process.platform === "win32") {
      const psJsxPath = jsxPath.replace(/'/g, "''");
      const psScript = `
$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
try {
  try {
    $app = New-Object -ComObject Photoshop.Application
  } catch {
    # If an orphaned Photoshop process revoked its COM class factory, terminate it and retry once
    Stop-Process -Name "Photoshop" -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
    $app = New-Object -ComObject Photoshop.Application
  }
  $res = $app.DoJavaScriptFile('${ psJsxPath }')
  if ($null -ne $res) {
    Write-Output $res
  }
} catch {
  $errObj = @{
    ok = $false
    error = $_.Exception.Message
    source = "WindowsCOM"
  } | ConvertTo-Json -Compress
  Write-Output $errObj
  exit 1
}
`;
      fs.writeFileSync(ps1Path, "\uFEFF" + psScript, "utf8");
      const proc = spawnSync(
        PS_EXE,
        ["-NonInteractive", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", ps1Path],
        {
          encoding: "utf8",
          timeout: timeoutMs,
          stdio: ["ignore", "pipe", "pipe"],
          windowsHide: true
        }
      );

      let rawText = "";
      if (fs.existsSync(outPath)) {
        rawText = fs.readFileSync(outPath, "utf8").replace(/^\uFEFF/, "").trim();
      }
      if (!rawText && proc.stdout) {
        rawText = proc.stdout.replace(/^\uFEFF/, "").trim();
      }

      if (!rawText) {
        return {
          ok: false,
          error: proc.stderr ? proc.stderr.trim() : "Empty response from Photoshop COM",
          exitCode: proc.status
        };
      }

      if (wrapTryCatch) {
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
      const appleScript = `tell application "Adobe Photoshop" to do javascript file POSIX file ${ toAsciiJsString(jsxPath) }`;
      const proc = spawnSync("osascript", ["-e", appleScript], {
        encoding: "utf8",
        timeout: timeoutMs,
        stdio: ["ignore", "pipe", "pipe"]
      });

      let rawText = "";
      if (fs.existsSync(outPath)) {
        rawText = fs.readFileSync(outPath, "utf8").replace(/^\uFEFF/, "").trim();
      }
      if (!rawText && proc.stdout) {
        rawText = proc.stdout.trim();
      }
      if (!rawText && proc.status !== 0) {
        return {
          ok: false,
          error: proc.stderr ? proc.stderr.trim() : "osascript execution failed",
          exitCode: proc.status
        };
      }
      if (wrapTryCatch) {
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
    } else {
      return { ok: false, error: `Unsupported platform: ${ process.platform }` };
    }
  } finally {
    for (const f of [jsxPath, outPath, ps1Path]) {
      try {
        if (fs.existsSync(f)) fs.unlinkSync(f);
      } catch (_) {}
    }
  }
}

/**
 * Tool 1: get_photoshop_status
 * Uses Node.js fs and tasklist.exe first so it never hangs in headless stdio MCP mode.
 */
function getPhotoshopStatus() {
  if (process.platform === "win32") {
    const executables = findWindowsPhotoshopExecutables();
    const procInfo = getWindowsPhotoshopProcess();

    const statusObj = {
      ok: true,
      platform: "win32",
      executables,
      comProgId: "Photoshop.Application",
      comRegistered: executables.length > 0,
      isRunning: procInfo.isRunning,
      processId: procInfo.processId,
      appVersion: null,
      openDocuments: []
    };

    if (procInfo.isRunning) {
      const docRes = runExtendScript(
        `
        var docs = [];
        for (var i = 0; i < app.documents.length; i++) {
          var d = app.documents[i];
          var modeStr = String(d.mode);
          docs.push({
            name: d.name,
            widthPx: Number(d.width.as("px")),
            heightPx: Number(d.height.as("px")),
            resolutionDpi: Number(d.resolution),
            colorMode: modeStr.indexOf("CMYK") >= 0 ? "CMYK" : (modeStr.indexOf("RGB") >= 0 ? "RGB" : modeStr),
            layersCount: Number(d.layers.length)
          });
        }
        return JSON.stringify({ appVersion: String(app.version), documents: docs });
      `,
        { timeout_ms: 8000 }
      );
      if (docRes && docRes.ok && docRes.data) {
        statusObj.appVersion = docRes.data.appVersion || null;
        statusObj.openDocuments = docRes.data.documents || [];
      }
    }

    return statusObj;
  } else {
    // macOS
    const apps = [];
    try {
      const entries = fs.readdirSync("/Applications");
      for (const name of entries) {
        if (name.startsWith("Adobe Photoshop")) {
          apps.push(path.join("/Applications", name));
        }
      }
    } catch (_) {}
    const ps = spawnSync("pgrep", ["-x", "Adobe Photoshop"], {
      encoding: "utf8",
      stdio: ["ignore", "pipe", "pipe"]
    });
    const isRunning = ps.status === 0;
    const statusObj = {
      ok: true,
      platform: process.platform,
      executables: apps,
      isRunning,
      openDocuments: []
    };
    if (isRunning) {
      const docRes = runExtendScript(`
        var docs = [];
        for (var i = 0; i < app.documents.length; i++) {
          var d = app.documents[i];
          var modeStr = String(d.mode);
          docs.push({
            name: d.name,
            widthPx: Number(d.width.as("px")),
            heightPx: Number(d.height.as("px")),
            resolutionDpi: Number(d.resolution),
            colorMode: modeStr.indexOf("CMYK") >= 0 ? "CMYK" : "RGB",
            layersCount: Number(d.layers.length)
          });
        }
        return JSON.stringify({ appVersion: String(app.version), documents: docs });
      `);
      if (docRes && docRes.ok && docRes.data) {
        statusObj.appVersion = docRes.data.appVersion;
        statusObj.openDocuments = docRes.data.documents || [];
      }
    }
    return statusObj;
  }
}

/**
 * Tool 2: execute_photoshop_jsx
 */
function executePhotoshopJsx(args = {}) {
  let code = args.script || "";
  if (args.script_path) {
    const resolved = path.resolve(args.script_path);
    if (!fs.existsSync(resolved)) {
      return { ok: false, error: `Script file not found: ${ resolved }` };
    }
    code = fs.readFileSync(resolved, "utf8").replace(/^\uFEFF/, "");
  }
  if (!code || !code.trim()) {
    return { ok: false, error: "Either 'script' or 'script_path' must be provided." };
  }
  const wrapTryCatch = args.wrap_try_catch !== false;
  return runExtendScript(code, { wrap_try_catch: wrapTryCatch });
}

/**
 * Tool 3: get_document_summary
 */
function getDocumentSummary(args = {}) {
  let tmpCopyToOpen = "";
  if (args.file_path) {
    const resolved = path.resolve(args.file_path);
    if (!fs.existsSync(resolved)) {
      return { ok: false, error: `Target file does not exist: ${ resolved }` };
    }
    const ext = path.extname(resolved);
    tmpCopyToOpen = path.join(os.tmpdir(), `agy_ps_open_${ process.pid }_${ Date.now() }${ ext }`);
    fs.copyFileSync(resolved, tmpCopyToOpen);
  }

  const jsx = `
    var targetPath = ${ toAsciiJsString(tmpCopyToOpen.replace(/\\/g, "/")) };
    if (targetPath && targetPath.length > 0) {
      var f = new File(targetPath);
      if (!f.exists) {
        throw new Error("Target file does not exist: " + targetPath);
      }
      app.open(f);
    }
    if (app.documents.length === 0) {
      throw new Error("No active document is open in Adobe Photoshop.");
    }
    var doc = app.activeDocument;
    var fullPathStr = "";
    try { fullPathStr = doc.fullName.fsName; } catch (e) { fullPathStr = doc.name; }

    function inspectLayers(container, depth) {
      var list = [];
      if (depth > 5) return list;
      var len = Math.min(container.layers.length, 100);
      for (var i = 0; i < len; i++) {
        var ly = container.layers[i];
        var b = [0, 0, 0, 0];
        try {
          b = [
            Number(ly.bounds[0].as("px")),
            Number(ly.bounds[1].as("px")),
            Number(ly.bounds[2].as("px")),
            Number(ly.bounds[3].as("px"))
          ];
        } catch (_b) {}

        var item = {
          index: i,
          name: String(ly.name),
          typename: String(ly.typename),
          visible: Boolean(ly.visible),
          opacity: Math.round(Number(ly.opacity)),
          blendMode: String(ly.blendMode),
          boundsPx: b
        };

        if (ly.typename === "ArtLayer") {
          item.kind = String(ly.kind);
          if (ly.kind === LayerKind.TEXT) {
            try {
              var ti = ly.textItem;
              item.textInfo = {
                contents: String(ti.contents || ""),
                font: String(ti.font || ""),
                sizePx: Number(ti.size.as("px"))
              };
            } catch (_t) {}
          }
        } else if (ly.typename === "LayerSet") {
          item.children = inspectLayers(ly, depth + 1);
        }
        list.push(item);
      }
      return list;
    }

    var modeStr = String(doc.mode);
    return JSON.stringify({
      name: doc.name,
      fullPath: fullPathStr,
      widthPx: Number(doc.width.as("px")),
      heightPx: Number(doc.height.as("px")),
      resolutionDpi: Number(doc.resolution),
      colorMode: modeStr.indexOf("CMYK") >= 0 ? "CMYK" : (modeStr.indexOf("RGB") >= 0 ? "RGB" : modeStr),
      bitsPerChannel: String(doc.bitsPerChannel),
      topLevelLayersCount: Number(doc.layers.length),
      artLayersCount: Number(doc.artLayers.length),
      layerSetsCount: Number(doc.layerSets.length),
      layers: inspectLayers(doc, 0)
    });
  `;

  try {
    return runExtendScript(jsx, { wrap_try_catch: true });
  } finally {
    if (tmpCopyToOpen && fs.existsSync(tmpCopyToOpen)) {
      try {
        fs.unlinkSync(tmpCopyToOpen);
      } catch (_) {}
    }
  }
}

/**
 * Helper to inspect PNG width & height from PNG file header (bytes 16..23)
 */
function readPngDimensions(filePath) {
  try {
    const fd = fs.openSync(filePath, "r");
    const buf = Buffer.alloc(24);
    fs.readSync(fd, buf, 0, 24, 0);
    fs.closeSync(fd);
    if (buf[0] === 0x89 && buf[1] === 0x50 && buf[2] === 0x4e && buf[3] === 0x47) {
      const width = buf.readUInt32BE(16);
      const height = buf.readUInt32BE(20);
      return { width, height };
    }
  } catch (_) {}
  return null;
}

/**
 * Tool 4: export_canvas_png
 */
function exportCanvasPng(args = {}) {
  if (!args.output_path) {
    return { ok: false, error: "'output_path' is required." };
  }
  const outResolved = path.resolve(args.output_path);
  const outDir = path.dirname(outResolved);
  if (!fs.existsSync(outDir)) {
    fs.mkdirSync(outDir, { recursive: true });
  }
  const scale = args.scale != null ? Number(args.scale) : 100;

  const tmpPng = path.join(
    os.tmpdir(),
    `agy_ps_export_${ process.pid }_${ Date.now() }.png`
  );

  const jsx = `
    if (app.documents.length === 0) {
      throw new Error("No active document is open in Adobe Photoshop.");
    }
    var origDoc = app.activeDocument;
    var wPx = Number(origDoc.width.as("px"));
    var hPx = Number(origDoc.height.as("px"));
    var scaleVal = ${ scale };

    var dup = origDoc.duplicate("AGY_Temp_Export", false);
    try {
      if (dup.mode !== DocumentMode.RGB) {
        dup.changeMode(ChangeMode.RGB);
      }
      if (scaleVal !== 100 && scaleVal > 0) {
        var newW = UnitValue(Math.round((wPx * scaleVal) / 100), "px");
        var newH = UnitValue(Math.round((hPx * scaleVal) / 100), "px");
        dup.resizeImage(newW, newH, origDoc.resolution, ResampleMethod.BICUBICSHARPER);
      }
      var pngOpts = new PNGSaveOptions();
      pngOpts.compression = 6;
      pngOpts.interlaced = false;
      var outFile = new File(${ toAsciiJsString(tmpPng.replace(/\\/g, "/")) });
      dup.saveAs(outFile, pngOpts, true, Extension.LOWERCASE);
    } finally {
      dup.close(SaveOptions.DONOTSAVECHANGES);
      app.activeDocument = origDoc;
    }

    return JSON.stringify({
      sourceDocument: origDoc.name,
      originalWidthPx: wPx,
      originalHeightPx: hPx,
      scale: scaleVal
    });
  `;

  const res = runExtendScript(jsx, { wrap_try_catch: true });
  if (!res.ok) return res;

  try {
    if (!fs.existsSync(tmpPng)) {
      return { ok: false, error: "Photoshop PNG save completed but temporary PNG was not created." };
    }
    fs.copyFileSync(tmpPng, outResolved);
    fs.unlinkSync(tmpPng);
    const dims = readPngDimensions(outResolved);
    const stat = fs.statSync(outResolved);
    return {
      ok: true,
      output_path: outResolved,
      file_size_bytes: stat.size,
      dimensions_px: dims,
      export_info: res.data
    };
  } catch (e) {
    return { ok: false, error: String(e.message || e) };
  }
}

/**
 * Tool 5: save_photoshop_document
 */
function savePhotoshopDocument(args = {}) {
  if (!args.output_path) {
    return { ok: false, error: "'output_path' is required." };
  }
  const outResolved = path.resolve(args.output_path);
  const outDir = path.dirname(outResolved);
  if (!fs.existsSync(outDir)) {
    fs.mkdirSync(outDir, { recursive: true });
  }
  const ext = path.extname(outResolved).toLowerCase();
  if (![".psd", ".png", ".jpg", ".jpeg", ".tif", ".tiff"].includes(ext)) {
    return {
      ok: false,
      error: `Unsupported extension '${ ext }'. Supported: .psd, .png, .jpg, .tiff`
    };
  }
  const rasterizeText = Boolean(args.rasterize_text);
  const cmykConvert = Boolean(args.cmyk_convert);
  const flatten = Boolean(args.flatten);

  const tmpSave = path.join(
    os.tmpdir(),
    `agy_ps_save_${ process.pid }_${ Date.now() }${ ext }`
  );

  const jsx = `
    if (app.documents.length === 0) {
      throw new Error("No active document is open in Adobe Photoshop.");
    }
    var origDoc = app.activeDocument;
    var ext = ${ toAsciiJsString(ext) };
    var doRasterizeText = ${ rasterizeText ? "true" : "false" };
    var doCmyk = ${ cmykConvert ? "true" : "false" };
    var doFlatten = ${ flatten ? "true" : "false" };

    // Work on a duplicate if destructive operations or non-PSD exports are requested
    var useDuplicate = (doRasterizeText || doCmyk || doFlatten || ext !== ".psd");
    var targetDoc = useDuplicate ? origDoc.duplicate("AGY_Temp_Save", false) : origDoc;
    var rasterizedCount = 0;

    function rasterizeAllTextLayers(container) {
      for (var i = container.layers.length - 1; i >= 0; i--) {
        var ly = container.layers[i];
        if (ly.typename === "ArtLayer" && ly.kind === LayerKind.TEXT) {
          try {
            ly.rasterize(RasterizeType.TEXTCONTENTS);
            rasterizedCount++;
          } catch (_r) {}
        } else if (ly.typename === "LayerSet") {
          rasterizeAllTextLayers(ly);
        }
      }
    }

    try {
      if (doRasterizeText) {
        rasterizeAllTextLayers(targetDoc);
      }
      if (doCmyk && targetDoc.mode !== DocumentMode.CMYK) {
        targetDoc.changeMode(ChangeMode.CMYK);
      }
      if (doFlatten) {
        targetDoc.flatten();
      }

      var destFile = new File(${ toAsciiJsString(tmpSave.replace(/\\/g, "/")) });

      if (ext === ".psd") {
        var psdOpts = new PhotoshopSaveOptions();
        psdOpts.layers = !doFlatten;
        psdOpts.embedColorProfile = true;
        psdOpts.maximizeCompatibility = true;
        targetDoc.saveAs(destFile, psdOpts, true, Extension.LOWERCASE);
      } else if (ext === ".png") {
        if (targetDoc.mode !== DocumentMode.RGB) {
          targetDoc.changeMode(ChangeMode.RGB);
        }
        var pngOpts = new PNGSaveOptions();
        pngOpts.compression = 6;
        pngOpts.interlaced = false;
        targetDoc.saveAs(destFile, pngOpts, true, Extension.LOWERCASE);
      } else if (ext === ".jpg" || ext === ".jpeg") {
        var jpgOpts = new JPEGSaveOptions();
        jpgOpts.quality = 12;
        jpgOpts.embedColorProfile = true;
        targetDoc.saveAs(destFile, jpgOpts, true, Extension.LOWERCASE);
      } else if (ext === ".tif" || ext === ".tiff") {
        var tifOpts = new TiffSaveOptions();
        tifOpts.layers = !doFlatten;
        tifOpts.imageCompression = TIFFEncoding.TIFFLZW;
        targetDoc.saveAs(destFile, tifOpts, true, Extension.LOWERCASE);
      }

      var finalMode = String(targetDoc.mode);
      return JSON.stringify({
        format: ext,
        rasterizedTextLayers: rasterizedCount,
        colorMode: finalMode.indexOf("CMYK") >= 0 ? "CMYK" : "RGB",
        flattened: doFlatten,
        layersCount: Number(targetDoc.layers.length)
      });
    } finally {
      if (useDuplicate && targetDoc) {
        try {
          targetDoc.close(SaveOptions.DONOTSAVECHANGES);
          app.activeDocument = origDoc;
        } catch (_c) {}
      }
    }
  `;

  const res = runExtendScript(jsx, { wrap_try_catch: true });
  if (!res.ok) return res;

  try {
    if (!fs.existsSync(tmpSave)) {
      return { ok: false, error: `Photoshop save completed but temporary file (${ ext }) was not found.` };
    }
    fs.copyFileSync(tmpSave, outResolved);
    fs.unlinkSync(tmpSave);
    const stat = fs.statSync(outResolved);
    return {
      ok: true,
      output_path: outResolved,
      file_size_bytes: stat.size,
      save_info: res.data
    };
  } catch (e) {
    return { ok: false, error: String(e.message || e) };
  }
}

const TOOLS_DEFINITION = [
  {
    name: "get_photoshop_status",
    description:
      "Check Adobe Photoshop installation, COM ProgID registration, running process status, and open documents list (name, width/height px, resolution dpi, colorMode RGB/CMYK, layers count).",
    inputSchema: {
      type: "object",
      properties: {},
      additionalProperties: false
    }
  },
  {
    name: "execute_photoshop_jsx",
    description:
      "Execute Adobe Photoshop ExtendScript (JSX / ActionManager) code or a .jsx file via COM (Windows PowerShell) or osascript (macOS) with UTF-8 protection and automatic try/catch error reporting.",
    inputSchema: {
      type: "object",
      properties: {
        script: {
          type: "string",
          description: "ExtendScript (JSX) code string to execute inside Adobe Photoshop."
        },
        script_path: {
          type: "string",
          description: "Path to a .jsx file to execute inside Adobe Photoshop."
        },
        wrap_try_catch: {
          type: "boolean",
          description: "Whether to wrap the script in a try/catch block and return structured JSON (default: true)."
        }
      },
      additionalProperties: false
    }
  },
  {
    name: "get_document_summary",
    description:
      "Get detailed structural summary of the active Photoshop document (or open a specified .psd/.psb/.png/.jpg/.tiff file first), including dimensions, resolution, colorMode, and full layer hierarchy tree (name, kind, visible, opacity, bounds, textInfo).",
    inputSchema: {
      type: "object",
      properties: {
        file_path: {
          type: "string",
          description: "Optional file path (.psd, .psb, .png, .jpg, .tiff) to open before inspecting."
        }
      },
      additionalProperties: false
    }
  },
  {
    name: "export_canvas_png",
    description:
      "Export the active Photoshop document canvas to a high-quality PNG file for visual inspection (read_file).",
    inputSchema: {
      type: "object",
      properties: {
        output_path: {
          type: "string",
          description: "Destination file path for the exported PNG."
        },
        scale: {
          type: "number",
          description: "Export scale percentage (default: 100 for 100% 1:1 pixel dimensions)."
        }
      },
      required: ["output_path"],
      additionalProperties: false
    }
  },
  {
    name: "save_photoshop_document",
    description:
      "Save or export the active Photoshop document as .psd, .png, .jpg, or .tiff, with optional text layer rasterization, CMYK conversion, and flattening.",
    inputSchema: {
      type: "object",
      properties: {
        output_path: {
          type: "string",
          description: "Destination file path (.psd, .png, .jpg, or .tiff)."
        },
        rasterize_text: {
          type: "boolean",
          description: "If true, rasterize all text layers on a duplicate before saving (default: false)."
        },
        cmyk_convert: {
          type: "boolean",
          description: "If true, convert document color mode to CMYK before saving (default: false)."
        },
        flatten: {
          type: "boolean",
          description: "If true, flatten all layers before saving (default: false)."
        }
      },
      required: ["output_path"],
      additionalProperties: false
    }
  }
];

function handleToolCall(name, args) {
  switch (name) {
    case "get_photoshop_status":
      return getPhotoshopStatus(args);
    case "execute_photoshop_jsx":
      return executePhotoshopJsx(args);
    case "get_document_summary":
      return getDocumentSummary(args);
    case "export_canvas_png":
      return exportCanvasPng(args);
    case "save_photoshop_document":
      return savePhotoshopDocument(args);
    default:
      return { ok: false, error: `Unknown tool: ${ name }` };
  }
}

/**
 * MCP stdio JSON-RPC 2.0 Server Loop
 * Supports both Content-Length header framing and newline-delimited JSON.
 */
function startMcpServer() {
  let framingMode = "newline";
  let buffer = Buffer.alloc(0);

  function sendResponse(obj) {
    const payload = JSON.stringify(obj);
    if (framingMode === "content-length") {
      const byteLen = Buffer.byteLength(payload, "utf8");
      process.stdout.write(`Content-Length: ${ byteLen }\r\n\r\n${ payload }`);
    } else {
      process.stdout.write(payload + "\n");
    }
  }

  function handleRpcMessage(msg) {
    if (!msg || typeof msg !== "object") return;
    const { id, method, params } = msg;

    if (method === "notifications/initialized" || method === "initialized") {
      return;
    }

    if (method === "initialize") {
      const clientProto = (params && params.protocolVersion) || "2024-11-05";
      sendResponse({
        jsonrpc: "2.0",
        id,
        result: {
          protocolVersion: clientProto,
          capabilities: {
            tools: {}
          },
          serverInfo: {
            name: "photoshop",
            version: "1.0.0"
          }
        }
      });
      return;
    }

    if (method === "ping") {
      sendResponse({
        jsonrpc: "2.0",
        id,
        result: {}
      });
      return;
    }

    if (method === "tools/list") {
      sendResponse({
        jsonrpc: "2.0",
        id,
        result: {
          tools: TOOLS_DEFINITION
        }
      });
      return;
    }

    if (method === "tools/call") {
      const toolName = params && params.name;
      const toolArgs = (params && params.arguments) || {};
      try {
        const res = handleToolCall(toolName, toolArgs);
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
          message: `Method not found: ${ method }`
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
          const msg = JSON.parse(bodyText);
          handleRpcMessage(msg);
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
            const msg = JSON.parse(line);
            handleRpcMessage(msg);
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
  getPhotoshopStatus,
  executePhotoshopJsx,
  getDocumentSummary,
  exportCanvasPng,
  savePhotoshopDocument,
  TOOLS_DEFINITION
};
