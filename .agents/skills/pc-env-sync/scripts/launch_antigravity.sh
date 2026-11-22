#!/usr/bin/env bash
set -uo pipefail

TARGET="${1:-ide}"
SKIP_UPDATE="${SKIP_UPDATE:-0}"
SKIP_SYNC="${SKIP_SYNC:-0}"

STATE_DIR="$HOME/Library/Application Support/agy"
mkdir -p "$STATE_DIR"
STAMP_FILE="$STATE_DIR/last_auto_sync.txt"

if [ "$SKIP_UPDATE" != "1" ]; then
  echo "=== [1/3] Checking agy CLI updates ==="
  for bin in "$HOME/.gemini/bin/agy" "$(command -v agy 2>/dev/null || true)"; do
    if [ -n "$bin" ] && [ -x "$bin" ]; then
      echo "  Checking: $bin"
      "$bin" update || true
      break
    fi
  done
fi

if [ "$SKIP_SYNC" != "1" ]; then
  echo ""
  echo "=== [2/3] Running pc-env-sync ==="
  SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  if [ -f "$SCRIPT_DIR/sync_mac_env.sh" ]; then
    bash "$SCRIPT_DIR/sync_mac_env.sh" || true
  fi
fi

date +%s > "$STAMP_FILE"

echo ""
echo "=== [3/3] Launching Antigravity ($TARGET) ==="
launch_app() {
  local app_name="$1"
  if [ -d "/Applications/$app_name" ]; then
    open -a "/Applications/$app_name"
    return 0
  elif [ -d "$HOME/Applications/$app_name" ]; then
    open -a "$HOME/Applications/$app_name"
    return 0
  fi
  return 1
}

if [ "$TARGET" = "app" ]; then
  launch_app "Antigravity.app" || launch_app "Antigravity IDE.app" || { echo "Antigravity app not found." >&2; exit 1; }
else
  launch_app "Antigravity IDE.app" || launch_app "Antigravity.app" || { echo "Antigravity IDE app not found." >&2; exit 1; }
fi
