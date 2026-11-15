#!/usr/bin/env node
/**
 * Adobe After Effects CLI Bridge for Antigravity
 */

const {
  getAfterEffectsStatus,
  executeAfterEffectsJsx,
  getProjectSummary,
  exportCompFramePng,
  saveAfterEffectsProject
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
  node .agents/mcp/aftereffects-mcp/cli.js status
  node .agents/mcp/aftereffects-mcp/cli.js summary [--file <aep_path>]
  node .agents/mcp/aftereffects-mcp/cli.js exec --code "<jsx>" | --file <script.jsx>
  node .agents/mcp/aftereffects-mcp/cli.js export-png --out <png_path> [--comp <name>] [--time <sec>]
  node .agents/mcp/aftereffects-mcp/cli.js save [--out <aep_path>] [--render-comp <name>] [--render-out <mp4_or_mov_path>]`);
    process.exit(0);
  }

  let res;
  switch (subcmd) {
    case "status":
      res = getAfterEffectsStatus();
      break;
    case "summary":
      res = getProjectSummary({ file_path: parsed.file || parsed.path });
      break;
    case "exec":
      res = executeAfterEffectsJsx({
        script: parsed.code || parsed.script,
        script_path: parsed.file || parsed["script-path"],
        wrap_try_catch: parseBool(parsed.wrap, true)
      });
      break;
    case "export-png":
      res = exportCompFramePng({
        output_path: parsed.out || parsed.output,
        comp_name: parsed.comp,
        time_seconds: parsed.time !== undefined ? Number(parsed.time) : undefined
      });
      break;
    case "save":
      res = saveAfterEffectsProject({
        output_path: parsed.out || parsed.output,
        render_comp_name: parsed["render-comp"],
        render_output_path: parsed["render-out"]
      });
      break;
    default:
      res = { ok: false, error: `Unknown subcommand: ${subcmd}` };
  }

  console.log(JSON.stringify(res, null, 2));
  process.exit(res && res.ok === false ? 1 : 0);
}

main();
