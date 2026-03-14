# IEEE Reference Manager — 参考文献管理助手

IEEE Trans 论文参考文献全流程管理工具。负责 BibTeX 审查与修复、引用格式校验、期刊名标准化、DOI 在线验证、Early Access 处理等。

## 核心能力

| 能力 | 说明 |
|------|------|
| **BibTeX 审查修复** | 重复条目检测、缺失字段检测、Early Access 识别与修正、作者数量合规（≤6 全列，≥7 et al.） |
| **引用格式审查** | 连续 `\cite{}` 合并、引用键交叉验证、missing/unused references 检测 |
| **期刊名标准化** | 检查是否使用 IEEE 标准宏（如 `IEEE_J_WCOM`），自动匹配替换建议 |
| **DOI 在线验证** | 通过 DOI 查询验证元数据（标题、作者、年份），检测错误 DOI |
| **格式规范检查** | @article/@inproceedings 类型、页码格式（`--`）、标题大小写保护 |
| **扩展条目支持** | @book, @techreport, @standard (IEEE/3GPP/ISO), @electronic, @misc (arXiv), @patent 等 |

## 工作模式

### 模式 A：全面审查

`"检查参考文献"` → 自动执行：文件定位 → 结构性检查 → 引用交叉验证 → 格式检查 → 输出报告（按严重/警告/建议分级）

### 模式 B：DOI 验证

`"验证 DOI"` → 逐条在线验证 DOI，比对元数据，标记不匹配或无法解析的条目

### 模式 C：单条修复

用户指定某个条目 → 定位修复，展示 Before/After 确认后执行

### 模式 D：新增参考文献

用户提供 DOI/标题/作者 → 搜索论文 → 生成规范 BibTeX → 查重 → 建议插入位置

## IEEE 参考文献核心规范

- 期刊名使用 IEEE 标准宏（IEEEabrv.bib 定义）
- 作者 ≤6 位全列，≥7 位用 et al.（通过 BSTcontrol 控制）
- Early Access：删除 `pages`，添加 `note = {early access}`
- 相邻 `\cite{a}, \cite{b}` 合并为 `\cite{a, b}`
- 页码使用双连字符 `--`

## 目录结构

```
ieee-reference-manager/
├── SKILL.md
└── references/
    ├── ieee-reference-rules.md     ← IEEE 格式规范详细参考
    └── utility-scripts.md          ← 辅助脚本说明
```

## 安装

```bash
cp -r ieee-reference-manager ~/.claude/skills/
```

## 触发词

`检查参考文献`、`修复引用格式`、`验证 DOI`、`整理 bib 文件`、`参考文献审查`
