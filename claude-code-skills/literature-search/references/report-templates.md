# 最终报告模版

最终报告采用多文件结构（总览 + 子方向独立文件）：

```
results/
├── {timestamp}_00_overview.md          <- 总览：推荐表 + 子方向文件链接
├── {timestamp}_01_AIGC_LLM_Inference.md   <- 子方向 A 完整论文详情
├── {timestamp}_02_SAGIN_Resource.md        <- 子方向 B 完整论文详情
├── ...
├── {timestamp}_final_report.bib        <- 所有精选论文 BibTeX
└── {timestamp}_final_report.json       <- 结构化 JSON
```

## 总览文件模版（`_00_overview.md`）

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

## 子方向文件模版（`_01_*.md`）

```markdown
# A. AIGC/LLM Inference at the Edge

**Topic**: Hierarchical AIGC Inference in SAGIN
**Papers in this sub-direction**: 8
[<- Back to Overview](.)

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
