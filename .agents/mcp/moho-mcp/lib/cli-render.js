"use strict";

/**
 * Moho Pro 14.5.1 Headless CLI Renderer (`Moho.exe -r`)
 * Supports all verified 14.5.1 CLI flags, UTF-8 log parsing, and single-frame PNG preview.
 */

const fs = require("fs");
const path = require("path");
const { spawnSync } = require("child_process");
const { detectMohoEnvironment } = require("./env");

function yesNo(val) {
  return val ? "yes" : "no";
}

/**
 * Parse Moho CLI render log (UTF-8) into structured metadata.
 */
function parseRenderLog(logText) {
  const info = {};
  if (!logText) return info;
  const patterns = {
    documentPath: /^Document Path:\s*(.+)$/m,
    fps: /^FPS:\s*([\d.]+)$/m,
    size: /^Size:\s*(\d+x\d+)$/m,
    projectFrames: /^Frames:\s*(.+)$/m,
    savePath: /^Save Path:\s*(.+)$/m,
    outputFormat: /^Output Format:\s*(.+)$/m,
    renderedFrames: /^Frames to render:\s*(.+)$/m,
    hardwareAcceleration: /^Hardware Acceleration:\s*(.+)$/m
  };
  for (const [k, re] of Object.entries(patterns)) {
    const m = logText.match(re);
    if (m) info[k] = m[1].trim();
  }
  info.completed = /\bDone!\b/.test(logText);
  return info;
}

/**
 * Render a .moho project headlessly using Moho.exe -r.
 */
function renderMoho(args = {}) {
  const env = detectMohoEnvironment();
  if (!env.installed || !env.mohoExe) {
    return { ok: false, error: "Moho 14 executable not found." };
  }

  const mohoPath = args.moho_path || args.file;
  if (!mohoPath) {
    return { ok: false, error: "moho_path is required" };
  }
  const resolvedMoho = path.resolve(mohoPath);
  if (!fs.existsSync(resolvedMoho)) {
    return { ok: false, error: `Moho project file not found: ${resolvedMoho}` };
  }

  const format = String(args.format || "png").toUpperCase();
  const explicitOutPath = args.output_path ? path.resolve(args.output_path) : null;
  const outFolder = explicitOutPath
    ? path.dirname(explicitOutPath)
    : args.outfolder || args.output_dir
    ? path.resolve(args.outfolder || args.output_dir)
    : path.dirname(resolvedMoho);

  fs.mkdirSync(outFolder, { recursive: true });

  const logPath = args.log_path
    ? path.resolve(args.log_path)
    : path.join(outFolder, `_moho_render_${Date.now()}.log`);

  const cliArgs = ["-r", resolvedMoho, "-f", format];

  if (explicitOutPath) {
    cliArgs.push("-o", explicitOutPath);
  } else {
    cliArgs.push("-outfolder", outFolder);
  }

  if (args.start_frame !== undefined) cliArgs.push("-start", String(args.start_frame));
  if (args.end_frame !== undefined) cliArgs.push("-end", String(args.end_frame));
  if (args.layercomp) cliArgs.push("-layercomp", String(args.layercomp));
  if (args.aa !== undefined) cliArgs.push("-aa", yesNo(args.aa));
  if (args.extrasmooth !== undefined) cliArgs.push("-extrasmooth", yesNo(args.extrasmooth));
  if (args.halfsize !== undefined) cliArgs.push("-halfsize", yesNo(args.halfsize));
  if (args.halffps !== undefined) cliArgs.push("-halffps", yesNo(args.halffps));
  if (args.fewparticles !== undefined) cliArgs.push("-fewparticles", yesNo(args.fewparticles));
  if (args.multithread !== undefined) cliArgs.push("-multithread", yesNo(args.multithread));
  if (args.shapefx !== undefined) cliArgs.push("-shapefx", yesNo(args.shapefx));
  if (args.layerfx !== undefined) cliArgs.push("-layerfx", yesNo(args.layerfx));
  if (args.ntscsafe !== undefined) cliArgs.push("-ntscsafe", yesNo(args.ntscsafe));
  if (args.premultiply !== undefined) cliArgs.push("-premultiply", yesNo(args.premultiply));
  if (args.addformatsuffix !== undefined) cliArgs.push("-addformatsuffix", yesNo(args.addformatsuffix));

  cliArgs.push(args.quiet ? "-q" : "-v");
  cliArgs.push("-log", logPath);

  const beforeFiles = new Set(fs.readdirSync(outFolder));
  const startedAt = Date.now();
  const timeoutMs = Number(args.timeout_ms || 300000);

  const proc = spawnSync(env.mohoExe, cliArgs, {
    encoding: "utf8",
    timeout: timeoutMs,
    windowsHide: true
  });

  const elapsedMs = Date.now() - startedAt;
  const logText = fs.existsSync(logPath)
    ? fs.readFileSync(logPath, "utf8").replace(/^\uFEFF/, "")
    : "";
  const parsedLog = parseRenderLog(logText);

  // Collect newly created or modified render outputs in outFolder
  const afterFiles = fs.readdirSync(outFolder);
  const generatedFiles = [];
  for (const name of afterFiles) {
    const full = path.join(outFolder, name);
    if (full === logPath) continue;
    try {
      const st = fs.statSync(full);
      if (st.isFile() && (!beforeFiles.has(name) || st.mtimeMs >= startedAt - 1000)) {
        generatedFiles.push({
          name,
          path: full,
          sizeBytes: st.size
        });
      }
    } catch (_) {}
  }

  // Cleanup temp log if user didn't explicitly ask for log_path
  if (!args.log_path && !args.keep_log && fs.existsSync(logPath)) {
    try { fs.unlinkSync(logPath); } catch (_) {}
  }

  const ok = proc.status === 0 && (parsedLog.completed || generatedFiles.length > 0);

  return {
    ok,
    exitCode: proc.status,
    elapsedMs,
    mohoPath: resolvedMoho,
    outFolder,
    format,
    generatedFiles,
    logSummary: parsedLog,
    rawLog: args.include_raw_log ? logText : undefined,
    error: ok ? undefined : (proc.error ? proc.error.message : (proc.stderr || logText || "Render failed"))
  };
}

/**
 * Convenience helper: render a single frame to a specific PNG path for instant visual QA.
 */
function renderPreviewFrame(args = {}) {
  const mohoPath = args.moho_path || args.file;
  const frame = args.frame !== undefined ? Number(args.frame) : 1;
  if (!mohoPath) return { ok: false, error: "moho_path is required" };

  const outPng = args.output_png
    ? path.resolve(args.output_png)
    : path.join(path.dirname(path.resolve(mohoPath)), `preview_frame_${frame}.png`);

  const tmpDir = path.join(path.dirname(outPng), `_moho_preview_tmp_${Date.now()}`);
  fs.mkdirSync(tmpDir, { recursive: true });

  try {
    const res = renderMoho({
      moho_path: mohoPath,
      format: "PNG",
      start_frame: frame,
      end_frame: frame,
      outfolder: tmpDir,
      aa: args.aa !== undefined ? args.aa : true,
      extrasmooth: args.extrasmooth !== undefined ? args.extrasmooth : true,
      halfsize: args.halfsize,
      timeout_ms: args.timeout_ms || 120000
    });

    if (!res.ok || res.generatedFiles.length === 0) {
      return {
        ok: false,
        frame,
        error: res.error || "No PNG frame produced",
        details: res
      };
    }

    const rendered = res.generatedFiles[0].path;
    fs.mkdirSync(path.dirname(outPng), { recursive: true });
    fs.copyFileSync(rendered, outPng);
    const sizeBytes = fs.statSync(outPng).size;

    return {
      ok: true,
      frame,
      pngPath: outPng,
      sizeBytes,
      elapsedMs: res.elapsedMs,
      logSummary: res.logSummary
    };
  } finally {
    try { fs.rmSync(tmpDir, { recursive: true, force: true }); } catch (_) {}
  }
}

module.exports = {
  renderMoho,
  renderPreviewFrame,
  parseRenderLog
};
