#!/usr/bin/env bash
set -uo pipefail

COOLDOWN_SEC="${COOLDOWN_SEC:-21600}"

# Drain stdin JSON required by Antigravity hook contract
cat >/dev/null 2>&1 || true

STATE_DIR="$HOME/Library/Application Support/agy"
mkdir -p "$STATE_DIR"
STAMP_FILE="$STATE_DIR/last_auto_sync.txt"
LOG_FILE="$STATE_DIR/auto_sync.log"

NOW_EPOCH="$(date +%s)"
SHOULD_RUN=1
if [ -f "$STAMP_FILE" ]; then
  LAST_RAW="$(cat "$STAMP_FILE" 2>/dev/null || echo 0)"
  if [[ "$LAST_RAW" =~ ^[0-9]+$ ]]; then
    DIFF=$((NOW_EPOCH - LAST_RAW))
    if [ "$DIFF" -lt "$COOLDOWN_SEC" ]; then
      SHOULD_RUN=0
    fi
  fi
fi

if [ "$SHOULD_RUN" -eq 1 ]; then
  echo "$NOW_EPOCH" > "$STAMP_FILE"
  SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  SYNC_SCRIPT="$SCRIPT_DIR/sync_mac_env.sh"
  nohup bash -c "
    exec >'$LOG_FILE' 2>&1
    for bin in \"\$HOME/.gemini/bin/agy\" \"\$(command -v agy 2>/dev/null || true)\"; do
      if [ -n \"\$bin\" ] && [ -x \"\$bin\" ]; then
        \"\$bin\" update || true
        break
      fi
    done
    if [ -f '$SYNC_SCRIPT' ]; then
      bash '$SYNC_SCRIPT' || true
    fi
  " >/dev/null 2>&1 &
fi

# Return valid empty hook JSON immediately without blocking session startup
echo "{}"
