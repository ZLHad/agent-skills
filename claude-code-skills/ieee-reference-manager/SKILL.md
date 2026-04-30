---
name: ieee-reference-manager
description: IEEE Trans 论文参考文献全流程管理助手。负责参考文献的格式校验、引用审查、BibTeX 条目修复、期刊名标准化、DOI/元数据在线验证、Early Access 处理、作者数量合规、重复条目检测等。当用户需要"检查参考文献"、"修复引用格式"、"验证 DOI"、"整理 bib 文件"、"参考文献审查"时触发。
allowed-tools: Read, Edit, Write, Bash, Glob, Grep, WebSearch, WebFetch, Agent
model: opus
---

# IEEE Trans 论文参考文献管理助手

## 核心能力

### 1. BibTeX 文件审查与修复
- 检测重复条目（相同 DOI / 相似标题 / 重复 key）
- 检测缺失必要字段（author, title, year, journal/booktitle, pages, volume, number）
- Early Access 文章识别与格式修正（删除占位 `pages = {1--1}`，将 DOI 合并进 note：`note = {early access, doi: 10.1109/XXX}`，并删除独立 `doi` 字段，避免 PDF 渲染重复）
- 作者数量合规检查（BibTeX author 字段必须列出所有作者，禁止使用 `and others` 省略）
- BSTcontrol 配置检查与建议
- 清理未引用的冗余条目

### 2. 引用格式审查
- 连续 `\cite{}` 合并检查（如 `\cite{a}, \cite{b}` → `\cite{a, b}`）
- 引用键名与 .bib 文件交叉验证（检测 missing/undefined references）
- 检查是否有被引用但 .bib 中不存在的条目
- 检查 .bib 中存在但未被引用的条目

### 3. 期刊名标准化
- 检查 journal 字段是否使用 IEEE 标准宏（如 `IEEE_J_WCOM`、`IEEE_J_VT`）
- 检测直接写全名或非标准缩写的条目
- 利用 IEEEabrv.bib / IEEEfull.bib 进行自动匹配和替换建议
- Conference 条目检查 `booktitle` 是否完整

### 4. DOI 与元数据在线验证
- 通过 DOI 在线查询验证论文元数据（标题、作者、年份、期刊）
- 检测 DOI 与实际论文是否匹配
- 检测疑似错误的 DOI（格式不正确、无法解析）
- 验证论文标题是否存在明显拼写错误

### 5. 格式规范检查
- `@article` vs `@inproceedings` 类型检查（期刊用 article，会议用 inproceedings）
- Conference 条目是否有 `booktitle`（不应用 `journal`）
- 页码格式检查（应使用 `--` 而非 `-`）
- 年份合理性检查
- 检查 `copyright`、`langid` 等非必要字段（可建议清理）
- 标题大小写保护检查（缩写词、专有名词是否用 `{{}}` 包裹）

### 6. Zotero/Crossref 污染字段清理
- 默认删除 12 类污染字段：`abstract`, `url`, `urldate`, `copyright`, `langid`, `language`, `annote`, `shorttitle`, `issn`, `keywords`, `file`, `publisher`（`@misc`/`@electronic` 除外）
- 非 Early Access 条目的 `note` 字段若含中文/备注，提示清理
- HTML 实体转义：`&amp;` → `\&`，`–`（em/en-dash）→ `--`（仅 pages 字段）
- Unicode 污染扫描：检测中文字符 `[\u4e00-\u9fff]` 和 Emoji，LaTeX 编译前必须清理

### 7. arXiv → IEEE 正刊升级
- 扫描所有 `@misc` / arXiv 条目，通过 Crossref API 查询是否已正式发表
- 若找到 IEEE 期刊版本，生成替换建议（保留原 key，更新 DOI/journal/volume/pages）
- 仅当 Crossref 返回 IEEE 期刊元数据时才视为正式发表，arXiv 预印本不等同于正式发表

### 8. Key 与第一作者一致性检查
- 从 `author` 字段提取第一作者 last name，与 bib key 前缀比对
- 不匹配时给出重命名建议（如 `xu2025generative` → `zeng2025generative`）

### 9. 扩展条目类型支持
- `@book` / `@incollection`：书籍和章节（需 publisher + address）
- `@techreport`：技术报告（需 institution + number）
- `@standard`：技术标准（IEEE / 3GPP / ISO，需 organization + number）
- `@electronic`：在线资源和网页（需 url + year）
- `@misc`：arXiv 预印本、待发表论文、RFC、白皮书等
- `@phdthesis` / `@mastersthesis`：学位论文（需 school + address）
- `@patent`：专利（需 nationality + number）

## 工作流程

### 模式 A：全面审查（用户说"检查参考文献"、"审查 ref"、"review references"）

**步骤 1：文件定位**
- 自动查找工作目录下的 `.bib` 文件和主 `.tex` 文件
- 识别 IEEEabrv.bib / IEEEfull.bib（标准宏文件，不修改）
- 识别用户的 Ref.bib（待审查文件）

**步骤 2：结构性检查**
- 解析所有 .bib 条目，提取 key、类型、字段
- 检测重复条目（基于 DOI 精确匹配 + 标题模糊匹配）
- 检测缺失必要字段
- 检查条目类型是否正确（article/inproceedings）

**步骤 3：引用交叉验证**
- 从 main.tex 提取所有 `\cite{...}` 引用键
- 与 .bib 文件条目交叉比对
- 报告：missing references（cited but not in bib）、unused entries（in bib but not cited）

**步骤 4：格式检查**
- 连续 \cite 合并检查
- 期刊名宏检查
- Early Access 识别
- 作者数量检查：检测所有使用 `and others` 的条目，标记为**严重警告**，提示需要补全完整作者列表
- 页码格式检查

**步骤 5：输出报告**
以表格形式汇总所有问题，按严重程度排序：
- **严重**（会导致编译错误或参考文献列表错误）
- **警告**（格式不规范但不影响编译）
- **建议**（可改可不改的优化项）

### 模式 B：DOI 验证（用户说"验证 DOI"、"verify references"、"检查论文真实性"）

**步骤 1**：提取所有 .bib 条目的 DOI
**步骤 2**：逐条通过 WebSearch 或 DOI resolver 验证
**步骤 3**：比对返回的元数据与 .bib 中的 title/author/year
**步骤 4**：标记不匹配或无法解析的条目

### 模式 C：单条修复（用户指定某个条目或某个问题）

直接定位并修复，遵循学术写作工作流（先展示 Before/After，等确认后修改）。

### 模式 D：新增参考文献（用户提供论文信息，需要生成 BibTeX 条目）

> ⚠️ **铁律**：作者列表 / 标题 / 卷期页 等元数据**必须来自 Crossref API 反查**，绝不允许凭印象或基于论文标题"推断"作者名。AI 在元数据生成上的幻觉率非常高（实测出现过 5 位作者中 4 位完全错误的案例），DOI 反查是消除幻觉的唯一可靠手段。

**步骤 1：DOI 优先获取**
- 若用户提供 DOI → 直接进步骤 2
- 若用户只提供标题 → 先 WebSearch 找到 DOI（优先 IEEE Xplore / dl.acm.org），再进步骤 2
- 若 DOI 始终找不到 → 显式告诉用户"无法验证元数据，建议用户手动从 IEEE Xplore 复制 BibTeX"，**不要凭推测生成**

**步骤 2：Crossref 反查（强制）**
```
WebFetch https://api.crossref.org/works/{DOI}
```
提取并核对：
- author（完整作者列表，含全名）
- title（标题，注意大小写保护）
- container-title（期刊全名）
- volume / issue / page / published 年月

**步骤 3：DOI 大小写规范化**
Crossref 常返回小写 DOI（如 `10.1109/tmc.2025.xxx`），但 IEEE 约定 publisher prefix 大写：
- ✅ `10.1109/TMC.2025.XXXX`
- ❌ `10.1109/tmc.2025.XXXX`
强制规则：`re.sub(r'(10\.1109/)([a-z]+)\.', lambda m: m.group(1) + m.group(2).upper() + '.', doi)`

**步骤 4：生成 BibTeX**
基于 Crossref 数据 + IEEE 期刊宏（IEEEabrv.bib 中查询匹配宏），生成规范条目。完成后 echo 给用户："以下信息来自 Crossref（DOI: XXX），请最终核对作者列表"。

**步骤 5：去重与命名**
- 检查是否与现有条目重复（DOI 精确匹配 + 标题模糊匹配）
- 检查 key 与第一作者一致（不匹配给重命名建议）
- 建议插入位置

### 模式 E：Zotero-to-IEEE 批量清理（用户说"清理 Zotero 导出"、"批量格式化"、"Zotero bib 转 IEEE"）

**背景**：Zotero/TechRxiv/Crossref 导出的 BibTeX 包含大量 IEEE Trans 不需要的字段，且常含中文 PDF 路径、HTML 实体、Emoji 等导致 LaTeX 编译失败。此模式专门处理此类"脏" .bib 文件。

**步骤 1：深度解析** — 使用大括号深度计数器提取字段（见 [污染字段清单](references/polluted-fields-checklist.md)），避免嵌套 `{{...}}` 解析失败

**步骤 2：污染字段清理** — 默认删除 12 类字段：
`abstract`、`url`、`urldate`、`copyright`、`langid`/`language`、`annote`、`shorttitle`、`issn`、`keywords`、`file`、`publisher`、非 Early Access 条目的 `note`

**步骤 3：HTML 实体转义** — `&amp;` → `\&`，em-dash `–` → `--`（仅 pages 字段）

**步骤 4：Unicode 污染扫描** — 正则 `[\u4e00-\u9fff]` + Emoji，报告给用户确认删除

**步骤 5：期刊名宏标准化** — 默认执行（非可选），使用预设映射表批量替换

**步骤 6：Key-作者一致性检查** — 不匹配给出重命名建议

**步骤 7：Early Access 处理** — 条件：`pages = {1--1}` 精确匹配 OR（无 volume AND 无 number AND 有 journal AND 有 DOI）；操作：删除独立 `doi` 字段，添加 `note = {early access, doi: XXX}`

**步骤 8：arXiv → IEEE 升级扫描** — 对每个 `@misc`/arXiv 条目调用 Crossref API 查询是否已正式发表

**步骤 9：BSTcontrol 保护** — 批处理时必须 `if etype.lower() == 'ieeetranbstctl': continue`

**步骤 10：输出变更报告** — 等用户确认后写入

### 模式 F：Early Access 升级扫描（用户说"检查 Early Access 升级状态"、"verify early access entries"、"投稿前回查 ref"）

**触发场景**：投稿前 / 大修阶段 / 补稿阶段。Early Access 论文从初版到正式发表通常跨数月到 1 年，本地 bib 不会自动同步——必须主动回查。

**步骤 1：扫描候选条目** — `grep -E "early access|note.*=.*early" Ref.bib` 提取所有含 `note = {early access, ...}` 或类似标记的条目

**步骤 2：逐条 Crossref API 查询** — 对每个候选 DOI 调用 `https://api.crossref.org/works/{DOI}`

**步骤 3：状态判定（决策树）**

| Crossref 返回字段 | 判定 | 建议动作 |
|---|---|---|
| volume + issue + page 都齐全 | **正式发表** | 升级条目：补 vol/no/pages/month；note 改为 `doi: ...`（去 "early access" 字样）|
| 仅有 page，无 volume / issue | **准正式发表（过渡态）** | 保守做法：保留 `early access` 字样，仅补 pages |
| volume / issue / page 都没 | **仍 Early Access** | 维持不动 |

**步骤 4：输出升级建议表** — 用户确认后批量 Edit

**注意**：Crossref 的 `issued.date-parts` 字段中 year 比初次 indexing 时间晚，可作为正式发表的旁证（但不是充分条件）。

## 核心规则

### IEEE 参考文献格式规范

1. **作者**：BibTeX 中使用全名（`Last, First Middle`），IEEEtran.bst 自动缩写为首字母
2. **期刊名**：必须使用 IEEE 标准宏（IEEEabrv.bib 中定义），不要硬编码全名或缩写
3. **作者数量**：
   - BibTeX 的 `author` 字段中必须列出所有作者的完整姓名，**不允许使用 `and others` 省略**
   - 作者截断由 BSTcontrol 的 `ctluse_forced_etal` 和 `ctlmax_names_forced_et_al` 自动控制，不在 bib 条目中手动处理
   - 唯一例外：作者数量超过 30 位的论文（如大型 ML 团队论文），此时可列出前 10 位 + `and others`
4. **Early Access 文章**（IEEEtran.bst 默认不显示独立 `doi` 字段，因此 DOI 必须合并进 note）：
   - 删除 `pages` 字段（`pages = {1--1}` 是 IEEE Xplore 占位符）
   - 删除独立 `doi = {...}` 字段（否则与 note 中的 doi 重复渲染）
   - 添加 `note = {early access, doi: 10.1109/XXX.XXXX.XXXXXXX}`（DOI 写在 note 内）
   - 不需要 `volume` 和 `number`
   - 精确识别规则：`pages = {1--1}` 精确匹配 OR（无 volume AND 无 number AND 有 journal AND 有 DOI）；避免把 `{1--16}` 误判为 Early Access
5. **引用合并**：相邻的 `\cite{a}, \cite{b}` 应合并为 `\cite{a, b}`
6. **条目类型**：
   - 期刊论文 → `@article`（需要 `journal`）
   - 会议论文 → `@inproceedings`（需要 `booktitle`，不用 `journal`）
7. **页码**：使用双连字符 `--`（如 `pages = {100--110}`）
8. **DOI 大小写**：IEEE 约定 publisher prefix 大写（`10.1109/TMC...`、`10.1109/TWC...`、`10.1109/JSAC...`），**Crossref 经常返回小写**，必须强制纠正：
   ```python
   re.sub(r'(10\.1109/)([a-z]+)\.', lambda m: m.group(1) + m.group(2).upper() + '.', doi)
   ```
9. **DOI 字段渲染（关键）—— 分 IEEEtran.bst 版本处理**：

   | bst 版本 | `doi=` 字段 | `note = {..., doi: ...}` | 推荐做法 |
   |---|---|---|---|
   | **v1.14+ (2015-)** | ✅ 自动渲染为 "doi: ..." | ✅ 也渲染 | **任选一种**，避免两处都写（会重复）|
   | **v1.12 / v1.13 (2007-2014)** | ❌ **静默忽略，DOI 蒸发** | ✅ 字符串原样输出 | **必须用 note**，否则 PDF 中 DOI 完全消失 |

   **审查时第一步**：`grep -E "version 1\.[0-9]+" IEEEtran.bst` 检测本地版本，再决定建议。

   **常见误判**：IEEE Reference Preparation Assistant 这类外部 validator 期望结构化 `doi=` 字段，但用户本地 bst 是 v1.12 时**绝不能照办**——它的"建议"如果照搬会让 PDF 渲染丢 DOI（实测案例已验证）。

10. **BSTcontrol**：必须在 .bib 文件开头定义，且在 .tex 中用 `\bstctlcite{IEEEexample:BSTcontrol}` 调用

### 命名约定

BibTeX key 推荐格式：`首作者姓年份+关键词`，如 `zhao2019computation`、`li2025secrecy`

### 常见错误清单

| 错误类型 | 示例 | 修复方法 |
|---------|------|---------|
| 重复条目 | 同一论文两个不同 key | 删除重复，统一引用 |
| \cite 未合并 | `\cite{a}, \cite{b}` | → `\cite{a, b}` |
| Early Access 保留占位页码 | `pages = {1--1}` | 删除 pages，DOI 合并进 note |
| Early Access DOI 重复 | 同时有 `doi = {...}` 和 `note = {early access, doi: ...}` | 删除独立 doi 字段 |
| Zotero 污染字段 | `abstract`, `file`, `keywords` 等含中文 | 按污染字段清单批量删除 |
| HTML 实体未转义 | `journal = {...&amp;...}` | `&amp;` → `\&` |
| Unicode 污染 | 中文 `note`、Emoji `⭐` | 扫描 `[\u4e00-\u9fff]` 清理 |
| Key 与第一作者不匹配 | `xu2025xxx` 但第一作者是 Zeng | 重命名为 `zeng2025xxx` |
| arXiv 预印本未升级 | `@misc` 但实际已发 IEEE 期刊 | Crossref 查询后替换为 @article |
| BSTcontrol 误处理 | 批处理时给 `@ieeetranbstctl` 加了 note | 解析时 `continue` 跳过 |
| Conference 用了 @article | `@article` + `booktitle` | 改为 `@inproceedings` |
| 期刊名硬编码 | `journal = {IEEE Trans. Wireless Commun.}` | → `journal = IEEE_J_WCOM` |
| 标题拼写错误 | "Computation Computational" | 核实原文实际标题 |
| 使用 `and others` 省略作者 | `author = {A and others}` | 补全所有作者完整姓名（≤30 位必须全列） |
| 缺失必要字段 | 无 volume/number/pages | 通过 DOI 补全 |
| **作者杜撰** | 凭印象写作者名（5/8 位错） | 必须 Crossref API 反查 (Mode D 步骤 2 强制) |
| **DOI 大小写** | `10.1109/tmc...` | 强制大写 publisher prefix → `10.1109/TMC...` |
| **Early Access 升级未跟进** | 论文已正式发表但 bib 仍标 early access | Mode F 投稿前回查 Crossref，补 vol/no/pages |
| **DOI 字段错误位置** | v1.12 bst 用 `doi=` 字段 | 检测 bst 版本：v1.12 用 `note`，v1.14+ 任选 |
| **杂志/网络文章错用 @article** | IEEE Spectrum 短文用 `@article` 但缺 vol/no/pages | 改用 `@misc` + `howpublished` + `url` |

## 辅助工具集成

项目中可能存在以下辅助脚本，如存在则优先利用：

### analyze_bib.py
- 功能：解析 .bib 文件，检测重复、分析引用覆盖率
- 调用：`python analyze_bib.py`
- 输出：详细分析报告

### nameTranslate.py
- 功能：将 .bib 中硬编码的期刊名替换为 IEEE 标准宏
- 调用：`python nameTranslate.py`
- 依赖：IEEEfull.bib 用于全名匹配

## 参考文件

- [IEEE 参考文献格式规范详细手册](references/ieee-reference-rules.md) - 各条目类型的必需字段、格式要求、IEEE 标准宏用法等完整规范
- [参考文献辅助脚本核心逻辑](references/utility-scripts.md) - analyze_bib.py 和 nameTranslate.py 的核心逻辑提取，可直接调用或参考实现
- [Zotero 污染字段清单与批量清理指南](references/polluted-fields-checklist.md) - 12 类污染字段清单、HTML 实体转义、嵌套大括号安全解析、期刊宏映射表、arXiv→IEEE 升级流程

## 注意事项

1. **不修改 IEEEabrv.bib 和 IEEEfull.bib**——这些是 IEEE 官方标准宏文件
2. **修改前必须展示 Before/After**，等用户确认后再执行（遵循全局 CLAUDE.md 规则）
3. **DOI 验证时注意**：部分新发表或 Early Access 文章可能尚未被搜索引擎索引
4. **标题中的特殊格式**（如 `{{...}}`）是 BibTeX 的大小写保护，不要随意删除
5. **作者列表 / 元数据生成时不要凭印象**——必须 Crossref API 反查（实测案例：5/8 位作者被 AI 杜撰）
6. **不要自动删除未引用条目**——用户可能正在写作中，留待确认
7. **审查 .bib 之前先 grep 检测 IEEEtran.bst 版本**——v1.12 与 v1.14 对 `doi=` 字段处理完全不同，盲目搬用 IEEE Reference Preparation Assistant 的"DOI 移到 doi 字段"建议会导致 PDF 渲染丢 DOI
8. **IEEE Reference Preparation Assistant 是辅助工具，不是绝对权威**——它的建议要结合本地 bst 版本和实际 PDF 渲染结果判断，不能盲从
