# Agent Skills

A collection of agent skills for [OpenClaw](https://github.com/ZLHad/openclaw) and [Claude Code](https://claude.ai/code).

## Structure

```
agent-skills/
├── openclaw-skills/       # Skills for OpenClaw
│   └── cc-bridge/         # Bridge skill to launch Claude Code from OpenClaw
└── claude-code-skills/    # Skills for Claude Code
    └── ieee-reference-manager/  # IEEE Trans reference management assistant
```

## OpenClaw Skills

### cc-bridge
Bridges OpenClaw and Claude Code. Enables launching and connecting to Claude Code sessions directly from OpenClaw.

**Install:**
```bash
claude skill install github:ZLHad/agent-skills/openclaw-skills/cc-bridge
```

## Claude Code Skills

### ieee-reference-manager
Full-pipeline IEEE Trans reference management assistant. Handles format validation, citation review, BibTeX fixes, journal name standardization, DOI/metadata verification, Early Access handling, author count compliance, and duplicate detection.

**Install:**
```bash
claude skill install github:ZLHad/agent-skills/claude-code-skills/ieee-reference-manager
```

## License

MIT
