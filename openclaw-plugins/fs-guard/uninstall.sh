#!/usr/bin/env bash
#
# fs-guard uninstaller for OpenClaw
#

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
NC='\033[0m'

info()  { echo -e "${CYAN}[fs-guard]${NC} $*"; }
ok()    { echo -e "${GREEN}[fs-guard]${NC} $*"; }
err()   { echo -e "${RED}[fs-guard]${NC} $*" >&2; }

OPENCLAW_DIR="${HOME}/.openclaw"
PLUGIN_DIR="${OPENCLAW_DIR}/extensions/fs-guard"
CONFIG_FILE="${OPENCLAW_DIR}/openclaw.json"

if ! command -v jq &>/dev/null; then
  err "jq is required: brew install jq (macOS) or apt install jq (Linux)"
  exit 1
fi

# Remove plugin files
if [ -d "$PLUGIN_DIR" ]; then
  rm -rf "$PLUGIN_DIR"
  ok "Removed plugin directory: ${PLUGIN_DIR}"
else
  info "Plugin directory not found, skipping."
fi

# Patch config
if [ -f "$CONFIG_FILE" ]; then
  cp "$CONFIG_FILE" "${CONFIG_FILE}.bak.fs-guard-uninstall"

  jq 'del(.plugins.allow[] | select(. == "fs-guard"))
    | del(.plugins.entries["fs-guard"])
    | .plugins.load.paths = [.plugins.load.paths[] | select(. | contains("fs-guard") | not)]' \
    "$CONFIG_FILE" > "${CONFIG_FILE}.tmp" \
    && mv "${CONFIG_FILE}.tmp" "$CONFIG_FILE"

  ok "Removed fs-guard from OpenClaw config"
fi

echo ""
ok "fs-guard uninstalled. Restart OpenClaw to take effect."
echo ""
