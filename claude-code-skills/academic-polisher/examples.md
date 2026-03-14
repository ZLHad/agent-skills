# Academic Polisher - 使用示例

## 示例 1：简单中文段落润色

### 用户输入
```
我们提出了一种新的资源分配算法来优化SAGIN网络的性能。
```

### Claude 输出
```markdown
## 🎯 润色后的版本

### 原文
我们提出了一种新的资源分配算法来优化SAGIN网络的性能。

### 润色后
We propose a novel resource allocation algorithm to optimize the performance of Space-Air-Ground Integrated Networks (SAGIN).

### 📝 修改说明
1. "我们提出" → "We propose"（现在时，描述自己的工作）
2. "新的" → "novel"（学术用词）
3. "SAGIN网络" → "Space-Air-Ground Integrated Networks (SAGIN)"（首次出现给全称）
4. "性能" → "performance"（直译即可）
```

---

## 示例 2：中英文混合段落

### 用户输入
```
我们的DRL算法主要考虑了三个指标：latency、energy consumption和QoS。实验表明这个方法比greedy algorithm好30%。
```

### Claude 输出
```markdown
## 📋 诊断报告

### 问题：
1. ❌ 中英文混合
2. ⚠️ DRL 首次出现需要全称
3. ⚠️ "好30%" 表达不够准确
4. ⚠️ 建议列表格式

## 🎯 润色后的版本

### 润色后（版本 1）
The proposed Deep Reinforcement Learning (DRL) algorithm jointly considers three key metrics: latency, energy consumption, and Quality of Service (QoS). Simulation results demonstrate that the proposed method achieves 30\% performance improvement compared to the greedy algorithm.

### 润色后（版本 2 - 更详细）
The proposed Deep Reinforcement Learning (DRL) algorithm is designed to jointly optimize three critical performance metrics:
\begin{itemize}
\item Latency: end-to-end delay from task generation to completion
\item Energy consumption: total energy cost including transmission and computation
\item Quality of Service (QoS): user satisfaction level measured by task completion rate
\end{itemize}
Extensive simulations demonstrate that the proposed method achieves a 30\% improvement in overall performance compared to the greedy algorithm baseline.
```

---

## 示例 3：数学公式润色

### 用户输入
```
优化目标是 min sum T_i，其中T_i包括传输时间t_trans_i和计算时间t_comp_i
```

### Claude 输出
```markdown
## 📋 诊断报告

### 问题：
1. ❌ 公式格式不规范
2. ❌ 符号命名不一致（T_i vs t_trans_i）
3. ❌ 缺少变量定义
4. ⚠️ 建议使用独立公式环境

## 🎯 润色后的版本

### 润色后
The objective is to minimize the total latency of all tasks:
\begin{equation}
\min_{x} \sum_{i=1}^{N} T_i = \sum_{i=1}^{N} \left( T_i^{\text{trans}} + T_i^{\text{comp}} \right)
\label{eq:objective}
\end{equation}
where $T_i^{\text{trans}}$ and $T_i^{\text{comp}}$ represent the transmission latency and computation latency of task $i$, respectively, and $N$ denotes the total number of tasks.

### 改进点：
1. ✅ 使用 equation 环境
2. ✅ 统一符号风格（都用 $T$ 开头）
3. ✅ 使用上标区分（$T^{\text{trans}}$）
4. ✅ 定义所有变量
5. ✅ 添加标签便于引用
```

---

## 示例 4：已有英文的润色

### 用户输入
```
In this paper, we propose a new method. This method is very good. It can reduce the delay a lot. We use DRL to do this.
```

### Claude 输出
```markdown
## 📋 诊断报告

### 问题：
1. ❌ 句子过于简短，缺少连贯性
2. ❌ 用词口语化："very good", "a lot"
3. ❌ 缺少量化数据
4. ❌ 重复使用 "This method"
5. ⚠️ 逻辑跳跃，缺少过渡

## 🎯 润色后的版本

### 润色后
This paper proposes a novel Deep Reinforcement Learning (DRL)-based method for latency reduction in computation offloading scenarios. The proposed approach effectively minimizes end-to-end delay by intelligently optimizing task allocation decisions. Simulation results demonstrate that the method achieves substantial latency reduction compared to existing approaches.

### 📝 主要改动：
1. 合并短句，提高流畅性
2. "very good" → "effectively minimizes"（具体说明好在哪里）
3. "reduce delay a lot" → "substantial latency reduction"（更学术）
4. 补充 "computation offloading scenarios"（说明应用场景）
5. 添加 "intelligently optimizing"（说明方法）
6. 建议补充具体百分比数据

### ⚠️ 建议：
如果有具体数据，可以改为：
"achieves X% latency reduction compared to baseline methods"
```

---

## 示例 5：含复杂公式的系统模型

### 用户输入
```
系统模型：考虑N个UAV和M个用户，UAV i的位置是(x_i, y_i, h)，用户j的位置是(x_j, y_j, 0)。信道增益可以表示为 g_ij = g0 * d_ij^(-alpha)，其中d_ij是距离。
```

### Claude 输出
```markdown
## 🎯 润色后的版本

### 润色后

\subsection{System Model}

We consider a SAGIN scenario consisting of $N$ Unmanned Aerial Vehicles (UAVs) and $M$ ground users. The 3D Cartesian coordinate of UAV $i$ is denoted as $(x_i, y_i, h)$, where $h$ represents the fixed altitude of all UAVs. The location of ground user $j$ is represented as $(x_j, y_j, 0)$.

The channel power gain between UAV $i$ and user $j$ is modeled using the free-space path loss model:
\begin{equation}
g_{ij} = g_0 d_{ij}^{-\alpha}
\label{eq:channel_gain}
\end{equation}
where $g_0$ denotes the channel gain at the reference distance, $\alpha$ is the path loss exponent, and $d_{ij}$ represents the Euclidean distance between UAV $i$ and user $j$, calculated as:
\begin{equation}
d_{ij} = \sqrt{(x_i - x_j)^2 + (y_i - y_j)^2 + h^2}
\label{eq:distance}
\end{equation}

### 📝 改进点：

1. **结构化**：添加 subsection 标题
2. **符号规范**：
   - $N$, $M$ 大写表示数量
   - $i \in \{1, \ldots, N\}$, $j \in \{1, \ldots, M\}$ 下标
   - 使用 $g_{ij}$ 而非 $g_ij$（更清晰）

3. **公式格式**：
   - 独立公式使用 equation 环境
   - 添加 \label{} 便于引用
   - 补充距离计算公式

4. **变量定义**：
   - 每个变量都有明确说明
   - 说明坐标系统（3D Cartesian）
   - 说明假设（fixed altitude）

5. **模型说明**：
   - 明确使用 "free-space path loss model"
   - 说明各参数的物理意义
```

---

## 使用技巧

### 技巧 1：分段处理长文本
```
我有一段很长的 Introduction，可以分几次给你：
第一段：[粘贴第一段]
```

Claude 会逐段润色，保持上下文连贯。

### 技巧 2：指定润色重点
```
帮我润色这段，重点是：
1. 强化动机
2. 补充引用
3. 使表达更简洁

[粘贴文本]
```

### 技巧 3：选择输出风格
```
润色这段，给我两个版本：
1. 简洁版（用于 Abstract）
2. 详细版（用于 Introduction）

[粘贴文本]
```

### 技巧 4：保留特定格式
```
润色时请保留：
- \cite{} 引用标记
- \ref{} 图表引用
- 自定义命令 \mycommand{}

[粘贴文本]
```

---

## 常见场景

### 场景 1：快速润色一个句子
**输入**：`这个算法很高效`
**输出**：`The proposed algorithm demonstrates high efficiency in terms of computational complexity and convergence speed.`

### 场景 2：翻译+润色一个段落
**输入**：中文段落
**输出**：
- 英文学术版本
- 问题诊断
- 修改说明

### 场景 3：修正英文语法和表达
**输入**：不够学术的英文
**输出**：
- 润色版本
- 语法错误修正
- 学术化改写

### 场景 4：规范化数学公式
**输入**：格式不规范的公式
**输出**：
- LaTeX 规范格式
- 变量定义
- 使用建议

---

## 完整交互示例

### 示例：中英文混合段落润色

**用户**：
```
帮我润色：我们的算法使用DRL来解决这个offloading problem，主要优化delay和energy两个目标。实验结果表明我们的方法比baseline好很多。
```

**Claude 响应**：

```markdown
## 📋 诊断报告

### 发现的问题：
1. ❌ 中英文混合
2. ❌ 术语不规范：DRL、offloading problem、delay、energy、baseline
3. ❌ 表达口语化："好很多"
4. ❌ 缺少量化数据
5. ⚠️ 时态问题："实验结果表明" 应该用过去时

---

## 🎯 润色后的版本

### 原文
我们的算法使用DRL来解决这个offloading problem，主要优化delay和energy两个目标。实验结果表明我们的方法比baseline好很多。

### 润色后（学术英文）
The proposed algorithm employs Deep Reinforcement Learning (DRL) to address the computation offloading problem, with the primary objective of jointly optimizing latency and energy consumption. Extensive simulation results demonstrate that the proposed method significantly outperforms baseline approaches, achieving an average improvement of X% in latency reduction and Y% in energy savings.

---

## 📝 修改说明

1. **"我们的算法"** → **"The proposed algorithm"**
   - 理由：学术论文常用 "proposed" 指代自己的工作

2. **"使用DRL"** → **"employs Deep Reinforcement Learning (DRL)"**
   - 理由：首次出现需要全称+缩写

3. **"offloading problem"** → **"computation offloading problem"**
   - 理由：使用完整术语

4. **"delay和energy"** → **"latency and energy consumption"**
   - 理由：使用规范术语

5. **"好很多"** → **"significantly outperforms... achieving X% and Y%"**
   - 理由：用具体数据替代主观评价

6. **时态调整**：
   - 描述自己的方法：现在时 "employs"
   - 描述实验结果：过去时 "demonstrated"

---

## ⚠️ 需要补充

请提供具体的实验数据：
- X% = 延迟降低的百分比
- Y% = 能耗节省的百分比
```

---

### 示例：含数学公式的润色

**用户**：
```
The objective function can be written as: min T = T_trans + T_comp, where T_trans is transmission time, T_comp is computing time.
```

**Claude 响应**：

```markdown
## 📋 诊断报告

### 问题：
1. ⚠️ 公式应该使用独立格式（equation 环境）
2. ⚠️ 缺少优化变量
3. ⚠️ 符号定义可以更规范
4. ✅ 英文表达基本正确，但可以更学术化

---

## 🎯 润色后的版本

### 原文
The objective function can be written as: min T = T_trans + T_comp, where T_trans is transmission time, T_comp is computing time.

### 润色后（版本 1：详细版）

The total latency minimization problem is formulated as:
\begin{equation}
\min_{x} T_{\text{total}}(x) = T_{\text{trans}}(x) + T_{\text{comp}}(x)
\label{eq:latency_min}
\end{equation}
where $T_{\text{trans}}(x)$ and $T_{\text{comp}}(x)$ represent the transmission latency and computation latency, respectively, as functions of the offloading decision $x$.

### 润色后（版本 2：简洁版）

The objective is to minimize the total latency:
\begin{equation}
\min_{x} T = T_{\text{trans}} + T_{\text{comp}}
\label{eq:total_latency}
\end{equation}
where $T_{\text{trans}}$ and $T_{\text{comp}}$ denote the transmission and computation latency, respectively.

---

## 📝 修改说明

1. **使用 equation 环境**：重要公式应该独立成行
2. **添加优化变量**：`\min_{x}` 明确是对什么进行优化
3. **符号规范化**：`T_{\text{trans}}` 使用 `\text{}` 使下标显示为正体
4. **表达优化**："can be written as" → "is formulated as"（更学术）
```
