# Zotero/Crossref 污染字段清理指南

> 来源：2026-04-05 实战经验，46 条参考文献批量清理，约 100 次格式修复。
> 适用场景：Zotero、TechRxiv、Crossref API 导出的 BibTeX 文件。

## 一、污染字段清单（默认删除）

Zotero 导出的 BibTeX 包含大量 IEEE Trans 不需要的字段，若不清理会占渲染空间、导致 LaTeX 编译失败。

| 字段 | 实战占比（46 条） | 问题 | IEEE Trans 是否需要 |
|------|-----------------|------|---------------------|
| `abstract` | 17 / 46 | 常含中文、长文本，LaTeX 编译错误 | ❌ 删除 |
| `url` | 28 / 46 | 占渲染空间，IEEEtran 不渲染 | ❌ 删除（`@misc`/`@electronic` 除外）|
| `urldate` | 16 / 46 | Zotero 专用访问日期 | ❌ 删除 |
| `copyright` | 2 / 46 | 法律声明 | ❌ 删除 |
| `langid` / `language` | 3 / 46 | Zotero 专用 | ❌ 删除 |
| `annote` | — | 作者备注 | ❌ 删除 |
| `shorttitle` | 7 / 46 | 冗余简短标题 | ❌ 删除 |
| `issn` | 28 / 46 | 期刊标识号 | ❌ 删除 |
| `keywords` | — | 常含中文/Emoji（⭐⭐⭐） | ❌ 删除 |
| `file` | — | 含中文 PDF 路径，编译必失败 | ❌ **必须**删除 |
| `publisher` | 30+ / 46 | "Institute of Electrical..." 冗余 | ❌ 删除（`@book` 除外）|
| `note` | — | Zotero 用户常写中文备注 | ⚠️ 仅保留 `early access` / `to be published` |
| `month` | 26 / 46 | 字符串 "jan" vs 数字 不一致 | ⚠️ 统一为小写宏 `jan`（不加花括号）|

### 批处理清理逻辑（伪代码）

```python
POLLUTED_FIELDS = {
    'abstract', 'url', 'urldate', 'copyright', 'langid', 'language',
    'annote', 'shorttitle', 'issn', 'keywords', 'file', 'publisher'
}
# 注意：以下条目类型保留部分字段
# @misc/@electronic  → 保留 url
# @book/@incollection → 保留 publisher

for entry in parse_bib(content):
    if entry.type.lower() == 'ieeetranbstctl':
        continue  # BSTcontrol 条目必须跳过
    for field in list(entry.fields):
        if field.lower() in POLLUTED_FIELDS:
            # 例外：@misc/@electronic 保留 url
            if field.lower() == 'url' and entry.type in ('misc', 'electronic'):
                continue
            if field.lower() == 'publisher' and entry.type in ('book', 'incollection'):
                continue
            entry.remove(field)

    # note 字段特殊处理
    if 'note' in entry.fields:
        note_value = entry.fields['note'].lower()
        if 'early access' not in note_value and 'to be published' not in note_value:
            entry.remove('note')
```

## 二、HTML 实体与特殊字符转义

Crossref API 返回的字段常含 HTML 实体，必须转义后才能交给 LaTeX：

```python
HTML_ENTITIES = {
    '&amp;':  r'\&',
    '&lt;':   r'\textless{}',
    '&gt;':   r'\textgreater{}',
    '&quot;': '"',
    '&#39;':  "'",
    '&nbsp;': ' ',
}
```

**em-dash / en-dash 修正**：Crossref/Zotero 导出的 pages 字段常含 `–`（U+2013 en-dash）或 `—`（U+2014 em-dash），必须转换为双 ASCII 连字符：

```python
# 仅对 pages 字段执行
pages = pages.replace('–', '--').replace('—', '--')
```

**典型案例**：
- `IEEE Communications Surveys &amp; Tutorials` → 改用宏 `IEEE_O_CSTO`
- `pages = {100–110}` → `pages = {100--110}`

## 三、Unicode 污染扫描

LaTeX 对中文字符和 Emoji 原生不支持（需加载 xeCJK）。新增 bib 后必须扫描：

```python
import re

def scan_unicode_pollution(content):
    issues = []
    # 中文字符范围
    chinese = re.findall(r'[\u4e00-\u9fff]+', content)
    if chinese:
        issues.append(f"中文字符: {set(chinese)}")
    # 常见 Emoji（不完整，可扩展）
    emoji = re.findall(r'[⭐✨🎯📌💡❌✅⚠️]', content)
    if emoji:
        issues.append(f"Emoji: {set(emoji)}")
    return issues
```

**典型错误**：`"Unicode character not set up for use with LaTeX"` 编译错误。

## 四、嵌套大括号安全解析

简单正则 `title\s*=\s*\{([^}]+)\}` 遇到 `title = {{AI} in {SAGIN}: ...}` 会在第一个 `}` 处截断。必须用深度计数：

```python
def extract_braced_field(content, field_name):
    """提取 BibTeX 字段值，正确处理嵌套大括号。"""
    import re
    m = re.search(rf'\b{field_name}\s*=\s*\{{', content, re.IGNORECASE)
    if not m:
        return None
    depth = 1
    start = m.end()
    i = start
    while i < len(content) and depth > 0:
        if content[i] == '{':
            depth += 1
        elif content[i] == '}':
            depth -= 1
        i += 1
    return content[start:i-1]
```

## 五、IEEE 期刊宏映射表（默认转换，非可选）

> ⚠️ 所有宏名已与 IEEEabrv.bib 核对（勿凭直觉拼写！）

```python
IEEE_JOURNAL_MACROS = {
    # 顶级 Trans 期刊
    'IEEE Transactions on Mobile Computing':                   'IEEE_J_MC',
    'IEEE Transactions on Wireless Communications':            'IEEE_J_WCOM',
    'IEEE Transactions on Communications':                     'IEEE_J_COM',
    'IEEE Transactions on Signal Processing':                  'IEEE_J_SP',
    'IEEE Transactions on Vehicular Technology':               'IEEE_J_VT',
    'IEEE Transactions on Information Theory':                 'IEEE_J_IT',
    'IEEE Transactions on Cognitive Communications and Networking':   'IEEE_J_CCN',
    'IEEE Transactions on Industrial Informatics':             'IEEE_J_IINF',   # ⚠️ 不是 IEEE_J_II
    'IEEE Transactions on Network Science and Engineering':    'IEEE_J_NSE',
    'IEEE Transactions on Networking':                         'IEEE_J_NET',    # IEEE/ACM
    'IEEE Transactions on Intelligent Transportation Systems': 'IEEE_J_ITS',
    'IEEE Transactions on Services Computing':                 'IEEE_J_SC',     # ⚠️ 不是 IEEE_J_SVC；勿与 IEEE_J_SUSC (Sustain. Comput.) 混淆

    # Journal 类
    'IEEE Journal on Selected Areas in Communications':        'IEEE_J_JSAC',   # ⚠️ 不是 IEEE_J_SAC
    'IEEE Internet of Things Journal':                         'IEEE_J_IOT',

    # Letters
    'IEEE Communications Letters':                             'IEEE_J_COML',
    'IEEE Wireless Communications Letters':                    'IEEE_J_WCOML',  # ⚠️ 不是 IEEE_J_WCL

    # Magazines
    'IEEE Network':                                            'IEEE_M_NET',
    'IEEE Communications Magazine':                            'IEEE_M_COM',
    'IEEE Wireless Communications':                            'IEEE_M_WCOM',
    'IEEE Spectrum':                                           'IEEE_M_SPECT',  # ⚠️ 不是 IEEE_M_SPEC

    # Open Access / Surveys
    'IEEE Communications Surveys & Tutorials':                 'IEEE_O_CSTO',   # ⚠️ 不是 IEEE_O_CST
    'IEEE Communications Surveys and Tutorials':               'IEEE_O_CSTO',
    'IEEE Access':                                             'IEEE_O_ACC',
}
```

**匹配策略**：
1. 精确字符串匹配（忽略大小写、统一空白）
2. 处理 `&amp;` / `&` / `and` 的变体
3. 未匹配时：调用 IEEEfull.bib 做模糊匹配（cutoff=0.8）
4. 仍未匹配：报告警告，保留原字段

## 六、Early Access 精确识别

```python
def detect_early_access(entry):
    pages = entry.get('pages', '')

    # 规则 1：精确匹配占位 pages
    if re.match(r'^\s*1--1\s*$', pages):
        return 'early_access'

    # 规则 2：无 volume AND 无 number AND 有 journal AND 有 DOI
    has_vol = bool(entry.get('volume'))
    has_num = bool(entry.get('number'))
    has_journal = bool(entry.get('journal'))
    has_doi = bool(entry.get('doi'))
    if not has_vol and not has_num and has_journal and has_doi:
        return 'likely_early_access'

    # 规则 3：note 字段已含 'early access'
    if 'early access' in entry.get('note', '').lower():
        return 'early_access'

    return None
```

**修复操作**：
```python
def fix_early_access(entry):
    doi = entry.pop('doi', None)
    entry.pop('pages', None)
    note = entry.get('note', '').strip()
    if doi:
        entry['note'] = f'early access, doi: {doi}'
    elif 'early access' not in note.lower():
        entry['note'] = 'early access'
```

## 七、BSTcontrol 条目保护

所有批处理脚本必须跳过 `@ieeetranbstctl` 条目，否则会误加 `note = {early access}`、删除关键字段等：

```python
for entry in entries:
    if entry.type.lower() == 'ieeetranbstctl':
        continue
    # ... 其他处理
```

## 八、arXiv → IEEE 正刊升级流程

**场景**：Zotero 中大量 `@misc`/arXiv 预印本实际已在 IEEE 期刊正式发表。

**实战案例**（2026-04-05）：
| Key | 原（Zotero） | 升级后 |
|-----|-------------|--------|
| `jiang2024large` | @misc arXiv:2309.01249 | IEEE ComMag 2025, DOI 10.1109/mcom.001.2300575 |
| `qu2025mobile` | TechRxiv preprint | IEEE CST 2025, DOI 10.1109/comst.2025.3527641 |
| `wang2026lowaltitude` | arXiv:2601.07307 | IEEE TMC 2026, DOI 10.1109/tmc.2026.3655156 |

**工作流**：
```
1. 扫描所有 @misc 条目，提取 title + 第一作者 last name
2. 调用 Crossref API：
   GET https://api.crossref.org/works?
       query.title=<title>&
       query.author=<lastname>&
       rows=5&
       filter=type:journal-article
3. 筛选返回结果中的 IEEE 期刊（container-title 含 "IEEE"）
4. 提取元数据：DOI, journal, volume, issue, page, published year
5. 生成替换条目：@article{原 key, ...}
6. 展示 Before/After，等用户确认
```

**注意**：只有 Crossref 返回 IEEE 期刊（`container-title` 含 IEEE）的才视为正式发表。arXiv 预印本 ≠ 正式发表。

## 九、Key 与第一作者一致性检查

```python
def check_key_author_match(entry):
    """从 author 字段提取第一作者 last name，与 key 前缀比对。"""
    author = entry.get('author', '')
    # BibTeX 格式: "Last, First and Last2, First2" 或 "First Last and First2 Last2"
    first_author = author.split(' and ')[0].strip()
    if ',' in first_author:
        last_name = first_author.split(',')[0].strip()
    else:
        last_name = first_author.split()[-1]

    last_name_norm = last_name.lower().replace('-', '').replace(' ', '')
    key_prefix = re.match(r'^([a-z]+)', entry.key.lower())

    if key_prefix and not key_prefix.group(1).startswith(last_name_norm[:4]):
        return f"Key '{entry.key}' 与第一作者 '{last_name}' 不匹配，建议重命名为 '{last_name_norm}XXXX'"
    return None
```

**实战经验**（2026-04-05）：46 条中 6 处不匹配
- `xu2025generative` → 实际第一作者 Zeng → `zeng2025generative`
- `wang2025flexgen` → 实际第一作者 Li → `li2025flexgen`
- `liu2026e2e` → 实际第一作者 Zhang → `zhang2026e2e`

**常见原因**：AI 搜索时盲目信任用户给的 key，或 Crossref 返回的 author 顺序与预期不同。

## 十、AI 搜集文献时的常见错误

| 错误类型 | 示例 | 预防 |
|---------|------|------|
| 搜索查询词过于宽泛 | "SAGIN MEC resource allocation 2025" → 0 结果 | 拆成多轮短查询 |
| 盲信 Crossref author 顺序 | Crossref 返回 `{Zeng, ... and Xu, ...}`，生成 `xu2025xxx` | 一律取 `author` 字段第一个 LastName |
| 把 arXiv 预印本当正式发表 | `du2025intelligent` (arXiv:2502.11386) 当 TMC 引用 | 只有 Crossref 返回 IEEE 期刊元数据才算 |
| 中文备注/Emoji 污染 | `keywords = {..., ⭐⭐⭐, ...}` | 扫描 `[\u4e00-\u9fff]` 和 Emoji |
| Early Access DOI 重复 | 同时有 `doi = {...}` 和 `note = {..., doi: ...}` | 只在 note 中保留 |
