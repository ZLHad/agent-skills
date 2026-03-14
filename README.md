# Agent Skills

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/ZLHad/agent-skills?style=social)](https://github.com/ZLHad/agent-skills/stargazers)

面向 [OpenClaw](https://github.com/nicepkg/openclaw) 和 [Claude Code](https://docs.anthropic.com/en/docs/claude-code) 的即插即用 Agent 技能包合集。

> **什么是 Agent Skill？** 模块化的能力扩展包，为 AI 代理注入特定领域的知识和工作流。无需配置 API Key，放入目录即可使用。

---

## 快速安装

```bash
# 克隆仓库
git clone --depth 1 https://github.com/ZLHad/agent-skills /tmp/agent-skills

# 安装 OpenClaw Skill
cp -r /tmp/agent-skills/openclaw-skills/<skill-name> ~/.openclaw/workspace/skills/

# 安装 Claude Code Skill
cp -r /tmp/agent-skills/claude-code-skills/<skill-name> ~/.claude/skills/

# 安装 OpenClaw Plugin（需要额外配置，见各插件 README）
bash /tmp/agent-skills/openclaw-plugins/<plugin-name>/install.sh
```

---

## OpenClaw Skills

通过 Telegram / QQ / 微信等聊天渠道远程调用的 Agent 技能。

| Skill | 说明 | 安装 |
|-------|------|------|
| **[claude-code-bridge](openclaw-skills/claude-code-bridge/)** | 通过聊天渠道远程操控完整的 Claude Code CLI 会话（tmux 桥接） | `cp -r ... ~/.openclaw/workspace/skills/` |
| **[info-feed-aggregator](openclaw-skills/info-feed-aggregator/)** | 多源学术信息聚合（arXiv、IEEE Xplore、Semantic Scholar、小红书等） | `cp -r ... ~/.openclaw/workspace/skills/` |

---

## OpenClaw Plugins

OpenClaw 扩展插件，通过 `before_tool_call` 钩子增强代理行为。

| Plugin | 说明 | 安装 |
|--------|------|------|
| **[fs-guard](openclaw-plugins/fs-guard/)** | 文件系统保护 — 阻止 AI 代理误删/覆盖关键文件，拦截危险命令 | `bash install.sh` |

```
Agent: write("~/.ssh/id_rsa", "")
  -> fs-guard: BLOCKED
  -> Agent: "需要修改 ~/.ssh/id_rsa，请确认是否继续？"
```

---

## Claude Code Skills

直接在 Claude Code 中使用的专业技能。

### 学术论文工具链

| Skill | 说明 |
|-------|------|
| **[literature-search](claude-code-skills/literature-search/)** | 文献检索助手 — IEEE Xplore / Semantic Scholar / arXiv 多源搜索，多轮去重，BibTeX 导出，分方向最终报告 |
| **[ieee-reference-manager](claude-code-skills/ieee-reference-manager/)** | IEEE 参考文献管理（BibTeX 校验、期刊名标准化、DOI 验证、重复检测） |
| **[zotero-citation](claude-code-skills/zotero-citation/)** | Zotero 文献引用（自动匹配引用位置，生成规范 Reference） |

### 知识管理

| Skill | 说明 |
|-------|------|
| **[conversation-knowledge-extractor](claude-code-skills/conversation-knowledge-extractor/)** | 对话知识提取（从聊天中提取方法论、写作偏好、常见错误等） |
| **[knowledge-base-manager](claude-code-skills/knowledge-base-manager/)** | 知识库管理（扫描/分析/整合知识文档，生成索引和进步报告） |

### 科研协作

| Skill | 说明 |
|-------|------|
| **[comms-research-partner](claude-code-skills/comms-research-partner/)** | 科研伙伴 — 论文讨论、头脑风暴、文献搜索、数学建模 |

### 开发工具

| Skill | 说明 |
|-------|------|
| **[skill-auditor](claude-code-skills/skill-auditor/)** | Skill 质量审查（渐进式披露规范、行数、frontmatter、参考文件链接检查） |

---

## 目录结构

```
agent-skills/
├── openclaw-skills/                  # OpenClaw Agent Skills
│   ├── claude-code-bridge/           #   远程 Claude Code 操控
│   └── info-feed-aggregator/         #   多源信息聚合
│
├── openclaw-plugins/                 # OpenClaw 扩展插件
│   └── fs-guard/                     #   文件系统保护
│
├── claude-code-skills/               # Claude Code Skills
│   ├── comms-research-partner/       #   科研伙伴
│   ├── conversation-knowledge-extractor/  #   对话知识提取
│   ├── ieee-reference-manager/       #   参考文献管理
│   ├── knowledge-base-manager/       #   知识库管理
│   ├── literature-search/            #   文献检索助手
│   ├── skill-auditor/               #   Skill 质量审查
│   └── zotero-citation/              #   Zotero 引用
│
├── README.md
├── LICENSE
└── .gitignore
```

## 贡献

欢迎贡献！你可以：
- 通过 Pull Request 提交新 Skill
- 在 [Issues](https://github.com/ZLHad/agent-skills/issues) 中反馈问题或建议
- 在 [Discussions](https://github.com/ZLHad/agent-skills/discussions) 中分享想法

## License

[MIT License](LICENSE) - Copyright (c) 2025 ZLHad
