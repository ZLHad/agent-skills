# Example Prompts 示例Prompt库

本文件提供符合完整性要求的Prompt示例。注意：最终输出的Prompt必须**完整自包含**，生图AI无需额外信息即可正确生成。

---

## 示例1：长短期上下文特征融合架构图（含详细网络结构）

### 完整Prompt

```
# 基于长短期上下文挖掘的自适应重构触发机制

## 1. 整体设计
- **图片类型**：算法框架图，展示特征提取与融合流程
- **视觉风格**：矢量扁平风格，学术蓝绿配色，模块化设计
- **画布比例**：16:9
- **整体布局**：从左到右的水平流水线，分为四个主要区域：输入区→双通道特征提取区→融合区→决策区

## 2. 详细场景描述

**左侧输入区**：
画面最左侧有一个浅灰色背景的滑动窗口模块。内部垂直排列5个小矩形数据块，颜色从浅蓝逐渐加深到深蓝，代表时序观测数据。窗口上方标注标题文字，下方有一个小的橙色矩形表示先验分布输入。

**中央双通道特征提取区（占据画面主体）**：
这是一个大的浅灰色背景区域，内部分为上下两个并行通道：

*上方长期通道（浅蓝色虚线边框区域）*：
- 左侧是一个Transformer自注意力模块，详细绘制：一个矩形框内部显示Multi-Head Attention结构——有三个输入接口分别标注Q、K、V，中间有4个平行的小矩形代表4个attention head，下方有Add&Norm横条，再下方有FFN模块
- 右侧是对比学习去噪模块：显示输入数据分成两个分支（代表两种数据增强视图），每个分支通过一个小型编码器（绘制为3层的小型神经网络结构：输入→隐藏层→输出），两个分支的输出用双向虚线连接，中间标注相似度计算符号
- 通道输出一个深蓝色圆形节点

*下方短期通道（浅绿色虚线边框区域）*：
- 内部绘制一个1D卷积网络的2.5D结构：3个层叠的特征图块，从左到右尺寸略微递减，每个块用不同深度的绿色表示
- 卷积核用小矩形滑动窗口示意
- 通道输出一个深绿色圆形节点

**右侧融合区**：
一个橙色边框的融合模块，内部显示门控机制：上方的蓝色输入和下方的绿色输入分别乘以权重系数后相加，用⊗和⊕符号表示，输出到右侧。

**最右侧决策区**：
一个紫色边框的策略网络模块，内部详细绘制一个小型MLP结构：3个输入节点→6个隐藏节点（一层）→1个输出节点。输出分叉为两个分支，分别指向一个红色小方块和一个灰色小方块，代表两种决策结果。

## 3. 连接与数据流
- 输入区到双通道：两条深灰色实线箭头，分别指向上下两个通道
- 先验分布到Transformer：一条橙色虚线箭头，标注"prior"
- 长期通道内部：蓝色实线箭头连接各模块
- 短期通道内部：绿色实线箭头连接各模块
- 双通道输出到融合模块：上方蓝色箭头标注"α"，下方绿色箭头标注"1-α"
- 融合到决策：紫色粗实线箭头
- 决策网络输出分叉：指向红色方块标注"触发重构"，指向灰色方块标注"维持配置"

## 4. 图中文字清单
**模块标题**：
- "Sliding Window 𝒲_t"（滑动窗口上方）
- "Prior π̂_t"（先验分布旁）
- "Long-term Channel"（上通道左上角）
- "Transformer"（Transformer模块内）
- "Multi-Head Attention"（注意力子模块）
- "Contrastive Learning"（对比学习模块）
- "InfoNCE"（对比学习内部）
- "Short-term Channel"（下通道左上角）
- "Conv1D"（卷积网络旁）
- "Adaptive Gating"（融合模块标题）
- "Policy Network π_θ"（策略网络标题）

**数学符号**：
- o_{t-L+1}, ..., o_t（滑动窗口内数据标注）
- h̃_t^L（长期通道输出圆旁）
- h_t^S（短期通道输出圆旁）
- α_t（融合模块内的权重）
- c_t = α_t h̃_t^L + (1-α_t)h_t^S（融合模块下方小字）
- s_t（决策网络输入标注）
- b_t ∈ {0,1}（决策输出旁）

**输出标签**：
- "b_t=1 Trigger"（红色方块旁）
- "b_t=0 Maintain"（灰色方块旁）

## 5. 配色方案
- 长期通道区域背景：浅蓝 #EBF5FB，边框 #3498DB
- 短期通道区域背景：浅绿 #EAFAF1，边框 #27AE60
- Transformer/注意力模块：深蓝 #2980B9
- 卷积网络：绿色系 #27AE60 到 #1E8449
- 融合模块：橙色 #E67E22，背景 #FEF9E7
- 策略网络：紫色 #8E44AD，背景 #F5EEF8
- 触发决策：红色 #E74C3C
- 维持决策：灰色 #95A5A6
- 主箭头：深灰 #333333
- 背景：白色 #FFFFFF

## 6. 重要约束
- 不要在图中显示任何坐标数值、区域编号或尺寸标注
- Transformer和CNN必须显示内部结构，不是简单方框
- 所有数学符号使用斜体
- 确保文字在各自背景上清晰可读

## 7. 图注
Figure X. Architecture of the adaptive reconstruction trigger mechanism based on long-short term context mining. The long-term channel extracts robust trend features through Transformer self-attention and contrastive learning denoising. The short-term channel captures high-frequency perturbations via lightweight Conv1D. The adaptive gating mechanism dynamically fuses dual-channel features to generate the trigger decision context.
```

---

## 示例2：双时间尺度协同优化框架（含时间轴）

### 完整Prompt

```
# 大小时间尺度协同优化框架

## 1. 整体设计
- **图片类型**：时序阶段图 + 算法架构混合
- **视觉风格**：矢量扁平，蓝绿橙三色区分不同尺度，带轻微2.5D效果
- **画布比例**：16:9
- **整体布局**：顶部时间轴 + 下方三层展开（触发层、大尺度优化层、小尺度决策层）

## 2. 详细场景描述

**顶部时间轴**：
画面顶部有一条水平的黑色粗实线作为时间轴，从左向右延伸，右端有箭头。时间轴上有若干垂直短线作为刻度。在特定位置有红色菱形标记代表重构时刻，标注为t_r和t_{r+1}。两个红色菱形之间用双向箭头标注"非重构区间"。时间轴上方有时间刻度的放大示意：大刻度代表Communication Round，小刻度代表Time Slot。

**触发层（时间轴下方第一层）**：
灰色背景的水平条带。左侧有一个简化的空天地网络场景小图（包含1颗卫星、2架无人机、地面基站和用户的简化图标）。中间是一个橙色边框的触发器模块，内部有一个开关图标和标注。右侧输出红色菱形序列，代表重构时刻集合。有箭头从触发器向下指向大尺度优化层，标注"当b_t=1时触发"。

**大尺度优化层（第二层，占较大空间）**：
深蓝色虚线边框的大区域，左上角有标签。内部分为左右两部分：

*左侧优化问题定义*：
- 三组图标分别代表三类优化变量：缓存图标（数据库符号）、计算图标（CPU符号）、带宽图标（管道符号），旁边分别标注变量符号
- 下方是目标函数的简化展示框

*右侧PE-ASO算法流程*：
- 绘制一个流程图，包含6个步骤框：初始化原子群→计算热点强度→构建势能场→计算修正适应度→更新原子质量→原子位置更新
- 在"原子位置更新"步骤旁，有一个小的原子作用力示意图：4个小圆点代表原子，中心有一个红色星形代表最优解，圆点之间有力的箭头
- 流程末端有一个蓝色圆形输出，代表最优配置
- 一条粗红色箭头从此输出向下指向小尺度层，标注"配置约束边界"

**小尺度决策层（第三层）**：
绿色虚线边框的大区域，标签在左上角。内部从左到右：

*左侧状态输入*：
- 小方框列出状态组成（队列长度、信道状态）和动作输出（卸载目标、路由路径）

*中间主动推理模块*：
- 绿色边框的主模块，顶部显示期望自由能公式框
- 内部分为两个小框：左边"认知价值"（蓝色调），右边"实用价值"（橙色调），各有简短说明
- 底部标注"选择argmin ℱ(a)执行"

*右侧TD误差修正模块*：
- 橙色边框模块
- 顶部显示TD误差公式
- 中间一个菱形决策框，标注条件判断
- 下方两个分支：一个标注"正常执行"，另一个展开显示Actor-Critic更新的两行公式
- Actor-Critic内部简要显示两个小型网络结构（各3层全连接）

一条虚线箭头从小尺度层向上弧形连接到触发器，标注"累积代价反馈G_t"

## 3. 连接与数据流
- 时间轴到触发层：垂直虚线连接红色菱形标记与下方对应区域
- 触发器到大尺度层：橙色粗箭头，标注"b_t=1触发"
- 大尺度到小尺度：红色粗箭头，标注配置约束
- 小尺度内部：绿色实线箭头连接模块
- 反馈回路：灰色虚线弧形箭头从小尺度到触发器

## 4. 图中文字清单
**时间轴**：
- "t"（时间轴末端）
- "t_r", "t_{r+1}"（红色菱形下方）
- "Communication Round"（大刻度标注）
- "Time Slot"（小刻度标注）

**触发层**：
- "SAGIN Scenario"（场景图旁）
- "Trigger π_θ"（触发器标题）
- "b_t ∈ {0,1}"（触发器输出）
- "𝒯_R = {t_{r1}, t_{r2}, ...}"（重构时刻集合）

**大尺度层**：
- "Large-scale Global Optimization (at t_r ∈ 𝒯_R)"（层标题）
- "χ^{cache}_{v,m}"、"χ^{comp}_{v,m}"、"χ^{bw}_{e,m}"（变量标注）
- "min J_{large}"（目标函数）
- "PE-ASO Algorithm"（算法标题）
- "Initialize"、"Hotspot Intensity"、"Potential Field"、"Modified Fitness"、"Mass Update"、"Position Update"（流程步骤）
- "χ*"（输出配置）

**小尺度层**：
- "Small-scale Online Decision (interval [t_r, t_{r+1}))"（层标题）
- "State s_t"、"Action a_t"（输入输出）
- "Active Inference"（主动推理标题）
- "ℱ(a) = -Epistemic + Instrumental"（EFE公式简化）
- "Epistemic Value"、"Instrumental Value"（两个价值框）
- "TD Error Correction"（TD模块标题）
- "δ_t = C_{small}(t) + γV(s_{t+1}) - V(s_t)"（TD公式）
- "|δ_t| > δ_{th}?"（判断条件）
- "Critic: φ_V ← ..."、"Actor: φ_π ← ..."（更新公式）
- "G_t"（反馈箭头标注）

## 5. 配色方案
- 时间轴：黑色 #333333
- 重构时刻标记：红色 #E74C3C
- 触发层：灰色背景 #F5F5F5，触发器橙色边框 #E67E22
- 大尺度层：蓝色边框 #2980B9，浅蓝背景 #EBF5FB
- 小尺度层：绿色边框 #27AE60，浅绿背景 #EAFAF1
- 主动推理模块：绿色 #27AE60
- TD修正模块：橙色 #E67E22
- 配置传递箭头：红色 #C0392B
- 反馈箭头：灰色虚线 #7F8C8D

## 6. 重要约束
- 不要显示任何坐标数值或像素尺寸
- Actor-Critic网络需要显示简化的层结构，不是空白方框
- 时间轴要清晰，重构时刻用红色菱形突出
- 三层用不同颜色边框清晰区分
- 所有数学公式使用正确格式

## 7. 图注
Figure X. Dual-timescale collaborative optimization framework. The trigger layer intelligently determines reconstruction moments based on long-short term context mining. At reconstruction moments t_r ∈ 𝒯_R, the large-scale optimization layer executes the PE-ASO algorithm to obtain global configuration χ*. During non-reconstruction intervals [t_r, t_{r+1}), the small-scale decision layer performs real-time offloading and routing decisions based on Active Inference, with TD error detection enabling rapid policy correction under sudden perturbations.
```

---

## 关键检查点

生成Prompt后，确保检查：

| 检查项 | 要求 |
|--------|------|
| 神经网络 | 详细描述层结构，非简单方框 |
| 数学符号 | 逐一列出，格式正确 |
| 文字标注 | 完整列出所有需显示的文字 |
| 元信息 | 不包含坐标、编号、尺寸 |
| 颜色 | 提供具体色号 |
| 连接关系 | 每条箭头的起点、终点、样式、标注 |
| 自包含 | 无需查看原文档即可理解并绘制 |
