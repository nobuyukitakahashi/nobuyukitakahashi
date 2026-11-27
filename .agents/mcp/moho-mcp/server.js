#!/usr/bin/env node
"use strict";

/**
 * Moho Pro 14.5.1 Local MCP Server (stdio JSON-RPC 2.0)
 * Zero external npm dependencies (Node.js built-in modules only).
 * Supports both Content-Length header framing and newline-delimited JSON-RPC.
 */

const { TOOLS_DEFINITION, handleToolCall } = require("./lib/mcp-tools");

function startMcpServer() {
  let framingMode = "newline";
  let buffer = Buffer.alloc(0);

  function sendResponse(obj) {
    const payload = JSON.stringify(obj);
    if (framingMode === "content-length") {
      const byteLen = Buffer.byteLength(payload, "utf8");
      process.stdout.write(`Content-Length: ${byteLen}\r\n\r\n${payload}`);
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
            name: "moho",
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
            isError: res && res.ok === false
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
                text: JSON.stringify(
                  { ok: false, error: String(err && err.message ? err.message : err) },
                  null,
                  2
                )
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
          message: `Method not found: ${method}`
        }
      });
    }
  }

  function processBuffer() {
    while (buffer.length > 0) {
      const preview = buffer.slice(0, Math.min(buffer.length, 64)).toString("utf8");
      const trimmedPreview = preview.replace(/^[\r\n\s]+/, "");
      if (trimmedPreview.length === 0) {
        buffer = buffer.slice(Buffer.byteLength(preview, "utf8"));
        continue;
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
  startMcpServer,
  TOOLS_DEFINITION,
  handleToolCall
};
