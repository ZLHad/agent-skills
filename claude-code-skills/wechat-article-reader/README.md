# WeChat Article Reader — 微信公众号文章抓取助手

通过 Playwright 无头浏览器抓取微信公众号文章，绕过反爬检测，提取全文内容。

## 核心能力

| 能力 | 说明 |
|------|------|
| **文章抓取** | 伪装移动端浏览器，绕过微信"环境异常"检测 |
| **内容提取** | 提取标题、作者、发布日期、正文、图片链接 |
| **后续处理** | 支持总结、翻译、讨论、保存为本地文件 |

## 工作流程

```
用户分享 mp.weixin.qq.com 链接
  ↓
检查 Playwright 依赖 → 缺少则自动安装
  ↓
运行无头浏览器抓取（伪装 iPhone Safari）
  ↓
提取文章元信息 + 正文 + 图片链接
  ↓
根据用户意图处理（阅读 / 总结 / 翻译 / 保存）
```

## 技术原理

微信公众号文章对纯 HTTP 请求会触发"环境异常"验证页面。本 skill 使用 Playwright 启动真实 Chromium 内核，伪装为 iPhone Safari 移动端访问，绕过 JS 环境检测。

## 目录结构

```
wechat-article-reader/
├── SKILL.md          # Skill 定义
├── README.md         # 说明文档
└── scripts/
    └── fetch.mjs     # 抓取脚本（Node.js + Playwright）
```

## 依赖

- Node.js
- Playwright（会自动安装）
- Chromium 浏览器内核（通过 `npx playwright install chromium` 安装）

## 触发词

`读公众号文章`、`抓取微信文章`、`read wechat`、或直接发送 `mp.weixin.qq.com` 链接
