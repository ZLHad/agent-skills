# Agent Skills

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/ZLHad/agent-skills?style=social)](https://github.com/ZLHad/agent-skills/stargazers)

A collection of ready-to-use agent skills for [OpenClaw](https://github.com/ZLHad/openclaw) and [Claude Code](https://docs.anthropic.com/en/docs/claude-code).

> **What are Agent Skills?** Modular, plug-and-play capability packs that extend AI agents with domain-specific knowledge and workflows — no API keys, no configuration, just drop in and go.

## Quick Install

```bash
# Clone the repo
git clone --depth 1 https://github.com/ZLHad/agent-skills /tmp/agent-skills

# Install an OpenClaw skill
cp -r /tmp/agent-skills/openclaw-skills/<skill-name> ~/.openclaw/workspace/skills/

# Install a Claude Code skill
cp -r /tmp/agent-skills/claude-code-skills/<skill-name> ~/.claude/skills/
```

## OpenClaw Skills

### Claude Code Bridge

Operate a **real, interactive Claude Code terminal session** remotely through any chat channel — QQ, Telegram, Discord, etc. Not a simple API wrapper — it's the full Claude Code CLI experience via tmux bridging.

```
Your Phone (QQ / Telegram / ...)
     │
     ▼
  OpenClaw Agent ──► Claude Code Bridge ──► Claude Code CLI (tmux)
     │                                           │
     └───────────── response ◄───────────────────┘
```

**Highlights:**
- Full Claude Code feature coverage: code editing, file I/O, git, slash commands, tool approval
- Persistent sessions — closing your chat app won't kill the session
- Sandbox mode — disposable temp directory, auto-cleanup on stop
- Custom working directory support
- Multi-session — each chat channel gets its own independent session

**Install:**
```bash
cp -r /tmp/agent-skills/openclaw-skills/claude-code-bridge ~/.openclaw/workspace/skills/
```

[Full documentation →](openclaw-skills/claude-code-bridge/README.md)

---

## OpenClaw Plugins

### fs-guard

Filesystem protection plugin that prevents AI agents from accidentally deleting, overwriting, or destroying critical files on your local machine.

```
Agent: write("~/.ssh/id_rsa", "")
  → fs-guard: BLOCKED — "Please ask the user for confirmation"
  → Agent: "Do you want me to modify ~/.ssh/id_rsa?"
```

**What it protects:**
- System paths (`/etc`, `/usr`, `/bin`, `/System`, `/Library`) — always blocked
- User configs (`~/.ssh`, `~/.gnupg`, `~/.zshrc`, `~/.claude`) — requires confirmation
- Dangerous commands (`rm -rf`, `dd`, `mkfs`, `curl|bash`, `git push --force`) — blocked
- Empty writes (clearing file content) — blocked
- Custom paths you define — requires confirmation

**Install:**
```bash
bash /tmp/agent-skills/openclaw-plugins/fs-guard/install.sh
```

[Full documentation →](openclaw-plugins/fs-guard/README.md)

---

## Claude Code Skills

### IEEE Reference Manager

Full-pipeline IEEE Trans reference management assistant for academic papers. Automates the tedious work of checking and fixing references in LaTeX manuscripts.

**What it does:**
- BibTeX format validation & auto-fix (missing fields, duplicate entries, key conflicts)
- Journal name standardization using IEEE official macros (`IEEE_J_WCOM`, etc.)
- DOI / metadata online verification via CrossRef & IEEE Xplore
- Early Access article detection and format correction
- Author count compliance (IEEE ≤6 full list, ≥7 use et al.)
- Cross-reference audit between `.tex` and `.bib` files
- Consecutive `\cite{}` merge suggestions

**Install:**
```bash
cp -r /tmp/agent-skills/claude-code-skills/ieee-reference-manager ~/.claude/skills/
```

---

## More Skills (Coming Soon)

Additional skills are available as standalone packages and will be integrated into this repo:

| Skill | Description |
|-------|-------------|
| **academic-polisher** | Academic paper polishing — converts mixed CN/EN drafts with LaTeX formulas into publication-ready English |
| **ieee-paper-revision** | Complete IEEE journal revision workflow: comment extraction, revision planning, manuscript editing, response letter |
| **review-planner** | Analyzes reviewer comments and generates a structured revision plan |
| **zotero-citation** | Zotero integration — auto-match references from your Zotero library for manuscript citations |
| **academic-figure-prompt** | Generates detailed prompts for creating research paper figures (architecture diagrams, system diagrams, etc.) |
| **conversation-knowledge-extractor** | Extracts key knowledge, methodologies, and patterns from conversations into a structured knowledge base |
| **knowledge-base-manager** | Scans, analyzes, and organizes knowledge base documents with indexing and progress tracking |
| **comms-research-partner** | Research companion for brainstorming, literature discussion, and academic exchange |

## Project Structure

```
agent-skills/
├── openclaw-skills/
│   └── claude-code-bridge/      # OpenClaw ↔ Claude Code tmux bridge
├── openclaw-plugins/
│   └── fs-guard/                # Filesystem protection plugin
├── claude-code-skills/
│   └── ieee-reference-manager/  # IEEE reference validation & fixing
└── README.md
```

## Contributing

Contributions welcome! Feel free to:
- Submit new skills via Pull Request
- Report issues or suggest improvements
- Share your own skill ideas in [Discussions](https://github.com/ZLHad/agent-skills/discussions)

## License

This project is licensed under the [MIT License](LICENSE).

Copyright (c) 2025 ZLHad. You are free to use, modify, and distribute this software for any purpose, commercial or non-commercial, with attribution.
