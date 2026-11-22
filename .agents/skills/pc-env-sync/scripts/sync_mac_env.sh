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
    "$drive_root/obsidian"
    "$drive_root/obsidian/nobuyukitakahashi"
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

for legacy_skill in adobe-illustrator adobe-photoshop adobe-premiere adobe-aftereffects; do
  rm -rf "$GLOBAL_SKILLS_DIR/$legacy_skill"
done

for src in "$WORKSPACE_ROOT/.agents/skills"/*; do
  if [ -d "$src" ] && [ -f "$src/SKILL.md" ]; then
    skill="$(basename "$src")"
    rm -rf "$GLOBAL_SKILLS_DIR/$skill"
    cp -R "$src" "$GLOBAL_SKILLS_DIR/"
    echo "  [OK] Synced skill: $skill"
  fi
done

GLOBAL_PLUGINS_DIR="$HOME/.gemini/config/plugins"
mkdir -p "$GLOBAL_PLUGINS_DIR"
# Remove legacy MCP wrapper plugins and stale schema caches (MCP registration is unified in global mcp_config.json)
rm -rf "$GLOBAL_PLUGINS_DIR/notebooklm-plugin" "$GLOBAL_PLUGINS_DIR/blender-plugin"
rm -rf "$HOME/.gemini/antigravity/mcp/blender-plugin_blender" "$HOME/.gemini/antigravity/mcp/notebooklm-plugin_notebooklm-research"
if [ -d "$WORKSPACE_ROOT/.agents/plugins/global-master-rules" ]; then
  rm -rf "$GLOBAL_PLUGINS_DIR/global-master-rules"
  cp -R "$WORKSPACE_ROOT/.agents/plugins/global-master-rules" "$GLOBAL_PLUGINS_DIR/"
  # Remove legacy duplicate rule copies so global-master-rules is injected only once within the 20k-token rules budget
  rm -f "$HOME/.gemini/config/AGENTS.md" "$HOME/.gemini/config/rules/AGENTS.md"
  echo "  [OK] Synced account-wide master rules (single source: ~/.gemini/config/plugins/global-master-rules/rules/AGENTS.md)"
fi

UV_BIN="$(command -v uv || true)"
UVX_BIN="$(command -v uvx || true)"

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
echo "=== [5/7] Verifying Official Blender Lab MCP (blender-mcp) ==="
if [ -z "$UV_BIN" ]; then
  echo "  [INFO] uv not found; attempting automatic installation..."
  if command -v brew >/dev/null 2>&1; then
    brew install uv || true
  else
    curl -LsSf https://astral.sh/uv/install.sh | sh || true
  fi
  export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:$PATH"
  UV_BIN="$(command -v uv || true)"
  UVX_BIN="$(command -v uvx || true)"
fi

BLENDER_MCP_BIN="$HOME/.local/bin/blender-mcp"
IS_OFFICIAL_BLENDER_MCP=0
if [ -x "$BLENDER_MCP_BIN" ]; then
  if "$BLENDER_MCP_BIN" --help 2>&1 | grep -q "MCP server for Blender" && ! "$BLENDER_MCP_BIN" --help 2>&1 | grep -q "mcp-for-blender"; then
    IS_OFFICIAL_BLENDER_MCP=1
  fi
fi

if [ "$IS_OFFICIAL_BLENDER_MCP" -eq 0 ] && [ -n "$UV_BIN" ]; then
  echo "  Installing official Blender Lab blender-mcp via uv tool (--force)..."
  "$UV_BIN" tool install --force --python 3.12 --from "git+https://projects.blender.org/lab/blender_mcp.git#subdirectory=mcp" blender-mcp
  if [ -x "$BLENDER_MCP_BIN" ] && "$BLENDER_MCP_BIN" --help 2>&1 | grep -q "MCP server for Blender"; then
    IS_OFFICIAL_BLENDER_MCP=1
  fi
fi

if [ "$IS_OFFICIAL_BLENDER_MCP" -eq 1 ]; then
  echo "  [OK] Official Blender Lab blender-mcp ready: $BLENDER_MCP_BIN"
else
  echo "  [INFO] Will use uvx for official Blender Lab blender-mcp: ${UVX_BIN:-uvx}"
fi

DETECTED_BLENDER_BIN=""
for b_cand in \
  "/Applications/Blender.app/Contents/MacOS/Blender" \
  "$HOME/Applications/Blender.app/Contents/MacOS/Blender" \
  "$(command -v blender 2>/dev/null || true)"; do
  if [ -n "$b_cand" ] && [ -x "$b_cand" ]; then
    DETECTED_BLENDER_BIN="$b_cand"
    break
  fi
done
if [ -z "$DETECTED_BLENDER_BIN" ]; then
  DETECTED_BLENDER_BIN="/Applications/Blender.app/Contents/MacOS/Blender"
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
  "$HOME/.gemini/antigravity-obsidian/mcp_config.json"
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
    const isOfficialBlender = process.argv[7] === "1";
    const blenderMcpBin = process.argv[8];
    const uvxBin = process.argv[9] || "uvx";
    const blenderBin = process.argv[10];

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
    json.mcpServers["blender"] = isOfficialBlender
      ? {
          command: blenderMcpBin,
          args: [],
          env: {
            BLENDER_PATH: blenderBin,
            BLENDER_MCP_HOST: "localhost",
            BLENDER_MCP_PORT: "9876"
          }
        }
      : {
          command: uvxBin,
          args: ["--python", "3.12", "--from", "git+https://projects.blender.org/lab/blender_mcp.git#subdirectory=mcp", "blender-mcp"],
          env: {
            BLENDER_PATH: blenderBin,
            BLENDER_MCP_HOST: "localhost",
            BLENDER_MCP_PORT: "9876"
          }
        };
    json.mcpServers["illustrator"] = {
      command: nodeBin,
      args: [process.argv[11]]
    };
    json.mcpServers["photoshop"] = {
      command: nodeBin,
      args: [process.argv[12]]
    };
    json.mcpServers["premiere"] = {
      command: nodeBin,
      args: [process.argv[13]]
    };
    json.mcpServers["aftereffects"] = {
      command: nodeBin,
      args: [process.argv[14]]
    };
    json.mcpServers["ptgui"] = {
      command: nodeBin,
      args: [process.argv[15]]
    };

    fs.writeFileSync(cfgPath, JSON.stringify(json, null, 2) + "\n", "utf8");
  ' "$cfg_path" "$NODE_BIN" "$MCP_VAULT_SCRIPT" "$OBSIDIAN_VAULT_PATH" "$NOTEBOOKLM_SCRIPT" "$DAVINCI_MCP_DIR" "$IS_OFFICIAL_BLENDER_MCP" "$BLENDER_MCP_BIN" "${UVX_BIN:-uvx}" "$DETECTED_BLENDER_BIN" "$WORKSPACE_ROOT/.agents/mcp/illustrator-mcp/server.js" "$WORKSPACE_ROOT/.agents/mcp/photoshop-mcp/server.js" "$WORKSPACE_ROOT/.agents/mcp/premiere-mcp/server.js" "$WORKSPACE_ROOT/.agents/mcp/aftereffects-mcp/server.js" "$WORKSPACE_ROOT/.agents/mcp/ptgui-mcp/server.js"
  echo "  [OK] Updated MCP config: $cfg_path"
done

# Ensure antigravity-obsidian profile trustedWorkspaces and migrate desktop obsidian.json if needed
"$NODE_BIN" -e '
  const fs = require("fs");
  const path = require("path");
  const os = require("os");
  const vaultPath = process.argv[1];
  const profDir = path.join(os.homedir(), ".gemini", "antigravity-obsidian");
  fs.mkdirSync(profDir, { recursive: true });
  const settingsPath = path.join(profDir, "settings.json");
  let settings = {};
  if (fs.existsSync(settingsPath)) {
    try { settings = JSON.parse(fs.readFileSync(settingsPath, "utf8")); } catch (_) {}
  }
  const existing = Array.isArray(settings.trustedWorkspaces) ? settings.trustedWorkspaces : [];
  const cleaned = [];
  for (const tw of existing) {
    if (tw && (!/[\/\\]obsidian[\/\\]nobuyukitakahashi([\/\\]|$)/.test(tw) || fs.existsSync(tw))) {
      if (!cleaned.includes(tw)) cleaned.push(tw);
    }
  }
  if (vaultPath && !cleaned.includes(vaultPath)) cleaned.push(vaultPath);
  settings.trustedWorkspaces = cleaned;
  fs.writeFileSync(settingsPath, JSON.stringify(settings, null, 2) + "\n", "utf8");

  const obsJsonPath = path.join(os.homedir(), "Library", "Application Support", "obsidian", "obsidian.json");
  if (fs.existsSync(obsJsonPath) && vaultPath && fs.existsSync(path.join(vaultPath, ".obsidian"))) {
    try {
      const obs = JSON.parse(fs.readFileSync(obsJsonPath, "utf8"));
      let changed = false;
      if (obs && obs.vaults) {
        for (const key of Object.keys(obs.vaults)) {
          const vp = obs.vaults[key]?.path;
          if (vp && /[\/\\]obsidian[\/\\]nobuyukitakahashi([\/\\]|$)/.test(vp) && !fs.existsSync(vp)) {
            obs.vaults[key].path = vaultPath;
            changed = true;
          }
        }
      }
      if (changed) {
        fs.writeFileSync(obsJsonPath, JSON.stringify(obs), "utf8");
        console.log("  [OK] Migrated Obsidian desktop vault path in " + obsJsonPath + " -> " + vaultPath);
      }
    } catch (_) {}
  }

  const pluginMainJs = path.join(vaultPath, ".obsidian", "plugins", "antigravity", "main.js");
  if (vaultPath && fs.existsSync(pluginMainJs)) {
    const raw = fs.readFileSync(pluginMainJs, "utf8");
    const target = "let P=[\"--hub\",`--hub-port=${y}`,`--app_data_dir=${u}`,`--project=${C}`,`--add-dir=${t}`];o&&P.push(\"--dangerously-skip-permissions\"),r&&P.push(`--agent=${r}`);let k={AGY_ENABLE_HUB:\"1\",...x.formatProxyEnv(c)},D=x.getEnrichedEnv(k),m=(0,Bt.spawn)(e,P,{cwd:t,env:D,stdio:[\"ignore\",\"pipe\",\"pipe\"],detached:process.platform!==\"win32\"});m.pid&&Mt(u,{pid:m.pid,port:y,profile:u,vaultPath:t,dangerouslySkipPermissions:o,startedAt:Date.now()}),this.recentOutput=[];let M=null,";
    if (raw.includes("--csrf_token=")) {
      console.log("  [OK] Obsidian Antigravity plugin already patched (--csrf_token)");
    } else if (raw.includes(target)) {
      const repl = "let B=(St.randomUUID?St.randomUUID():St.randomBytes(16).toString(\"hex\")),P=[\"--hub\",`--hub-port=${y}`,`--app_data_dir=${u}`,`--csrf_token=${B}`,`--project=${C}`,`--add-dir=${t}`];o&&P.push(\"--dangerously-skip-permissions\"),r&&P.push(`--agent=${r}`);let k={AGY_ENABLE_HUB:\"1\",...x.formatProxyEnv(c)},D=x.getEnrichedEnv(k),m=(0,Bt.spawn)(e,P,{cwd:t,env:D,stdio:[\"ignore\",\"pipe\",\"pipe\"],detached:process.platform!==\"win32\"});m.pid&&Mt(u,{pid:m.pid,port:y,profile:u,vaultPath:t,dangerouslySkipPermissions:o,startedAt:Date.now()}),this.recentOutput=[];let M=B,";
      fs.writeFileSync(pluginMainJs, raw.replace(target, repl), "utf8");
      console.log("  [OK] Patched Obsidian Antigravity plugin (--csrf_token) to prevent white screen");
    }
  }
' "$OBSIDIAN_VAULT_PATH"
echo "  [OK] Updated Obsidian plugin trustedWorkspaces: $HOME/.gemini/antigravity-obsidian/settings.json"

if [ -x "$DETECTED_BLENDER_BIN" ]; then
  echo ""
  echo "=== [6.5/7] Verifying Official Blender Lab Add-on (bl_ext.user_default.mcp) ==="
  CHECK_PY="import bpy, addon_utils; d, s = addon_utils.check('bl_ext.user_default.mcp'); ext_dir = bpy.utils.user_resource('EXTENSIONS'); print('BLENDER_MCP_EXT_STATUS:' + str(d) + '|' + str(s) + '|' + str(bpy.context.preferences.system.use_online_access) + '|' + ext_dir)"
  CHECK_OUT="$("$DETECTED_BLENDER_BIN" --background --online-mode --python-expr "$CHECK_PY" 2>&1 || true)"
  STATUS_LINE="$(printf '%s\n' "$CHECK_OUT" | grep 'BLENDER_MCP_EXT_STATUS:' | tail -n 1 || true)"
  EXT_INSTALLED=0
  EXT_ENABLED=0
  ONLINE_ENABLED=0
  if [ -n "$STATUS_LINE" ]; then
    VALS="${STATUS_LINE#BLENDER_MCP_EXT_STATUS:}"
    IFS='|' read -r D_VAL S_VAL O_VAL EXT_BASE <<< "$VALS"
    [ "$D_VAL" = "True" ] && EXT_ENABLED=1
    [ "$O_VAL" = "True" ] && ONLINE_ENABLED=1
    MANIFEST="$EXT_BASE/user_default/mcp/blender_manifest.toml"
    if [ -f "$MANIFEST" ] && grep -q 'maintainer *= *"Blender Lab"' "$MANIFEST"; then
      EXT_INSTALLED=1
    fi
  fi
  if [ "$EXT_INSTALLED" -eq 0 ]; then
    echo "  Installing official Blender Lab MCP add-on into Blender..."
    TMP_DIR="$(mktemp -d)"
    git clone --depth 1 https://projects.blender.org/lab/blender_mcp.git "$TMP_DIR/repo"
    "$DETECTED_BLENDER_BIN" --command extension build --source-dir "$TMP_DIR/repo/addon/blender_mcp_addon" --output-filepath "$TMP_DIR/mcp.zip"
    "$DETECTED_BLENDER_BIN" --command extension install-file -r user_default -e "$TMP_DIR/mcp.zip"
    rm -rf "$TMP_DIR"
    EXT_INSTALLED=1
  fi
  if [ "$EXT_INSTALLED" -eq 1 ] && { [ "$EXT_ENABLED" -eq 0 ] || [ "$ONLINE_ENABLED" -eq 0 ]; }; then
    echo "  Enabling Blender Online Access and bl_ext.user_default.mcp auto-start..."
    "$DETECTED_BLENDER_BIN" --background --online-mode --python-expr "import bpy; bpy.context.preferences.system.use_online_access = True; bpy.ops.preferences.addon_enable(module='bl_ext.user_default.mcp'); p = bpy.context.preferences.addons['bl_ext.user_default.mcp'].preferences; p.host = 'localhost'; p.port = 9876; p.use_autostart = True; bpy.ops.wm.save_userpref()"
  elif [ "$EXT_INSTALLED" -eq 1 ]; then
    echo "  [OK] Official Blender Lab MCP add-on enabled with Online Access ($DETECTED_BLENDER_BIN)"
  fi
fi

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
echo "=== [7.5/7] Configuring SessionStart Hook & Auto-Sync Launchers ==="
GLOBAL_SCRIPTS_DIR="$HOME/.gemini/config/skills/pc-env-sync/scripts"
if [ -d "$GLOBAL_SCRIPTS_DIR" ]; then
  chmod +x "$GLOBAL_SCRIPTS_DIR/"*.sh 2>/dev/null || true
fi

HOOKS_JSON="$HOME/.gemini/config/hooks.json"
SESSION_HOOK_SH="$GLOBAL_SCRIPTS_DIR/session_start_sync.sh"
if command -v node >/dev/null 2>&1; then
  node -e '
    const fs = require("fs");
    const hooksPath = process.argv[1];
    const hookScript = process.argv[2];
    let obj = {};
    if (fs.existsSync(hooksPath)) {
      try { obj = JSON.parse(fs.readFileSync(hooksPath, "utf8")) || {}; } catch (_) { obj = {}; }
    }
    obj["pc-env-sync"] = {
      SessionStart: [
        {
          type: "command",
          command: `bash "${hookScript}"`,
          timeout: 15
        }
      ]
    };
    fs.writeFileSync(hooksPath, JSON.stringify(obj, null, 2) + "\n", "utf8");
  ' "$HOOKS_JSON" "$SESSION_HOOK_SH"
  echo "  [OK] Registered SessionStart hook in: $HOOKS_JSON"
fi

LAUNCH_SH="$GLOBAL_SCRIPTS_DIR/launch_antigravity.sh"
DESKTOP_DIR="$HOME/Desktop"
if [ -d "$DESKTOP_DIR" ]; then
  if [ -d "/Applications/Antigravity IDE.app" ] || [ -d "$HOME/Applications/Antigravity IDE.app" ]; then
    CMD_IDE="$DESKTOP_DIR/Antigravity IDE (Auto Sync).command"
    printf '#!/usr/bin/env bash\nbash "%s" ide\n' "$LAUNCH_SH" > "$CMD_IDE"
    chmod +x "$CMD_IDE"
    echo "  [OK] Created launcher: $CMD_IDE"
  fi
  if [ -d "/Applications/Antigravity.app" ] || [ -d "$HOME/Applications/Antigravity.app" ]; then
    CMD_APP="$DESKTOP_DIR/Antigravity (Auto Sync).command"
    printf '#!/usr/bin/env bash\nbash "%s" app\n' "$LAUNCH_SH" > "$CMD_APP"
    chmod +x "$CMD_APP"
    echo "  [OK] Created launcher: $CMD_APP"
  fi
fi

echo ""
echo "=== Mac Environment Sync Complete (Reload Antigravity if MCP config was updated) ==="
