# Session 文档工作流（Level 2/3）

session 文档是 DesignNotes/ 的骨架——记录每次会话的讨论过程、决策、新问题。**设计得好，未来任何时候都能回溯"当初为什么这么决定"**。

## 命名约定

```
DesignNotes/
└── YYYY-MM-DD_session-NN_主题.md
```

- **日期**：ISO 格式 `2026-04-22`
- **编号**：两位数 `00, 01, ... 09, 10, 11, ...`，单调递增（同一天多个 session 也是递增，不是从 0 重来）
- **主题**：4-10 字，概括本次会话核心（如"架构初步讨论"、"记忆架构重构"）

## 单份 session 文档模板

```markdown
# Session NN — {主题}

**日期**：YYYY-MM-DD
**参与**：{用户} + Claude
**重要程度**：⭐（一般） / ⭐⭐（重大决策）/ ⭐⭐⭐（战略级）

---

## 本次会话做了什么

{2-5 句话概述}

---

## 一、{第一个议题}

### 起因

{为什么讨论这个}

### 过程 / 判断

{关键讨论点和思路}

### 决策

{明确的结论，可以直接被引用}

### 产出

{创建/修改了哪些文件}

---

## 二、{第二个议题}

...

---

## 当前项目状态汇总（可选，session 重要时加）

| 模块 | 状态 | 本次变化 |
|-----|------|---------|
| ... | ... | ... |

---

## 下次会话的起点

{开放的问题 / 待拍板的点 / 推荐的下一步}
```

## 触发条件（什么时候写 session doc）

**满足任一就在会话末尾主动写**（不要等用户催）：

1. 本次对话**产生了重大设计决策或认知修正**
2. 完成了**重要功能、模块**的修改或讨论
3. 用户主动说"记录一下这次会话"

## 完整收尾流程（Level 2/3）

满足触发条件时，会话末尾按顺序做这几件事：

### 1. 创建 session 文档

在 `DesignNotes/` 下写入 `YYYY-MM-DD_session-NN_主题.md`（按上面的模板）

### 2. 更新 `DesignNotes/README.md` 索引

在对应日期/主题分组下加一行：

```markdown
| [**session-NN**](YYYY-MM-DD_session-NN_主题.md) ⭐⭐ | MM-DD | **主题** | {关键产出一两句} |
```

并更新文档末尾的"下次会话起点"指向最新 session。

### 3. 创建符号链接（如有 doc 站点）

```bash
ln -s /abs/path/to/DesignNotes/YYYY-MM-DD_session-NN_主题.md \
      /abs/path/to/doc/docs/discussion/sessions/YYYY-MM-DD_session-NN_主题.md
```

### 4. 更新 `mkdocs.yml` nav（如有 doc 站点）

在 `nav: 讨论记录 > Session 档案:` 下加一行：

```yaml
- session-NN 主题: discussion/sessions/YYYY-MM-DD_session-NN_主题.md
```

### 5. 验证 build

```bash
cd doc && mkdocs build --strict
```

应该 0 warning 通过。

## 不修改历史原则

**旧 session 文档不修改**——新 session 可以"修正"旧结论，但通过**新增 session 说明认知演进**，不改旧文。

**例外**（可以追溯修改旧文的情况）：
- **隐私消毒**：泄露了真实姓名/敏感信息的追溯替换
- **链接修复**：文件名改了，修历史文档里的链接
- **明显错别字 / 格式错误**

## 跨 session 的认知升级——memory

重大战略决策除了写 session doc，还要同步更新 **project memory**：

- **DesignNotes** 记过程（"为什么这么决定"）
- **memory** 记结论（"现在的共识是什么"）
- **doc/** 记最新状态（"是什么 / 怎么做"）

三者互补，不重复。

## 常见坑

**坑 1：忘记创建符号链接**

结果：session doc 存在于 DesignNotes/，但 doc 站点打不开。检查清单一定要覆盖 "symlink + nav + build"。

**坑 2：session 编号跳号**

结果：审阅历史时困惑。如果真的漏写了几次会话，补写用"session-NN-late"或者接下去编号，但在 README 索引里说明。

**坑 3：每次对话都写 session**

结果：session 库变成流水账。只在**满足触发条件**时写——闲聊调参、小 bug 修复不需要。
