# CLAUDE.md — Level 2 中等模板

适合中型项目、需要前后端分离或对外文档展示、单人到小团队协作。在 Level 1 基础上加入 **doc/ 正式文档站点** 的双轨协作规范。

---

## 模板内容

```markdown
# {项目名称} — 项目规范

## 项目概述

{用户提供的一句话描述}

**关键认知**（讨论过程中凝练的 2-3 条核心决策，可留空待后续填充）：
- ...
- ...

当前阶段：**{阶段}**。

## 协作模式：文档双轨制

本项目维护两套互补的文档：

- **DesignNotes/** — 会话讨论记录，按 session 编号追加。记录"为什么"和"怎么得出结论的"，**不修改历史**
- **doc/** — MkDocs 正式文档站点。按主题结构化，**反映最新状态**，记录"是什么"和"怎么做"

重大决策同时在两处体现：DesignNotes 记过程，doc 记结论。

### DesignNotes/ 的维护

1. 每次会话产出一份文档：`日期_session-NN_主题.md`
2. 讨论过程中有价值的想法和决策即时写入
3. 新 session 可以"修正"旧 session 的结论，但**不改旧文**
4. `DesignNotes/README.md` 是索引，每次新增 session 要更新
5. **会话末尾主动写 session doc 的触发条件**（满足任一即写）：
   - 本次对话产生了重大设计决策或认知修正
   - 完成了重要功能、模块的修改或讨论
   - 用户主动说"记录一下这次会话"

   满足条件时主动创建 session 文档、更新 README 索引、创建 `discussion/sessions/` 符号链接、更新 mkdocs.yml nav。

### doc/ MkDocs 站点的维护

站点结构：`overview/` + `development/` + `architecture/` + `discussion/`。

本地运行：`cd doc && mkdocs serve` → http://127.0.0.1:8000

**核心原则**：
- doc/ 下的内容反映**最新决策状态**，不留"session-N 修正"之类的过程元信息
- 战略级决策变化时，同步更新 `overview/` 和 `architecture/` 下相关文档
- `discussion/sessions/` 是指向 `DesignNotes/` 的符号链接，保持单源
- 每次结构性修改后验证 `mkdocs build --strict` 干净通过

### Doc 状态标记约定

每份 Doc 用 emoji 标注完整度：

- 🔴 **待撰写**：placeholder，尚未实质内容
- 🟡 **骨架版 / 框架版**：结构和原则确定，字段细节待补
- 🟢 **完成**：可作为契约使用

### 跨 session 的认知升级

重大战略决策同步更新 **project memory**——DesignNotes 记过程，memory 记结论，doc 记最新状态。

### 每次会话开始时

1. memory 自动加载（反映最新战略级决策）
2. 读最新的 session 文档（当前起点）
3. 按任务需要读 doc/ 下的相关章节

## 目录结构

```
{项目名称}/
├── CLAUDE.md                     ← 本文件，协作规范
├── DesignNotes/                  ← 按 session 追加的讨论记录
├── doc/                          ← MkDocs 正式文档站点
│   └── docs/{overview,development,architecture,discussion}/
└── (待建) {根据项目需要}
```

## 语言与风格

- {语言偏好}
- 设计文档要**有观点、有判断**，不要面面俱到地罗列
- 代码和技术方案用**段落式说明**，不堆 bullet point
- 正式文档（doc/ 下）避免 "session-N 修正"之类的元信息噪音——讨论过程留在 DesignNotes/ 里

## 需要特别注意的约束

（项目讨论过程中逐步填充项目特定的约束。常见例子：）

1. ...
2. ...
3. ...
```

---

## 使用说明

- **关键认知**和**特别约束**两章可以先留占位，等首轮讨论后再填实
- Doc 8 份全集可能不全适合所有项目——根据项目类型选 3-5 份（参考 `doc-system.md`）
- 如果项目涉及参考资料管理、多用户/多环境、跨模块架构约束——升级到 Level 3
