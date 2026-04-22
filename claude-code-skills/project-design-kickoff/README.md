# project-design-kickoff

复杂项目"对话式迭代设计"工作流的一键初始化。**按复杂度分三档**，从个人 POC 到大型长期系统都能覆盖。

## 解决什么问题

用 Claude Code 做项目设计时，最有价值的不是最终文档，而是讨论过程中涌现的想法和决策。这个 skill 为新项目搭建一套"边讨论边沉淀"的脚手架：

- **CLAUDE.md** 定义协作契约（怎么讨论、怎么记录、怎么恢复上下文）
- **DesignNotes/** 按 session 积累设计思考
- **Memory** 跨 session 保留核心结论
- **（可选）doc/** MkDocs 正式文档站点
- **（可选）ReferenceItems/** 外部参考资料管理

## 复杂度三档

| Level | 适合 | 交付内容 | 时长 |
|-------|------|---------|------|
| **1 轻量** | POC / 个人小项目 / 脚本探索 | DesignNotes + 精简 CLAUDE.md | ~5 分钟 |
| **2 中等** | 中型项目 / 前后端分离 / 需对外文档 | L1 + MkDocs + 3-5 份 Doc 骨架 | ~15 分钟 |
| **3 复杂** | 大型系统 / 长期迭代 / 多模块协作 | L2 + ReferenceItems + 架构扩展性预留 + 全套 Doc 体系 | ~30-60 分钟 |

初始化时会自然语言收集项目信息 + AskUserQuestion 推荐合适的 Level。

## 使用

在新项目目录下说：

```
初始化项目
```

或：

```
project design kickoff
```

会交互式收集项目信息、推荐并确认 Level、生成对应脚手架、进入第一轮设计讨论。

## 触发词

- 初始化项目、新项目、项目初始化、开始新项目
- project design kickoff、project kickoff、design kickoff

## 文件结构

```
project-design-kickoff/
├── SKILL.md                      # 主入口（简短，指向 reference）
├── README.md                     # 本文件
└── references/                    # 按需读取的详细模板
    ├── claude-md-level-1.md     # L1 CLAUDE.md 模板
    ├── claude-md-level-2.md     # L2 CLAUDE.md 模板
    ├── claude-md-level-3.md     # L3 CLAUDE.md 模板
    ├── doc-system.md            # 8 份 Doc 体系说明
    ├── architecture-patterns.md # 4 条架构扩展性原则
    ├── references-management.md # ReferenceItems 管理规范
    ├── session-workflow.md      # session doc 完整流程
    └── mkdocs-setup.md          # MkDocs 最小配置
```

## 设计理念

1. **渐进披露**：SKILL.md 主入口不塞所有模板，按 Level 按需读 `references/*.md`，节省 context
2. **Level 不是一锤子买卖**：项目可以从 L1 起步，后来升到 L2/L3
3. **传递思维而非面面俱到**：模板精炼、突出关键原则，不追求穷举所有字段
4. **讨论过程第一**：文档是讨论的沉淀，不要追求一次写完美

## 演进

这个 skill 是从 `design-kickoff`（Level 1 的原型版本）**升级改名**而来。原版 `design-kickoff` 已废弃。

经验来自一个复杂 Agent 项目的实战——8 份 Doc 体系、MemoryProvider 防注入架构、知识库与记忆分层、会话 doc 触发规则等思维被泛化成 reference 模板。
