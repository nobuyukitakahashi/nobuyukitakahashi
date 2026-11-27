#!/usr/bin/env node
"use strict";

/**
 * Moho Pro 14.5.1 Bridge Installer & MCP Config Synchronizer
 * 1. Generates a clean 24x24 PNG tool icon (pure Node.js zlib, zero external deps).
 * 2. Deploys Lua 5.4 bridge scripts into Moho's Custom Content Folder (EditableFilesDir/Scripts).
 * 3. Safely registers "moho" MCP server in Antigravity mcp_config.json files without touching other servers.
 */

const fs = require("fs");
const path = require("path");
const os = require("os");
const zlib = require("zlib");
const { detectMohoEnvironment, BRIDGE_DIR } = require("./lib/env");
const { crc32 } = require("./lib/zip");

/**
 * Generate a crisp 24x24 RGBA PNG icon (teal/indigo badge with "M" motif) using built-in zlib.
 */
function buildToolIconPng() {
  const w = 24;
  const h = 24;
  const raw = Buffer.alloc((w * 4 + 1) * h);

  for (let y = 0; y < h; y++) {
    const rowStart = y * (w * 4 + 1);
    raw[rowStart] = 0; // filter None
    for (let x = 0; x < w; x++) {
      const px = rowStart + 1 + x * 4;
      const dx = x - 11.5;
      const dy = y - 11.5;
      const dist = Math.sqrt(dx * dx + dy * dy);
      if (dist > 11.2) {
        raw[px] = 0; raw[px + 1] = 0; raw[px + 2] = 0; raw[px + 3] = 0;
        continue;
      }
      // Rounded badge gradient (#0ea5e9 -> #4f46e5)
      let r = Math.round(14 + (x / w) * 65);
      let g = Math.round(165 - (y / h) * 95);
      let b = Math.round(233 - (y / h) * 4);
      let a = 255;

      // Crisp white "M" glyph inside
      const inLeftStem = x >= 5 && x <= 7 && y >= 6 && y <= 17;
      const inRightStem = x >= 16 && x <= 18 && y >= 6 && y <= 17;
      const inLeftDiag = x >= 7 && x <= 12 && Math.abs((y - 6) - (x - 7) * 1.2) <= 1.2 && y <= 14;
      const inRightDiag = x >= 12 && x <= 16 && Math.abs((y - 6) - (16 - x) * 1.2) <= 1.2 && y <= 14;
      if (inLeftStem || inRightStem || inLeftDiag || inRightDiag) {
        r = 255; g = 255; b = 255;
      }
      raw[px] = r; raw[px + 1] = g; raw[px + 2] = b; raw[px + 3] = a;
    }
  }

  function makeChunk(type, data) {
    const len = Buffer.alloc(4);
    len.writeUInt32BE(data.length, 0);
    const typeBuf = Buffer.from(type, "ascii");
    const crcBuf = Buffer.alloc(4);
    crcBuf.writeUInt32BE(crc32(Buffer.concat([typeBuf, data])), 0);
    return Buffer.concat([len, typeBuf, data, crcBuf]);
  }

  const sig = Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]);
  const ihdr = Buffer.alloc(13);
  ihdr.writeUInt32BE(w, 0);
  ihdr.writeUInt32BE(h, 4);
  ihdr[8] = 8; // bit depth
  ihdr[9] = 6; // RGBA
  ihdr[10] = 0; ihdr[11] = 0; ihdr[12] = 0;

  const idat = zlib.deflateSync(raw);
  return Buffer.concat([
    sig,
    makeChunk("IHDR", ihdr),
    makeChunk("IDAT", idat),
    makeChunk("IEND", Buffer.alloc(0))
  ]);
}

function copyFileEnsureDir(src, dest) {
  fs.mkdirSync(path.dirname(dest), { recursive: true });
  fs.copyFileSync(src, dest);
}

function registerMcpConfig(configPath, serverScriptPath) {
  if (!fs.existsSync(configPath)) {
    return { path: configPath, updated: false, reason: "config_not_found" };
  }
  const raw = fs.readFileSync(configPath, "utf8").replace(/^\uFEFF/, "");
  const json = JSON.parse(raw);
  json.mcpServers = json.mcpServers || {};
  json.mcpServers.moho = {
    command: process.execPath,
    args: [serverScriptPath]
  };
  fs.writeFileSync(configPath, JSON.stringify(json, null, 2) + "\n", "utf8");
  return { path: configPath, updated: true };
}

function main() {
  const skipMcp = process.argv.includes("--no-mcp");
  const ifInstalled = process.argv.includes("--if-installed");
  const env = detectMohoEnvironment();
  if (ifInstalled && (!env.installed || !env.editableFilesDir)) {
    console.log(JSON.stringify({
      ok: true,
      skipped: true,
      reason: "moho_not_installed_or_no_content_dir",
      mohoInstalled: env.installed,
      hasEditableFilesDir: Boolean(env.editableFilesDir)
    }, null, 2));
    process.exit(0);
  }
  if (!env.editableFilesDir) {
    console.error("ERROR: Could not locate Moho Custom Content Folder (EditableFilesDir).");
    process.exit(1);
  }

  const luaSrcRoot = path.join(__dirname, "lua");
  const scriptsDestRoot = path.join(env.editableFilesDir, "Scripts");

  // 1. Write 24x24 icon PNG in source lua/Tool/ and deploy to Moho Pro/Scripts/Tool/
  const iconPng = buildToolIconPng();
  const srcIconPath = path.join(luaSrcRoot, "Tool", "agy_moho_bridge.png");
  fs.mkdirSync(path.dirname(srcIconPath), { recursive: true });
  fs.writeFileSync(srcIconPath, iconPng);

  // 2. Deploy all Lua bridge files
  const copies = [
    [
      path.join(luaSrcRoot, "Utility", "agy_json.lua"),
      path.join(scriptsDestRoot, "Utility", "agy_json.lua")
    ],
    [
      path.join(luaSrcRoot, "Tool", "agy_moho_bridge.lua"),
      path.join(scriptsDestRoot, "Tool", "agy_moho_bridge.lua")
    ],
    [
      srcIconPath,
      path.join(scriptsDestRoot, "Tool", "agy_moho_bridge.png")
    ],
    [
      path.join(luaSrcRoot, "Menu", "Antigravity", "agy_moho_bridge_panel.lua"),
      path.join(scriptsDestRoot, "Menu", "Antigravity", "agy_moho_bridge_panel.lua")
    ]
  ];

  const deployed = [];
  for (const [src, dest] of copies) {
    copyFileEnsureDir(src, dest);
    deployed.push(dest);
  }

  // Ensure IPC directory exists
  fs.mkdirSync(BRIDGE_DIR, { recursive: true });

  // 3. Register MCP server in Antigravity configs (unless --no-mcp)
  const mcpResults = [];
  const serverPath = path.resolve(__dirname, "server.js");
  if (!skipMcp) {
    const geminiHome = path.join(os.homedir(), ".gemini");
    const configs = [
      path.join(geminiHome, "antigravity", "mcp_config.json"),
      path.join(geminiHome, "config", "mcp_config.json"),
      path.join(geminiHome, "antigravity-obsidian", "mcp_config.json")
    ];
    for (const cfg of configs) {
      mcpResults.push(registerMcpConfig(cfg, serverPath));
    }
  }

  const summary = {
    ok: true,
    mohoVersion: env.version,
    mohoExe: env.mohoExe,
    editableFilesDir: env.editableFilesDir,
    bridgeDir: BRIDGE_DIR,
    deployedScripts: deployed,
    mcpRegistration: mcpResults
  };
  console.log(JSON.stringify(summary, null, 2));
}

main();
