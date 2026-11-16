#!/usr/bin/env node
/**
 * PTGui Pro 13 CLI Bridge for Antigravity
 * Allows calling all 6 PTGui MCP tools directly via `node .agents/mcp/ptgui-mcp/cli.js <subcommand>`
 *
 * Usage:
 *   node .agents/mcp/ptgui-mcp/cli.js status
 *   node .agents/mcp/ptgui-mcp/cli.js create --images "img1.jpg,img2.jpg" --out <project.pts> [--dir <img_dir>] [--template <tpl.pts>] [--pano-out <pano.jpg>] [--projection equirectangular]
 *   node .agents/mcp/ptgui-mcp/cli.js summary --file <project.pts>
 *   node .agents/mcp/ptgui-mcp/cli.js update --file <project.pts> [--save-as <out.pts>] [--pano-out <pano.jpg>] [--projection equirectangular] [--hfov 360] [--vfov 180] [--format jpeg] [--quality 95] [--width 8000] [--height 4000] [--blend zerooverlap] [--fill-holes true]
 *   node .agents/mcp/ptgui-mcp/cli.js stitch --file <project.pts> [--out <pano.jpg>] [--scale 0.25] [--force-stitch true] [--mode stitchnogui|batch]
 *   node .agents/mcp/ptgui-mcp/cli.js open --file <project.pts|pano.jpg> [--viewer true]
 */

const {
  getPtguiStatus,
  createPtguiProject,
  getProjectSummary,
  updateProjectSettings,
  stitchProject,
  openInPtguiGui
} = require("./server.js");

function parseArgs(argv) {
  const args = { _: [] };
  for (let i = 0; i < argv.length; i++) {
    const token = argv[i];
    if (token.startsWith("--")) {
      const key = token.slice(2);
      const next = argv[i + 1];
      if (next !== undefined && !next.startsWith("--")) {
        args[key] = next;
        i++;
      } else {
        args[key] = "true";
      }
    } else {
      args._.push(token);
    }
  }
  return args;
}

function parseBool(val, defaultVal) {
  if (val === undefined) return defaultVal;
  const s = String(val).toLowerCase().trim();
  if (s === "true" || s === "1" || s === "yes") return true;
  if (s === "false" || s === "0" || s === "no") return false;
  return defaultVal;
}

function parseNum(val) {
  return val !== undefined ? Number(val) : undefined;
}

function printUsage() {
  console.log(`Usage:
  node .agents/mcp/ptgui-mcp/cli.js status
  node .agents/mcp/ptgui-mcp/cli.js create --images "img1.jpg,img2.jpg" --out <project.pts> [--dir <img_dir>] [--template <tpl.pts>] [--pano-out <pano.jpg>] [--projection equirectangular]
  node .agents/mcp/ptgui-mcp/cli.js summary --file <project.pts>
  node .agents/mcp/ptgui-mcp/cli.js update --file <project.pts> [--save-as <out.pts>] [--pano-out <pano.jpg>] [--projection equirectangular] [--hfov 360] [--vfov 180] [--format jpeg] [--quality 95] [--width 8000] [--height 4000] [--blend zerooverlap] [--fill-holes true]
  node .agents/mcp/ptgui-mcp/cli.js stitch --file <project.pts> [--out <pano.jpg>] [--scale 0.25] [--force-stitch true] [--mode stitchnogui|batch]
  node .agents/mcp/ptgui-mcp/cli.js open --file <project.pts|pano.jpg> [--viewer true]`);
}

function main() {
  const parsed = parseArgs(process.argv.slice(2));
  const subcmd = parsed._[0];

  if (!subcmd || subcmd === "help" || parsed.help) {
    printUsage();
    process.exit(0);
  }

  let res;
  switch (subcmd) {
    case "status": {
      res = getPtguiStatus();
      break;
    }
    case "create": {
      const images = parsed.images
        ? String(parsed.images)
            .split(",")
            .map((s) => s.trim())
            .filter(Boolean)
        : parsed._.slice(1);
      res = createPtguiProject({
        images,
        image_dir: parsed.dir || parsed["image-dir"],
        output_pts_path: parsed.out || parsed.output || parsed.pts,
        template_path: parsed.template,
        panorama_output_path: parsed["pano-out"] || parsed.pano,
        projection: parsed.projection,
        hfov: parseNum(parsed.hfov),
        vfov: parseNum(parsed.vfov),
        file_format: parsed.format || parsed["file-format"],
        jpeg_quality: parseNum(parsed.quality || parsed["jpeg-quality"]),
        width: parseNum(parsed.width),
        height: parseNum(parsed.height),
        fraction_of_optimum_size: parseNum(parsed.scale || parsed.fraction),
        blend_engine: parsed.blend || parsed["blend-engine"],
        fill_holes: parseBool(parsed["fill-holes"], undefined)
      });
      break;
    }
    case "summary": {
      res = getProjectSummary({
        pts_path: parsed.file || parsed.pts || parsed.path || parsed._[1]
      });
      break;
    }
    case "update": {
      let rawPatch;
      if (parsed.patch) {
        try {
          rawPatch = JSON.parse(parsed.patch);
        } catch (err) {
          console.error(`Invalid --patch JSON: ${ err.message }`);
          process.exit(1);
        }
      }
      res = updateProjectSettings({
        pts_path: parsed.file || parsed.pts || parsed.path || parsed._[1],
        save_as_path: parsed["save-as"] || parsed.out,
        panorama_output_path: parsed["pano-out"] || parsed.pano,
        projection: parsed.projection,
        hfov: parseNum(parsed.hfov),
        vfov: parseNum(parsed.vfov),
        file_format: parsed.format || parsed["file-format"],
        jpeg_quality: parseNum(parsed.quality || parsed["jpeg-quality"]),
        tiff_bitdepth: parsed["tiff-bitdepth"],
        tiff_compression: parsed["tiff-compression"],
        psd_layermode: parsed["psd-layermode"],
        output_size_mode: parsed["size-mode"],
        fraction_of_optimum_size: parseNum(parsed.scale || parsed.fraction),
        width: parseNum(parsed.width),
        height: parseNum(parsed.height),
        blend_engine: parsed.blend || parsed["blend-engine"],
        fill_holes: parseBool(parsed["fill-holes"], undefined),
        seam_finding: parseBool(parsed["seam-finding"], undefined),
        lens_projection: parsed["lens-projection"],
        focal_length: parseNum(parsed["focal-length"]),
        raw_patch: rawPatch
      });
      break;
    }
    case "stitch": {
      res = stitchProject({
        pts_path: parsed.file || parsed.pts || parsed.path || parsed._[1],
        output_path: parsed.out || parsed.output || parsed["pano-out"],
        scale_fraction: parseNum(parsed.scale || parsed.fraction),
        align: parseBool(parsed.align, undefined),
        force_stitch: parseBool(parsed["force-stitch"], undefined),
        persist_overrides: parseBool(parsed.persist, false),
        mode: parsed.mode || "stitchnogui",
        timeout_ms: parseNum(parsed.timeout)
      });
      break;
    }
    case "open": {
      res = openInPtguiGui({
        file_path: parsed.file || parsed.pts || parsed.path || parsed._[1],
        use_viewer: parseBool(parsed.viewer || parsed["use-viewer"], false)
      });
      break;
    }
    default: {
      console.error(`Unknown subcommand: ${ subcmd }`);
      printUsage();
      process.exit(1);
    }
  }

  console.log(JSON.stringify(res, null, 2));
  if (res && res.ok === false) {
    process.exit(1);
  }
}

main();
