# IEEE Paper Revision — 论文修改全流程助手

IEEE 学术论文修改（大修/小修）全流程工具，从解析审稿意见到生成修改稿和回复信。

## 核心能力

| 能力 | 说明 |
|------|------|
| **意见解析** | 提取编辑决定、AE 评语、逐条审稿意见 |
| **修改规划** | 按评审人组织修改清单，标注优先级 |
| **稿件修改** | 蓝色标记修改内容（`\color{blue}`） |
| **回复信生成** | 逐条回复，引用修改后文本，标注修改位置 |

## 工作流程

```
Phase 1: Comment Extraction & Planning
  解析审稿邮件 → 提取逐条意见 → 生成修改计划
   ↓
Phase 2: Iterative Revision
  逐条处理：编辑稿件（蓝色标记）+ 撰写回复条目
   ↓
Phase 3: Finalization
  验证完整性 → 清理旧标记 → 编译最终版本
```

## 回复信格式

每条回复包含：
- 审稿人原文引用
- 详细回复（感谢 + 分析 + 解释修改）
- 修改位置标注（Section/Page/Line）
- 蓝色引用修改后文本

## 目录结构

```
ieee-paper-revision/
├── SKILL.md
└── references/
    ├── response-letter-format.md    ← 回复信格式规范
    └── revision-workflow.md         ← 详细修改工作流
```

## 安装

```bash
cp -r ieee-paper-revision ~/.claude/skills/
```

## 触发词

`修改论文`、`处理审稿意见`、`写回复信`、`大修`、`小修`、`revision`、`respond to reviewers`
