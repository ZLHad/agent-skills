# 搜索参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--keywords` | 搜索关键词（**推荐每次只传 1 个 2-4 词短语**；多个时受 `--match-mode` 控制） | 必填 |
| `--match-mode` | `any` = OR 连接（广召回，默认）；`all` = AND-of-exact-phrase（严格，易 0 结果） | any |
| `--sources` | 数据源列表 | ieee semantic_scholar arxiv |
| `--max-results` | 每源每轮最大结果数 | 30 |
| `--time-range` | 时间范围：1y/3y/5y/all | 3y |
| `--sort` | 排序：relevance/date/citations | relevance |
| `--output-dir` | 输出目录 | results |
| `--output-format` | 输出格式：json/markdown/bibtex/all | all |
| `--journals` | 限定期刊（逗号分隔） | 无（不限） |
| `--min-citations` | 最低引用数 | 0 |
