#!/usr/bin/env node
/**
 * Adobe Illustrator Local MCP Server (stdio JSON-RPC 2.0)
 * Zero external npm dependencies (Node.js built-in modules only).
 * Supports both Content-Length header framing and newline-delimited JSON-RPC.
 * Supports Windows (COM Illustrator.Application via PowerShell) and macOS (osascript).
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
 * Fast Node.js native detection of Adobe Illustrator executables on Windows
 */
function findWindowsIllustratorExecutables() {
  const results = [];
  const adobeDirs = ["C:\\Program Files\\Adobe", "C:\\Program Files (x86)\\Adobe"];
  for (const baseDir of adobeDirs) {
    try {
      if (!fs.existsSync(baseDir)) continue;
      const entries = fs.readdirSync(baseDir);
      for (const entry of entries) {
        if (entry.toLowerCase().startsWith("adobe illustrator")) {
          const exePath = path.join(
            baseDir,
            entry,
            "Support Files",
            "Contents",
            "Windows",
            "Illustrator.exe"
          );
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
function getWindowsIllustratorProcess() {
  try {
    const proc = spawnSync(
      TASKLIST_EXE,
      ["/FI", "IMAGENAME eq Illustrator.exe", "/FO", "CSV", "/NH"],
      {
        encoding: "utf8",
        timeout: 5000,
        stdio: ["ignore", "pipe", "pipe"],
        windowsHide: true
      }
    );
    const out = (proc.stdout || "").trim();
    const lines = out.split(/\r?\n/).filter((l) => l.toLowerCase().includes("illustrator.exe"));
    if (lines.length > 0) {
      const cols = lines[0].split('","').map((s) => s.replace(/^"|"$/g, ""));
      const pid = parseInt(cols[1], 10);
      return { isRunning: true, processId: isNaN(pid) ? null : pid };
    }
  } catch (_) {}
  return { isRunning: false, processId: null };
}

/**
 * Execute ExtendScript (JSX) in Adobe Illustrator and return parsed result.
 */
function runExtendScript(jsxCode, options = {}) {
  const wrapTryCatch = options.wrap_try_catch !== false;
  const timeoutMs = options.timeout_ms || 120000;

  const tmpId = `agy_ai_${ process.pid }_${ Date.now() }_${ Math.random().toString(36).slice(2, 8) }`;
  const tmpDir = os.tmpdir();
  const jsxPath = path.join(tmpDir, `${ tmpId }.jsx`);
  const outPath = path.join(tmpDir, `${ tmpId }_out.txt`);
  const ps1Path = path.join(tmpDir, `${ tmpId }.ps1`);

  const escapedOutPath = toAsciiJsString(outPath.replace(/\\/g, "/"));

  const finalJsx = wrapTryCatch
    ? `${ JSX_JSON_POLYFILL }
(function() {
  var __resPayload = "";
  try {
    app.userInteractionLevel = UserInteractionLevel.DONTDISPLAYALERTS;
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
      const psScript = `
$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
try {
  if (Get-Process -Name "Illustrator" -ErrorAction SilentlyContinue) {
    try {
      $null = [System.Runtime.InteropServices.Marshal]::GetActiveObject("Illustrator.Application")
    } catch {
      Stop-Process -Name "Illustrator" -Force -ErrorAction SilentlyContinue
      Start-Sleep -Seconds 2
    }
  }
  $app = New-Object -ComObject Illustrator.Application
  $res = $app.DoJavaScriptFile(${ toAsciiJsString(jsxPath) })
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
          error: proc.stderr ? proc.stderr.trim() : "Empty response from Illustrator COM",
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
      const appleScript = `tell application "Adobe Illustrator" to do javascript file POSIX file ${ toAsciiJsString(jsxPath) }`;
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
 * Tool 1: get_illustrator_status
 * Uses Node.js fs and tasklist.exe first so it never hangs in headless stdio MCP mode.
 */
function getIllustratorStatus() {
  if (process.platform === "win32") {
    const executables = findWindowsIllustratorExecutables();
    const procInfo = getWindowsIllustratorProcess();

    const statusObj = {
      ok: true,
      platform: "win32",
      executables,
      comProgId: "Illustrator.Application",
      comRegistered: executables.length > 0,
      isRunning: procInfo.isRunning,
      processId: procInfo.processId,
      appVersion: null,
      openDocuments: []
    };

    // Only query COM for open documents if Illustrator is running AND has an active COM object in ROT
    if (procInfo.isRunning) {
      const checkPs = `
$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
try {
  $app = [System.Runtime.InteropServices.Marshal]::GetActiveObject("Illustrator.Application")
  $docs = @()
  $count = $app.Documents.Count
  for ($i = 1; $i -le $count; $i++) {
    $d = $app.Documents.Item($i)
    $docs += @{
      name = [string]$d.Name
      colorSpace = if ([int]$d.DocumentColorSpace -eq 2) { "CMYK" } else { "RGB" }
      artboards = [int]$d.Artboards.Count
      widthPt = [double]$d.Width
      heightPt = [double]$d.Height
    }
  }
  @{ active = $true; version = [string]$app.Version; documents = $docs } | ConvertTo-Json -Depth 5 -Compress
} catch {
  @{ active = $false } | ConvertTo-Json -Compress
}
`;
      try {
        const comProc = spawnSync(
          PS_EXE,
          ["-NonInteractive", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", checkPs],
          {
            encoding: "utf8",
            timeout: 5000,
            stdio: ["ignore", "pipe", "pipe"],
            windowsHide: true
          }
        );
        const raw = (comProc.stdout || "").replace(/^\uFEFF/, "").trim();
        if (raw) {
          const parsed = JSON.parse(raw);
          if (parsed.active) {
            statusObj.appVersion = parsed.version || null;
            statusObj.openDocuments = Array.isArray(parsed.documents)
              ? parsed.documents
              : parsed.documents
              ? [parsed.documents]
              : [];
          } else {
            statusObj.comNote = "Illustrator process detected in background (-Embedding standby); will re-attach on next execute/summary call.";
          }
        }
      } catch (_) {}
    }

    return statusObj;
  } else {
    // macOS
    const apps = [];
    try {
      const entries = fs.readdirSync("/Applications");
      for (const name of entries) {
        if (name.startsWith("Adobe Illustrator")) {
          apps.push(path.join("/Applications", name));
        }
      }
    } catch (_) {}
    const ps = spawnSync("pgrep", ["-x", "Adobe Illustrator"], {
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
          var cs = String(d.documentColorSpace);
          docs.push({
            name: d.name,
            colorSpace: cs.indexOf("CMYK") >= 0 ? "CMYK" : "RGB",
            artboards: d.artboards.length
          });
        }
        return JSON.stringify({ appVersion: app.version, documents: docs });
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
 * Tool 2: execute_illustrator_jsx
 */
function executeIllustratorJsx(args = {}) {
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
  const filePath = args.file_path ? path.resolve(args.file_path).replace(/\\/g, "/") : "";
  const jsx = `
    var targetPath = ${ toAsciiJsString(filePath) };
    if (targetPath && targetPath.length > 0) {
      var f = new File(targetPath);
      if (!f.exists) {
        throw new Error("Target file does not exist: " + targetPath);
      }
      app.open(f);
    }
    if (app.documents.length === 0) {
      throw new Error("No active document is open in Adobe Illustrator.");
    }
    var doc = app.activeDocument;
    var fullPathStr = "";
    try { fullPathStr = doc.fullName.fsName; } catch (e) { fullPathStr = doc.name; }

    var artboards = [];
    for (var i = 0; i < doc.artboards.length; i++) {
      var ab = doc.artboards[i];
      var r = ab.artboardRect; // [left, top, right, bottom]
      artboards.push({
        index: i,
        name: ab.name,
        rect: [Number(r[0]), Number(r[1]), Number(r[2]), Number(r[3])],
        widthPt: Number(r[2] - r[0]),
        heightPt: Number(r[1] - r[3])
      });
    }

    var layers = [];
    for (var j = 0; j < doc.layers.length; j++) {
      var ly = doc.layers[j];
      layers.push({
        index: j,
        name: ly.name,
        visible: Boolean(ly.visible),
        locked: Boolean(ly.locked),
        pageItemsCount: Number(ly.pageItems.length),
        pathItemsCount: Number(ly.pathItems.length),
        textFramesCount: Number(ly.textFrames.length)
      });
    }

    var textFrames = [];
    var maxTexts = Math.min(doc.textFrames.length, 100);
    for (var k = 0; k < maxTexts; k++) {
      var tf = doc.textFrames[k];
      var fontName = "";
      var fontSize = null;
      try {
        if (tf.textRange && tf.textRange.characterAttributes) {
          fontSize = Number(tf.textRange.characterAttributes.size);
          if (tf.textRange.characterAttributes.textFont) {
            fontName = tf.textRange.characterAttributes.textFont.name;
          }
        }
      } catch (te) {}
      textFrames.push({
        index: k,
        contents: String(tf.contents || ""),
        position: [Number(tf.left), Number(tf.top)],
        fontName: fontName,
        fontSize: fontSize
      });
    }

    var swatches = [];
    var maxSwatches = Math.min(doc.swatches.length, 100);
    for (var s = 0; s < maxSwatches; s++) {
      var sw = doc.swatches[s];
      var cInfo = { name: sw.name, type: String(sw.color ? sw.color.typename : "Unknown") };
      try {
        if (sw.color && sw.color.typename === "CMYKColor") {
          cInfo.cmyk = [
            Math.round(sw.color.cyan * 100) / 100,
            Math.round(sw.color.magenta * 100) / 100,
            Math.round(sw.color.yellow * 100) / 100,
            Math.round(sw.color.black * 100) / 100
          ];
        } else if (sw.color && sw.color.typename === "RGBColor") {
          cInfo.rgb = [
            Math.round(sw.color.red),
            Math.round(sw.color.green),
            Math.round(sw.color.blue)
          ];
        }
      } catch (ce) {}
      swatches.push(cInfo);
    }

    var csStr = String(doc.documentColorSpace);
    return JSON.stringify({
      name: doc.name,
      fullPath: fullPathStr,
      colorSpace: csStr.indexOf("CMYK") >= 0 ? "CMYK" : "RGB",
      rulerUnits: String(doc.rulerUnits),
      widthPt: Number(doc.width),
      heightPt: Number(doc.height),
      artboards: artboards,
      layers: layers,
      counts: {
        pageItems: Number(doc.pageItems.length),
        pathItems: Number(doc.pathItems.length),
        compoundPathItems: Number(doc.compoundPathItems.length),
        textFrames: Number(doc.textFrames.length),
        placedItems: Number(doc.placedItems.length),
        groupItems: Number(doc.groupItems.length)
      },
      textFrames: textFrames,
      swatches: swatches
    });
  `;
  return runExtendScript(jsx, { wrap_try_catch: true });
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
 * Tool 4: export_artboard_png
 */
function exportArtboardPng(args = {}) {
  if (!args.output_path) {
    return { ok: false, error: "'output_path' is required." };
  }
  const outResolved = path.resolve(args.output_path);
  const outDir = path.dirname(outResolved);
  if (!fs.existsSync(outDir)) {
    fs.mkdirSync(outDir, { recursive: true });
  }
  const artboardIndex = args.artboard_index != null ? Number(args.artboard_index) : 0;
  const scale = args.scale != null ? Number(args.scale) : 200;
  const transparency = args.transparency !== false;

  const tmpPng = path.join(
    os.tmpdir(),
    `agy_ai_export_${ process.pid }_${ Date.now() }.png`
  );

  const jsx = `
    if (app.documents.length === 0) {
      throw new Error("No active document is open in Adobe Illustrator.");
    }
    var doc = app.activeDocument;
    var abIdx = ${ artboardIndex };
    if (abIdx < 0 || abIdx >= doc.artboards.length) {
      throw new Error("Invalid artboard_index: " + abIdx + " (count: " + doc.artboards.length + ")");
    }
    doc.artboards.setActiveArtboardIndex(abIdx);
    var ab = doc.artboards[abIdx];
    var r = ab.artboardRect;

    var opts = new ExportOptionsPNG24();
    opts.antiAliasing = true;
    opts.artBoardClipping = true;
    opts.transparency = ${ transparency ? "true" : "false" };
    opts.horizontalScale = ${ scale };
    opts.verticalScale = ${ scale };

    var outFile = new File(${ toAsciiJsString(tmpPng.replace(/\\/g, "/")) });
    doc.exportFile(outFile, ExportType.PNG24, opts);

    return JSON.stringify({
      artboardIndex: abIdx,
      artboardName: ab.name,
      artboardWidthPt: Number(r[2] - r[0]),
      artboardHeightPt: Number(r[1] - r[3]),
      scale: ${ scale },
      transparency: ${ transparency ? "true" : "false" }
    });
  `;

  const res = runExtendScript(jsx, { wrap_try_catch: true });
  if (!res.ok) return res;

  try {
    if (!fs.existsSync(tmpPng)) {
      return { ok: false, error: "Illustrator exportFile completed but temporary PNG was not created." };
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
 * Tool 5: save_illustrator_document
 */
function saveIllustratorDocument(args = {}) {
  if (!args.output_path) {
    return { ok: false, error: "'output_path' is required." };
  }
  const outResolved = path.resolve(args.output_path);
  const outDir = path.dirname(outResolved);
  if (!fs.existsSync(outDir)) {
    fs.mkdirSync(outDir, { recursive: true });
  }
  const ext = path.extname(outResolved).toLowerCase();
  if (![".ai", ".pdf", ".svg", ".eps"].includes(ext)) {
    return {
      ok: false,
      error: `Unsupported extension '${ ext }'. Supported: .ai, .pdf, .svg, .eps`
    };
  }
  const outlineText = Boolean(args.outline_text);
  const cmykConvert = Boolean(args.cmyk_convert);

  const tmpSave = path.join(
    os.tmpdir(),
    `agy_ai_save_${ process.pid }_${ Date.now() }${ ext }`
  );

  const jsx = `
    if (app.documents.length === 0) {
      throw new Error("No active document is open in Adobe Illustrator.");
    }
    var doc = app.activeDocument;
    if (${ cmykConvert ? "true" : "false" }) {
      try {
        app.executeMenuCommand("doc-color-cmyk");
      } catch (ce) {}
    }

    var outlinedCount = 0;
    if (${ outlineText ? "true" : "false" }) {
      for (var i = doc.textFrames.length - 1; i >= 0; i--) {
        try {
          doc.textFrames[i].createOutline();
          outlinedCount++;
        } catch (oe) {}
      }
    }

    var destFile = new File(${ toAsciiJsString(tmpSave.replace(/\\/g, "/")) });
    var ext = ${ toAsciiJsString(ext) };

    if (ext === ".ai") {
      var aiOpts = new IllustratorSaveOptions();
      aiOpts.pdfCompatible = true;
      aiOpts.embedICCProfile = true;
      aiOpts.compressed = true;
      doc.saveAs(destFile, aiOpts);
    } else if (ext === ".pdf") {
      var pdfOpts = new PDFSaveOptions();
      pdfOpts.pDFXStandard = PDFXStandard.PDFXNONE;
      pdfOpts.compatibility = PDFCompatibility.ACROBAT7;
      pdfOpts.preserveEditability = true;
      doc.saveAs(destFile, pdfOpts);
    } else if (ext === ".eps") {
      var epsOpts = new EPSSaveOptions();
      epsOpts.cmykPostScript = true;
      epsOpts.embedAllFonts = true;
      doc.saveAs(destFile, epsOpts);
    } else if (ext === ".svg") {
      var svgOpts = new ExportOptionsSVG();
      svgOpts.embedRasterImages = true;
      svgOpts.fontSubsetting = SVGFontSubsetting.None;
      svgOpts.documentEncoding = SVGDocumentEncoding.UTF8;
      doc.exportFile(destFile, ExportType.SVG, svgOpts);
    }

    return JSON.stringify({
      format: ext,
      outlinedTextFrames: outlinedCount,
      colorSpace: String(doc.documentColorSpace).indexOf("CMYK") >= 0 ? "CMYK" : "RGB",
      remainingTextFrames: Number(doc.textFrames.length)
    });
  `;

  const res = runExtendScript(jsx, { wrap_try_catch: true });
  if (!res.ok) return res;

  try {
    if (!fs.existsSync(tmpSave)) {
      return { ok: false, error: `Illustrator save completed but temporary file (${ ext }) was not found.` };
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
    name: "get_illustrator_status",
    description:
      "Check Adobe Illustrator installation, COM ProgID registration, running process status, and open documents list (name, colorSpace CMYK/RGB, artboards count).",
    inputSchema: {
      type: "object",
      properties: {},
      additionalProperties: false
    }
  },
  {
    name: "execute_illustrator_jsx",
    description:
      "Execute Adobe Illustrator ExtendScript (JSX) code or a .jsx file via COM (Windows PowerShell) or osascript (macOS) with UTF-8 protection and automatic try/catch error reporting.",
    inputSchema: {
      type: "object",
      properties: {
        script: {
          type: "string",
          description: "ExtendScript (JSX) code string to execute inside Adobe Illustrator."
        },
        script_path: {
          type: "string",
          description: "Path to a .jsx file to execute inside Adobe Illustrator."
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
      "Get detailed structural summary of the active Illustrator document (or open a specified .ai/.svg/.pdf/.eps file first), including colorSpace (CMYK/RGB), artboards & coordinates, layers, textFrames, pathItems count, and swatches.",
    inputSchema: {
      type: "object",
      properties: {
        file_path: {
          type: "string",
          description: "Optional file path (.ai, .svg, .pdf, .eps) to open before inspecting."
        }
      },
      additionalProperties: false
    }
  },
  {
    name: "export_artboard_png",
    description:
      "Export a specified artboard of the active Illustrator document to a high-resolution PNG24 file for visual inspection (read_file).",
    inputSchema: {
      type: "object",
      properties: {
        output_path: {
          type: "string",
          description: "Destination file path for the exported PNG."
        },
        artboard_index: {
          type: "number",
          description: "0-based artboard index to export (default: 0)."
        },
        scale: {
          type: "number",
          description: "Export scale percentage (default: 200 for 200% high-res)."
        },
        transparency: {
          type: "boolean",
          description: "Whether to preserve transparent background (default: true)."
        }
      },
      required: ["output_path"],
      additionalProperties: false
    }
  },
  {
    name: "save_illustrator_document",
    description:
      "Save or export the active Illustrator document as .ai, .pdf, .svg, or .eps, with optional text outlining (createOutline) and CMYK conversion.",
    inputSchema: {
      type: "object",
      properties: {
        output_path: {
          type: "string",
          description: "Destination file path (.ai, .pdf, .svg, or .eps)."
        },
        outline_text: {
          type: "boolean",
          description: "If true, convert all text frames to outlines (createOutline) before saving (default: false)."
        },
        cmyk_convert: {
          type: "boolean",
          description: "If true, convert document color space to CMYK before saving (default: false)."
        }
      },
      required: ["output_path"],
      additionalProperties: false
    }
  }
];

function handleToolCall(name, args) {
  switch (name) {
    case "get_illustrator_status":
      return getIllustratorStatus(args);
    case "execute_illustrator_jsx":
      return executeIllustratorJsx(args);
    case "get_document_summary":
      return getDocumentSummary(args);
    case "export_artboard_png":
      return exportArtboardPng(args);
    case "save_illustrator_document":
      return saveIllustratorDocument(args);
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
            name: "illustrator",
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
  getIllustratorStatus,
  executeIllustratorJsx,
  getDocumentSummary,
  exportArtboardPng,
  saveIllustratorDocument,
  TOOLS_DEFINITION
};
