#!/usr/bin/env node
/**
 * Antigravity Lifecycle Hook: Organization Governance Guard (Cross-Platform)
 * Enforces:
 * 1. Single-source editing: blocks direct writes to ~/.gemini/config/(skills|rules|plugins/global-master-rules)/
 * 2. Delivery subfolder discipline: blocks direct file placement under 04_Delivery_Dept/outputs/<genre>/<file>
 * 3. Rule size guardrail: prompts before writing >24,000 bytes to AGENTS.md or SKILL.md
 */
"use strict";

const path = require("path");

function normalizePath(p) {
  return String(p || "").replace(/\\/g, "/");
}

function respond(obj) {
  process.stdout.write(JSON.stringify(obj) + "\n");
}

let raw = "";
process.stdin.setEncoding("utf8");
process.stdin.on("data", (chunk) => {
  raw += chunk;
});

process.stdin.on("end", () => {
  try {
    if (!raw.trim()) {
      return respond({ decision: "allow" });
    }
    const payload = JSON.parse(raw);
    const toolCall = payload.toolCall || {};
    const toolName = String(toolCall.name || "");
    const args = toolCall.args || {};

    if (toolName !== "write_file" && toolName !== "edit_file") {
      return respond({ decision: "allow" });
    }

    const targetPath = normalizePath(args.Path || args.path || "");
    if (!targetPath) {
      return respond({ decision: "allow" });
    }

    // 1. Block direct edits to synced ~/.gemini/config copies
    if (/\/\.gemini\/config\/(skills|rules|plugins\/global-master-rules)\//i.test(targetPath)) {
      return respond({
        decision: "deny",
        reason:
          "単一ソース原則違反: ~/.gemini/config/ 配下の同期コピーは直接編集禁止です。nobuyukitakahashi/.agents/ 原本を編集し、sync_pc_env.ps1 / sync_mac_env.sh で同期してください。",
      });
    }

    // 2. Block direct file placement directly under 04_Delivery_Dept/outputs/<genre>/<file>
    const deliveryMatch = targetPath.match(/04_Delivery_Dept\/outputs\/([^/]+)\/([^/]+)$/i);
    if (deliveryMatch) {
      const fileName = deliveryMatch[2];
      if (fileName !== ".gitkeep" && fileName !== "INDEX.md") {
        return respond({
          decision: "deny",
          reason:
            "納品サブフォルダ規約違反: 04_Delivery_Dept/outputs/<genre>/ 直下へのファイル配置は禁止です。必ず <案件サブフォルダ>/ 配下（例: 04_Delivery_Dept/outputs/" +
            deliveryMatch[1] +
            "/<案件サブフォルダ>/" +
            fileName +
            "）へ格納してください。",
        });
      }
    }

    // 3. Warn if writing > 24,000 bytes into AGENTS.md or SKILL.md
    const baseName = path.posix.basename(targetPath);
    if (toolName === "write_file" && (baseName === "AGENTS.md" || baseName === "SKILL.md")) {
      const content = typeof args.Content === "string" ? args.Content : "";
      const byteLen = Buffer.byteLength(content, "utf8");
      if (byteLen > 24000) {
        return respond({
          decision: "ask",
          reason:
            baseName +
            " が 24,000 バイト上限を超過しています (" +
            byteLen +
            " B)。切り捨て防止のため references/ への分離を検討してください。",
        });
      }
    }

    return respond({ decision: "allow" });
  } catch (_) {
    // Fail-safe: never break tool execution on unexpected payload
    return respond({ decision: "allow" });
  }
});
