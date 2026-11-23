#!/usr/bin/env node
/**
 * Gemini Notebook Official API CLI Bridge
 *
 * Allows direct terminal invocation of all Gemini Notebook MCP tools and
 * interactive OAuth 2.0 Desktop Client setup/login with automatic token refresh.
 *
 * Usage:
 *   node .agents/mcp/gemini-notebook-mcp/cli.js status [--live]
 *   node .agents/mcp/gemini-notebook-mcp/cli.js auth-setup --client-secret <client_secret.json> --project <GCP_PROJECT_ID>
 *   node .agents/mcp/gemini-notebook-mcp/cli.js login [--project <GCP_PROJECT_ID>] [--port 0] [--no-open]
 *   node .agents/mcp/gemini-notebook-mcp/cli.js notebooks-list [--page-size 50] [--all]
 *   node .agents/mcp/gemini-notebook-mcp/cli.js notebook-get --name <notebooks/...>
 *   node .agents/mcp/gemini-notebook-mcp/cli.js notebook-create --name <display_name>
 *   node .agents/mcp/gemini-notebook-mcp/cli.js notebook-rename --notebook <notebooks/...> --name <new_display_name>
 *   node .agents/mcp/gemini-notebook-mcp/cli.js sources-list --notebook <notebooks/...> [--page-size 50] [--all]
 *   node .agents/mcp/gemini-notebook-mcp/cli.js source-get --name <notebooks/.../sources/...> [--notebook <notebooks/...>]
 *   node .agents/mcp/gemini-notebook-mcp/cli.js add-web --notebook <notebooks/...> --url <https://...> [--title <name>] [--wait]
 *   node .agents/mcp/gemini-notebook-mcp/cli.js add-text --notebook <notebooks/...> --title <name> (--text <str> | --file <path>) [--mime text/markdown] [--wait]
 *   node .agents/mcp/gemini-notebook-mcp/cli.js upload-file --notebook <notebooks/...> --file <path> [--title <name>] [--mime <mime>] [--wait]
 */

const {
  saveOAuthClientConfig,
  runOAuthLoginFlow,
  getGeminiNotebookStatus,
  listNotebooks,
  getNotebook,
  createNotebook,
  renameNotebook,
  listSources,
  getSource,
  addWebSource,
  addTextSource,
  uploadFileSource
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

function parseBool(val, defaultVal = false) {
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
  console.log(`Gemini Notebook Official API CLI Bridge
Usage:
  node .agents/mcp/gemini-notebook-mcp/cli.js status [--live]
  node .agents/mcp/gemini-notebook-mcp/cli.js auth-setup --client-secret <client_secret.json> --project <GCP_PROJECT_ID>
  node .agents/mcp/gemini-notebook-mcp/cli.js login [--project <GCP_PROJECT_ID>] [--port 0] [--no-open]
  node .agents/mcp/gemini-notebook-mcp/cli.js notebooks-list [--page-size 50] [--page-token <tok>] [--all]
  node .agents/mcp/gemini-notebook-mcp/cli.js notebook-get --name <notebooks/...>
  node .agents/mcp/gemini-notebook-mcp/cli.js notebook-create --name <display_name>
  node .agents/mcp/gemini-notebook-mcp/cli.js notebook-rename --notebook <notebooks/...> --name <new_display_name>
  node .agents/mcp/gemini-notebook-mcp/cli.js sources-list --notebook <notebooks/...> [--page-size 50] [--page-token <tok>] [--all]
  node .agents/mcp/gemini-notebook-mcp/cli.js source-get --name <notebooks/.../sources/...> [--notebook <notebooks/...>]
  node .agents/mcp/gemini-notebook-mcp/cli.js add-web --notebook <notebooks/...> --url <https://...> [--title <name>] [--wait] [--timeout 60]
  node .agents/mcp/gemini-notebook-mcp/cli.js add-text --notebook <notebooks/...> --title <name> (--text <str> | --file <path>) [--mime text/markdown] [--wait]
  node .agents/mcp/gemini-notebook-mcp/cli.js upload-file --notebook <notebooks/...> --file <path> [--title <name>] [--mime <mime>] [--wait]`);
}

async function main() {
  const parsed = parseArgs(process.argv.slice(2));
  const subcmd = parsed._[0];

  if (!subcmd || subcmd === "help" || parsed.help) {
    printUsage();
    process.exit(0);
  }

  let res;
  switch (subcmd) {
    case "status":
      res = await getGeminiNotebookStatus({
        live_check: parseBool(parsed.live || parsed["live-check"], false)
      });
      break;

    case "auth-setup":
      res = saveOAuthClientConfig({
        client_secret_path: parsed["client-secret"] || parsed.file || parsed._[1],
        client_id: parsed["client-id"],
        client_secret: parsed.secret,
        project_id: parsed.project || parsed["project-id"]
      });
      break;

    case "login":
      res = await runOAuthLoginFlow({
        project_id: parsed.project || parsed["project-id"],
        port: parseNum(parsed.port) || 0,
        open_browser: !parseBool(parsed["no-open"], false),
        timeout_ms: (parseNum(parsed.timeout) || 180) * 1000
      });
      break;

    case "notebooks-list":
      res = await listNotebooks({
        page_size: parseNum(parsed["page-size"]),
        page_token: parsed["page-token"],
        fetch_all: parseBool(parsed.all || parsed["fetch-all"], false)
      });
      break;

    case "notebook-get":
      res = await getNotebook({
        notebook_name: parsed.name || parsed.notebook || parsed._[1]
      });
      break;

    case "notebook-create":
      res = await createNotebook({
        display_name: parsed.name || parsed.title || parsed._[1]
      });
      break;

    case "notebook-rename":
      res = await renameNotebook({
        notebook_name: parsed.notebook || parsed.target,
        display_name: parsed.name || parsed.title || parsed["new-name"]
      });
      break;

    case "sources-list":
      res = await listSources({
        notebook_name: parsed.notebook || parsed.parent || parsed._[1],
        page_size: parseNum(parsed["page-size"]),
        page_token: parsed["page-token"],
        fetch_all: parseBool(parsed.all || parsed["fetch-all"], false)
      });
      break;

    case "source-get":
      res = await getSource({
        source_name: parsed.name || parsed.source || parsed._[1],
        notebook_name: parsed.notebook
      });
      break;

    case "add-web":
      res = await addWebSource({
        notebook_name: parsed.notebook || parsed.parent,
        url: parsed.url || parsed._[1],
        display_name: parsed.title || parsed.name,
        wait_until_active: parseBool(parsed.wait, false),
        timeout_seconds: parseNum(parsed.timeout)
      });
      break;

    case "add-text":
      res = await addTextSource({
        notebook_name: parsed.notebook || parsed.parent,
        display_name: parsed.title || parsed.name,
        content: parsed.text || parsed.content,
        file_path: parsed.file,
        mime_type: parsed.mime || parsed["mime-type"],
        wait_until_active: parseBool(parsed.wait, false),
        timeout_seconds: parseNum(parsed.timeout)
      });
      break;

    case "upload-file":
      res = await uploadFileSource({
        notebook_name: parsed.notebook || parsed.parent,
        file_path: parsed.file || parsed._[1],
        display_name: parsed.title || parsed.name,
        mime_type: parsed.mime || parsed["mime-type"],
        wait_until_active: parseBool(parsed.wait, false),
        timeout_seconds: parseNum(parsed.timeout)
      });
      break;

    default:
      console.error(`Unknown subcommand: ${subcmd}`);
      printUsage();
      process.exit(1);
  }

  console.log(JSON.stringify(res, null, 2));
  if (res && res.ok === false) {
    process.exit(1);
  }
}

main().catch((err) => {
  console.error(JSON.stringify({ ok: false, error: String(err.message || err) }, null, 2));
  process.exit(1);
});
