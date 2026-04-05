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

## 参考文件

详细参考资料按主题拆分到独立文件，按需查阅：

- [IEEE 顶刊/顶会参考](references/ieee-venues.md) — 通信、CS/AI 领域推荐期刊与会议列表
- [最终报告模版](references/report-templates.md) — 总览文件与子方向文件的输出格式模版
- [使用案例](references/usage-examples.md) — 完整的端到端搜索案例演示
- [搜索参数说明](references/search-params.md) — search.py 所有命令行参数的详细说明

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
cd ~/.claude/skills/literature-search
python3 scripts/search.py --keywords "hybrid action deep reinforcement learning" \
  --sources ieee semantic_scholar arxiv \
  --max-results 30 \
  --time-range 3y \
  --sort relevance \
  --output-dir results
```

完整参数说明见 [搜索参数说明](references/search-params.md)。

#### ⚠️ 关键词构造规则（踩坑经验，必读）

IEEE Xplore 的 REST 搜索对**多词引号短语极其敏感**——多个引号短语之间默认是 AND-of-exact-phrase 匹配，
一次塞入多个并列概念（例如 `"TD3 UAV offloading" "resource allocation"`）几乎必定返回 0 结果。

**推荐做法（单关键词原则）：**
- **每次搜索只传 1 个 2–4 词的精炼短语**（`--keywords "hybrid action reinforcement learning"`）
- **禁止**把多个并列概念拼进同一个 `--keywords` 调用
- 不同角度 → **发起多轮搜索**，每轮 1 个关键词，最后用 `--merge` 合并去重

**如果必须一次传多个关键词：**
- 默认 `--match-mode any`（v2 起默认）会用 OR 连接，保持高召回
- 仅当你**明确**想要 AND-of-exact-phrase 的严格过滤时才用 `--match-mode all`
- 中文关键词：IEEE/arXiv 是英文库，**先翻译成英文**再搜；可以在 `--round-id` 中保留中英文对照便于回溯

#### 多轮搜索策略

不要只用一组关键词！针对同一主题，从不同角度搜索：

1. **核心术语搜索**：直接使用研究主题的标准术语
2. **同义词/变体搜索**：使用不同表述（如 `"reconfigurable intelligent surface"` vs `"RIS"` vs `"intelligent reflecting surface"`）
3. **方法论搜索**：从技术方法角度搜索（如 `"deep reinforcement learning resource allocation"`）
4. **应用场景搜索**：从应用角度搜索（如 `"UAV trajectory optimization"`）
5. **补充搜索**：如果某个子方向结果不够，追加搜索

每轮搜索结果会自动去重合并。

#### 故障处理（Failure Recovery）

| 现象 | 诊断 | 行动 |
|------|------|------|
| 返回 0 篇 | 关键词太长/太具体/AND 过严 | 拆分成更短短语；或 `--match-mode any`；或换同义词 |
| 返回超时/连接失败 | 源暂时不可用 | 换 `--sources arxiv crossref`；先跑 `--health` 诊断 |
| HTTP 429 / Semantic Scholar 长延时 | 被限流 | 等待 60s 后重试；或从 `--sources` 中临时移除 S2 |
| 结果 < 3 篇 | 关键词过于specific | 提示 AI 换更generic的 2-3 词短语重试 |

**搜索前先跑 health check**（强烈推荐）：
```bash
python3 scripts/search.py --health
```
根据返回的 `ok` 和 `latency_ms` 动态调整 `--sources` 列表，跳过不可用源。

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
2. **读取合并后 JSON**，筛选 IEEE 顶刊/顶会论文（默认保留 Early Access；仅当用户明确要求"不要 Early Access / 只要正式发表"时排除）
3. **Early Access 识别启发式**（IEEE REST 不返回 volume/issue，可用以下规则粗判）：
   - `volume == ""` 且 `number == ""` 且 `pages` 为 "1--xx" → 很可能 Early Access
   - 需要精确判断时，对候选 DOI 调用 Crossref：`https://api.crossref.org/works/{doi}`，
     若返回的 `message.volume` 和 `message.page` 均缺失则标记为 Early Access
4. **自动初筛**（当结果 > 40 篇时）：按 venue 白名单 + 年份 + citation count 过滤到目标数量
   - 优先级：`IEEE 顶刊 IF > 与主题的 abstract 相关度 > 引用数 > 发表时间`
5. **分类整理**：根据论文内容将论文归入 Related Work 子方向
6. **生成分类映射 JSON**（categories.json）并调用最终报告生成

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

输出格式和模版详见 [最终报告模版](references/report-templates.md)。

### 阶段 4：与用户确认结果

向用户展示最终报告后：

1. 询问是否需要**补充搜索**某个子方向
2. 询问是否需要**排除/增加**某些论文
3. 询问是否需要**调整分组方式**
4. 确认最终结果后，可将 BibTeX 导出到用户论文项目目录

## 依赖安装

```bash
pip install requests feedparser
```

## 快速参考（踩坑速查）

| 场景 | 正确做法 | 错误做法 |
|------|---------|---------|
| 多关键词搜索 | 1 关键词/轮，多轮 merge | 一次塞 2+ 多词短语到 `--keywords` |
| 中文主题 | 先翻译为英文，`--round-id` 存中英对照 | 直接用中文喂给 IEEE |
| Semantic Scholar 429 | 从 `--sources` 临时去掉 | 硬刷直到 timeout |
| 结果 = 0 | 短语拆短 / 换同义词 / `--match-mode any` | 直接放弃 |
| 结果 > 40 篇 | venue + 年份 + citation 初筛到目标数 | 全部丢给用户手动筛 |
| Early Access 判断 | 默认保留；需要时用 Crossref 补 volume/issue | 靠肉眼看 `contentType` 字段 |
| 读摘要 | 直接读 JSON 字段（完整） | 从 markdown 预览中 grep |

## 注意事项

- IEEE Xplore 搜索使用网页 REST 端点，无需 API Key，但有速率限制，搜索间隔建议 >= 1 秒
- IEEE Xplore 默认匹配模式已改为 `--match-mode any`（OR 连接，高召回），AND 严格模式请显式传 `--match-mode all`
- Semantic Scholar API 免费层 1000 次/5min，但经常 429 限流；搜索前跑 `--health` 确认可用性
- arXiv API 无需密钥，但建议控制请求频率
- Crossref 可作为 DOI 元数据的权威来源，用于补全 volume/issue/pages 和识别 Early Access
- 多轮搜索时自动去重（基于 DOI → arXiv ID → 标题哈希）
- 如果某个源连接失败，会自动跳过并使用其他源
- 搜索结果保存在 `results/` 目录，包含时间戳，不会覆盖历史记录
- **JSON 和 Markdown 报告中的摘要都保持完整**，不做截断；若只读 markdown 截取了前 N 字符，请改读 `*_papers.json` 的 `abstract` 字段
- IEEE 顶刊/顶会完整列表见 [IEEE 顶刊/顶会参考](references/ieee-venues.md)
