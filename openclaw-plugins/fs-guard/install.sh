#!/usr/bin/env bash
#
# fs-guard installer for OpenClaw
# Protects critical files from destructive AI agent operations.
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/ZLHad/agent-skills/main/openclaw-plugins/fs-guard/install.sh | bash
#   or:
#   bash install.sh
#

set -euo pipefail

# ── Colors ────────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

info()  { echo -e "${CYAN}[fs-guard]${NC} $*"; }
ok()    { echo -e "${GREEN}[fs-guard]${NC} $*"; }
warn()  { echo -e "${YELLOW}[fs-guard]${NC} $*"; }
err()   { echo -e "${RED}[fs-guard]${NC} $*" >&2; }

# ── Preflight checks ─────────────────────────────────────────────────
OPENCLAW_DIR="${HOME}/.openclaw"
EXTENSIONS_DIR="${OPENCLAW_DIR}/extensions"
PLUGIN_DIR="${EXTENSIONS_DIR}/fs-guard"
CONFIG_FILE="${OPENCLAW_DIR}/openclaw.json"

if [ ! -d "$OPENCLAW_DIR" ]; then
  err "OpenClaw not found at ${OPENCLAW_DIR}. Please install OpenClaw first."
  exit 1
fi

if [ ! -f "$CONFIG_FILE" ]; then
  err "OpenClaw config not found at ${CONFIG_FILE}."
  exit 1
fi

# Check for jq (needed for config patching)
if ! command -v jq &>/dev/null; then
  err "jq is required but not installed."
  echo "  Install with: brew install jq (macOS) or apt install jq (Linux)"
  exit 1
fi

# ── Determine script directory (for local install) ────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)"

# ── Install plugin files ─────────────────────────────────────────────
info "Installing fs-guard plugin..."

mkdir -p "$PLUGIN_DIR"

# Copy plugin files (from local directory or embedded)
if [ -f "${SCRIPT_DIR}/index.ts" ]; then
  cp "${SCRIPT_DIR}/index.ts" "$PLUGIN_DIR/"
  cp "${SCRIPT_DIR}/package.json" "$PLUGIN_DIR/"
  cp "${SCRIPT_DIR}/openclaw.plugin.json" "$PLUGIN_DIR/"
  ok "Plugin files copied to ${PLUGIN_DIR}"
else
  err "Plugin source files not found in ${SCRIPT_DIR}."
  err "Please run this script from the fs-guard directory."
  exit 1
fi

# ── Patch openclaw.json ──────────────────────────────────────────────
info "Patching OpenClaw config..."

# Backup config
cp "$CONFIG_FILE" "${CONFIG_FILE}.bak.fs-guard"
ok "Config backed up to ${CONFIG_FILE}.bak.fs-guard"

# Add fs-guard to plugins.allow (if not already there)
if jq -e '.plugins.allow | index("fs-guard")' "$CONFIG_FILE" &>/dev/null; then
  info "fs-guard already in plugins.allow, skipping."
else
  jq '.plugins.allow += ["fs-guard"]' "$CONFIG_FILE" > "${CONFIG_FILE}.tmp" \
    && mv "${CONFIG_FILE}.tmp" "$CONFIG_FILE"
  ok "Added fs-guard to plugins.allow"
fi

# Add fs-guard load path (if not already there)
LOAD_PATH="${PLUGIN_DIR}"
if jq -e --arg p "$LOAD_PATH" '.plugins.load.paths | index($p)' "$CONFIG_FILE" &>/dev/null; then
  info "Load path already configured, skipping."
else
  jq --arg p "$LOAD_PATH" '.plugins.load.paths += [$p]' "$CONFIG_FILE" > "${CONFIG_FILE}.tmp" \
    && mv "${CONFIG_FILE}.tmp" "$CONFIG_FILE"
  ok "Added load path: ${LOAD_PATH}"
fi

# Add fs-guard plugin entry with default config (if not already there)
if jq -e '.plugins.entries["fs-guard"]' "$CONFIG_FILE" &>/dev/null; then
  info "Plugin entry already exists, skipping."
else
  jq '.plugins.entries["fs-guard"] = {
    "enabled": true,
    "config": {
      "protectedPaths": [],
      "allowedWritePaths": [
        (env.HOME + "/.openclaw/workspace"),
        "/tmp"
      ],
      "blockEmptyWrites": true
    }
  }' "$CONFIG_FILE" > "${CONFIG_FILE}.tmp" \
    && mv "${CONFIG_FILE}.tmp" "$CONFIG_FILE"
  ok "Added fs-guard plugin entry with default config"
fi

# ── Summary ───────────────────────────────────────────────────────────
echo ""
ok "============================================"
ok "  fs-guard installed successfully!"
ok "============================================"
echo ""
info "Protected by default:"
echo "  - System paths: /etc, /usr, /bin, /sbin, /System, /Library, ..."
echo "  - User configs: ~/.ssh, ~/.gnupg, ~/.config, ~/.zshrc, ~/.claude, ..."
echo "  - Dangerous commands: rm -rf, dd, mkfs, curl|bash, git push --force, ..."
echo "  - Empty file writes (clearing file content)"
echo ""
info "To add custom protected paths, edit:"
echo "  ${CONFIG_FILE}"
echo "  → plugins.entries.fs-guard.config.protectedPaths"
echo ""
info "Example — protect Documents and Desktop:"
echo '  "protectedPaths": ["~/Documents", "~/Desktop", "~/Downloads"]'
echo ""
warn "Restart OpenClaw to activate:"
echo "  launchctl unload ~/Library/LaunchAgents/ai.openclaw.gateway.plist"
echo "  launchctl unload ~/Library/LaunchAgents/ai.openclaw.node.plist"
echo "  launchctl load ~/Library/LaunchAgents/ai.openclaw.gateway.plist"
echo "  launchctl load ~/Library/LaunchAgents/ai.openclaw.node.plist"
echo ""
info "Or if you use the openclaw CLI:"
echo "  openclaw restart"
echo ""
