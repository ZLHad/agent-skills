# Conversation Knowledge Extractor — 对话知识提取

从当前对话窗口中深度提取和结构化知识，生成可复用的个人知识库文档。特别针对学术写作场景进行深度记录（修改前后对比、写作偏好、习惯模式）。

## 核心功能

- **智能识别对话类型**：学术写作、学术探讨、编程任务、综合对话
- **分类型深度提取**：不同类型使用不同模板，确保信息完整
- **智能标注分级**：高频问题（⭐⭐⭐）、重要洞察（💡）、需强化记忆（⚠️）、认知演进（🔄）、个人偏好（📌）
- **三层输出结构**：执行摘要 → 结构化详细内容 → 可执行建议

## 工作流程

```
1. 对话全览分析（识别话题数、类型、转折点）
   ↓
2. 话题分类与深度提取（按类型选择模板）
   ↓
3. 智能标注与分级
   ↓
4. 生成分级文档
   ↓
5. 输出保存（knowledge-{YYYYMMDD}-{主题}-{序号}.md）
```

## 提取模板

| 类型 | 模板 | 详细程度 |
|------|------|----------|
| 学术写作（最高优先级） | academic-writing-template.md | 3000-5000 字 |
| 学术探讨 | academic-discussion-template.md | 2000-3000 字 |
| 技术任务 | technical-task-template.md | 1500-2500 字 |
| 综合对话 | general-conversation-template.md | 视内容而定 |

## 学术写作特殊处理

- **修改对比记录**：完整记录原文 → 修改后文本 → 语法/表达/逻辑/风格分析 → 可复用规则
- **写作模式识别**：引言偏好、论证逻辑、段落组织、过渡句、结论风格
- **个人习惯追踪**：常用句式、偏好连接词、论证方式、表达陷阱

## 目录结构

```
conversation-knowledge-extractor/
├── SKILL.md
├── references/
│   ├── academic-writing-template.md
│   ├── academic-discussion-template.md
│   ├── general-conversation-template.md
│   └── technical-task-template.md
└── templates/
    └── output-example.md
```

## 安装

```bash
cp -r conversation-knowledge-extractor ~/.claude/skills/
```

## 配合 Knowledge Base Manager

```
对话学习 → 触发本 Skill 提取知识 → 保存到本地 → 积累 5-10 个文件 → 用 knowledge-base-manager 整理
```

## 触发词

`总结这次对话`、`提取知识点`、`整理对话精华`、`构建知识库`、`记录学习内容`
