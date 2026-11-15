#!/usr/bin/env node
/**
 * Adobe Premiere Pro CLI Bridge for Antigravity
 */

const {
  getPremiereStatus,
  executePremiereJsx,
  getProjectSummary,
  exportFramePng,
  saveOrExportPremiere
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

function main() {
  const parsed = parseArgs(process.argv.slice(2));
  const subcmd = parsed._[0];

  if (!subcmd || subcmd === "help" || parsed.help) {
    console.log(`Usage:
  node .agents/mcp/premiere-mcp/cli.js status
  node .agents/mcp/premiere-mcp/cli.js summary
  node .agents/mcp/premiere-mcp/cli.js exec --code "<jsx>" | --file <script.jsx>
  node .agents/mcp/premiere-mcp/cli.js export-png --out <png_path> [--time <sec>]
  node .agents/mcp/premiere-mcp/cli.js save [--save-as <prproj>] [--export-out <mp4>] [--preset <epr>]`);
    process.exit(0);
  }

  let res;
  switch (subcmd) {
    case "status":
      res = getPremiereStatus();
      break;
    case "summary":
      res = getProjectSummary();
      break;
    case "exec":
      res = executePremiereJsx({
        script: parsed.code || parsed.script,
        script_path: parsed.file || parsed["script-path"],
        wrap_try_catch: parseBool(parsed.wrap, true)
      });
      break;
    case "export-png":
      res = exportFramePng({
        output_path: parsed.out || parsed.output,
        time_seconds: parsed.time !== undefined ? Number(parsed.time) : undefined
      });
      break;
    case "save":
      res = saveOrExportPremiere({
        save_project: parsed["save-as"] ? false : true,
        save_as_path: parsed["save-as"],
        export_media_path: parsed["export-out"],
        export_preset_path: parsed.preset
      });
      break;
    default:
      res = { ok: false, error: `Unknown subcommand: ${subcmd}` };
  }

  console.log(JSON.stringify(res, null, 2));
  process.exit(res && res.ok === false ? 1 : 0);
}

main();
