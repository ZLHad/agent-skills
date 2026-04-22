# MkDocs 最小配置（Level 2/3）

Level 2/3 项目推荐用 **MkDocs Material** 搭建正式文档站点。轻量、markdown 原生、中文友好、学习成本低。

## 最小依赖

```bash
pip install mkdocs-material mkdocs-glightbox
```

或项目 Poetry：

```toml
[tool.poetry.group.docs.dependencies]
mkdocs-material = "^9.5"
mkdocs-glightbox = "^0.4"
```

## 最小 `doc/mkdocs.yml` 模板

```yaml
site_name: {项目名} 文档
site_description: {一句话项目描述}
site_author: {昵称}
site_url: http://localhost:8000

docs_dir: docs

theme:
  name: material
  language: zh
  palette:
    - media: "(prefers-color-scheme: light)"
      scheme: default
      primary: indigo
      accent: indigo
      toggle:
        icon: material/weather-sunny
        name: 切换到深色模式
    - media: "(prefers-color-scheme: dark)"
      scheme: slate
      primary: indigo
      accent: indigo
      toggle:
        icon: material/weather-night
        name: 切换到浅色模式
  features:
    - navigation.tabs
    - navigation.tabs.sticky
    - navigation.sections
    - navigation.expand
    - navigation.top
    - navigation.instant
    - navigation.tracking
    - navigation.indexes
    - toc.follow
    - search.suggest
    - search.highlight
    - content.code.copy
    - content.tabs.link

markdown_extensions:
  - abbr
  - admonition
  - attr_list
  - def_list
  - footnotes
  - md_in_html
  - toc:
      permalink: true
      toc_depth: 4
  - tables
  - pymdownx.arithmatex:
      generic: true
  - pymdownx.details
  - pymdownx.highlight:
      anchor_linenums: true
      line_spans: __span
      pygments_lang_class: true
  - pymdownx.inlinehilite
  - pymdownx.superfences:
      custom_fences:
        - name: mermaid
          class: mermaid
          format: !!python/name:pymdownx.superfences.fence_code_format
  - pymdownx.tabbed:
      alternate_style: true
  - pymdownx.tasklist:
      custom_checkbox: true

plugins:
  - search:
      lang:
        - zh
        - en
  - glightbox

nav:
  - 首页: index.md
  - 项目概览:
      - overview/index.md
      - ...
  - 开发文档:
      - development/index.md
      - ...
  - 系统架构:
      - architecture/index.md
      - ...
  # Level 3 才加：
  - 参考项目:
      - references/index.md
      - ...
  - 讨论记录:
      - discussion/index.md
      - Session 档案:
          - session-00 {主题}: discussion/sessions/YYYY-MM-DD_session-00_{主题}.md

extra:
  generator: false
```

## `docs/` 目录结构（Level 2）

```
doc/
├── mkdocs.yml
└── docs/
    ├── index.md               ← 项目首页（复用项目 README 或单独写）
    ├── overview/
    │   ├── index.md
    │   └── vision.md          ← 项目愿景（根据项目需要）
    ├── development/
    │   ├── index.md
    │   └── 01_feature_spec.md  ← 按 doc-system.md 选取的 Doc
    ├── architecture/
    │   ├── index.md
    │   └── layers.md          ← 分层架构
    └── discussion/
        ├── index.md
        └── sessions/          ← 符号链接到 DesignNotes/ 的 session 文档
```

## `docs/` 目录结构（Level 3）

Level 2 基础上加：

```
doc/docs/
└── references/
    ├── index.md               ← 参考项目总索引 + 分层借鉴策略表
    └── <项目>.md              ← 每个重要参考的分析文档
```

## 本地开发

```bash
cd doc
mkdocs serve --dev-addr 127.0.0.1:8000
# 浏览器访问 http://127.0.0.1:8000
# 改 .md 文件自动热重载
```

## 构建验证

每次结构性修改后：

```bash
cd doc && mkdocs build --strict
```

`--strict` 模式会把任何 warning（broken link / missing nav / anchor 缺失等）提升为 error，确保站点健康。

## 两个小约定

**1. nav 里不留孤立文件**

所有 `docs/` 下的 .md 都应该在 `mkdocs.yml` nav 里有入口，否则虽然能构建但用户浏览不到。

**2. 符号链接而非复制**

`discussion/sessions/` 里的 session 文档是指向 `DesignNotes/` 的**符号链接**（`ln -s`），保证 DesignNotes 是单一数据源，改一处即更新。
