#!/usr/bin/env bash
# Antigravity Remote Agents (Linux VM) 向け 3点セット（clasp / Gemini Notebook / Colab GPU）自動セットアップ
# 何度実行しても安全です。`bash .agents/scripts/bootstrap_remote_3kit.sh --check` で状態確認のみ実行できます。
set -u

CHECK_ONLY=0
case "${1:-}" in
  --check) CHECK_ONLY=1 ;;
  -h|--help) printf 'Usage: bash bootstrap_remote_3kit.sh [--check]\n'; exit 0 ;;
  "") ;;
  *) printf 'Unknown option: %s\nUsage: bash bootstrap_remote_3kit.sh [--check]\n' "$1"; exit 1 ;;
esac

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd -P)"
UPLOAD_DIR="${ANTIGRAVITY_UPLOAD_DIR:-/home/antigravity/upload}"
export PATH="$HOME/.local/bin:$PATH"

seed_secret_file() {
  local src_name="$1" dst_path="$2"
  local src="$UPLOAD_DIR/$src_name"
  if [ -f "$src" ] && [ ! -s "$dst_path" ]; then
    mkdir -p "$(dirname "$dst_path")"
    cp "$src" "$dst_path" && chmod 600 "$dst_path"
    printf '[SEED] %s -> %s (0600)\n' "$src_name" "$dst_path"
  fi
}

if [ "$CHECK_ONLY" -eq 0 ]; then
  mkdir -p "$HOME/.local/bin" "$HOME/.config/colab-api" "$HOME/.config/gemini-notebook-api" "$HOME/.config/gemini-notebook-mcp" "$HOME/.local/share/python_keyring"
  chmod 700 "$HOME/.config/colab-api" "$HOME/.config/gemini-notebook-api" "$HOME/.config/gemini-notebook-mcp" "$HOME/.local/share/python_keyring" 2>/dev/null || true

  # 1. Helper scripts -> ~/.local/bin
  for f in colab_api.py nb.py; do
    if [ -f "$SCRIPT_DIR/$f" ]; then
      cp "$SCRIPT_DIR/$f" "$HOME/.local/bin/$f"
      chmod 755 "$HOME/.local/bin/$f"
    fi
  done

  # 2. clasp 3.x (requires Node 22+)
  if ! command -v clasp >/dev/null 2>&1; then
    if command -v npm >/dev/null 2>&1; then
      npm install -g @google/clasp@3 >/dev/null 2>&1 || true
    fi
  fi

  # 3. uv + google-colab-cli (with keyrings.alt for headless Linux)
  if ! command -v uv >/dev/null 2>&1; then
    arch="$(uname -m 2>/dev/null || echo '')"
    pkg=""
    case "$arch" in
      x86_64|amd64) pkg="uv-x86_64-unknown-linux-gnu" ;;
      aarch64|arm64) pkg="uv-aarch64-unknown-linux-gnu" ;;
    esac
    if [ -n "$pkg" ]; then
      tmp_dir="$(mktemp -d /tmp/uv-inst.XXXXXX)"
      if curl -fsSL "https://github.com/astral-sh/uv/releases/latest/download/${pkg}.tar.gz" -o "$tmp_dir/uv.tgz" 2>/dev/null \
         && tar -xz -C "$tmp_dir" -f "$tmp_dir/uv.tgz" 2>/dev/null; then
        uv_bin="$(find "$tmp_dir" -type f -name uv | head -n 1)"
        [ -n "$uv_bin" ] && cp "$uv_bin" "$HOME/.local/bin/uv" && chmod 755 "$HOME/.local/bin/uv"
      fi
      rm -rf "$tmp_dir"
    fi
  fi
  if command -v uv >/dev/null 2>&1 && ! command -v colab >/dev/null 2>&1; then
    uv tool install --with keyrings.alt google-colab-cli >/dev/null 2>&1 || true
  fi

  # 4. Safe auth seeding from Remote Agents Upload Files (never prints secret contents)
  if [ -d "$UPLOAD_DIR" ]; then
    seed_secret_file "clasprc.json" "$HOME/.clasprc.json"
    seed_secret_file ".clasprc.json" "$HOME/.clasprc.json"
    seed_secret_file "colab-keyring.cfg" "$HOME/.local/share/python_keyring/keyring_pass.cfg"
    seed_secret_file "keyring_pass.cfg" "$HOME/.local/share/python_keyring/keyring_pass.cfg"
    seed_secret_file "colab-config.json" "$HOME/.config/colab-api/config.json"
    seed_secret_file "gemini-notebook-config.json" "$HOME/.config/gemini-notebook-mcp/config.json"
    seed_secret_file "gemini-notebook-tokens.json" "$HOME/.config/gemini-notebook-mcp/tokens.json"
  fi
fi

py_bin="$(command -v python3 || command -v python || true)"
show_row() {
  if [ "$1" -eq 1 ]; then printf '[OK] %s\n' "$2"; else printf '[TODO] %s\n' "$2"; fi
}

printf '\n=== Remote Agents 3-Kit Status ===\n'
ok_node=0; command -v node >/dev/null 2>&1 && ok_node=1
ok_clasp=0; command -v clasp >/dev/null 2>&1 && ok_clasp=1
ok_uv=0; command -v uv >/dev/null 2>&1 && ok_uv=1
ok_colab=0; command -v colab >/dev/null 2>&1 && ok_colab=1
ok_capi=0; [ -n "$py_bin" ] && [ -f "$HOME/.local/bin/colab_api.py" ] && "$py_bin" "$HOME/.local/bin/colab_api.py" --help >/dev/null 2>&1 && ok_capi=1
ok_nb=0; [ -n "$py_bin" ] && [ -f "$HOME/.local/bin/nb.py" ] && "$py_bin" "$HOME/.local/bin/nb.py" --help >/dev/null 2>&1 && ok_nb=1
ok_clasp_auth=0; [ -s "$HOME/.clasprc.json" ] && ok_clasp_auth=1
ok_colab_auth=0; [ -s "$HOME/.local/share/python_keyring/keyring_pass.cfg" ] && ok_colab_auth=1
ok_colab_proj=0; { [ -n "${COLAB_QUOTA_PROJECT:-}" ] || [ -s "$HOME/.config/colab-api/config.json" ]; } && ok_colab_proj=1
ok_nb_auth=0; { [ -s "$HOME/.config/gemini-notebook-mcp/tokens.json" ] || [ -s "$HOME/.config/gemini-notebook-api/token.json" ]; } && ok_nb_auth=1

show_row "$ok_node"       "Node.js ($(node -v 2>/dev/null || echo missing))"
show_row "$ok_clasp"      "clasp ($(clasp --version 2>/dev/null | head -n 1 || echo missing))"
show_row "$ok_uv"         "uv"
show_row "$ok_colab"      "Colab CLI (colab)"
show_row "$ok_capi"       "colab_api.py (~/.local/bin/colab_api.py)"
show_row "$ok_nb"         "nb.py (~/.local/bin/nb.py)"
show_row "$ok_clasp_auth" "clasp auth (~/.clasprc.json)"
show_row "$ok_colab_auth" "Colab keyring (~/.local/share/python_keyring/keyring_pass.cfg)"
show_row "$ok_colab_proj" "Colab quota project (~/.config/colab-api/config.json or COLAB_QUOTA_PROJECT)"
show_row "$ok_nb_auth"    "Gemini Notebook auth (gemini-notebook-mcp or gemini-notebook-api)"
exit 0
