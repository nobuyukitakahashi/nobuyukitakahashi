#!/usr/bin/env bash
set -euo pipefail
export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"

echo "=== [1/6] Detecting Workspace & Google Drive Paths (macOS) ==="
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_ROOT="$(cd "$SCRIPT_DIR/../../../.." && pwd)"
DRIVE_ROOT="$(cd "$WORKSPACE_ROOT/../.." && pwd)"
OBSIDIAN_VAULT_PATH="$DRIVE_ROOT/obsidian/nobuyukitakahashi/nobuyukitakahashi"

echo "  Workspace : $WORKSPACE_ROOT"
echo "  DriveRoot : $DRIVE_ROOT"
echo "  VaultPath : $OBSIDIAN_VAULT_PATH"

echo ""
echo "=== [2/5] Syncing Latest GitHub Repository (git pull) ==="
pushd "$WORKSPACE_ROOT" > /dev/null
git pull origin main --ff-only || echo "  [WARN] git pull skipped"
popd > /dev/null

echo ""
echo "=== [3/5] Syncing Global Skills (~/.gemini/config/skills) ==="
GLOBAL_SKILLS_DIR="$HOME/.gemini/config/skills"
mkdir -p "$GLOBAL_SKILLS_DIR"

SKILLS_TO_SYNC=(
  "obsidian-markdown"
  "obsidian-bases"
  "obsidian-cli"
  "json-canvas"
  "defuddle"
  "knap"
  "audio-meeting-minutes"
  "auto-git-sync"
  "wordpress-avada-maintenance"
  "pc-env-sync"
)

for skill in "${SKILLS_TO_SYNC[@]}"; do
  src="$WORKSPACE_ROOT/.agents/skills/$skill"
  if [ -d "$src" ]; then
    cp -R "$src" "$GLOBAL_SKILLS_DIR/"
    echo "  [OK] Synced skill: $skill"
  fi
done

echo ""
echo "=== [4/7] Verifying DaVinci Resolve MCP (davinci-resolve-mcp) ==="
DAVINCI_MCP_DIR="$HOME/.gemini/mcp-servers/davinci-resolve-mcp"
mkdir -p "$HOME/.gemini/mcp-servers"
if [ ! -d "$DAVINCI_MCP_DIR" ]; then
  echo "  Cloning davinci-resolve-mcp..."
  git clone https://github.com/samuelgursky/davinci-resolve-mcp.git "$DAVINCI_MCP_DIR"
fi
if [ ! -f "$DAVINCI_MCP_DIR/venv/bin/python" ]; then
  echo "  Setting up Python 3.12 venv for davinci-resolve-mcp..."
  /opt/homebrew/bin/uv venv "$DAVINCI_MCP_DIR/venv" --python 3.12
  /opt/homebrew/bin/uv pip install --python "$DAVINCI_MCP_DIR/venv/bin/python" -r "$DAVINCI_MCP_DIR/requirements.txt"
else
  echo "  [OK] davinci-resolve-mcp venv ready: $DAVINCI_MCP_DIR/venv/bin/python"
fi

echo ""
echo "=== [5/7] Verifying Blender MCP (blender-mcp) ==="
BLENDER_MCP_DIR="$HOME/.gemini/mcp-servers/blender-mcp"
if [ ! -d "$BLENDER_MCP_DIR" ]; then
  echo "  Cloning blender-mcp..."
  git clone https://github.com/ahujasid/blender-mcp.git "$BLENDER_MCP_DIR"
fi
if [ ! -f "$BLENDER_MCP_DIR/venv/bin/mcp-for-blender" ]; then
  echo "  Setting up Python 3.12 venv for blender-mcp..."
  /opt/homebrew/bin/uv venv "$BLENDER_MCP_DIR/venv" --python 3.12
  /opt/homebrew/bin/uv pip install --python "$BLENDER_MCP_DIR/venv/bin/python" -e "$BLENDER_MCP_DIR"
  "$BLENDER_MCP_DIR/venv/bin/mcp-for-blender" setup --yes || true
else
  echo "  [OK] blender-mcp venv ready: $BLENDER_MCP_DIR/venv/bin/mcp-for-blender"
fi

echo ""
echo "=== [6/7] Verifying Obsidian MCP (@bitbonsai/mcpvault) & NotebookLM MCP ==="
NPM_GLOBAL_MODULES="$(npm root -g)"
MCP_VAULT_SCRIPT="$NPM_GLOBAL_MODULES/@bitbonsai/mcpvault/dist/server.js"
NOTEBOOKLM_SCRIPT="$NPM_GLOBAL_MODULES/notebooklm-mcp/dist/index.js"
NODE_BIN="$(command -v node)"

if [ ! -f "$MCP_VAULT_SCRIPT" ]; then
  echo "  Installing @bitbonsai/mcpvault globally..."
  npm install -g "@bitbonsai/mcpvault"
else
  echo "  [OK] @bitbonsai/mcpvault already installed: $MCP_VAULT_SCRIPT"
fi

if [ ! -f "$NOTEBOOKLM_SCRIPT" ]; then
  echo "  Installing notebooklm-mcp globally..."
  npm install -g "notebooklm-mcp"
else
  echo "  [OK] notebooklm-mcp already installed: $NOTEBOOKLM_SCRIPT"
fi

MCP_CONFIG_PATHS=(
  "$HOME/.gemini/config/mcp_config.json"
  "$HOME/.gemini/antigravity/mcp_config.json"
)

for cfg_path in "${MCP_CONFIG_PATHS[@]}"; do
  mkdir -p "$(dirname "$cfg_path")"
  "$NODE_BIN" -e '
    const fs = require("fs");
    const cfgPath = process.argv[1];
    const nodeBin = process.argv[2];
    const vaultScript = process.argv[3];
    const vaultPath = process.argv[4];
    const nlmScript = process.argv[5];
    const davinciDir = process.argv[6];
    const blenderDir = process.argv[7];

    let json = { mcpServers: {} };
    if (fs.existsSync(cfgPath) && fs.readFileSync(cfgPath, "utf8").trim().length > 0) {
      try { json = JSON.parse(fs.readFileSync(cfgPath, "utf8")); } catch (e) {}
    }
    if (!json.mcpServers) json.mcpServers = {};

    json.mcpServers["obsidian"] = {
      command: nodeBin,
      args: [vaultScript, vaultPath]
    };
    json.mcpServers["notebooklm-research"] = {
      command: nodeBin,
      args: [nlmScript]
    };
    json.mcpServers["davinci-resolve"] = {
      command: davinciDir + "/venv/bin/python",
      args: [davinciDir + "/src/server.py"],
      env: {
        RESOLVE_SCRIPT_API: "/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting",
        RESOLVE_SCRIPT_LIB: "/Applications/DaVinci Resolve/DaVinci Resolve.app/Contents/Libraries/Fusion/fusionscript.so",
        PYTHONPATH: "/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting/Modules"
      }
    };
    json.mcpServers["blender"] = {
      command: blenderDir + "/venv/bin/mcp-for-blender",
      args: []
    };

    fs.writeFileSync(cfgPath, JSON.stringify(json, null, 2) + "\n", "utf8");
  ' "$cfg_path" "$NODE_BIN" "$MCP_VAULT_SCRIPT" "$OBSIDIAN_VAULT_PATH" "$NOTEBOOKLM_SCRIPT" "$DAVINCI_MCP_DIR" "$BLENDER_MCP_DIR"
  echo "  [OK] Updated MCP config: $cfg_path"
done

echo ""
echo "=== [7/7] Checking NotebookLM Auth Directory ==="
NOTEBOOKLM_STATE_DIR="$HOME/Library/Application Support/notebooklm-mcp/browser_state"
mkdir -p "$NOTEBOOKLM_STATE_DIR"
NOTEBOOKLM_STATE_FILE="$NOTEBOOKLM_STATE_DIR/state.json"
if [ -f "$NOTEBOOKLM_STATE_FILE" ]; then
  echo "  [OK] NotebookLM state.json exists ($NOTEBOOKLM_STATE_FILE)"
else
  echo "  [INFO] NotebookLM state.json not found on this Mac yet (run setup_auth when needed)"
fi

echo ""
echo "=== Mac Environment Sync Complete ==="
