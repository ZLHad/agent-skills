# 针对不同章节的润色策略

## Abstract

- **简洁明了**：每句话都要有信息量
- **结构**：背景 → 问题 → 方法 → 结果 → 结论
- **避免**：引用、公式、缩写（除非极常见）
- **长度**：IEEE 一般 150-250 词

### 示例模板
```
[Background] Recent advances in X have enabled Y.
[Problem] However, existing approaches face challenges in Z.
[Method] In this paper, we propose a novel A that leverages B to address C.
[Results] Extensive simulations demonstrate that the proposed method achieves X% improvement in Y compared to baseline methods.
[Conclusion] The results validate the effectiveness of the proposed approach for Z applications.
```

---

## Introduction

- **宽→窄**：从大背景逐步聚焦到具体问题
- **动机**：清晰说明为什么需要这个研究
- **贡献**：明确列出（通常用 bullet points）
- **结构**：通常 4-6 段

### 段落结构示例
```latex
% 第 1 段：大背景
The proliferation of X has led to Y...

% 第 2 段：具体问题
However, existing solutions face several challenges...

% 第 3 段：相关工作的不足
While recent studies [X, Y] have investigated..., they have limitations in...

% 第 4 段：我们的方法
To address these challenges, this paper proposes...

% 第 5 段：主要贡献
The main contributions of this work are summarized as follows:
\begin{itemize}
\item Contribution 1: ...
\item Contribution 2: ...
\item Contribution 3: ...
\end{itemize}

% 第 6 段：论文结构
The remainder of this paper is organized as follows...
```

---

## Related Work

- **分类组织**：按主题或方法分组
- **批判性评述**：不仅总结，还要指出不足
- **与本文对比**：突出本文的独特性

---

## System Model / Problem Formulation

- **精确定义**：所有符号、假设、约束
- **公式清晰**：重要公式独立成行并编号
- **逻辑严密**：从简单到复杂，层层推进

---

## Proposed Method

- **可复现**：足够详细，他人能实现
- **算法伪代码**：使用 algorithm2e 或 algorithmic 包
- **复杂度分析**：时间/空间复杂度

---

## Simulation Results

- **客观描述**：基于数据，不过度解读
- **图表引用**："As shown in Fig. X, ..."
- **对比分析**：与 baseline 对比，说明优势
- **参数设置**：表格列出所有参数

---

## Conclusion

- **总结贡献**：简明扼要
- **局限性**：（可选）诚实说明
- **未来工作**：指出研究方向
