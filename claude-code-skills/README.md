# Claude Code Skills Collection

面向学术科研与日常工具场景的 Claude Code 自定义 Skills 合集。

## Skills 列表

| Skill | 说明 | 触发词 |
|-------|------|--------|
| [academic-polisher](academic-polisher/) | 学术论文润色，中英文混合/公式文本转规范学术英文 | `润色`、`polish`、`改写` |
| [academic-figure-prompt](academic-figure-prompt/) | 生成科研插图的详细绘制 Prompt | `画论文图`、`生成绘图prompt`、`设计架构图` |
| [literature-search](literature-search/) | 多数据源学术文献检索（IEEE Xplore / Semantic Scholar / arXiv） | `查文献`、`搜论文`、`literature search` |
| [ieee-paper-revision](ieee-paper-revision/) | IEEE 期刊论文大修/小修全流程（审稿意见处理 + 回复信） | `修改论文`、`处理审稿意见`、`revision` |
| [ieee-reference-manager](ieee-reference-manager/) | IEEE 参考文献格式校验、BibTeX 修复、DOI 验证 | `检查参考文献`、`修复引用格式` |
| [review-planner](review-planner/) | 分析审稿意见并制定修改规划 | `审稿意见`、`修订要求` |
| [zotero-citation](zotero-citation/) | 通过 Zotero 本地 API 匹配与分配参考文献 | `引用文献`、`从Zotero选文献` |
| [comms-research-partner](comms-research-partner/) | 科研讨论伙伴（论文讨论、数学建模、头脑风暴） | `讨论论文`、`头脑风暴`、`帮我理解` |
| [conversation-knowledge-extractor](conversation-knowledge-extractor/) | 从对话中提取知识点，生成可复用知识库文档 | `总结这次对话`、`提取知识点` |
| [knowledge-base-manager](knowledge-base-manager/) | 管理与整理本地知识库文档 | `整理知识库`、`生成学习报告` |
| [skill-auditor](skill-auditor/) | 审查 Skill 质量与规范性 | `审查skill`、`skill audit` |
| [wechat-article-reader](wechat-article-reader/) | 微信公众号文章抓取（Playwright 无头浏览器） | `读公众号文章`、发送 `mp.weixin.qq.com` 链接 |

## 安装

将目标 skill 目录复制到 `~/.claude/skills/` 即可：

```bash
# 安装单个 skill
cp -r <skill-name> ~/.claude/skills/

# 安装全部
cp -r */ ~/.claude/skills/
```

部分 skill 有额外依赖，详见各 skill 目录下的 README。

## 目录结构约定

```
<skill-name>/
├── SKILL.md              ← Skill 定义（frontmatter + 工作流 + 规则）
├── README.md             ← 用户说明文档
├── references/           ← 参考知识文件（可选）
└── scripts/              ← 实现脚本（可选）
```
