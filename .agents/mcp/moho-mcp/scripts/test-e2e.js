#!/usr/bin/env node
"use strict";

/**
 * End-to-End Automated Test Suite for Moho Pro 14.5.1 Full-Control Environment
 * Tests:
 *   1. Environment & Bridge Deployment Verification
 *   2. Headless .moho ZIP/JSON Engine (Inspect, Create, Patch, Unpack, Pack)
 *   3. Headless Moho.exe -r CLI Renderer (on both Tutorial and newly generated .moho)
 *   4. MCP Server stdio JSON-RPC 2.0 Protocol (initialize, tools/list, tools/call)
 *   5. Live Lua 5.4 Bridge (if running Moho GUI has an active visible window)
 */

const fs = require("fs");
const path = require("path");
const os = require("os");
const { spawnSync } = require("child_process");
const { handleToolCall, TOOLS_DEFINITION } = require("../lib/mcp-tools");

function assert(cond, msg) {
  if (!cond) throw new Error(`ASSERTION FAILED: ${msg}`);
}

function runMcpProtocolTest() {
  const serverPath = path.resolve(__dirname, "..", "server.js");
  const req1 = JSON.stringify({
    jsonrpc: "2.0",
    id: 1,
    method: "initialize",
    params: { protocolVersion: "2024-11-05", clientInfo: { name: "test", version: "1.0" }, capabilities: {} }
  });
  const req2 = JSON.stringify({ jsonrpc: "2.0", id: 2, method: "tools/list", params: {} });
  const req3 = JSON.stringify({
    jsonrpc: "2.0",
    id: 3,
    method: "tools/call",
    params: { name: "get_moho_status", arguments: {} }
  });

  // Test Content-Length framing on req1 + req2 + req3
  function frame(s) {
    return `Content-Length: ${Buffer.byteLength(s, "utf8")}\r\n\r\n${s}`;
  }
  const input = frame(req1) + frame(req2) + frame(req3);
  const proc = spawnSync(process.execPath, [serverPath], {
    input,
    encoding: "utf8",
    timeout: 15000
  });
  assert(proc.status === 0, `MCP server exited with ${proc.status}: ${proc.stderr}`);

  const out = proc.stdout || "";
  const bodies = [];
  let cursor = 0;
  while (cursor < out.length) {
    const idx = out.indexOf("Content-Length:", cursor);
    if (idx === -1) break;
    const sep = out.indexOf("\r\n\r\n", idx);
    const len = parseInt(out.slice(idx + 15, sep).trim(), 10);
    const buf = Buffer.from(out.slice(sep + 4), "utf8");
    const bodyStr = buf.slice(0, len).toString("utf8");
    bodies.push(JSON.parse(bodyStr));
    cursor = sep + 4 + bodyStr.length;
  }

  assert(bodies.length === 3, `Expected 3 MCP responses, got ${bodies.length}`);
  assert(bodies[0].result.serverInfo.name === "moho", "MCP serverInfo.name should be 'moho'");
  assert(
    bodies[1].result.tools.length === TOOLS_DEFINITION.length,
    `Expected ${TOOLS_DEFINITION.length} MCP tools, got ${bodies[1].result.tools.length}`
  );
  const statusPayload = JSON.parse(bodies[2].result.content[0].text);
  assert(statusPayload.ok === true && statusPayload.installed === true, "MCP get_moho_status failed");
  return {
    ok: true,
    responses: bodies.length,
    toolCount: bodies[1].result.tools.length,
    mohoVersion: statusPayload.version
  };
}

function main() {
  const testOutDir = path.join(os.tmpdir(), "agy-moho-e2e-verification");
  fs.mkdirSync(testOutDir, { recursive: true });

  const report = {
    startedAt: new Date().toISOString(),
    tests: {}
  };

  // TEST 1: Status & Deployment
  const status = handleToolCall("get_moho_status", {});
  assert(status.ok === true, "Moho not installed");
  assert(status.bridgeInstalled === true, "Lua bridge not installed");
  report.tests.status = {
    ok: true,
    version: status.version,
    editableFilesDir: status.editableFilesDir,
    bridgeInstalled: status.bridgeInstalled
  };

  // TEST 2: Inspect Tutorial 1.01.moho
  const tutPath = path.join(status.editableFilesDir, "Tutorials", "1 - Basics", "Tutorial 1.01.moho");
  const inspected = handleToolCall("inspect_moho_file", { moho_path: tutPath });
  assert(inspected.ok === true && inspected.projectData.width === 320, "Tutorial 1.01 inspect mismatch");
  report.tests.inspectTutorial = {
    ok: true,
    width: inspected.projectData.width,
    height: inspected.projectData.height,
    totalLayers: inspected.counts.totalLayers
  };

  // TEST 3: Create brand-new .moho headlessly + Patch + Unpack/Pack round-trip
  const createdMoho = path.join(testOutDir, "headless_demo.moho");
  const created = handleToolCall("create_moho_file", {
    output_path: createdMoho,
    width: 1280,
    height: 720,
    fps: 30,
    start_frame: 1,
    end_frame: 60,
    back_color: { r: 28, g: 36, b: 58, a: 255 },
    layers: ["Background", "Character_Vector", "Foreground"]
  });
  assert(created.ok === true && fs.existsSync(createdMoho), "create_moho_file failed");

  const patchedMoho = path.join(testOutDir, "headless_demo_patched.moho");
  const patched = handleToolCall("patch_moho_file", {
    moho_path: createdMoho,
    save_as: patchedMoho,
    fps: 24,
    layer_updates: [{ name: "Foreground", rename: "FX_Overlay", visible: false }],
    set_paths: { "project_data.end_frame": 96 }
  });
  assert(patched.ok === true && fs.existsSync(patchedMoho), "patch_moho_file failed");

  const unpackedDir = path.join(testOutDir, "unpacked_demo");
  const unpacked = handleToolCall("unpack_moho_file", { moho_path: patchedMoho, output_dir: unpackedDir });
  assert(unpacked.ok === true && fs.existsSync(path.join(unpackedDir, "Project.mohoproj")), "unpack failed");

  const repackedMoho = path.join(testOutDir, "headless_demo_repacked.moho");
  const repacked = handleToolCall("pack_moho_file", { input_dir: unpackedDir, output_path: repackedMoho });
  assert(repacked.ok === true && fs.existsSync(repackedMoho), "pack failed");

  const repackedInfo = handleToolCall("inspect_moho_file", { moho_path: repackedMoho });
  assert(repackedInfo.projectData.width === 1280 && repackedInfo.projectData.height === 720, "width/height mismatch");
  assert(repackedInfo.projectData.fps === 24 && repackedInfo.projectData.endFrame === 96, "fps/endFrame mismatch");
  assert(repackedInfo.layers[2].name === "FX_Overlay" && repackedInfo.layers[2].visible === false, "layer patch mismatch");

  report.tests.headlessFileEngine = {
    ok: true,
    createdMoho,
    repackedMoho,
    verifiedLayers: repackedInfo.layers.map((l) => `${l.name}(vis=${l.visible})`)
  };

  // TEST 4: Headless CLI Render (Moho.exe -r) on BOTH repacked custom .moho AND Tutorial 1.01
  const previewCustomPng = path.join(testOutDir, "headless_demo_frame1.png");
  const renderCustom = handleToolCall("render_preview_frame", {
    moho_path: repackedMoho,
    frame: 1,
    output_png: previewCustomPng
  });
  assert(renderCustom.ok === true && renderCustom.sizeBytes > 100, `Render custom .moho failed: ${renderCustom.error}`);

  const previewTutPng = path.join(testOutDir, "tutorial_101_frame1.png");
  const renderTut = handleToolCall("render_preview_frame", {
    moho_path: tutPath,
    frame: 1,
    output_png: previewTutPng
  });
  assert(renderTut.ok === true && renderTut.sizeBytes > 100, `Render tutorial .moho failed: ${renderTut.error}`);

  report.tests.headlessCliRender = {
    ok: true,
    customPng: { path: previewCustomPng, sizeBytes: renderCustom.sizeBytes, size: renderCustom.logSummary.size },
    tutorialPng: { path: previewTutPng, sizeBytes: renderTut.sizeBytes, size: renderTut.logSummary.size }
  };

  // TEST 5: MCP stdio JSON-RPC 2.0 Protocol
  report.tests.mcpProtocol = runMcpProtocolTest();

  // TEST 6: Live Lua 5.4 Bridge (optional live GUI check)
  const livePing = handleToolCall("execute_moho_lua", {
    code: 'return { luaVersion = _VERSION, bridgeVersion = AGY_MohoBridge and AGY_MohoBridge.VERSION or "unknown", hasDoc = (moho.document ~= nil) }',
    update_ui: false,
    timeout_ms: 4500
  });
  report.tests.liveLuaBridge = livePing.ok
    ? { ok: true, connected: true, result: livePing.result, elapsedMs: livePing.elapsedMs }
    : {
        ok: false,
        skipped: true,
        connected: false,
        note: "Moho GUI not actively responding to live bridge yet (launch or reload Moho GUI scripts via Ctrl+Shift+Alt+L to enable live Lua).",
        detail: livePing.error
      };

  report.ok = true;
  report.finishedAt = new Date().toISOString();
  fs.writeFileSync(path.join(testOutDir, "e2e_report.json"), JSON.stringify(report, null, 2) + "\n", "utf8");
  console.log(JSON.stringify(report, null, 2));
}

main();
