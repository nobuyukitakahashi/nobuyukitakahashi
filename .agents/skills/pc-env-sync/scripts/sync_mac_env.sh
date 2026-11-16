#!/usr/bin/env bash
set -euo pipefail
export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:$PATH"

EXPLICIT_WORKSPACE=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --workspace)
      EXPLICIT_WORKSPACE="${2:-}"
      shift 2
      ;;
    *)
      shift
      ;;
  esac
done

is_agy_workspace() {
  local dir="$1"
  [[ -n "$dir" && -f "$dir/.agents/skills/pc-env-sync/SKILL.md" ]]
}

resolve_workspace_root() {
  if [[ -n "$EXPLICIT_WORKSPACE" ]] && is_agy_workspace "$EXPLICIT_WORKSPACE"; then
    (cd "$EXPLICIT_WORKSPACE" && pwd)
    return 0
  fi
  if [[ -n "${AGY_WORKSPACE_ROOT:-}" ]] && is_agy_workspace "$AGY_WORKSPACE_ROOT"; then
    (cd "$AGY_WORKSPACE_ROOT" && pwd)
    return 0
  fi

  local script_dir script_candidate
  script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  script_candidate="$(cd "$script_dir/../../../.." 2>/dev/null && pwd || true)"
  if is_agy_workspace "$script_candidate" && [[ -d "$script_candidate/.git" ]]; then
    echo "$script_candidate"
    return 0
  fi

  local cur="$PWD"
  while [[ -n "$cur" && "$cur" != "/" ]]; do
    if is_agy_workspace "$cur"; then
      echo "$cur"
      return 0
    fi
    cur="$(dirname "$cur")"
  done

  if command -v node >/dev/null 2>&1; then
    local cfg_extracted
    cfg_extracted="$(node -e '
      const fs = require("fs");
      const path = require("path");
      const os = require("os");
      const files = [
        path.join(os.homedir(), ".gemini/antigravity/mcp_config.json"),
        path.join(os.homedir(), ".gemini/config/mcp_config.json")
      ];
      for (const f of files) {
        if (!fs.existsSync(f)) continue;
        try {
          const j = JSON.parse(fs.readFileSync(f, "utf8"));
          for (const v of Object.values(j.mcpServers || {})) {
            for (const a of (v.args || [])) {
              if (typeof a === "string") {
                const m = a.match(/^(.+?)\/\.agents\/mcp\//);
                if (m && fs.existsSync(path.join(m[1], ".agents/skills/pc-env-sync/SKILL.md"))) {
                  console.log(m[1]);
                  process.exit(0);
                }
              }
            }
          }
        } catch (_) {}
      }
    ' 2>/dev/null || true)"
    if is_agy_workspace "$cfg_extracted"; then
      echo "$cfg_extracted"
      return 0
    fi
  fi

  local patterns=(
    "$HOME/Library/CloudStorage"/GoogleDrive-*/*/git/nobuyukitakahashi
    "$HOME/Library/CloudStorage"/GoogleDrive-*/*/nobuyukitakahashi
    "$HOME/Google Drive"/*/git/nobuyukitakahashi
    "$HOME/git/nobuyukitakahashi"
    "$HOME/nobuyukitakahashi"
    /Volumes/*/git/nobuyukitakahashi
    /Volumes/*/*/git/nobuyukitakahashi
  )
  local cand
  for cand in "${patterns[@]}"; do
    if is_agy_workspace "$cand"; then
      (cd "$cand" && pwd)
      return 0
    fi
  done

  echo "[ERROR] Could not locate 'nobuyukitakahashi' workspace. Pass --workspace <path> or run inside the repository." >&2
  return 1
}

resolve_obsidian_vault() {
  local drive_root="$1"
  local candidates=(
    "$drive_root/obsidian/nobuyukitakahashi/nobuyukitakahashi"
    "$drive_root/obsidian"
  )
  local c
  for c in "${candidates[@]}"; do
    if [[ -d "$c/.obsidian" ]]; then
      echo "$c"
      return 0
    fi
  done

  if command -v node >/dev/null 2>&1; then
    local existing_vault
    existing_vault="$(node -e '
      const fs = require("fs");
      const path = require("path");
      const os = require("os");
      const files = [
        path.join(os.homedir(), ".gemini/antigravity/mcp_config.json"),
        path.join(os.homedir(), ".gemini/config/mcp_config.json")
      ];
      for (const f of files) {
        if (!fs.existsSync(f)) continue;
        try {
          const j = JSON.parse(fs.readFileSync(f, "utf8"));
          const v = j?.mcpServers?.obsidian?.args?.[1];
          if (v && fs.existsSync(path.join(v, ".obsidian"))) {
            console.log(v);
            process.exit(0);
          }
        } catch (_) {}
      }
    ' 2>/dev/null || true)"
    if [[ -n "$existing_vault" ]]; then
      echo "$existing_vault"
      return 0
    fi
  fi

  for c in "${candidates[@]}"; do
    if [[ -d "$c" ]]; then
      echo "$c"
      return 0
    fi
  done
  echo "${candidates[0]}"
}

echo "=== [1/7] Detecting Workspace, Tools & Google Drive Paths (macOS) ==="
for cmd in git node npm; do
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "[ERROR] Required command '$cmd' not found in PATH." >&2
    exit 1
  fi
done

WORKSPACE_ROOT="$(resolve_workspace_root)"
DRIVE_ROOT="$(cd "$WORKSPACE_ROOT/../.." && pwd)"
OBSIDIAN_VAULT_PATH="$(resolve_obsidian_vault "$DRIVE_ROOT")"

echo "  Workspace : $WORKSPACE_ROOT"
echo "  DriveRoot : $DRIVE_ROOT"
echo "  VaultPath : $OBSIDIAN_VAULT_PATH"
if [[ ! -d "$OBSIDIAN_VAULT_PATH/.obsidian" ]]; then
  echo "  [WARN] .obsidian directory not found at VaultPath yet (Google Drive sync may still be in progress)"
fi

if [[ -z "$(git config --global user.name 2>/dev/null || true)" ]]; then
  git config --global user.name "nobuyukitakahashi"
fi
if [[ -z "$(git config --global user.email 2>/dev/null || true)" ]]; then
  git config --global user.email "nobuyukitakahashi@outlook.com"
fi
git config --global core.quotepath false
git config --global init.defaultBranch main
git config --global --replace-all safe.directory "*"

SSH_VAULT_FILE="$DRIVE_ROOT/_private_backup/ssh/ssh_keys_latest.agyvault"
SSH_VAULT_SCRIPT="$WORKSPACE_ROOT/.agents/skills/pc-env-sync/scripts/ssh_vault.js"
if [[ ! -f "$HOME/.ssh/id_ed25519" ]]; then
  if [[ -f "$SSH_VAULT_FILE" && -f "$SSH_VAULT_SCRIPT" ]]; then
    echo "  [INFO] ~/.ssh/id_ed25519 not found, but encrypted SSH backup exists:"
    echo "         $SSH_VAULT_FILE"
    echo "         To restore all SSH keys, run in your terminal:"
    echo "         node \"$SSH_VAULT_SCRIPT\" restore"
  else
    echo "  [INFO] ~/.ssh/id_ed25519 not found on this Mac (copy keys or run ssh_vault.js restore if backed up)"
  fi
fi

echo ""
echo "=== [2/7] Syncing Latest GitHub Repository (git pull) ==="
pushd "$WORKSPACE_ROOT" > /dev/null
git pull origin main --ff-only || echo "  [WARN] git pull skipped"
popd > /dev/null

echo ""
echo "=== [3/7] Syncing Global Skills (~/.gemini/config/skills) ==="
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
  "adobe-illustrator"
  "adobe-photoshop"
  "adobe-premiere"
  "adobe-aftereffects"
  "blender"
  "illustrator"
  "photoshop"
  "premiere"
  "aftereffects"
  "davinci"
  "pano2vr"
  "krpano"
  "ptgui"
  "writing"
  "pc-env-sync"
)

for skill in "${SKILLS_TO_SYNC[@]}"; do
  src="$WORKSPACE_ROOT/.agents/skills/$skill"
  if [ -d "$src" ]; then
    rm -rf "$GLOBAL_SKILLS_DIR/$skill"
    cp -R "$src" "$GLOBAL_SKILLS_DIR/"
    echo "  [OK] Synced skill: $skill"
  fi
done

GLOBAL_PLUGINS_DIR="$HOME/.gemini/config/plugins"
mkdir -p "$GLOBAL_PLUGINS_DIR"
if [ -d "$WORKSPACE_ROOT/.agents/plugins/notebooklm-plugin" ]; then
  rm -rf "$GLOBAL_PLUGINS_DIR/notebooklm-plugin"
  cp -R "$WORKSPACE_ROOT/.agents/plugins/notebooklm-plugin" "$GLOBAL_PLUGINS_DIR/"
  echo "  [OK] Synced global plugin: notebooklm-plugin"
fi
if [ -d "$WORKSPACE_ROOT/.agents/plugins/global-master-rules" ]; then
  rm -rf "$GLOBAL_PLUGINS_DIR/global-master-rules"
  cp -R "$WORKSPACE_ROOT/.agents/plugins/global-master-rules" "$GLOBAL_PLUGINS_DIR/"
  mkdir -p "$HOME/.gemini/config/rules"
  cp "$WORKSPACE_ROOT/.agents/plugins/global-master-rules/rules/AGENTS.md" "$HOME/.gemini/config/AGENTS.md"
  cp "$WORKSPACE_ROOT/.agents/plugins/global-master-rules/rules/AGENTS.md" "$HOME/.gemini/config/rules/AGENTS.md"
  echo "  [OK] Synced account-wide master rules (~/.gemini/config/rules/AGENTS.md & plugin)"
fi

UV_BIN="$(command -v uv || true)"

echo ""
echo "=== [4/7] Verifying DaVinci Resolve MCP (davinci-resolve-mcp) ==="
DAVINCI_MCP_DIR="$HOME/.gemini/mcp-servers/davinci-resolve-mcp"
mkdir -p "$HOME/.gemini/mcp-servers"
if [ ! -d "$DAVINCI_MCP_DIR" ]; then
  echo "  Cloning davinci-resolve-mcp..."
  git clone https://github.com/samuelgursky/davinci-resolve-mcp.git "$DAVINCI_MCP_DIR"
fi
if [ ! -f "$DAVINCI_MCP_DIR/venv/bin/python" ]; then
  if [ -n "$UV_BIN" ]; then
    echo "  Setting up Python 3.12 venv for davinci-resolve-mcp..."
    "$UV_BIN" venv "$DAVINCI_MCP_DIR/venv" --python 3.12
    "$UV_BIN" pip install --python "$DAVINCI_MCP_DIR/venv/bin/python" -r "$DAVINCI_MCP_DIR/requirements.txt"
  else
    echo "  [WARN] uv not found; skipping davinci-resolve-mcp venv setup"
  fi
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
  if [ -n "$UV_BIN" ]; then
    echo "  Setting up Python 3.12 venv for blender-mcp..."
    "$UV_BIN" venv "$BLENDER_MCP_DIR/venv" --python 3.12
    "$UV_BIN" pip install --python "$BLENDER_MCP_DIR/venv/bin/python" -e "$BLENDER_MCP_DIR"
    "$BLENDER_MCP_DIR/venv/bin/mcp-for-blender" setup --yes || true
  else
    echo "  [WARN] uv not found; skipping blender-mcp venv setup"
  fi
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
    json.mcpServers["illustrator"] = {
      command: nodeBin,
      args: [process.argv[8]]
    };
    json.mcpServers["photoshop"] = {
      command: nodeBin,
      args: [process.argv[9]]
    };
    json.mcpServers["premiere"] = {
      command: nodeBin,
      args: [process.argv[10]]
    };
    json.mcpServers["aftereffects"] = {
      command: nodeBin,
      args: [process.argv[11]]
    };
    json.mcpServers["ptgui"] = {
      command: nodeBin,
      args: [process.argv[12]]
    };

    fs.writeFileSync(cfgPath, JSON.stringify(json, null, 2) + "\n", "utf8");
  ' "$cfg_path" "$NODE_BIN" "$MCP_VAULT_SCRIPT" "$OBSIDIAN_VAULT_PATH" "$NOTEBOOKLM_SCRIPT" "$DAVINCI_MCP_DIR" "$BLENDER_MCP_DIR" "$WORKSPACE_ROOT/.agents/mcp/illustrator-mcp/server.js" "$WORKSPACE_ROOT/.agents/mcp/photoshop-mcp/server.js" "$WORKSPACE_ROOT/.agents/mcp/premiere-mcp/server.js" "$WORKSPACE_ROOT/.agents/mcp/aftereffects-mcp/server.js" "$WORKSPACE_ROOT/.agents/mcp/ptgui-mcp/server.js"
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
echo "=== Mac Environment Sync Complete (Reload Antigravity if MCP config was updated) ==="
