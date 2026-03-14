# Literature Search — 文献检索助手

学术文献检索工具，专为撰写 Related Work / 文献综述设计。从 IEEE Xplore、Semantic Scholar、arXiv 等数据库检索论文，自动去重评分，生成分方向整理报告和 BibTeX。

## 核心特性

- **多数据源搜索**：IEEE Xplore（REST API，无需密钥）、Semantic Scholar（Graph API v1）、arXiv（Atom API）、Crossref（元数据补充）
- **多轮多关键词**：同一主题从不同角度搜索（核心术语、同义词、方法论、应用场景），自动去重
- **智能评分排序**：基于关键词匹配（0-0.5）+ 时效性（0-0.15）+ 引用数（0-0.15）+ 质量信号（0-0.2）
- **交互式工作流**：搜索前确认主题、期刊偏好、时间范围、目标数量
- **多文件报告**：总览文件 + 每个子方向独立 MD + BibTeX + JSON
- **BibTeX 元数据准确**：经 Crossref 交叉验证，字段完全匹配

## 四阶段工作流

```
1. 交互式需求确认 → 2. 多轮搜索执行 → 3. 结果整理与报告生成 → 4. 用户确认与补充
```

### 阶段 1：需求确认

确认研究主题、期刊/会议偏好、时间范围（默认近 3 年）、最终精选数量（默认 25-40 篇）、已知文献。

### 阶段 2：多轮搜索

针对同一主题，使用 2-5 组关键词从不同角度搜索。每轮结果自动去重合并（基于 DOI → arXiv ID → 标题哈希）。

### 阶段 3：整理报告

合并去重 → 筛选顶刊 → 按子方向分类 → 生成最终报告。

### 阶段 4：用户确认

补充搜索、增减论文、调整分组，确认后导出 BibTeX。

## 输出文件结构

```
results/
├── {ts}_00_overview.md              ← 总览：子方向索引 + 推荐论文表
├── {ts}_01_SubDirection_A.md        ← 子方向 A 完整论文详情 + BibTeX
├── {ts}_02_SubDirection_B.md        ← 子方向 B
├── ...
├── {ts}_final_report.bib            ← 所有精选论文 BibTeX
└── {ts}_final_report.json           ← 结构化 JSON
```

## 代码结构

```
literature-search/
├── SKILL.md                         ← Skill 定义 + 完整工作流说明
├── requirements.txt                 ← requests, feedparser
└── scripts/
    ├── search.py                    ← CLI 入口（--keywords / --merge / --finalize / --health）
    ├── aggregator.py                ← 去重 + 相关性评分 + 排序
    ├── reporter.py                  ← 多文件报告生成（MD + BibTeX + JSON）
    ├── sources/
    │   ├── base.py                  ← PaperItem 数据模型 + PaperSource 接口
    │   ├── ieee_xplore.py           ← IEEE Xplore 源
    │   ├── semantic_scholar.py      ← Semantic Scholar 源
    │   ├── arxiv_source.py          ← arXiv 源
    │   └── crossref_source.py       ← Crossref 源
    └── utils/
        └── http_client.py           ← HTTP 客户端（重试 + 限速）
```

## 安装

```bash
cp -r literature-search ~/.claude/skills/
pip install requests feedparser
```

## CLI 用法

```bash
cd scripts

# 搜索
python3 search.py --keywords "movable antenna" "beamforming" \
  --sources ieee semantic_scholar arxiv \
  --max-results 30 --time-range 3y --sort relevance -o results

# 合并多轮结果
python3 search.py --merge results/*_papers.json -o results

# 生成最终分类报告
python3 search.py --finalize results/merged_papers.json \
  --categories categories.json \
  --topic "Research Topic" -o results

# 健康检查
python3 search.py --health
```

## 支持的 IEEE 顶刊/顶会

**期刊**：JSAC, TWC, TCOM, TSP, TMC, TCCN, TVT, IoT-J, WCL, CL

**会议**：GLOBECOM, ICC, WCNC, INFOCOM, VTC

## 触发词

`查文献`、`搜论文`、`literature search`、`related work`、`文献综述`、`找参考文献`、`搜相关工作`、`survey papers`、`search papers`
