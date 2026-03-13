# Zotero Local API 参考手册

## MCP 配置

配置文件位置：`~/.claude/.mcp.json`

```json
{
  "mcpServers": {
    "zotero": {
      "command": "/Users/zhanglinghao/.local/bin/zotero-mcp",
      "env": {
        "ZOTERO_LOCAL": "true"
      }
    }
  }
}
```

安装方式：
- 自动：`zotero-mcp setup`
- 手动：编辑 `~/.claude/.mcp.json`
- 二进制：`uv tool install zotero-mcp`

---

## API 端点速查

| 端点 | 功能 |
|------|------|
| `GET /api/users/0/items?limit=1` | 测试连接 |
| `GET /api/users/{id}/collections` | 获取所有分类 |
| `GET /api/users/{id}/collections/{key}/items` | 获取分类下条目 |
| `GET /api/users/{id}/items/{key}` | 获取单条目详情 |
| `GET /api/users/{id}/items/{key}/children` | 获取子条目（附件/笔记） |

基础 URL：`http://localhost:23119`

---

## 读取文献 PDF 全文

Zotero 本地 API **无法**直接下载 PDF（返回 0 字节），但可通过本地文件系统访问。

### 获取 PDF 本地路径

```bash
# 1. 查询文献的附件子条目
curl -s "http://localhost:23119/api/users/{USER_ID}/items/{ITEM_KEY}/children" | python3 -c "
import json, sys
data = json.load(sys.stdin)
for item in data:
    d = item['data']
    if d.get('itemType') == 'attachment' and d.get('contentType') == 'application/pdf':
        print('Attachment KEY:', item['key'])
        print('Filename:', d.get('filename', ''))
        print('Local path: ~/Zotero/storage/' + item['key'] + '/' + d.get('filename', ''))"
```

### 本地存储结构

```
~/Zotero/storage/{ATTACHMENT_KEY}/
├── 论文文件名.pdf          ← PDF 原文件
├── .zotero-ft-cache        ← Zotero 全文文本缓存（纯文本，可直接 cat）
└── .zotero-reader-state    ← 阅读状态
```

### 读取方式

**使用 `pdftotext` 提取全文**（推荐）：
```bash
pdftotext ~/Zotero/storage/{ATTACHMENT_KEY}/文件名.pdf -
```

输出纯文本到 stdout，可直接管道处理。如需截取前 N 行：
```bash
pdftotext ~/Zotero/storage/{ATTACHMENT_KEY}/文件名.pdf - | head -200
```

**仅在用户明确要求精读某篇文献时使用**，常规匹配只需摘要即可。

---

## 获取单篇文献完整元数据

```bash
curl -s "http://localhost:23119/api/users/{USER_ID}/items/{ITEM_KEY}" | python3 -c "
import json, sys
item = json.load(sys.stdin)
d = item['data']
creators = ', '.join([f\"{c.get('firstName','')}{' ' if c.get('firstName') else ''}{c.get('lastName','')}\" for c in d.get('creators',[])])
print(f'Title: {d.get(\"title\",\"\")}')
print(f'Authors: {creators}')
print(f'Journal: {d.get(\"publicationTitle\",\"\") or d.get(\"proceedingsTitle\",\"\")}')
print(f'Volume: {d.get(\"volume\",\"\")}')
print(f'Issue: {d.get(\"issue\",\"\")}')
print(f'Pages: {d.get(\"pages\",\"\")}')
print(f'DOI: {d.get(\"DOI\",\"\")}')
print(f'Date: {d.get(\"date\",\"\")}')
print(f'Abstract: {d.get(\"abstractNote\",\"\")[:500]}')"
```

---

## 元数据字段映射

| Zotero 字段 | 含义 | IEEE Reference 对应 |
|---|---|---|
| `title` | 论文标题 | 标题部分 |
| `creators[].firstName/lastName` | 作者 | 作者列表 |
| `publicationTitle` | 期刊名 | 斜体期刊缩写 |
| `proceedingsTitle` | 会议名 | 会议论文期刊名 |
| `volume` | 卷号 | vol. X |
| `issue` | 期号 | no. X |
| `pages` | 页码 | pp. X–Y |
| `date` | 日期 | 年份/月份 |
| `DOI` | DOI | 可选 |
| `abstractNote` | 摘要 | 用于理解文献内容、匹配引用位置 |
| `itemType` | 类型 | journalArticle / preprint / conferencePaper |

---

## 批量查询技巧

### 批量获取多篇文献

```bash
for key in KEY1 KEY2 KEY3; do
  echo "========== KEY=$key =========="
  curl -s "http://localhost:23119/api/users/{USER_ID}/items/$key" | python3 -c "
import json, sys
item = json.load(sys.stdin)
d = item['data']
creators = ', '.join([c.get('lastName','') for c in d.get('creators',[])])
print(f'Title: {d.get(\"title\",\"\")}')
print(f'Authors: {creators}')
print(f'Date: {d.get(\"date\",\"\")}')
print(f'Abstract: {d.get(\"abstractNote\",\"\")[:300]}')"
done
```

### 查询包含子分类的 Collection

需要先获取子分类的 key，再逐个查询。父分类 API **不会**自动返回子分类的条目。

```bash
# 1. 获取所有 Collection，找到父分类的子分类
curl -s "http://localhost:23119/api/users/{USER_ID}/collections" | python3 -c "
import json, sys
data = json.load(sys.stdin)
parent_key = 'TARGET_PARENT_KEY'
for c in data:
    if c['data'].get('parentCollection') == parent_key:
        print(f\"Sub: {c['key']}: {c['data']['name']}\")"

# 2. 对每个子分类查询文献
```

---

## IEEE 常用期刊缩写

| 全称 | IEEE 缩写 |
|------|-----------|
| IEEE Transactions on Vehicular Technology | IEEE Trans. Veh. Technol. |
| IEEE Journal on Selected Areas in Communications | IEEE J. Sel. Areas Commun. |
| IEEE Transactions on Wireless Communications | IEEE Trans. Wireless Commun. |
| IEEE Communications Magazine | IEEE Commun. Mag. |
| IEEE Wireless Communications | IEEE Wireless Commun. |
| IEEE Communications Surveys & Tutorials | IEEE Commun. Surv. Tutorials |
| IEEE Transactions on Communications | IEEE Trans. Commun. |
| IEEE Transactions on Signal Processing | IEEE Trans. Signal Process. |
| IEEE Internet of Things Journal | IEEE Internet Things J. |
| IEEE Transactions on Mobile Computing | IEEE Trans. Mobile Comput. |

---

## 踩坑记录

### zsh URL 引号问题
- **问题**：`curl http://localhost:23119/api/users/0/items?limit=1` 报 `no matches found`
- **原因**：zsh 将 `?` 解释为通配符
- **解决**：URL 加双引号

### 子分类文献不自动包含
- **问题**：查询父 Collection 不返回子分类条目
- **解决**：先获取子分类 key，逐个查询

### 混入非文献条目
- **问题**：API 返回 PDF 附件和笔记
- **解决**：过滤 `itemType not in ('attachment', 'note')`

### 多版本论文
- **问题**：项目中可能有 `.tex` 旧版 + `.docx` 新版
- **解决**：先列出所有候选文件，让用户确认最新版本
