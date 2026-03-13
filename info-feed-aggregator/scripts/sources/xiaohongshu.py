"""Xiaohongshu (Little Red Book) source via web search or RSSHub."""

import re
import time
from datetime import datetime
from typing import Dict, Any, List, Optional
from urllib.parse import quote_plus, unquote, urlparse, parse_qs

import requests

from .base import InfoSource, FeedItem


class XiaohongshuSource(InfoSource):
    name = "xiaohongshu"

    SEARCH_HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    }

    def search(
        self,
        keywords: List[str],
        max_results: int = 20,
        time_range: Optional[str] = None,
        **kwargs,
    ) -> List[FeedItem]:
        method = self.config.get("method", "web_search")

        if method == "web_search":
            return self._search_ddg(keywords, max_results)
        elif method == "rsshub":
            return self._search_rsshub(keywords, max_results)
        else:
            self.logger.warning(f"Unknown xiaohongshu method: {method}")
            return []

    # ------------------------------------------------------------------
    # Method 1: DuckDuckGo HTML search (default, no config needed)
    # ------------------------------------------------------------------

    def _search_ddg(
        self, keywords: List[str], max_results: int
    ) -> List[FeedItem]:
        """Search XHS content via DuckDuckGo site:xiaohongshu.com."""
        query = f"site:www.xiaohongshu.com {' '.join(keywords)}"
        self.logger.info(f"Xiaohongshu DDG search: {query}")

        items = []
        now_iso = datetime.utcnow().isoformat() + "Z"

        try:
            session = requests.Session()
            session.headers.update(self.SEARCH_HEADERS)

            encoded_q = quote_plus(query)
            url = f"https://html.duckduckgo.com/html/?q={encoded_q}"

            resp = session.get(url, timeout=15)
            resp.raise_for_status()
            html = resp.text

            items = self._parse_ddg_results(html, keywords, now_iso)

        except Exception as e:
            self.logger.error(f"Xiaohongshu DDG search failed: {e}")
            return []

        self.logger.info(f"Xiaohongshu DDG returned {len(items)} items")
        return items[:max_results]

    def _parse_ddg_results(
        self, html: str, keywords: List[str], now_iso: str
    ) -> List[FeedItem]:
        """Parse DuckDuckGo HTML search results for XHS links."""
        items = []

        # DDG HTML results: <a class="result__a" href="//duckduckgo.com/l/?uddg=REAL_URL">title</a>
        results = re.findall(
            r'class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>',
            html,
            re.DOTALL,
        )

        for url_raw, title_html in results:
            # Extract real URL from DDG redirect
            real_url = url_raw
            if "uddg=" in url_raw:
                parsed = urlparse(url_raw)
                qs = parse_qs(parsed.query)
                uddg = qs.get("uddg", [])
                if uddg:
                    real_url = unquote(uddg[0])

            # Only include xiaohongshu.com results
            if "xiaohongshu.com" not in real_url:
                continue

            title = re.sub(r"<[^>]+>", "", title_html).strip()
            if not title:
                continue

            # Find the snippet for this result
            # DDG: <a class="result__snippet" ...>snippet text</a>
            # Find the snippet after this result
            idx = html.find(url_raw)
            if idx > 0:
                snippet_block = html[idx:idx + 2000]
                snippet_match = re.search(
                    r'class="result__snippet"[^>]*>(.*?)</a>',
                    snippet_block,
                    re.DOTALL,
                )
            else:
                snippet_match = None

            abstract = ""
            if snippet_match:
                abstract = re.sub(r"<[^>]+>", "", snippet_match.group(1)).strip()

            # Try to extract date
            pub_date = ""
            date_match = re.search(r'(\d{4}[-/]\d{1,2}[-/]\d{1,2})', abstract or "")
            if date_match:
                pub_date = date_match.group(1).replace("/", "-")

            item = FeedItem(
                title=title,
                url=real_url,
                source_type="xiaohongshu",
                fetched_at=now_iso,
                abstract=abstract or "",
                published_date=pub_date,
                tags=["xiaohongshu"],
                language="zh",
                matched_keywords=[
                    kw for kw in keywords
                    if kw.lower() in f"{title} {abstract}".lower()
                ],
            )
            items.append(item)

        return items

    # ------------------------------------------------------------------
    # Method 2: RSSHub
    # ------------------------------------------------------------------

    def _search_rsshub(
        self, keywords: List[str], max_results: int
    ) -> List[FeedItem]:
        """Fetch from RSSHub xiaohongshu routes."""
        import feedparser

        rsshub_base = self.config.get("rsshub_base_url", "https://rsshub.app").rstrip("/")
        routes = self.config.get("routes", [])

        if not routes:
            for kw in keywords:
                routes.append(f"/xiaohongshu/search/{kw}")

        items = []
        now_iso = datetime.utcnow().isoformat() + "Z"
        keywords_lower = [kw.lower() for kw in keywords]

        for route in routes[:5]:
            url = f"{rsshub_base}{route}"
            self.logger.info(f"Xiaohongshu RSSHub: {url}")

            try:
                text = self.http.get_text(url, timeout=15)
            except Exception as e:
                self.logger.error(f"Xiaohongshu RSSHub failed: {e}")
                continue

            feed = feedparser.parse(text)
            for entry in feed.entries[:max_results]:
                title = entry.get("title", "")
                summary = entry.get("summary", "") or entry.get("description", "")
                link = entry.get("link", "")

                text_lower = f"{title} {summary}".lower()
                if keywords and not any(kw in text_lower for kw in keywords_lower):
                    continue

                pub_date = ""
                if entry.get("published_parsed"):
                    try:
                        dt = datetime(*entry.published_parsed[:6])
                        pub_date = dt.strftime("%Y-%m-%d")
                    except (TypeError, ValueError):
                        pass

                clean_summary = re.sub(r"<[^>]+>", "", summary).strip()

                # Extract images
                media_urls = []
                content_html = summary
                if entry.get("content"):
                    content_html = entry.content[0].get("value", "")
                img_matches = re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', content_html)
                media_urls.extend(img_matches[:5])

                item = FeedItem(
                    title=title,
                    url=link,
                    source_type="xiaohongshu",
                    fetched_at=now_iso,
                    abstract=clean_summary or "",
                    published_date=pub_date,
                    tags=["xiaohongshu"],
                    language="zh",
                    media_urls=media_urls if media_urls else None,
                    matched_keywords=[kw for kw in keywords if kw.lower() in text_lower],
                )
                items.append(item)

        self.logger.info(f"Xiaohongshu RSSHub returned {len(items)} items")
        return items[:max_results]

    # ------------------------------------------------------------------
    # Health check
    # ------------------------------------------------------------------

    def health_check(self) -> Dict[str, Any]:
        method = self.config.get("method", "web_search")

        if method == "web_search":
            start = time.time()
            try:
                resp = requests.get(
                    "https://html.duckduckgo.com/html/",
                    timeout=10,
                    headers=self.SEARCH_HEADERS,
                )
                resp.raise_for_status()
                latency = int((time.time() - start) * 1000)
                return {"ok": True, "message": "Xiaohongshu (DDG search) reachable", "latency_ms": latency}
            except Exception as e:
                latency = int((time.time() - start) * 1000)
                return {"ok": False, "message": str(e), "latency_ms": latency}
        elif method == "rsshub":
            base = self.config.get("rsshub_base_url", "https://rsshub.app")
            start = time.time()
            try:
                self.http.get_text(base, timeout=10)
                latency = int((time.time() - start) * 1000)
                return {"ok": True, "message": "Xiaohongshu (RSSHub) reachable", "latency_ms": latency}
            except Exception as e:
                latency = int((time.time() - start) * 1000)
                return {"ok": False, "message": str(e), "latency_ms": latency}
        else:
            return {"ok": False, "message": f"Unknown method: {method}", "latency_ms": 0}
