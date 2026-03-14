# Review Planner — 审稿意见分析与修改规划

分析审稿意见并制定按章节组织的修改规划。只提供分析和建议，不直接修改论文。

## 核心能力

| 能力 | 说明 |
|------|------|
| **意见解析** | 读取审稿意见，识别每条意见涉及的章节和重要程度 |
| **章节对照** | 将意见对应到 main.tex 具体行号位置 |
| **修改规划** | 按论文原文顺序生成 REVISION_PLAN.md |
| **具体建议** | 提供修改方向、参考模板和注意事项 |
| **矛盾处理** | 识别审稿意见间的矛盾，提供折中方案 |

## 工作流程

```
1. 定位并读取 Review Comments
   ↓
2. 内部分析（识别章节、标记重要程度）
   ↓
3. 对照 main.tex 定位行号
   ↓
4. 按章节组织修改规划 → REVISION_PLAN.md
   ↓
5. 提供具体修改建议 → MODIFICATION_DETAILS.md
   ↓
6. 交互确认 → 预览文件 → 用户确认后执行
```

## 输出文件

```
revision_workspace/
├── REVISION_PLAN.md            ← 按章节组织的修订计划（主文件）
├── MODIFICATION_DETAILS.md     ← 详细修改建议
├── PREVIEW_*.md                ← 各修改点的预览文件（临时）
└── RESPONSE_LETTER_DRAFT.md    ← 回复信草稿（可选）
```

## 与 ieee-paper-revision 的关系

- **review-planner**：分析 + 规划，不修改原文
- **ieee-paper-revision**：执行修改 + 生成回复信

建议先用 review-planner 制定计划，再用 ieee-paper-revision 执行修改。

## 安装

```bash
cp -r review-planner ~/.claude/skills/
```

## 触发词

`审稿意见`、`review comments`、`修订`、`revision`、`修改计划`、`response letter`
