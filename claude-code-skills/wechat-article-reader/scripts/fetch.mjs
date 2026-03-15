/**
 * 微信公众号文章抓取脚本
 * 使用 Playwright 无头浏览器，伪装移动端访问绕过反爬检测
 *
 * 用法: node fetch.mjs <url> [--html]
 *   --html  同时输出原始 HTML（用于保留图片链接等）
 */

import { chromium } from "playwright";

const url = process.argv[2];
const wantHtml = process.argv.includes("--html");

if (!url) {
  console.error("Usage: node fetch.mjs <wechat-article-url> [--html]");
  process.exit(1);
}

(async () => {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    userAgent:
      "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) " +
      "AppleWebKit/605.1.15 (KHTML, like Gecko) " +
      "Version/17.0 Mobile/15E148 Safari/604.1",
    viewport: { width: 375, height: 812 },
    locale: "zh-CN",
  });

  const page = await context.newPage();

  try {
    await page.goto(url, { waitUntil: "networkidle", timeout: 30000 });
    await page.waitForTimeout(3000);

    // 检测是否被拦截
    const blocked = await page.evaluate(() => {
      const el = document.querySelector(".weui-msg__title");
      return el && el.textContent.includes("异常");
    });

    if (blocked) {
      console.error("ERROR: 被微信反爬拦截（环境异常），请稍后重试");
      process.exit(2);
    }

    // 提取文章内容
    const result = await page.evaluate(() => {
      const titleEl =
        document.querySelector("#activity-name") ||
        document.querySelector(".rich_media_title");
      const authorEl =
        document.querySelector("#js_name") ||
        document.querySelector(".rich_media_meta_nickname");
      const dateEl = document.querySelector("#publish_time");
      const contentEl =
        document.querySelector("#js_content") ||
        document.querySelector(".rich_media_content");

      // 提取图片信息
      const images = [];
      if (contentEl) {
        contentEl.querySelectorAll("img").forEach((img) => {
          const src = img.dataset.src || img.src;
          const alt = img.alt || "";
          if (src && !src.startsWith("data:")) {
            images.push({ src, alt });
          }
        });
      }

      return {
        title: titleEl ? titleEl.textContent.trim() : "",
        author: authorEl ? authorEl.textContent.trim() : "",
        date: dateEl ? dateEl.textContent.trim() : "",
        text: contentEl ? contentEl.innerText : "",
        html: contentEl ? contentEl.innerHTML : "",
        images,
      };
    });

    // 输出结果
    console.log("---META---");
    console.log(JSON.stringify({
      title: result.title,
      author: result.author,
      date: result.date,
      imageCount: result.images.length,
    }));
    console.log("---TEXT---");
    console.log(result.text);

    if (wantHtml) {
      console.log("---HTML---");
      console.log(result.html);
    }

    if (result.images.length > 0) {
      console.log("---IMAGES---");
      result.images.forEach((img, i) => {
        console.log(`[${i + 1}] ${img.alt || "(no alt)"}: ${img.src}`);
      });
    }
  } catch (e) {
    console.error("ERROR:", e.message);
    process.exit(1);
  } finally {
    await browser.close();
  }
})();
