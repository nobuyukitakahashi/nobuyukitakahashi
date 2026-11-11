#!/usr/bin/env node
/**
 * Adobe Illustrator CLI Bridge for Antigravity
 * Allows calling all 5 Illustrator MCP tools directly via `node .agents/mcp/illustrator-mcp/cli.js <subcommand>`
 *
 * Usage:
 *   node .agents/mcp/illustrator-mcp/cli.js status
 *   node .agents/mcp/illustrator-mcp/cli.js summary [--file <path>]
 *   node .agents/mcp/illustrator-mcp/cli.js exec --code "<jsx>" | --file <script.jsx>
 *   node .agents/mcp/illustrator-mcp/cli.js export-png --out <png_path> [--artboard 0] [--scale 200] [--transparent true]
 *   node .agents/mcp/illustrator-mcp/cli.js save --out <ai_or_pdf_or_svg_path> [--outline-text true] [--cmyk true]
 */

const {
  getIllustratorStatus,
  executeIllustratorJsx,
  getDocumentSummary,
  exportArtboardPng,
  saveIllustratorDocument
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
  node .agents/mcp/illustrator-mcp/cli.js status
  node .agents/mcp/illustrator-mcp/cli.js summary [--file <path>]
  node .agents/mcp/illustrator-mcp/cli.js exec --code "<jsx>" | --file <script.jsx>
  node .agents/mcp/illustrator-mcp/cli.js export-png --out <png_path> [--artboard 0] [--scale 200] [--transparent true]
  node .agents/mcp/illustrator-mcp/cli.js save --out <ai_or_pdf_or_svg_path> [--outline-text true] [--cmyk true]`);
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
      res = getIllustratorStatus();
      break;
    }
    case "summary": {
      res = getDocumentSummary({
        file_path: parsed.file || parsed.path
      });
      break;
    }
    case "exec": {
      res = executeIllustratorJsx({
        script: parsed.code || parsed.script,
        script_path: parsed.file || parsed["script-path"],
        wrap_try_catch: parseBool(parsed.wrap, true)
      });
      break;
    }
    case "export-png": {
      res = exportArtboardPng({
        output_path: parsed.out || parsed.output,
        artboard_index: parsed.artboard !== undefined ? Number(parsed.artboard) : 0,
        scale: parsed.scale !== undefined ? Number(parsed.scale) : 200,
        transparency: parseBool(parsed.transparent !== undefined ? parsed.transparent : parsed.transparency, true)
      });
      break;
    }
    case "save": {
      res = saveIllustratorDocument({
        output_path: parsed.out || parsed.output,
        outline_text: parseBool(parsed["outline-text"], false),
        cmyk_convert: parseBool(parsed.cmyk || parsed["cmyk-convert"], false)
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
