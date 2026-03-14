---
name: literature-search
description: >
  学术文献检索助手，专为撰写 Related Work / 文献综述设计。
  从 IEEE Xplore、Semantic Scholar、arXiv 检索论文，默认聚焦 IEEE 顶刊/顶会。
  支持交互式需求确认、多轮多关键词搜索、BibTeX 导出、摘要收集。
  触发词：查文献、搜论文、literature search、related work、文献综述、
  找参考文献、搜相关工作、survey papers、search papers
allowed-tools: Read, Edit, Bash, Write, Glob, Grep, WebSearch, WebFetch, AskUserQuestion
model: opus
---

# Literature Search — 文献检索助手

专为撰写 Related Work / 文献综述设计的学术文献检索工具。从 IEEE Xplore、Semantic Scholar、arXiv 等学术数据库检索论文，收集元数据、摘要和 BibTeX，为后续撰写文献综述提供素材。

## 核心能力

| 数据源 | 方法 | 说明 |
|--------|------|------|
| IEEE Xplore | REST API (无需密钥) | 默认首选，IEEE 顶刊/顶会全覆盖 |
| Semantic Scholar | Graph API v1 | 跨数据库搜索，含 TL;DR 和引用数 |
| arXiv | Atom API | 预印本，最新研究进展 |
| Google Scholar | WebSearch 备用 | 补充搜索，覆盖面广 |

## 工作流程

### 阶段 1：交互式需求确认（必须）

在开始搜索之前，**必须**与用户确认以下信息。使用 AskUserQuestion 工具逐一确认：

**第一轮提问（核心需求）：**

向用户提出以下问题，可以一次性提出：

1. **研究主题**：你要查找的具体研究主题是什么？（例如："movable antenna beamforming"、"LLM-based network optimization"）
2. **使用场景**：这些文献用于什么？（例如：Related Work 的某个子节、完整综述、开题调研）
3. **期刊/会议偏好**：
   - 默认 IEEE 顶刊（TWC, TCOM, TSP, JSAC, TMC, TCCN, TVT, IoT-J, WCL 等）
   - 是否需要包含会议论文（ICC, GLOBECOM, WCNC, INFOCOM 等）
   - 是否需要扩展到非 IEEE 源（arXiv, Semantic Scholar）
4. **时间范围**：优先查找哪个时间段的论文？（默认近 3 年）
5. **最终精选数量**：最终报告中希望保留多少篇？给出目标区间，例如：
   - Related Work 某个子节：10-15 篇
   - 完整 Related Work：20-40 篇
   - 开题调研/综述：50-80 篇
   - 默认建议：**25-40 篇**（搜索阶段会广泛收集，最终报告精选到目标区间）
6. **已知文献**：是否已经有一些相关论文？（有助于确定搜索方向和避免重复）

**根据用户回答，确定搜索策略：**
- 拆解 2-5 组搜索关键词（不同角度、不同术语）
- 确定数据源优先级
- 确定筛选条件（年份、期刊、引用数等）
- 根据目标数量，预估每个子方向分配的论文名额

向用户简要展示搜索计划（含各子方向预估数量）后，确认是否开始。

### 阶段 2：多轮搜索执行

使用 Python 脚本执行搜索：

```bash
cd /Users/zhanglinghao/Documents/Code/Skills/skills/claude-code-skills/literature-search
python3 scripts/search.py --keywords "keyword1" "keyword2" \
  --sources ieee semantic_scholar arxiv \
  --max-results 30 \
  --time-range 3y \
  --sort relevance \
  --output-dir results
```

**多轮搜索策略：**

不要只用一组关键词！针对同一主题，从不同角度搜索：

1. **核心术语搜索**：直接使用研究主题的标准术语
2. **同义词/变体搜索**：使用不同表述（如 "reconfigurable intelligent surface" vs "RIS" vs "intelligent reflecting surface"）
3. **方法论搜索**：从技术方法角度搜索（如 "deep reinforcement learning resource allocation"）
4. **应用场景搜索**：从应用角度搜索（如 "UAV communication trajectory optimization"）
5. **补充搜索**：如果某个子方向结果不够，追加搜索

每轮搜索结果会自动去重合并。

**Google Scholar 补充搜索**（当 API 搜索结果不够时）：

使用 WebSearch 工具搜索：
```
site:scholar.google.com "exact phrase" related topic
```

或搜索特定期刊：
```
site:ieeexplore.ieee.org "keyword" "IEEE Transactions on"
```

### 阶段 3：结果整理与最终报告生成

搜索完成后，合并所有轮次结果去重，然后进行分析整理：

1. **合并去重**：`python3 scripts/search.py --merge results/*_papers.json -o results`
2. **读取合并后 JSON**，筛选 IEEE 顶刊/顶会论文（排除 early access、低相关度论文）
3. **分类整理**：根据论文内容将论文归入 Related Work 子方向
4. **生成分类映射 JSON**（categories.json）并调用最终报告生成

#### 生成最终报告

准备分类映射文件 `categories.json`，格式为 `{"子方向名称": [DOI列表]}`:

```json
{
  "A. AIGC/LLM Inference at Edge": [
    "10.1109/TMC.2024.3415661",
    "10.1109/TWC.2024.3497923"
  ],
  "B. SAGIN Resource Management": [
    "10.1109/JSAC.2024.3459073"
  ]
}
```

然后生成最终报告：

```bash
python3 scripts/search.py --finalize results/merged_papers.json \
  --categories categories.json \
  --topic "Hierarchical AIGC Inference in SAGIN" \
  -o results
```

输出多文件结构（总览 + 子方向独立文件）：

```
results/
├── {timestamp}_00_overview.md          ← 总览：推荐表 + 子方向文件链接
├── {timestamp}_01_AIGC_LLM_Inference.md   ← 子方向 A 完整论文详情
├── {timestamp}_02_SAGIN_Resource.md        ← 子方向 B 完整论文详情
├── ...
├── {timestamp}_final_report.bib        ← 所有精选论文 BibTeX
└── {timestamp}_final_report.json       ← 结构化 JSON
```

#### 总览文件模版（`_00_overview.md`）

```markdown
# Related Work Literature Survey Report

**Date**: 2026-03-15
**Topic**: Hierarchical AIGC Inference in SAGIN
**Total Selected**: 35 papers
**Sub-directions**: 6

---

## Sub-direction Files

- [A. AIGC/LLM Inference at the Edge]({timestamp}_01_AIGC_LLM_Inference.md) (8 papers)
- [B. SAGIN Resource Management]({timestamp}_02_SAGIN_Resource.md) (6 papers)
- ...

---

## Overview: Recommended Papers by Sub-direction

### [A. AIGC/LLM Inference at the Edge]({timestamp}_01_AIGC_LLM_Inference.md)

| # | Paper | Venue | Year | Citations | Core Contribution |
|---|-------|-------|------|-----------|-------------------|
| 1 | [Beyond the Cloud: Edge Inference...](url) | IEEE TWC | 2025 | 45 | LLM边缘推理框架... |
| 2 | [QoE-Aware Offloading for AIGC...](url) | IEEE TMC | 2025 | 8 | AIGC QoE优化... |

### [B. SAGIN Resource Management]({timestamp}_02_SAGIN_Resource.md)
...
```

#### 子方向文件模版（`_01_*.md`）

```markdown
# A. AIGC/LLM Inference at the Edge

**Topic**: Hierarchical AIGC Inference in SAGIN
**Papers in this sub-direction**: 8
[← Back to Overview](.)

---

#### 1. [Beyond the Cloud: Edge Inference for Generative LLMs](url)

**Authors**: Author1, Author2, ...
**Year**: 2025
**Venue**: IEEE Transactions on Wireless Communications
**Citations**: 45
**DOI**: 10.1109/TWC.2024.3497923

**Abstract**: [完整摘要，不截断]

**TL;DR**: [如有]

<details><summary>BibTeX</summary>

bibtex
@article{Author2025, ... }

</details>
```

### 阶段 4：与用户确认结果

向用户展示最终报告后：

1. 询问是否需要**补充搜索**某个子方向
2. 询问是否需要**排除/增加**某些论文
3. 询问是否需要**调整分组方式**
4. 确认最终结果后，可将 BibTeX 导出到用户论文项目目录

## 搜索参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--keywords` | 搜索关键词（多个空格分隔） | 必填 |
| `--sources` | 数据源列表 | ieee semantic_scholar arxiv |
| `--max-results` | 每源每轮最大结果数 | 30 |
| `--time-range` | 时间范围：1y/3y/5y/all | 3y |
| `--sort` | 排序：relevance/date/citations | relevance |
| `--output-dir` | 输出目录 | results |
| `--output-format` | 输出格式：json/markdown/bibtex/all | all |
| `--journals` | 限定期刊（逗号分隔） | 无（不限） |
| `--min-citations` | 最低引用数 | 0 |

## IEEE 顶刊/顶会参考

### 通信领域 IEEE 顶刊
- **IEEE JSAC** — J. Sel. Areas Commun.（综合最佳，影响因子最高）
- **IEEE TWC** — Trans. Wireless Commun.（无线通信旗舰）
- **IEEE TCOM** — Trans. Commun.（通信理论与系统）
- **IEEE TSP** — Trans. Signal Process.（信号处理）
- **IEEE TMC** — Trans. Mobile Comput.（移动计算）
- **IEEE TCCN** — Trans. Cognitive Commun. Netw.
- **IEEE TVT** — Trans. Veh. Technol.
- **IEEE IoT-J** — Internet of Things J.
- **IEEE WCL** — Wireless Commun. Lett.
- **IEEE CL** — Commun. Lett.

### 通信领域 IEEE 顶会
- **IEEE GLOBECOM** — Global Commun. Conf.
- **IEEE ICC** — Int. Conf. Commun.
- **IEEE WCNC** — Wireless Commun. Netw. Conf.
- **IEEE INFOCOM** — Int. Conf. Computer Commun.
- **IEEE VTC** — Veh. Technol. Conf.

### CS/AI 领域补充
- **IEEE TPAMI** — Trans. Pattern Anal. Mach. Intell.
- **IEEE TNNLS** — Trans. Neural Netw. Learn. Syst.
- **NeurIPS, ICML, ICLR, AAAI** — AI 顶会

## 依赖安装

```bash
pip install requests feedparser
```

## 注意事项

- IEEE Xplore 搜索使用网页 REST 端点，无需 API Key，但有速率限制，搜索间隔建议 ≥ 1 秒
- Semantic Scholar API 免费层 1000 次/5min，一般够用
- arXiv API 无需密钥，但建议控制请求频率
- 多轮搜索时自动去重（基于 DOI → arXiv ID → 标题哈希）
- 如果某个源连接失败，会自动跳过并使用其他源
- 搜索结果保存在 `results/` 目录，包含时间戳，不会覆盖历史记录
- **Markdown 报告中的摘要保持完整**，不做截断，确保后续精读和综述撰写有完整信息

## 使用案例

### 案例：为 "SAGIN 中分层 AIGC 推理" 论文撰写 Related Work

**用户需求**：论文涉及 AIGC 边缘推理、SAGIN 架构、语义压缩、UAV-LEO 计算卸载、双时间尺度优化、DRL 资源分配。需要 IEEE 顶刊近 3 年论文。

**执行过程**：

1. **分析论文主题**，拆解为 7 个搜索子方向
2. **10 轮搜索**，每轮使用不同关键词组合：
   - "AIGC" "edge inference"
   - "generative AI" "mobile edge computing"
   - "space-air-ground integrated network" "resource allocation"
   - "semantic communication" "task-oriented"
   - "UAV" "computation offloading" "edge computing"
   - "two-timescale" "optimization" "resource allocation"
   - "deep reinforcement learning" "resource allocation" "wireless network"
   - "model caching" "edge computing"
   - "LEO satellite" "edge computing" "task offloading"
   - "large language model" "inference" "edge"
3. **合并去重**：289 篇 → 286 篇（去重后）
4. **筛选 IEEE 顶刊**：286 篇 → 135 篇（IEEE Trans/Journal + 顶会，2023+ 年）
5. **按子方向分类**，为每个方向推荐 5-8 篇核心论文
6. **生成最终报告**：总览推荐表 + 完整论文详情 + BibTeX

**最终输出**：6 个子方向共约 35 篇精选论文，含完整摘要和 BibTeX，可直接用于撰写 Related Work。
