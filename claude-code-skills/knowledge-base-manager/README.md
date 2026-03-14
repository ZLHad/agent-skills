# Knowledge Base Manager — 知识库管理助手

智能管理和整理本地知识库文档。扫描、分析、整合由 conversation-knowledge-extractor 生成的知识库文件，生成结构化索引、专题整理报告、进步追踪分析。

## 核心功能

- **增量/全量整理**：增量模式只处理新文件（默认），全量模式完整重建索引
- **学术写作深度分析**：错误模式分析、写作模式提取、个人习惯档案、进步追踪
- **学术探讨深度分析**：概念网络构建、思维框架提取、认知演进追踪
- **结构化输出**：整理报告、错误手册、模式库、思维框架库、多维索引

## 工作流程

```
1. 参数配置（路径、整理模式、类型筛选、输出详细度）
   ↓
2. 文件扫描与解析（识别 knowledge-*.md，提取 YAML 元数据）
   ↓
3. 智能分析与提取（按类型深度处理）
   ↓
4. 生成结构化输出（报告 + 专题文档 + 索引）
   ↓
5. 输出与交付（展示摘要 + 提供文件 + 给出建议）
```

## 生成的文档

| 文档 | 说明 | 位置 |
|------|------|------|
| 整理报告 | 摘要 + 详细统计 + 文档清单 | `整理报告/` |
| 错误手册 | 高频错误 Top10 + 改正进展 | `专题整理/` |
| 模式库 | 可复用写作模板 + 成功案例 | `专题整理/` |
| 思维框架库 | 分析框架 + 问题解决模板 | `专题整理/` |
| 索引文件 | 主题/标签/时间索引 | `索引/` |

## 与 conversation-knowledge-extractor 配合

```
对话学习 → conversation-knowledge-extractor 提取 → 保存到本地
   → 积累 5-10 个文件 → knowledge-base-manager 整理 → 结构化知识体系
```

## 目录结构

```
knowledge-base-manager/
├── SKILL.md
├── references/
│   ├── academic-writing-analysis.md      ← 学术写作深度分析参考
│   ├── academic-discussion-analysis.md   ← 学术探讨深度分析参考
│   ├── smart-features.md                 ← 智能特性说明
│   ├── output-file-specs.md              ← 输出文件规范
│   ├── quality-assurance.md              ← 质量保证检查清单
│   └── academic-writing-workflow.md      ← 学术写作专题工作流
└── templates/
    ├── organizing-report-template.md     ← 整理报告模板
    ├── writing-errors-handbook-template.md ← 错误手册模板
    ├── specialized-docs-templates.md     ← 专题文档模板
    └── index-templates.md               ← 索引文件模板
```

## 安装

```bash
cp -r knowledge-base-manager ~/.claude/skills/
```

## 触发词

`整理知识库`、`管理本地知识`、`更新知识索引`、`整理学习记录`、`生成学习报告`
