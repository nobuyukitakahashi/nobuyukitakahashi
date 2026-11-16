#!/usr/bin/env node
/**
 * PTGui Pro 13 Local MCP Server (stdio JSON-RPC 2.0)
 * Zero external npm dependencies (Node.js built-in modules only).
 * Supports both Content-Length header framing and newline-delimited JSON-RPC.
 * Supports Windows (C:\Program Files\PTGui\PTGui.exe) and macOS (/Applications/PTGui Pro.app).
 */

const fs = require("fs");
const path = require("path");
const os = require("os");
const { spawnSync, spawn } = require("child_process");

const IS_WIN = process.platform === "win32";
const IS_MAC = process.platform === "darwin";

/**
 * Locate PTGui executable, PTGuiViewer executable, and user data directories.
 */
function detectPtguiEnvironment() {
  const exeCandidates = IS_WIN
    ? [
        process.env.PTGUI_PATH,
        "C:\\Program Files\\PTGui\\PTGui.exe",
        "C:\\Program Files (x86)\\PTGui\\PTGui.exe"
      ].filter(Boolean)
    : IS_MAC
    ? [
        process.env.PTGUI_PATH,
        "/Applications/PTGui Pro.app/Contents/MacOS/PTGui Pro",
        "/Applications/PTGui.app/Contents/MacOS/PTGui",
        path.join(os.homedir(), "Applications/PTGui Pro.app/Contents/MacOS/PTGui Pro")
      ].filter(Boolean)
    : [process.env.PTGUI_PATH, "/usr/local/bin/PTGui", "/usr/bin/PTGui"].filter(Boolean);

  let ptguiExe = null;
  for (const cand of exeCandidates) {
    if (cand && fs.existsSync(cand)) {
      ptguiExe = cand;
      break;
    }
  }

  let viewerExe = null;
  let webViewerDir = null;
  if (ptguiExe) {
    const installDir = path.dirname(ptguiExe);
    const viewerCand = IS_WIN
      ? path.join(installDir, "PTGuiViewer.exe")
      : IS_MAC
      ? "/Applications/PTGui Viewer.app/Contents/MacOS/PTGui Viewer"
      : null;
    if (viewerCand && fs.existsSync(viewerCand)) {
      viewerExe = viewerCand;
    }
    const webCand = path.join(installDir, "PTGuiViewer");
    if (fs.existsSync(webCand)) {
      webViewerDir = webCand;
    }
  }

  const appDataDir = IS_WIN
    ? path.join(process.env.APPDATA || path.join(os.homedir(), "AppData", "Roaming"), "PTGui")
    : IS_MAC
    ? path.join(os.homedir(), "Library", "Application Support", "PTGui")
    : path.join(os.homedir(), ".ptgui");

  const templatesDir = path.join(appDataDir, "Templates");
  const batchListsDir = path.join(appDataDir, "Batch Lists");
  const configXmlPath = path.join(appDataDir, "Configuration.xml");

  let configVersion = null;
  let licenseAcceptedVersion = null;
  if (fs.existsSync(configXmlPath)) {
    try {
      const xml = fs.readFileSync(configXmlPath, "utf8");
      const verMatch = xml.match(/Name="ConfigVersion"[^>]*Value="(\d+)"/i);
      if (verMatch) {
        const raw = parseInt(verMatch[1], 10);
        const major = Math.floor(raw / 10000);
        const minor = Math.floor((raw % 10000) / 100);
        const patch = raw % 100;
        configVersion = `${major}.${minor}.${ String(patch).padStart(2, "0") }`;
      }
      const licMatch = xml.match(/<Group Name="LicenseAccepted">\s*<Option Name="([^"]+)"/i);
      if (licMatch) {
        licenseAcceptedVersion = licMatch[1];
      }
    } catch (_) {}
  }

  const templates = [];
  if (fs.existsSync(templatesDir)) {
    try {
      for (const f of fs.readdirSync(templatesDir)) {
        if (f.toLowerCase().endsWith(".pts")) {
          templates.push({
            name: f,
            path: path.join(templatesDir, f)
          });
        }
      }
    } catch (_) {}
  }

  const batchLists = [];
  if (fs.existsSync(batchListsDir)) {
    try {
      for (const f of fs.readdirSync(batchListsDir)) {
        if (f.toLowerCase().endsWith(".ptgbatch")) {
          batchLists.push({
            name: f,
            path: path.join(batchListsDir, f)
          });
        }
      }
    } catch (_) {}
  }

  return {
    installed: Boolean(ptguiExe),
    platform: process.platform,
    ptguiExe,
    viewerExe,
    webViewerDir,
    appDataDir: fs.existsSync(appDataDir) ? appDataDir : null,
    templatesDir: fs.existsSync(templatesDir) ? templatesDir : null,
    batchListsDir: fs.existsSync(batchListsDir) ? batchListsDir : null,
    version: licenseAcceptedVersion || configVersion || (ptguiExe ? "13.x" : null),
    templates,
    batchLists
  };
}

/**
 * Tool 1: get_ptgui_status
 */
function getPtguiStatus() {
  const env = detectPtguiEnvironment();
  return {
    ok: env.installed,
    ...env,
    capabilities: {
      cliCreateProject: true,
      cliStitchNoGui: true,
      cliBatch: true,
      jsonPtsSchema: "https://www.ptgui.com/schemas/project_v55.schema.json"
    }
  };
}

/**
 * Helper: Read and parse a .pts JSON file safely (strips UTF-8 BOM if present).
 */
function readPtsJson(ptsPath) {
  const resolved = path.resolve(ptsPath);
  if (!fs.existsSync(resolved)) {
    throw new Error(`PTS project file not found: ${ resolved }`);
  }
  const raw = fs.readFileSync(resolved, "utf8").replace(/^\uFEFF/, "");
  try {
    return JSON.parse(raw);
  } catch (err) {
    throw new Error(`Failed to parse .pts file as JSON (${ resolved }): ${ err.message }`);
  }
}

/**
 * Helper: Write a .pts JSON file in UTF-8 without BOM.
 */
function writePtsJson(ptsPath, data) {
  const resolved = path.resolve(ptsPath);
  const dir = path.dirname(resolved);
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
  const text = JSON.stringify(data, null, "\t") + "\n";
  fs.writeFileSync(resolved, text, { encoding: "utf8" });
  return resolved;
}

/**
 * Deep merge utility for raw_patch
 */
function deepMerge(target, source) {
  if (!source || typeof source !== "object" || Array.isArray(source)) {
    return source;
  }
  const out = target && typeof target === "object" && !Array.isArray(target) ? target : {};
  for (const key of Object.keys(source)) {
    const val = source[key];
    if (val && typeof val === "object" && !Array.isArray(val)) {
      out[key] = deepMerge(out[key], val);
    } else {
      out[key] = val;
    }
  }
  return out;
}

/**
 * Apply structured settings onto a parsed PTGui v55 JSON object.
 */
function applyProjectSettingsToPtsObject(ptsData, settings = {}) {
  if (!ptsData || !ptsData.project) {
    throw new Error("Invalid .pts JSON structure: missing 'project' root key.");
  }
  const proj = ptsData.project;
  proj.panoramaparams = proj.panoramaparams || {};
  proj.outputsize = proj.outputsize || {};
  proj.blend = proj.blend || {};
  proj.projectsettings = proj.projectsettings || {};
  proj.projectsettings.alignsettings = proj.projectsettings.alignsettings || {};
  proj.projectsettings.batchstitchersettings = proj.projectsettings.batchstitchersettings || {};
  proj.outputcomponents = proj.outputcomponents || {};
  proj.hdrsettings = proj.hdrsettings || {};

  if (settings.panorama_output_path !== undefined) {
    proj.panoramaparams.outputfile = settings.panorama_output_path
      ? path.resolve(settings.panorama_output_path)
      : "";
  }

  if (settings.projection !== undefined) {
    proj.panoramaparams.projection = String(settings.projection);
  }
  if (settings.hfov !== undefined) {
    proj.panoramaparams.hfov = Number(settings.hfov);
  }
  if (settings.vfov !== undefined) {
    proj.panoramaparams.vfov = Number(settings.vfov);
  }

  if (settings.file_format !== undefined) {
    proj.panoramaparams.fileformat = String(settings.file_format).toLowerCase();
  }
  if (settings.jpeg_quality !== undefined) {
    proj.panoramaparams.jpegparams = proj.panoramaparams.jpegparams || {};
    proj.panoramaparams.jpegparams.quality = Number(settings.jpeg_quality);
  }
  if (settings.tiff_bitdepth !== undefined || settings.tiff_compression !== undefined) {
    proj.panoramaparams.tiffparams = proj.panoramaparams.tiffparams || {};
    if (settings.tiff_bitdepth !== undefined) {
      proj.panoramaparams.tiffparams.datatype = String(settings.tiff_bitdepth);
    }
    if (settings.tiff_compression !== undefined) {
      proj.panoramaparams.tiffparams.compression = String(settings.tiff_compression);
    }
  }
  if (settings.psd_layermode !== undefined) {
    proj.panoramaparams.psdparams = proj.panoramaparams.psdparams || {};
    proj.panoramaparams.psdparams.layermode = String(settings.psd_layermode);
  }

  if (settings.output_size_mode !== undefined) {
    proj.outputsize.mode = String(settings.output_size_mode);
  }
  if (settings.fraction_of_optimum_size !== undefined) {
    proj.outputsize.mode = settings.output_size_mode || "relative";
    proj.outputsize.fractionofoptimumsize = Number(settings.fraction_of_optimum_size);
  }
  if (settings.width !== undefined || settings.height !== undefined) {
    proj.outputsize.mode = settings.output_size_mode || "fixed";
    if (settings.width !== undefined) proj.outputsize.width = Number(settings.width);
    if (settings.height !== undefined) proj.outputsize.height = Number(settings.height);
  }

  if (settings.blend_engine !== undefined) {
    proj.blend.engine = String(settings.blend_engine);
  }
  if (settings.fill_holes !== undefined) {
    proj.blend.fillholes = Boolean(settings.fill_holes);
  }
  if (settings.seam_finding !== undefined) {
    proj.blend.seamfinding = Boolean(settings.seam_finding);
  }

  if (settings.align_settings && typeof settings.align_settings === "object") {
    const as = settings.align_settings;
    if (as.generate_cp !== undefined) proj.projectsettings.alignsettings.generatecp = Boolean(as.generate_cp);
    if (as.optimize !== undefined) proj.projectsettings.alignsettings.optimize = Boolean(as.optimize);
    if (as.roughly_align !== undefined) proj.projectsettings.alignsettings.roughlyalign = Boolean(as.roughly_align);
    if (as.straighten !== undefined) proj.projectsettings.alignsettings.straighten = Boolean(as.straighten);
    if (as.fit !== undefined) proj.projectsettings.alignsettings.fit = Boolean(as.fit);
    if (as.choose_projection !== undefined) {
      proj.projectsettings.alignsettings.chooseprojection = Boolean(as.choose_projection);
    }
    if (as.optimize_exposure !== undefined) {
      proj.projectsettings.alignsettings.optimizeexposure = Boolean(as.optimize_exposure);
    }
  }

  if (settings.batch_stitch_settings && typeof settings.batch_stitch_settings === "object") {
    const bs = settings.batch_stitch_settings;
    if (bs.align !== undefined) proj.projectsettings.batchstitchersettings.align = Boolean(bs.align);
    if (bs.stitch !== undefined) proj.projectsettings.batchstitchersettings.stitch = Boolean(bs.stitch);
    if (bs.stitch_only_if_control_points !== undefined) {
      proj.projectsettings.batchstitchersettings.stitchonlyifcontrolpoints = Boolean(
        bs.stitch_only_if_control_points
      );
    }
  }

  if (settings.hdr_settings && typeof settings.hdr_settings === "object") {
    const hs = settings.hdr_settings;
    if (hs.ldr_panorama !== undefined) proj.outputcomponents.ldrpanorama = Boolean(hs.ldr_panorama);
    if (hs.hdr_blended !== undefined) proj.outputcomponents.hdrblended = Boolean(hs.hdr_blended);
    if (hs.tonemap_panorama !== undefined) proj.hdrsettings.tonemappanorama = Boolean(hs.tonemap_panorama);
    if (hs.hdr_file_format !== undefined) proj.hdrsettings.fileformat = String(hs.hdr_file_format);
    if (hs.hdr_method !== undefined) proj.hdrsettings.hdrmethod = String(hs.hdr_method);
  }

  if (settings.lens_projection !== undefined || settings.focal_length !== undefined) {
    if (Array.isArray(proj.globallenses) && proj.globallenses.length > 0) {
      const gl0 = proj.globallenses[0];
      if (gl0 && gl0.lens && gl0.lens.params) {
        if (settings.lens_projection !== undefined) {
          gl0.lens.params.projection = String(settings.lens_projection);
        }
        if (settings.focal_length !== undefined) {
          gl0.lens.params.focallength = Number(settings.focal_length);
        }
      }
    }
  }

  if (Array.isArray(settings.image_positions) && Array.isArray(proj.imagegroups)) {
    for (const pos of settings.image_positions) {
      const idx = Number(pos.index);
      if (Number.isInteger(idx) && idx >= 0 && idx < proj.imagegroups.length) {
        const ig = proj.imagegroups[idx];
        if (ig.position && ig.position.params) {
          if (pos.yaw !== undefined) ig.position.params.yaw = Number(pos.yaw);
          if (pos.pitch !== undefined) ig.position.params.pitch = Number(pos.pitch);
          if (pos.roll !== undefined) ig.position.params.roll = Number(pos.roll);
        }
        if (ig.linkable && ig.linkable.position && ig.linkable.position.params) {
          if (pos.yaw !== undefined) ig.linkable.position.params.yaw = Number(pos.yaw);
          if (pos.pitch !== undefined) ig.linkable.position.params.pitch = Number(pos.pitch);
          if (pos.roll !== undefined) ig.linkable.position.params.roll = Number(pos.roll);
        }
      }
    }
  }

  if (settings.raw_patch && typeof settings.raw_patch === "object") {
    deepMerge(ptsData, settings.raw_patch);
  }

  return ptsData;
}

/**
 * Summarize a parsed .pts JSON object.
 */
function summarizePtsObject(ptsData, filePath) {
  const proj = (ptsData && ptsData.project) || {};
  const imageGroups = Array.isArray(proj.imagegroups) ? proj.imagegroups : [];
  const images = [];
  imageGroups.forEach((ig, groupIdx) => {
    const pos = (ig.position && ig.position.params) || {};
    const groupImages = Array.isArray(ig.images) ? ig.images : [];
    groupImages.forEach((im) => {
      images.push({
        groupIndex: groupIdx,
        filename: im.filename,
        size: ig.size || null,
        include: im.include !== false,
        yaw: pos.yaw ?? 0,
        pitch: pos.pitch ?? 0,
        roll: pos.roll ?? 0,
        aperture: im.metadata ? im.metadata.aperture : null,
        exposuretime: im.metadata ? im.metadata.exposuretime : null,
        iso: im.metadata ? im.metadata.iso : null
      });
    });
  });

  const globalLenses = Array.isArray(proj.globallenses)
    ? proj.globallenses.map((gl, idx) => ({
        index: idx,
        projection: gl.lens && gl.lens.params ? gl.lens.params.projection : null,
        focalLength: gl.lens && gl.lens.params ? gl.lens.params.focallength : null,
        sensorDiagonal: gl.lens && gl.lens.params ? gl.lens.params.sensordiagonal : null
      }))
    : [];

  return {
    filePath: filePath ? path.resolve(filePath) : null,
    software: ptsData.software || null,
    contentType: ptsData.contenttype || null,
    fileVersion: ptsData.fileversion || null,
    imageGroupCount: imageGroups.length,
    totalImageCount: images.length,
    controlPointCount: Array.isArray(proj.controlpoints) ? proj.controlpoints.length : 0,
    hasBeenOptimized: Boolean(proj.hasbeenoptimized),
    autoCpDone: Boolean(proj.autocpdone),
    globalLenses,
    panoramaParams: {
      outputFile: proj.panoramaparams ? proj.panoramaparams.outputfile : "",
      projection: proj.panoramaparams ? proj.panoramaparams.projection : null,
      hfov: proj.panoramaparams ? proj.panoramaparams.hfov : null,
      vfov: proj.panoramaparams ? proj.panoramaparams.vfov : null,
      fileFormat: proj.panoramaparams ? proj.panoramaparams.fileformat : null,
      jpegQuality:
        proj.panoramaparams && proj.panoramaparams.jpegparams
          ? proj.panoramaparams.jpegparams.quality
          : null,
      outputCrop: proj.panoramaparams ? proj.panoramaparams.outputcrop : null
    },
    outputSize: proj.outputsize || null,
    blend: proj.blend || null,
    outputComponents: proj.outputcomponents || null,
    alignSettings: proj.projectsettings ? proj.projectsettings.alignsettings : null,
    batchStitcherSettings: proj.projectsettings ? proj.projectsettings.batchstitchersettings : null,
    images
  };
}

/**
 * Tool 2: create_ptgui_project
 */
function createPtguiProject(args = {}) {
  const env = detectPtguiEnvironment();
  if (!env.installed) {
    return { ok: false, error: "PTGui executable not found on this machine." };
  }

  let imageList = Array.isArray(args.images) ? [...args.images] : [];
  if (args.image_dir) {
    const dirPath = path.resolve(args.image_dir);
    if (!fs.existsSync(dirPath)) {
      return { ok: false, error: `image_dir does not exist: ${ dirPath }` };
    }
    const exts = Array.isArray(args.extensions)
      ? args.extensions.map((e) => e.toLowerCase().replace(/^\./, ""))
      : ["jpg", "jpeg", "tif", "tiff", "png", "dng", "cr2", "cr3", "nef", "arw", "orf", "rw2", "exr", "hdr"];
    const entries = fs
      .readdirSync(dirPath)
      .filter((f) => {
        const ext = path.extname(f).toLowerCase().replace(/^\./, "");
        return exts.includes(ext);
      })
      .sort()
      .map((f) => path.join(dirPath, f));
    imageList = imageList.concat(entries);
  }

  imageList = imageList.map((p) => path.resolve(p));
  if (imageList.length === 0) {
    return { ok: false, error: "No source images provided in 'images' or found in 'image_dir'." };
  }
  for (const img of imageList) {
    if (!fs.existsSync(img)) {
      return { ok: false, error: `Source image not found: ${ img }` };
    }
  }

  if (!args.output_pts_path) {
    return { ok: false, error: "'output_pts_path' is required." };
  }
  const outputPtsPath = path.resolve(args.output_pts_path);
  const outDir = path.dirname(outputPtsPath);
  if (!fs.existsSync(outDir)) {
    fs.mkdirSync(outDir, { recursive: true });
  }

  const cliArgs = ["-createproject", ...imageList, "-output", outputPtsPath];
  if (args.template_path) {
    const tplPath = path.resolve(args.template_path);
    if (!fs.existsSync(tplPath)) {
      return { ok: false, error: `Template file not found: ${ tplPath }` };
    }
    cliArgs.push("-template", tplPath);
  }

  const startMs = Date.now();
  const proc = spawnSync(env.ptguiExe, cliArgs, {
    windowsHide: true,
    timeout: args.timeout_ms || 120000
  });
  const elapsedMs = Date.now() - startMs;

  if (proc.error) {
    return { ok: false, error: `Failed to execute PTGui CLI: ${ proc.error.message }` };
  }
  if (!fs.existsSync(outputPtsPath)) {
    return {
      ok: false,
      exitCode: proc.status,
      error: `PTGui exited with code ${ proc.status } and did not create ${ outputPtsPath }.`
    };
  }

  // Apply optional post-creation settings onto the JSON .pts file
  const hasSettings =
    args.panorama_output_path !== undefined ||
    args.projection !== undefined ||
    args.hfov !== undefined ||
    args.vfov !== undefined ||
    args.file_format !== undefined ||
    args.jpeg_quality !== undefined ||
    args.width !== undefined ||
    args.height !== undefined ||
    args.fraction_of_optimum_size !== undefined ||
    args.blend_engine !== undefined ||
    args.fill_holes !== undefined ||
    args.align_settings !== undefined ||
    args.batch_stitch_settings !== undefined ||
    args.hdr_settings !== undefined ||
    args.lens_projection !== undefined ||
    args.focal_length !== undefined ||
    args.image_positions !== undefined ||
    args.raw_patch !== undefined;

  let ptsData = readPtsJson(outputPtsPath);
  if (hasSettings) {
    ptsData = applyProjectSettingsToPtsObject(ptsData, args);
    writePtsJson(outputPtsPath, ptsData);
  }

  return {
    ok: true,
    exitCode: proc.status,
    elapsedMs,
    outputPtsPath,
    summary: summarizePtsObject(ptsData, outputPtsPath)
  };
}

/**
 * Tool 3: get_project_summary
 */
function getProjectSummary(args = {}) {
  const ptsPath = args.pts_path || args.file_path;
  if (!ptsPath) {
    return { ok: false, error: "'pts_path' is required." };
  }
  try {
    const ptsData = readPtsJson(ptsPath);
    return {
      ok: true,
      summary: summarizePtsObject(ptsData, ptsPath)
    };
  } catch (err) {
    return { ok: false, error: err.message };
  }
}

/**
 * Tool 4: update_project_settings
 */
function updateProjectSettings(args = {}) {
  const ptsPath = args.pts_path || args.file_path;
  if (!ptsPath) {
    return { ok: false, error: "'pts_path' is required." };
  }
  try {
    const ptsData = readPtsJson(ptsPath);
    const updated = applyProjectSettingsToPtsObject(ptsData, args);
    const saveTarget = args.save_as_path ? path.resolve(args.save_as_path) : path.resolve(ptsPath);
    writePtsJson(saveTarget, updated);
    return {
      ok: true,
      savedPtsPath: saveTarget,
      summary: summarizePtsObject(updated, saveTarget)
    };
  } catch (err) {
    return { ok: false, error: err.message };
  }
}

/**
 * Resolve the actual panorama output path from a .pts project JSON.
 */
function resolvePanoramaOutputPath(ptsData, ptsFilePath) {
  const proj = (ptsData && ptsData.project) || {};
  const pp = proj.panoramaparams || {};
  const rawOut = pp.outputfile || "";
  const format = (pp.fileformat || "jpeg").toLowerCase();
  const extMap = {
    jpeg: ".jpg",
    tiff: ".tif",
    psd: ".psd",
    exr: ".exr",
    dng: ".dng",
    png: ".png",
    qtvr: ".mov"
  };
  const ext = extMap[format] || `.${ format }`;

  if (rawOut && rawOut.trim().length > 0) {
    return path.isAbsolute(rawOut)
      ? rawOut
      : path.resolve(path.dirname(ptsFilePath), rawOut);
  }
  const base = path.basename(ptsFilePath, path.extname(ptsFilePath));
  return path.join(path.dirname(ptsFilePath), `${ base }${ ext }`);
}

/**
 * Tool 5: stitch_project
 */
function stitchProject(args = {}) {
  const env = detectPtguiEnvironment();
  if (!env.installed) {
    return { ok: false, error: "PTGui executable not found on this machine." };
  }

  const ptsPathRaw = args.pts_path || args.file_path;
  if (!ptsPathRaw) {
    return { ok: false, error: "'pts_path' is required." };
  }
  const ptsPath = path.resolve(ptsPathRaw);
  if (!fs.existsSync(ptsPath)) {
    return { ok: false, error: `PTS file not found: ${ ptsPath }` };
  }

  let ptsData = readPtsJson(ptsPath);
  let targetPtsToRun = ptsPath;
  let tempPtsPath = null;

  const needsOverride =
    args.output_path !== undefined ||
    args.scale_fraction !== undefined ||
    args.force_stitch !== undefined ||
    args.align !== undefined;

  if (needsOverride) {
    const clone = JSON.parse(JSON.stringify(ptsData));
    clone.project = clone.project || {};
    clone.project.panoramaparams = clone.project.panoramaparams || {};
    clone.project.outputsize = clone.project.outputsize || {};
    clone.project.projectsettings = clone.project.projectsettings || {};
    clone.project.projectsettings.batchstitchersettings =
      clone.project.projectsettings.batchstitchersettings || {};

    if (args.output_path) {
      const resolvedOut = path.resolve(args.output_path);
      const outDir = path.dirname(resolvedOut);
      if (!fs.existsSync(outDir)) {
        fs.mkdirSync(outDir, { recursive: true });
      }
      clone.project.panoramaparams.outputfile = resolvedOut;
      const ext = path.extname(resolvedOut).toLowerCase();
      if (ext === ".jpg" || ext === ".jpeg") clone.project.panoramaparams.fileformat = "jpeg";
      else if (ext === ".tif" || ext === ".tiff") clone.project.panoramaparams.fileformat = "tiff";
      else if (ext === ".psd" || ext === ".psb") clone.project.panoramaparams.fileformat = "psd";
      else if (ext === ".exr") clone.project.panoramaparams.fileformat = "exr";
      else if (ext === ".dng") clone.project.panoramaparams.fileformat = "dng";
    }

    if (args.scale_fraction !== undefined) {
      clone.project.outputsize.mode = "relative";
      clone.project.outputsize.fractionofoptimumsize = Number(args.scale_fraction);
    }

    if (args.align !== undefined) {
      clone.project.projectsettings.batchstitchersettings.align = Boolean(args.align);
    }

    if (args.force_stitch !== undefined) {
      clone.project.projectsettings.batchstitchersettings.stitchonlyifcontrolpoints = !Boolean(
        args.force_stitch
      );
    }

    if (args.persist_overrides) {
      writePtsJson(ptsPath, clone);
      ptsData = clone;
    } else {
      tempPtsPath = path.join(
        path.dirname(ptsPath),
        `${ path.basename(ptsPath, ".pts") }.__tmp_stitch_${ Date.now() }.pts`
      );
      writePtsJson(tempPtsPath, clone);
      targetPtsToRun = tempPtsPath;
      ptsData = clone;
    }
  } else {
    // Ensure output directory exists
    const expectedOut = resolvePanoramaOutputPath(ptsData, ptsPath);
    const outDir = path.dirname(expectedOut);
    if (!fs.existsSync(outDir)) {
      fs.mkdirSync(outDir, { recursive: true });
    }
  }

  const expectedOutputFile = resolvePanoramaOutputPath(ptsData, ptsPath);
  const mode = args.mode === "batch" ? "-batch" : "-stitchnogui";
  const cliArgs = [mode, targetPtsToRun];

  const startMs = Date.now();
  let proc;
  try {
    proc = spawnSync(env.ptguiExe, cliArgs, {
      windowsHide: true,
      timeout: args.timeout_ms || 600000
    });
  } finally {
    if (tempPtsPath && fs.existsSync(tempPtsPath)) {
      try {
        fs.unlinkSync(tempPtsPath);
      } catch (_) {}
    }
  }
  const elapsedMs = Date.now() - startMs;

  if (proc.error) {
    return { ok: false, error: `Failed to execute PTGui stitch: ${ proc.error.message }` };
  }

  const outputExists = fs.existsSync(expectedOutputFile);
  let outputFileSize = null;
  if (outputExists) {
    try {
      outputFileSize = fs.statSync(expectedOutputFile).size;
    } catch (_) {}
  }

  return {
    ok: proc.status === 0 && (mode === "-batch" || outputExists),
    mode,
    exitCode: proc.status,
    elapsedMs,
    ptsPath,
    panoramaOutputPath: expectedOutputFile,
    outputExists,
    outputFileSize,
    note:
      !outputExists && mode === "-stitchnogui"
        ? "Output file was not created. If images lack sufficient overlap/control points, set force_stitch: true or inspect control points."
        : undefined
  };
}

/**
 * Tool 6: open_in_ptgui_gui
 */
function openInPtguiGui(args = {}) {
  const env = detectPtguiEnvironment();
  if (!env.installed) {
    return { ok: false, error: "PTGui executable not found on this machine." };
  }
  const targetFile = args.file_path || args.pts_path;
  if (!targetFile) {
    return { ok: false, error: "'file_path' is required." };
  }
  const resolved = path.resolve(targetFile);
  if (!fs.existsSync(resolved)) {
    return { ok: false, error: `File not found: ${ resolved }` };
  }

  const useViewer = Boolean(args.use_viewer);
  const exeToLaunch = useViewer ? env.viewerExe || env.ptguiExe : env.ptguiExe;

  try {
    const child = spawn(exeToLaunch, [resolved], {
      detached: true,
      stdio: "ignore"
    });
    child.unref();
    return {
      ok: true,
      launchedExecutable: exeToLaunch,
      filePath: resolved,
      pid: child.pid
    };
  } catch (err) {
    return { ok: false, error: `Failed to launch GUI: ${ err.message }` };
  }
}

const TOOLS_DEFINITION = [
  {
    name: "get_ptgui_status",
    description:
      "Check PTGui Pro 13 installation status, executable paths (PTGui.exe / PTGuiViewer.exe), version, saved user templates (.pts), and headless CLI capabilities.",
    inputSchema: {
      type: "object",
      properties: {},
      additionalProperties: false
    }
  },
  {
    name: "create_ptgui_project",
    description:
      "Create a new PTGui project (.pts JSON v55) headlessly via 'PTGui -createproject' from source images or a directory, optionally applying a template and configuring projection, output path, format, resolution, HDR, or alignment settings.",
    inputSchema: {
      type: "object",
      properties: {
        images: {
          type: "array",
          items: { type: "string" },
          description: "Array of source image paths to include in the panorama project."
        },
        image_dir: {
          type: "string",
          description: "Optional directory path from which to automatically collect source images."
        },
        output_pts_path: {
          type: "string",
          description: "Destination path for the generated .pts project file."
        },
        template_path: {
          type: "string",
          description: "Optional path to a .pts template file to apply."
        },
        panorama_output_path: {
          type: "string",
          description: "Optional destination path for the stitched panorama output image."
        },
        projection: {
          type: "string",
          description:
            "Panorama projection (e.g. 'equirectangular', 'rectilinear', 'cylindrical', 'stereographic', 'mercator')."
        },
        hfov: {
          type: "number",
          description: "Horizontal Field of View in degrees (e.g. 360 for full spherical equirectangular)."
        },
        vfov: {
          type: "number",
          description: "Vertical Field of View in degrees (e.g. 180 for full spherical equirectangular)."
        },
        file_format: {
          type: "string",
          description: "Output image format ('jpeg', 'tiff', 'psd', 'exr', 'dng')."
        },
        jpeg_quality: {
          type: "number",
          description: "JPEG compression quality (1-100, default 95)."
        },
        width: {
          type: "number",
          description: "Fixed output width in pixels (sets outputsize.mode = 'fixed')."
        },
        height: {
          type: "number",
          description: "Fixed output height in pixels (sets outputsize.mode = 'fixed')."
        },
        fraction_of_optimum_size: {
          type: "number",
          description: "Relative output size fraction of optimum resolution (0.05 to 1.0, default 1.0)."
        },
        blend_engine: {
          type: "string",
          description: "Blending engine ('zerooverlap' or 'multiband')."
        },
        fill_holes: {
          type: "boolean",
          description: "Whether to fill holes in the stitched panorama."
        }
      },
      required: ["output_pts_path"],
      additionalProperties: true
    }
  },
  {
    name: "get_project_summary",
    description:
      "Read and inspect a PTGui .pts (JSON) project file, returning source image count, lens parameters, projection, FOV, output format/path, blending settings, and control point count.",
    inputSchema: {
      type: "object",
      properties: {
        pts_path: {
          type: "string",
          description: "Path to the .pts project file."
        }
      },
      required: ["pts_path"],
      additionalProperties: false
    }
  },
  {
    name: "update_project_settings",
    description:
      "Update parameters inside a PTGui .pts (JSON v55) project file: projection, HFOV/VFOV, output file path, format (jpeg/tiff/psd/exr/dng), fixed or relative resolution, blending (zerooverlap/multiband/fillholes), HDR settings, lens projection/focal length, per-image yaw/pitch/roll, or raw JSON patch.",
    inputSchema: {
      type: "object",
      properties: {
        pts_path: {
          type: "string",
          description: "Path to the existing .pts project file."
        },
        save_as_path: {
          type: "string",
          description: "Optional new path to save the modified .pts file (defaults to overwriting pts_path)."
        },
        panorama_output_path: {
          type: "string",
          description: "Output path for the stitched panorama file."
        },
        projection: {
          type: "string",
          description: "Panorama projection ('equirectangular', 'rectilinear', 'cylindrical', 'stereographic')."
        },
        hfov: { type: "number", description: "Horizontal FOV in degrees (e.g. 360)." },
        vfov: { type: "number", description: "Vertical FOV in degrees (e.g. 180)." },
        file_format: {
          type: "string",
          description: "Output format ('jpeg', 'tiff', 'psd', 'exr', 'dng')."
        },
        jpeg_quality: { type: "number", description: "JPEG quality (1-100)." },
        tiff_bitdepth: { type: "string", description: "TIFF bit depth ('u8', 'u16', 'f32')." },
        tiff_compression: {
          type: "string",
          description: "TIFF compression ('deflate', 'lzw', 'none', 'jpegxl')."
        },
        psd_layermode: {
          type: "string",
          description: "PSD layer mode ('layered', 'blended', 'both')."
        },
        output_size_mode: {
          type: "string",
          description: "Output size mode ('relative' or 'fixed')."
        },
        fraction_of_optimum_size: {
          type: "number",
          description: "Fraction of optimum size when mode is 'relative' (e.g. 1.0 or 0.25 for preview)."
        },
        width: { type: "number", description: "Fixed panorama width in pixels." },
        height: { type: "number", description: "Fixed panorama height in pixels." },
        blend_engine: { type: "string", description: "Blending engine ('zerooverlap' or 'multiband')." },
        fill_holes: { type: "boolean", description: "Fill sky/nadir holes automatically." },
        seam_finding: { type: "boolean", description: "Enable optimum seam finding." },
        lens_projection: {
          type: "string",
          description: "Global lens projection ('rectilinear', 'fisheye_circular', 'fisheye_fullframe', 'equirectangular')."
        },
        focal_length: { type: "number", description: "Global lens focal length in mm." },
        image_positions: {
          type: "array",
          description: "Optional per-image yaw/pitch/roll overrides: [{ index, yaw, pitch, roll }].",
          items: {
            type: "object",
            properties: {
              index: { type: "number" },
              yaw: { type: "number" },
              pitch: { type: "number" },
              roll: { type: "number" }
            },
            required: ["index"]
          }
        },
        align_settings: {
          type: "object",
          description: "Alignment flags (generate_cp, optimize, roughly_align, straighten, fit, choose_projection, optimize_exposure)."
        },
        batch_stitch_settings: {
          type: "object",
          description: "Batch stitcher flags (align, stitch, stitch_only_if_control_points)."
        },
        hdr_settings: {
          type: "object",
          description: "HDR settings (ldr_panorama, hdr_blended, tonemap_panorama, hdr_file_format, hdr_method)."
        },
        raw_patch: {
          type: "object",
          description: "Optional deep-merge JSON patch applied directly to the .pts root object."
        }
      },
      required: ["pts_path"],
      additionalProperties: true
    }
  },
  {
    name: "stitch_project",
    description:
      "Run headless alignment and stitching on a .pts project file via 'PTGui -stitchnogui' (or queue via '-batch'). Supports temporary overrides for output_path, scale_fraction (for fast visual audit previews), and force_stitch.",
    inputSchema: {
      type: "object",
      properties: {
        pts_path: {
          type: "string",
          description: "Path to the .pts project file to stitch."
        },
        output_path: {
          type: "string",
          description: "Optional override destination path for the rendered panorama image."
        },
        scale_fraction: {
          type: "number",
          description: "Optional relative size fraction (e.g. 0.25 for fast preview rendering, 1.0 for full optimum resolution)."
        },
        align: {
          type: "boolean",
          description: "Override batchstitchersettings.align before stitching."
        },
        force_stitch: {
          type: "boolean",
          description: "If true, sets stitchonlyifcontrolpoints=false so PTGui stitches even when automatic control points are sparse or pre-positioned."
        },
        persist_overrides: {
          type: "boolean",
          description: "If true, write the overrides permanently into pts_path instead of using a temporary .pts copy."
        },
        mode: {
          type: "string",
          enum: ["stitchnogui", "batch"],
          description: "Execution mode: 'stitchnogui' (default, headless synchronous CLI) or 'batch' (Batch Stitcher GUI queue)."
        },
        timeout_ms: {
          type: "number",
          description: "Maximum wait time in milliseconds (default 600000 = 10 minutes)."
        }
      },
      required: ["pts_path"],
      additionalProperties: false
    }
  },
  {
    name: "open_in_ptgui_gui",
    description:
      "Open a .pts project file or stitched panorama image in the PTGui Pro GUI or PTGuiViewer.exe for interactive inspection.",
    inputSchema: {
      type: "object",
      properties: {
        file_path: {
          type: "string",
          description: "Path to the .pts project or panorama image file."
        },
        use_viewer: {
          type: "boolean",
          description: "If true, open with PTGuiViewer.exe instead of PTGui.exe."
        }
      },
      required: ["file_path"],
      additionalProperties: false
    }
  }
];

function handleToolCall(name, args) {
  switch (name) {
    case "get_ptgui_status":
      return getPtguiStatus(args);
    case "create_ptgui_project":
      return createPtguiProject(args);
    case "get_project_summary":
      return getProjectSummary(args);
    case "update_project_settings":
      return updateProjectSettings(args);
    case "stitch_project":
      return stitchProject(args);
    case "open_in_ptgui_gui":
      return openInPtguiGui(args);
    default:
      return { ok: false, error: `Unknown tool: ${ name }` };
  }
}

/**
 * MCP stdio JSON-RPC 2.0 Server Loop
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
            name: "ptgui",
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
  getPtguiStatus,
  createPtguiProject,
  getProjectSummary,
  updateProjectSettings,
  stitchProject,
  openInPtguiGui,
  TOOLS_DEFINITION
};
