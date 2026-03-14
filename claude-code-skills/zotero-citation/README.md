# Zotero Citation — 文献引用工作流助手

通过 Zotero 本地 API 读取文献库，为用户指定的文字段落或论文全文智能匹配参考文献，生成规范格式的 Reference 或 BibTeX。

## 核心功能

- **段落级匹配**：分析段落中的每个论点，从 Zotero 候选文献中匹配，标注引用位置
- **全文级匹配**：读取整篇论文，逐段分析并分配参考文献，输出引用位置表
- **多格式输出**：IEEE Reference 文本（默认）或 BibTeX 条目
- **深度阅读**：按需通过本地路径提取 PDF 全文进行精准匹配

## 工作流程

```
1. 确认输入（段落/全文）与 Zotero 环境
   ↓
2. 获取候选文献（选择 Collection）
   ↓
3. 文献-文本匹配（按论点类型匹配）
   ↓
4. 确认输出格式（IEEE / APA / BibTeX）
   ↓
5. 生成输出（标注引用位置 + Reference 列表）
```

## 匹配规则

| 文本内容类型 | 匹配文献类型 |
|-------------|-------------|
| 背景/综述性论点 | survey / tutorial 类 |
| 具体技术声明 | 该技术代表性论文 |
| 概念定义 | 定义该概念的论文 |
| 方法论论点 | 提出该方法的论文 |
| 应用场景描述 | 与场景最匹配的论文 |
| 数据/结论引用 | 提供该数据的原始论文 |

## 前置条件

1. **Zotero Desktop 运行中**
2. **本地 API 已启用**：Zotero → 编辑 → 设置 → 高级 → 允许其他应用程序通过 API 访问

验证连接：
```bash
curl -s "http://localhost:23119/api/users/0/items?limit=1"
```

## 输出格式

**IEEE Reference**（默认）：
```
[N] A. B. Author1, C. D. Author2, and E. F. Author3, "Title," Journal Name, vol. X, no. Y, pp. XX–YY, Mon. Year.
```

**BibTeX**：通过 Zotero API `format=bibtex` 直接导出或手动组装。

## 目录结构

```
zotero-citation/
├── SKILL.md
└── references/
    └── zotero-api-reference.md     ← Zotero 本地 API 端点详细参考
```

## 安装

```bash
cp -r zotero-citation ~/.claude/skills/
```

## 触发词

`引用文献`、`分配参考文献`、`从 Zotero 选文献`、`生成 Reference 列表`、`匹配引用位置`、`添加参考文献`、`给这段话配引用`、`帮我找合适的参考文献`
