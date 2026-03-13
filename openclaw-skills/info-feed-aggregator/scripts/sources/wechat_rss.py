"""WeChat Official Account source via Sogou search or RSSHub."""

import re
import time
from datetime import datetime
from typing import Dict, Any, List, Optional

import requests

from .base import InfoSource, FeedItem


def _decode_html_entities(text: str) -> str:
    """Decode common HTML entities in text."""
    import html
    text = html.unescape(text)
    return text


class WeChatRSSSource(InfoSource):
    name = "wechat"

    SOGOU_SEARCH_URL = "https://weixin.sogou.com/weixin"
    SOGOU_HEADERS = {
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
        method = self.config.get("method", "sogou")

        if method == "sogou":
            return self._search_sogou(keywords, max_results)
        elif method == "rsshub":
            return self._search_rsshub(keywords, max_results)
        elif method == "wewe-rss":
            return self._search_wewe(keywords, max_results)
        else:
            self.logger.warning(f"Unknown wechat method: {method}")
            return []

    # ------------------------------------------------------------------
    # Method 1: Sogou WeChat search (default, no config needed)
    # ------------------------------------------------------------------

    def _search_sogou(
        self, keywords: List[str], max_results: int
    ) -> List[FeedItem]:
        """Search WeChat articles via Sogou (weixin.sogou.com)."""
        query = " ".join(keywords)
        self.logger.info(f"WeChat Sogou search: {query}")

        all_items = []
        now_iso = datetime.utcnow().isoformat() + "Z"
        # Sogou returns ~10 results per page. Paginate to get more.
        pages_needed = min((max_results + 9) // 10, 3)  # Max 3 pages

        try:
            session = requests.Session()
            session.headers.update(self.SOGOU_HEADERS)

            # Visit homepage to get cookies
            session.get("https://weixin.sogou.com/", timeout=10)
            time.sleep(0.5)

            for page in range(1, pages_needed + 1):
                params = {
                    "type": "2",
                    "query": query,
                    "ie": "utf8",
                    "s_from": "input",
                    "_sug_": "n",
                    "_sug_type_": "",
                    "page": page,
                }
                resp = session.get(
                    self.SOGOU_SEARCH_URL,
                    params=params,
                    timeout=15,
                )
                resp.raise_for_status()

                page_items = self._parse_sogou_html(resp.text, keywords, now_iso)
                all_items.extend(page_items)

                if len(all_items) >= max_results or len(page_items) == 0:
                    break
                if page < pages_needed:
                    time.sleep(1)  # Rate limit between pages

        except Exception as e:
            self.logger.error(f"WeChat Sogou search failed: {e}")

        self.logger.info(f"WeChat Sogou returned {len(all_items)} items")
        return all_items[:max_results]

    def _parse_sogou_html(
        self, html: str, keywords: List[str], now_iso: str
    ) -> List[FeedItem]:
        """Parse Sogou WeChat search result HTML."""
        items = []

        # Each result is in <ul class="news-list"> / <li>
        # Use regex to avoid extra dependency on lxml
        article_blocks = re.findall(
            r'<li[^>]*id="sogou_vr_\d+_box_\d+"[^>]*>(.*?)</li>',
            html,
            re.DOTALL,
        )

        if not article_blocks:
            # Fallback: try to find txt-box blocks
            article_blocks = re.findall(
                r'<div class="txt-box">(.*?)</div>\s*(?:</div>\s*)*</li>',
                html,
                re.DOTALL,
            )

        for block in article_blocks:
            # Title and link
            title_match = re.search(
                r'<h3>.*?<a[^>]+href=["\']([^"\']+)["\'][^>]*>(.*?)</a>',
                block,
                re.DOTALL,
            )
            if not title_match:
                continue

            url = title_match.group(1)
            # Ensure URL is absolute (Sogou returns relative /link?url=...)
            if url.startswith("/"):
                url = f"https://weixin.sogou.com{url}"
            title = re.sub(r"<[^>]+>", "", title_match.group(2)).strip()
            title = _decode_html_entities(title)

            if not title:
                continue

            # Abstract
            abstract_match = re.search(
                r'<p class="txt-info"[^>]*>(.*?)</p>',
                block,
                re.DOTALL,
            )
            abstract = ""
            if abstract_match:
                abstract = re.sub(r"<[^>]+>", "", abstract_match.group(1)).strip()
                abstract = _decode_html_entities(abstract)

            # Source account name
            account_match = re.search(
                r'<a[^>]*class="account"[^>]*>(.*?)</a>',
                block,
                re.DOTALL,
            )
            account = ""
            if account_match:
                account = re.sub(r"<[^>]+>", "", account_match.group(1)).strip()

            # Date (unix timestamp)
            date_match = re.search(r'<span[^>]*\bt=["\'](\d+)["\']', block)
            pub_date = ""
            if date_match:
                try:
                    ts = int(date_match.group(1))
                    pub_date = datetime.fromtimestamp(ts).strftime("%Y-%m-%d")
                except (ValueError, OSError):
                    pass

            tags = ["wechat"]
            if account:
                tags.append(account)

            item = FeedItem(
                title=title,
                url=url,
                source_type="wechat",
                fetched_at=now_iso,
                abstract=abstract or "",
                published_date=pub_date,
                tags=tags,
                language="zh",
                matched_keywords=[
                    kw for kw in keywords
                    if kw.lower() in f"{title} {abstract}".lower()
                ],
            )
            items.append(item)

        return items

    # ------------------------------------------------------------------
    # Method 2: RSSHub (needs RSSHub instance + account list)
    # ------------------------------------------------------------------

    def _search_rsshub(
        self, keywords: List[str], max_results: int
    ) -> List[FeedItem]:
        """Fetch from RSSHub WeChat routes."""
        import feedparser

        rsshub_base = self.config.get("rsshub_base_url", "https://rsshub.app").rstrip("/")
        accounts = self.config.get("accounts", [])

        if not accounts:
            self.logger.warning("No WeChat accounts configured for rsshub method")
            return []

        items = []
        now_iso = datetime.utcnow().isoformat() + "Z"
        keywords_lower = [kw.lower() for kw in keywords]

        for account in accounts:
            if isinstance(account, str):
                account_id, account_label = account, account
            else:
                account_id = account.get("id", "")
                account_label = account.get("label", account_id)

            if not account_id:
                continue

            url = f"{rsshub_base}/wechat/mp/{account_id}"
            self.logger.info(f"WeChat RSSHub fetching: {account_label}")

            try:
                text = self.http.get_text(url, timeout=15)
            except Exception as e:
                self.logger.error(f"WeChat RSSHub fetch failed for {account_label}: {e}")
                continue

            feed = feedparser.parse(text)

            for entry in feed.entries[:max_results]:
                title = entry.get("title", "")
                summary = entry.get("summary", "") or entry.get("description", "")
                link = entry.get("link", "")

                text_lower = f"{title} {summary}".lower()
                matched = [kw for kw in keywords_lower if kw in text_lower]
                if keywords and not matched:
                    continue

                pub_date = ""
                if entry.get("published_parsed"):
                    try:
                        dt = datetime(*entry.published_parsed[:6])
                        pub_date = dt.strftime("%Y-%m-%d")
                    except (TypeError, ValueError):
                        pass

                clean_summary = re.sub(r"<[^>]+>", "", summary).strip()

                item = FeedItem(
                    title=title,
                    url=link,
                    source_type="wechat",
                    fetched_at=now_iso,
                    abstract=clean_summary or "",
                    published_date=pub_date,
                    tags=[account_label],
                    language="zh",
                    matched_keywords=[kw for kw in keywords if kw.lower() in text_lower],
                )
                items.append(item)

        self.logger.info(f"WeChat RSSHub returned {len(items)} items")
        return items[:max_results]

    # ------------------------------------------------------------------
    # Method 3: WeWeRSS (self-hosted)
    # ------------------------------------------------------------------

    def _search_wewe(
        self, keywords: List[str], max_results: int
    ) -> List[FeedItem]:
        """Fetch from WeWeRSS instance."""
        import feedparser

        wewe_base = self.config.get("wewe_rss_url", "http://localhost:4000")
        accounts = self.config.get("accounts", [])

        if not accounts:
            self.logger.warning("No WeChat accounts configured for wewe-rss method")
            return []

        items = []
        now_iso = datetime.utcnow().isoformat() + "Z"
        keywords_lower = [kw.lower() for kw in keywords]

        for account in accounts:
            account_id = account if isinstance(account, str) else account.get("id", "")
            if not account_id:
                continue

            url = f"{wewe_base}/feeds/{account_id}.xml"
            try:
                text = self.http.get_text(url, timeout=15)
            except Exception as e:
                self.logger.error(f"WeWeRSS fetch failed: {e}")
                continue

            feed = feedparser.parse(text)
            for entry in feed.entries[:max_results]:
                title = entry.get("title", "")
                summary = entry.get("summary", "") or entry.get("description", "")
                link = entry.get("link", "")

                text_lower = f"{title} {summary}".lower()
                if keywords and not any(kw in text_lower for kw in keywords_lower):
                    continue

                clean_summary = re.sub(r"<[^>]+>", "", summary).strip()
                item = FeedItem(
                    title=title,
                    url=link,
                    source_type="wechat",
                    fetched_at=now_iso,
                    abstract=clean_summary or "",
                    language="zh",
                    matched_keywords=[kw for kw in keywords if kw.lower() in text_lower],
                )
                items.append(item)

        self.logger.info(f"WeWeRSS returned {len(items)} items")
        return items[:max_results]

    # ------------------------------------------------------------------
    # Health check
    # ------------------------------------------------------------------

    def health_check(self) -> Dict[str, Any]:
        method = self.config.get("method", "sogou")

        if method == "sogou":
            start = time.time()
            try:
                resp = requests.get(
                    "https://weixin.sogou.com/",
                    timeout=10,
                    headers=self.SOGOU_HEADERS,
                )
                resp.raise_for_status()
                latency = int((time.time() - start) * 1000)
                return {"ok": True, "message": "Sogou WeChat reachable", "latency_ms": latency}
            except Exception as e:
                latency = int((time.time() - start) * 1000)
                return {"ok": False, "message": str(e), "latency_ms": latency}
        elif method == "rsshub":
            base = self.config.get("rsshub_base_url", "https://rsshub.app")
            start = time.time()
            try:
                self.http.get_text(base, timeout=10)
                latency = int((time.time() - start) * 1000)
                return {"ok": True, "message": "WeChat (RSSHub) reachable", "latency_ms": latency}
            except Exception as e:
                latency = int((time.time() - start) * 1000)
                return {"ok": False, "message": str(e), "latency_ms": latency}
        elif method == "wewe-rss":
            base = self.config.get("wewe_rss_url", "http://localhost:4000")
            start = time.time()
            try:
                self.http.get_text(base, timeout=10)
                latency = int((time.time() - start) * 1000)
                return {"ok": True, "message": "WeWeRSS reachable", "latency_ms": latency}
            except Exception as e:
                latency = int((time.time() - start) * 1000)
                return {"ok": False, "message": str(e), "latency_ms": latency}
        else:
            return {"ok": False, "message": f"Unknown method: {method}", "latency_ms": 0}
