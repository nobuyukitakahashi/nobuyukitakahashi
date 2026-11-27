"use strict";

/**
 * Headless .moho Archive & Project.mohoproj JSON Engine
 * Allows full offline inspection, creation, patching, unpacking, and packing
 * of Moho Pro 14.5.1 project files without launching the GUI.
 */

const fs = require("fs");
const path = require("path");
const crypto = require("crypto");
const { readZipFile, writeZipFile } = require("./zip");
const { detectMohoEnvironment } = require("./env");
const { parseMohoJson, stringifyMohoJson } = require("./float-json");

function newUuid() {
  return crypto.randomUUID ? crypto.randomUUID() : crypto.randomBytes(16).toString("hex");
}

function nowMohoDate() {
  const d = new Date();
  const pad = (n) => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`;
}

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

function setByDotPath(obj, dotPath, value) {
  const parts = String(dotPath).split(".").filter(Boolean);
  if (parts.length === 0) throw new Error("Empty dot path");
  let cur = obj;
  for (let i = 0; i < parts.length - 1; i++) {
    const key = /^\d+$/.test(parts[i]) ? parseInt(parts[i], 10) : parts[i];
    if (cur[key] === undefined || cur[key] === null) {
      const nextIsIdx = /^\d+$/.test(parts[i + 1]);
      cur[key] = nextIsIdx ? [] : {};
    }
    cur = cur[key];
  }
  const last = /^\d+$/.test(parts[parts.length - 1])
    ? parseInt(parts[parts.length - 1], 10)
    : parts[parts.length - 1];
  cur[last] = value;
}

function loadMohoArchive(mohoPath) {
  const resolved = path.resolve(mohoPath);
  const entries = readZipFile(resolved);
  let projEntryName = null;
  for (const name of entries.keys()) {
    if (name.toLowerCase().endsWith(".mohoproj")) {
      projEntryName = name;
      break;
    }
  }
  if (!projEntryName) {
    throw new Error(`No .mohoproj file found inside archive: ${resolved}`);
  }
  const rawJson = entries.get(projEntryName).toString("utf8").replace(/^\uFEFF/, "");
  const { data: proj, floatMeta } = parseMohoJson(rawJson);
  return { resolved, entries, projEntryName, proj, floatMeta };
}

function summarizeLayer(layer, depth = 0, indexPath = []) {
  const info = {
    path: indexPath.join("."),
    depth,
    name: layer.name || "(unnamed)",
    type: layer.type || "Unknown",
    uuid: layer.uuid || null,
    visible: layer.visible !== undefined ? layer.visible : true,
    parentBone: layer.parent_bone !== undefined ? layer.parent_bone : -1,
    origin: layer.origin || null
  };

  if (layer.mesh && typeof layer.mesh === "object") {
    info.mesh = {
      points: Array.isArray(layer.mesh.points) ? layer.mesh.points.length : 0,
      curves: Array.isArray(layer.mesh.curves) ? layer.mesh.curves.length : 0,
      shapes: Array.isArray(layer.mesh.shapes) ? layer.mesh.shapes.length : 0,
      groups: Array.isArray(layer.mesh.groups) ? layer.mesh.groups.length : 0
    };
  }

  if (layer.skeleton && typeof layer.skeleton === "object") {
    const bones = Array.isArray(layer.skeleton.bones) ? layer.skeleton.bones : [];
    info.skeleton = {
      boneCount: bones.length,
      bindingMode: layer.skeleton.binding_mode,
      bones: bones.slice(0, 60).map((b, idx) => ({
        index: idx,
        name: b.name || `Bone ${idx}`,
        parent: b.parent_bone !== undefined ? b.parent_bone : -1,
        length: b.length,
        strength: b.strength
      }))
    };
  }

  if (Array.isArray(layer.layers) && layer.layers.length > 0) {
    info.children = layer.layers.map((child, i) =>
      summarizeLayer(child, depth + 1, [...indexPath, i])
    );
  }

  return info;
}

function countLayersRecursive(layers) {
  if (!Array.isArray(layers)) return 0;
  let total = 0;
  for (const l of layers) {
    total += 1;
    if (Array.isArray(l.layers)) total += countLayersRecursive(l.layers);
  }
  return total;
}

function findLayerByName(layers, targetName) {
  if (!Array.isArray(layers)) return null;
  for (const l of layers) {
    if (l.name === targetName) return l;
    if (Array.isArray(l.layers)) {
      const found = findLayerByName(l.layers, targetName);
      if (found) return found;
    }
  }
  return null;
}

/**
 * Inspect any .moho project file headlessly.
 */
function inspectMohoFile(args = {}) {
  const mohoPath = args.moho_path || args.file || args.path;
  if (!mohoPath) throw new Error("moho_path is required");

  const { resolved, entries, projEntryName, proj, floatMeta } = loadMohoArchive(mohoPath);
  const pd = proj.project_data || {};
  const layers = Array.isArray(proj.layers) ? proj.layers : [];
  const layerTree = layers.map((l, i) => summarizeLayer(l, 0, [i]));

  return {
    ok: true,
    mohoPath: resolved,
    fileSizeBytes: fs.statSync(resolved).size,
    archiveEntries: Array.from(entries.keys()),
    projectEntry: projEntryName,
    formatVersion: proj.version,
    majorVersion: proj.major_version,
    revVersion: proj.rev_version,
    docUuid: proj.doc_uuid,
    createdDate: proj.created_date,
    modifiedDate: proj.modified_date,
    projectData: {
      width: pd.width,
      height: pd.height,
      fps: pd.fps,
      startFrame: pd.start_frame,
      endFrame: pd.end_frame,
      backColor: pd.back_color,
      antialiasing: pd.antialiasing,
      depthSort: pd.depth_sort,
      depthOfField: pd.depth_of_field,
      soundtrack: pd.soundtrack || ""
    },
    counts: {
      topLevelLayers: layers.length,
      totalLayers: countLayersRecursive(layers),
      styles: Array.isArray(proj.styles) ? proj.styles.length : 0,
      layerComps: Array.isArray(proj.layercomps) ? proj.layercomps.length : 0
    },
    styles: Array.isArray(proj.styles)
      ? proj.styles.map((s) => ({ name: s.name, uuid: s.uuid }))
      : [],
    layerComps: Array.isArray(proj.layercomps)
      ? proj.layercomps.map((c) => ({ name: c.name }))
      : [],
    layers: layerTree
  };
}

/**
 * Locate a clean Moho 14.5.1 reference template .moho file from the local installation.
 */
function findBaseTemplateMoho() {
  const env = detectMohoEnvironment();
  const candidates = [];
  if (env.editableFilesDir) {
    candidates.push(
      path.join(env.editableFilesDir, "Tutorials", "1 - Basics", "Tutorial 1.01.moho"),
      path.join(env.editableFilesDir, "Tutorials", "11 - Moho 14", "Tutorial 11.01.moho")
    );
  }
  if (env.mohoExe) {
    const base = path.dirname(env.mohoExe);
    candidates.push(
      path.join(base, "Resources", "MohoFiles", "StylePreview.moho")
    );
  }
  for (const c of candidates) {
    if (c && fs.existsSync(c)) return c;
  }
  return null;
}

/**
 * Build a clean blank MeshLayer object cloned from an existing valid template layer.
 */
function buildCleanVectorLayer(templateMeshLayer, name = "Vector Layer") {
  const lyr = JSON.parse(JSON.stringify(templateMeshLayer));
  lyr.name = name;
  lyr.uuid = newUuid();
  lyr.visible = true;
  if (lyr.mesh) {
    lyr.mesh.points = [];
    lyr.mesh.curves = [];
    lyr.mesh.shapes = [];
    lyr.mesh.groups = [];
    lyr.mesh.next_shape_id = 0;
    if (lyr.mesh.shape_order && typeof lyr.mesh.shape_order === "object" && !Array.isArray(lyr.mesh.shape_order)) {
      lyr.mesh.shape_order.when = [0];
      lyr.mesh.shape_order.val = [""];
      if (Array.isArray(lyr.mesh.shape_order.interp) && lyr.mesh.shape_order.interp.length > 0) {
        lyr.mesh.shape_order.interp = [lyr.mesh.shape_order.interp[0]];
      }
    }
  }
  return lyr;
}

/**
 * Create a brand-new, 100% Moho 14.5.1 compliant .moho project file headlessly.
 */
function createMohoFile(args = {}) {
  const outputPath = args.output_path || args.moho_path || args.out;
  if (!outputPath) throw new Error("output_path is required");

  const templatePath = args.template_path || findBaseTemplateMoho();
  if (!templatePath || !fs.existsSync(templatePath)) {
    throw new Error("Could not locate a clean Moho base template file. Provide template_path.");
  }

  const { entries, projEntryName, proj, floatMeta } = loadMohoArchive(templatePath);

  // Clone and sanitize project metadata
  const nowStr = nowMohoDate();
  proj.doc_uuid = newUuid();
  proj.created_date = nowStr;
  proj.modified_date = nowStr;
  proj.comment = args.comment !== undefined ? String(args.comment) : "Created by Antigravity Moho Control";

  proj.project_data = proj.project_data || {};
  proj.project_data.width = args.width !== undefined ? Number(args.width) : 1920;
  proj.project_data.height = args.height !== undefined ? Number(args.height) : 1080;
  proj.project_data.fps = args.fps !== undefined ? Number(args.fps) : 24.0;
  proj.project_data.start_frame = args.start_frame !== undefined ? Number(args.start_frame) : 1;
  proj.project_data.end_frame = args.end_frame !== undefined ? Number(args.end_frame) : 240;

  if (args.back_color && typeof args.back_color === "object") {
    proj.project_data.back_color = {
      r: Number(args.back_color.r ?? 234),
      g: Number(args.back_color.g ?? 234),
      b: Number(args.back_color.b ?? 234),
      a: Number(args.back_color.a ?? 255)
    };
  }

  // Unless keep_template_layers is true, replace layers with clean blank vector layer(s)
  if (!args.keep_template_layers) {
    const templateMesh = (proj.layers || []).find((l) => l.type === "MeshLayer") || proj.layers[0];
    const requestedLayers = Array.isArray(args.layers) && args.layers.length > 0
      ? args.layers
      : [{ name: "Layer 1", type: "MeshLayer" }];

    proj.layers = requestedLayers.map((spec, idx) => {
      const name = typeof spec === "string" ? spec : (spec.name || `Layer ${idx + 1}`);
      return buildCleanVectorLayer(templateMesh, name);
    });
  }

  // Write Moho float-preserving compact JSON back into archive
  const outEntries = new Map();
  outEntries.set(projEntryName, Buffer.from(stringifyMohoJson(proj, floatMeta, 0), "utf8"));
  if (entries.has("preview.jpg")) {
    outEntries.set("preview.jpg", entries.get("preview.jpg"));
  }

  const savedPath = writeZipFile(outputPath, outEntries);
  return {
    ok: true,
    mohoPath: savedPath,
    templateUsed: templatePath,
    docUuid: proj.doc_uuid,
    width: proj.project_data.width,
    height: proj.project_data.height,
    fps: proj.project_data.fps,
    startFrame: proj.project_data.start_frame,
    endFrame: proj.project_data.end_frame,
    layerCount: proj.layers.length
  };
}

/**
 * Patch an existing .moho file headlessly (project settings, layer properties, dot-paths, or raw JSON merge).
 */
function patchMohoFile(args = {}) {
  const mohoPath = args.moho_path || args.file || args.path;
  if (!mohoPath) throw new Error("moho_path is required");

  const { resolved, entries, projEntryName, proj, floatMeta } = loadMohoArchive(mohoPath);
  const changes = [];

  proj.project_data = proj.project_data || {};
  const pd = proj.project_data;

  const numericMap = {
    width: "width",
    height: "height",
    fps: "fps",
    start_frame: "start_frame",
    end_frame: "end_frame",
    noise_grain: "noise_grain",
    pixelation: "pixelation"
  };

  for (const [argKey, pdKey] of Object.entries(numericMap)) {
    if (args[argKey] !== undefined) {
      pd[pdKey] = Number(args[argKey]);
      changes.push(`project_data.${pdKey}=${pd[pdKey]}`);
    }
  }

  if (args.antialiasing !== undefined) {
    pd.antialiasing = Boolean(args.antialiasing);
    changes.push(`project_data.antialiasing=${pd.antialiasing}`);
  }

  if (args.back_color && typeof args.back_color === "object") {
    pd.back_color = {
      r: Number(args.back_color.r ?? pd.back_color?.r ?? 234),
      g: Number(args.back_color.g ?? pd.back_color?.g ?? 234),
      b: Number(args.back_color.b ?? pd.back_color?.b ?? 234),
      a: Number(args.back_color.a ?? pd.back_color?.a ?? 255)
    };
    changes.push("project_data.back_color");
  }

  if (args.comment !== undefined) {
    proj.comment = String(args.comment);
    changes.push("comment");
  }

  // Layer-level structured updates: [{ name, rename, visible, origin, ... }]
  if (Array.isArray(args.layer_updates)) {
    for (const upd of args.layer_updates) {
      const lyr = findLayerByName(proj.layers, upd.name);
      if (!lyr) {
        throw new Error(`Layer not found for update: "${upd.name}"`);
      }
      if (upd.rename !== undefined) {
        lyr.name = String(upd.rename);
        changes.push(`layer[${upd.name}].rename=${lyr.name}`);
      }
      if (upd.visible !== undefined) {
        lyr.visible = Boolean(upd.visible);
        changes.push(`layer[${lyr.name}].visible=${lyr.visible}`);
      }
      if (upd.origin && Array.isArray(upd.origin) && upd.origin.length >= 2) {
        lyr.origin = [Number(upd.origin[0]), Number(upd.origin[1])];
        changes.push(`layer[${lyr.name}].origin`);
      }
      if (upd.render_only !== undefined) {
        lyr.render_only = Boolean(upd.render_only);
        changes.push(`layer[${lyr.name}].render_only=${lyr.render_only}`);
      }
      if (upd.edit_only !== undefined) {
        lyr.edit_only = Boolean(upd.edit_only);
        changes.push(`layer[${lyr.name}].edit_only=${lyr.edit_only}`);
      }
    }
  }

  // Arbitrary dot-path assignments: { "project_data.fps": 30, "layers.0.name": "BG" }
  if (args.set_paths && typeof args.set_paths === "object") {
    for (const [dotPath, value] of Object.entries(args.set_paths)) {
      setByDotPath(proj, dotPath, value);
      changes.push(`set:${dotPath}`);
    }
  }

  // Arbitrary raw deep-merge patch
  if (args.raw_patch && typeof args.raw_patch === "object") {
    deepMerge(proj, args.raw_patch);
    changes.push("raw_patch");
  }

  proj.modified_date = nowMohoDate();
  entries.set(projEntryName, Buffer.from(stringifyMohoJson(proj, floatMeta, 0), "utf8"));

  const targetPath = args.save_as ? path.resolve(args.save_as) : resolved;
  writeZipFile(targetPath, entries);

  return {
    ok: true,
    sourcePath: resolved,
    savedPath: targetPath,
    changes,
    projectData: {
      width: pd.width,
      height: pd.height,
      fps: pd.fps,
      startFrame: pd.start_frame,
      endFrame: pd.end_frame
    }
  };
}

/**
 * Unpack a .moho archive into a directory with pretty-printed Project.mohoproj JSON.
 */
function unpackMohoFile(args = {}) {
  const mohoPath = args.moho_path || args.file;
  const outputDir = args.output_dir || args.out_dir;
  if (!mohoPath || !outputDir) throw new Error("moho_path and output_dir are required");

  const resolved = path.resolve(mohoPath);
  const targetDir = path.resolve(outputDir);
  const pretty = args.pretty !== false;

  const entries = readZipFile(resolved);
  fs.mkdirSync(targetDir, { recursive: true });
  const extracted = [];

  for (const [name, buf] of entries.entries()) {
    const dest = path.resolve(targetDir, name);
    if (dest !== targetDir && !dest.startsWith(targetDir + path.sep)) {
      throw new Error(`Unsafe archive entry path rejected (Zip Slip): "${name}"`);
    }
    fs.mkdirSync(path.dirname(dest), { recursive: true });
    if (pretty && name.toLowerCase().endsWith(".mohoproj")) {
      const { data, floatMeta } = parseMohoJson(buf.toString("utf8"));
      fs.writeFileSync(dest, stringifyMohoJson(data, floatMeta, 2) + "\n", "utf8");
    } else {
      fs.writeFileSync(dest, buf);
    }
    extracted.push(name);
  }

  return {
    ok: true,
    mohoPath: resolved,
    outputDir: targetDir,
    files: extracted
  };
}

/**
 * Pack a directory containing Project.mohoproj (and assets) into a valid .moho archive.
 */
function packMohoFile(args = {}) {
  const inputDir = args.input_dir || args.dir;
  const outputPath = args.output_path || args.moho_path || args.out;
  if (!inputDir || !outputPath) throw new Error("input_dir and output_path are required");

  const srcDir = path.resolve(inputDir);
  if (!fs.existsSync(srcDir) || !fs.statSync(srcDir).isDirectory()) {
    throw new Error(`Input directory not found: ${srcDir}`);
  }

  const entries = new Map();
  let hasProj = false;

  function walk(curDir, relPrefix) {
    for (const dirent of fs.readdirSync(curDir, { withFileTypes: true })) {
      const full = path.join(curDir, dirent.name);
      const rel = relPrefix ? `${relPrefix}/${dirent.name}` : dirent.name;
      if (dirent.isDirectory()) {
        walk(full, rel);
      } else if (dirent.isFile()) {
        if (dirent.name.toLowerCase().endsWith(".mohoproj")) {
          hasProj = true;
          // Validate & minify JSON while preserving float `.0` tokens for Moho C++ parser
          const { data, floatMeta } = parseMohoJson(fs.readFileSync(full, "utf8"));
          entries.set(rel, Buffer.from(stringifyMohoJson(data, floatMeta, 0), "utf8"));
        } else {
          entries.set(rel, fs.readFileSync(full));
        }
      }
    }
  }

  walk(srcDir, "");
  if (!hasProj) {
    throw new Error(`No .mohoproj file found in directory: ${srcDir}`);
  }

  const saved = writeZipFile(outputPath, entries);
  return {
    ok: true,
    inputDir: srcDir,
    mohoPath: saved,
    entryCount: entries.size,
    entries: Array.from(entries.keys())
  };
}

module.exports = {
  inspectMohoFile,
  createMohoFile,
  patchMohoFile,
  unpackMohoFile,
  packMohoFile,
  findBaseTemplateMoho
};
