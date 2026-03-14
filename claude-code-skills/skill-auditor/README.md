# Skill Auditor — 自定义 Skill 质量审查

审查自定义 Claude Code Skills 的质量与规范性，确保符合渐进式披露最佳实践。

## 审查维度

| 维度 | 检查项 |
|------|--------|
| **Frontmatter** | name、description、allowed-tools、model、触发词覆盖 |
| **SKILL.md 正文** | 行数 ≤500、核心工作流完整、参考文件链接、冗余内容拆分 |
| **目录结构** | SKILL.md 必须、README.md 建议、references/ 规范 |
| **参考文件** | 双向链接完整性（SKILL.md ↔ references/*.md） |
| **渐进式披露** | 三阶段合规（frontmatter → SKILL.md → references） |

## 渐进式披露原理

| 阶段 | 触发时机 | 加载内容 | Token 开销 |
|------|----------|----------|------------|
| Stage 1 | 会话启动 | 仅 YAML frontmatter | ~50/skill |
| Stage 2 | 用户输入匹配 | 完整 SKILL.md | 1000-5000 |
| Stage 3 | 执行中按需读取 | references/ scripts/ | 按需 |

## 输出格式

生成审查报告表格（Skill / 行数 / Frontmatter / 参考链接 / README / 总评），按严重度标注问题并给出修复建议。

## 安装

```bash
cp -r skill-auditor ~/.claude/skills/
```

## 触发词

`审查skill`、`检查skill质量`、`skill audit`、`review skills`、`检查技能规范`
