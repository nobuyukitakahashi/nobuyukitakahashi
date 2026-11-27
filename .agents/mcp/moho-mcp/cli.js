#!/usr/bin/env node
"use strict";

/**
 * Moho Pro 14.5.1 Direct CLI Bridge
 * Execute any Moho MCP tool or raw Lua script directly from terminal without needing MCP.
 */

const fs = require("fs");
const path = require("path");
const { TOOLS_DEFINITION, handleToolCall } = require("./lib/mcp-tools");

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

function parseBool(val, defVal) {
  if (val === undefined) return defVal;
  const s = String(val).toLowerCase().trim();
  if (s === "true" || s === "1" || s === "yes") return true;
  if (s === "false" || s === "0" || s === "no") return false;
  return defVal;
}

function parseNum(val) {
  return val !== undefined ? Number(val) : undefined;
}

function parseJsonArg(val, label) {
  if (!val) return undefined;
  try {
    return JSON.parse(val);
  } catch (err) {
    console.error(`Invalid JSON for --${label}: ${err.message}`);
    process.exit(1);
  }
}

function printUsage() {
  console.log(`Moho Pro 14.5.1 Direct Control CLI

Usage:
  node .agents/mcp/moho-mcp/cli.js status [--ping]
  node .agents/mcp/moho-mcp/cli.js tools
  node .agents/mcp/moho-mcp/cli.js inspect --file <project.moho>
  node .agents/mcp/moho-mcp/cli.js create --out <new.moho> [--width 1920] [--height 1080] [--fps 24] [--start 1] [--end 240] [--layers "BG,Character"]
  node .agents/mcp/moho-mcp/cli.js patch --file <project.moho> [--save-as <out.moho>] [--width N] [--height N] [--fps N] [--start N] [--end N] [--set-paths '{"project_data.fps":30}']
  node .agents/mcp/moho-mcp/cli.js unpack --file <project.moho> --out <dir>
  node .agents/mcp/moho-mcp/cli.js pack --dir <dir> --out <project.moho>
  node .agents/mcp/moho-mcp/cli.js render --file <project.moho> [--format PNG|MP4|QT|JPEG] [--start 1] [--end 24] [--outfolder <dir>] [--out <file>] [--halfsize false]
  node .agents/mcp/moho-mcp/cli.js preview --file <project.moho> [--frame 1] --out <preview.png>
  node .agents/mcp/moho-mcp/cli.js open [--file <project.moho>] [--reload] [--nudge]
  node .agents/mcp/moho-mcp/cli.js lua --code "return moho.document:Name()" | --file <script.lua> [--args '{"k":"v"}']
  node .agents/mcp/moho-mcp/cli.js live-summary
  node .agents/mcp/moho-mcp/cli.js call <tool_name> [--json '{"...":...}'] [--json-file <args.json>]
`);
}

function main() {
  const parsed = parseArgs(process.argv.slice(2));
  const subcmd = parsed._[0];

  if (!subcmd || subcmd === "help" || parsed.help) {
    printUsage();
    process.exit(0);
  }

  let res;
  try {
    switch (subcmd) {
      case "tools": {
        res = {
          ok: true,
          count: TOOLS_DEFINITION.length,
          tools: TOOLS_DEFINITION.map((t) => ({ name: t.name, description: t.description }))
        };
        break;
      }
      case "status": {
        res = handleToolCall("get_moho_status", {
          ping_live: parseBool(parsed.ping || parsed["ping-live"], false)
        });
        break;
      }
      case "inspect": {
        res = handleToolCall("inspect_moho_file", {
          moho_path: parsed.file || parsed.path || parsed._[1]
        });
        break;
      }
      case "create": {
        const layers = parsed.layers
          ? String(parsed.layers).split(",").map((s) => s.trim()).filter(Boolean)
          : undefined;
        res = handleToolCall("create_moho_file", {
          output_path: parsed.out || parsed.output || parsed._[1],
          width: parseNum(parsed.width),
          height: parseNum(parsed.height),
          fps: parseNum(parsed.fps),
          start_frame: parseNum(parsed.start || parsed["start-frame"]),
          end_frame: parseNum(parsed.end || parsed["end-frame"]),
          back_color: parseJsonArg(parsed["back-color"], "back-color"),
          layers,
          comment: parsed.comment,
          template_path: parsed.template,
          keep_template_layers: parseBool(parsed["keep-template-layers"], false)
        });
        break;
      }
      case "patch": {
        res = handleToolCall("patch_moho_file", {
          moho_path: parsed.file || parsed.path || parsed._[1],
          save_as: parsed["save-as"] || parsed.out,
          width: parseNum(parsed.width),
          height: parseNum(parsed.height),
          fps: parseNum(parsed.fps),
          start_frame: parseNum(parsed.start || parsed["start-frame"]),
          end_frame: parseNum(parsed.end || parsed["end-frame"]),
          antialiasing: parseBool(parsed.aa || parsed.antialiasing, undefined),
          back_color: parseJsonArg(parsed["back-color"], "back-color"),
          comment: parsed.comment,
          layer_updates: parseJsonArg(parsed["layer-updates"], "layer-updates"),
          set_paths: parseJsonArg(parsed["set-paths"], "set-paths"),
          raw_patch: parseJsonArg(parsed["raw-patch"], "raw-patch")
        });
        break;
      }
      case "unpack": {
        res = handleToolCall("unpack_moho_file", {
          moho_path: parsed.file || parsed._[1],
          output_dir: parsed.out || parsed.dir || parsed._[2],
          pretty: parseBool(parsed.pretty, true)
        });
        break;
      }
      case "pack": {
        res = handleToolCall("pack_moho_file", {
          input_dir: parsed.dir || parsed.in || parsed._[1],
          output_path: parsed.out || parsed.file || parsed._[2]
        });
        break;
      }
      case "render": {
        res = handleToolCall("render_moho", {
          moho_path: parsed.file || parsed._[1],
          format: parsed.format || parsed.f || "PNG",
          outfolder: parsed.outfolder || parsed.dir,
          output_path: parsed.out || parsed.o,
          start_frame: parseNum(parsed.start || parsed["start-frame"]),
          end_frame: parseNum(parsed.end || parsed["end-frame"]),
          layercomp: parsed.layercomp,
          aa: parseBool(parsed.aa, undefined),
          extrasmooth: parseBool(parsed.extrasmooth, undefined),
          halfsize: parseBool(parsed.halfsize, undefined),
          halffps: parseBool(parsed.halffps, undefined),
          multithread: parseBool(parsed.multithread, undefined),
          timeout_ms: parseNum(parsed.timeout)
        });
        break;
      }
      case "preview": {
        res = handleToolCall("render_preview_frame", {
          moho_path: parsed.file || parsed._[1],
          frame: parseNum(parsed.frame),
          output_png: parsed.out || parsed.png || parsed._[2],
          halfsize: parseBool(parsed.halfsize, undefined)
        });
        break;
      }
      case "open": {
        res = handleToolCall("open_in_moho", {
          moho_path: parsed.file || parsed._[1],
          reload_scripts: parseBool(parsed.reload, false),
          nudge_only: parseBool(parsed.nudge, false)
        });
        break;
      }
      case "lua": {
        let code = parsed.code;
        if (!code && parsed.file) {
          code = fs.readFileSync(path.resolve(parsed.file), "utf8").replace(/^\uFEFF/, "");
        }
        res = handleToolCall("execute_moho_lua", {
          code,
          args: parseJsonArg(parsed.args, "args") || {},
          update_ui: parseBool(parsed["update-ui"], true),
          timeout_ms: parseNum(parsed.timeout)
        });
        break;
      }
      case "live-summary": {
        res = handleToolCall("get_live_document_summary", {
          timeout_ms: parseNum(parsed.timeout)
        });
        break;
      }
      case "call": {
        const toolName = parsed._[1] || parsed.tool;
        if (!toolName) {
          console.error("Tool name is required for `call` subcommand");
          process.exit(1);
        }
        let toolArgs = {};
        if (parsed["json-file"]) {
          toolArgs = JSON.parse(
            fs.readFileSync(path.resolve(parsed["json-file"]), "utf8").replace(/^\uFEFF/, "")
          );
        } else if (parsed.json) {
          toolArgs = parseJsonArg(parsed.json, "json") || {};
        }
        res = handleToolCall(toolName, toolArgs);
        break;
      }
      default: {
        // Allow calling MCP tool names directly as subcommands
        if (TOOLS_DEFINITION.some((t) => t.name === subcmd)) {
          const toolArgs = parsed["json-file"]
            ? JSON.parse(fs.readFileSync(path.resolve(parsed["json-file"]), "utf8").replace(/^\uFEFF/, ""))
            : parseJsonArg(parsed.json, "json") || {};
          res = handleToolCall(subcmd, toolArgs);
        } else {
          console.error(`Unknown subcommand: ${subcmd}`);
          printUsage();
          process.exit(1);
        }
      }
    }
  } catch (err) {
    res = { ok: false, error: String(err && err.message ? err.message : err) };
  }

  console.log(JSON.stringify(res, null, 2));
  process.exit(res && res.ok === false ? 1 : 0);
}

main();
