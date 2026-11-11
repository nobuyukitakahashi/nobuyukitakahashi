#!/usr/bin/env node
/**
 * Adobe Photoshop CLI Bridge for Antigravity
 * Allows calling all 5 Photoshop MCP tools directly via `node .agents/mcp/photoshop-mcp/cli.js <subcommand>`
 *
 * Usage:
 *   node .agents/mcp/photoshop-mcp/cli.js status
 *   node .agents/mcp/photoshop-mcp/cli.js summary [--file <path>]
 *   node .agents/mcp/photoshop-mcp/cli.js exec --code "<jsx>" | --file <script.jsx>
 *   node .agents/mcp/photoshop-mcp/cli.js export-png --out <png_path> [--scale 100]
 *   node .agents/mcp/photoshop-mcp/cli.js save --out <psd_or_png_or_jpg_or_tiff_path> [--rasterize-text true] [--cmyk true] [--flatten true]
 */

const {
  getPhotoshopStatus,
  executePhotoshopJsx,
  getDocumentSummary,
  exportCanvasPng,
  savePhotoshopDocument
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

function printUsage() {
  console.log(`Usage:
  node .agents/mcp/photoshop-mcp/cli.js status
  node .agents/mcp/photoshop-mcp/cli.js summary [--file <path>]
  node .agents/mcp/photoshop-mcp/cli.js exec --code "<jsx>" | --file <script.jsx>
  node .agents/mcp/photoshop-mcp/cli.js export-png --out <png_path> [--scale 100]
  node .agents/mcp/photoshop-mcp/cli.js save --out <psd_or_png_or_jpg_or_tiff_path> [--rasterize-text true] [--cmyk true] [--flatten true]`);
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
      res = getPhotoshopStatus();
      break;
    }
    case "summary": {
      res = getDocumentSummary({
        file_path: parsed.file || parsed.path || parsed._[1]
      });
      break;
    }
    case "exec": {
      res = executePhotoshopJsx({
        script: parsed.code || parsed.script,
        script_path: parsed.file || parsed["script-path"] || parsed._[1],
        wrap_try_catch: parseBool(parsed.wrap, true)
      });
      break;
    }
    case "export-png": {
      res = exportCanvasPng({
        output_path: parsed.out || parsed.output || parsed._[1],
        scale: parsed.scale !== undefined ? Number(parsed.scale) : 100
      });
      break;
    }
    case "save": {
      res = savePhotoshopDocument({
        output_path: parsed.out || parsed.output || parsed._[1],
        rasterize_text: parseBool(parsed["rasterize-text"], false),
        cmyk_convert: parseBool(parsed.cmyk || parsed["cmyk-convert"], false),
        flatten: parseBool(parsed.flatten, false)
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
