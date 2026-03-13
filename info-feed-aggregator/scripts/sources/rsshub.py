"""RSSHub source: generic RSS feed fetcher via RSSHub instance."""

import time
from datetime import datetime
from typing import Dict, Any, List, Optional

import feedparser

from .base import InfoSource, FeedItem


class RSSHubSource(InfoSource):
    name = "rsshub"

    def search(
        self,
        keywords: List[str],
        max_results: int = 20,
        time_range: Optional[str] = None,
        **kwargs,
    ) -> List[FeedItem]:
        base_url = self.config.get("base_url", "https://rsshub.app").rstrip("/")
        routes = self.config.get("routes", [])

        if not routes:
            self.logger.warning("No RSSHub routes configured")
            return []

        items = []
        now_iso = datetime.utcnow().isoformat() + "Z"
        keywords_lower = [kw.lower() for kw in keywords]

        for route in routes:
            route_path = route if isinstance(route, str) else route.get("path", "")
            route_label = route if isinstance(route, str) else route.get("label", route_path)

            if not route_path:
                continue

            url = f"{base_url}{route_path}"
            self.logger.info(f"RSSHub fetching: {url}")

            try:
                text = self.http.get_text(url, timeout=15)
            except Exception as e:
                self.logger.error(f"RSSHub fetch failed for {route_path}: {e}")
                continue

            feed = feedparser.parse(text)

            for entry in feed.entries[:max_results]:
                title = entry.get("title", "")
                summary = entry.get("summary", "") or entry.get("description", "")
                link = entry.get("link", "")

                # Keyword filter: check if any keyword appears in title or summary
                text_lower = f"{title} {summary}".lower()
                matched = [kw for kw in keywords_lower if kw in text_lower]
                if keywords and not matched:
                    continue

                # Date
                pub_date = ""
                if entry.get("published_parsed"):
                    try:
                        dt = datetime(*entry.published_parsed[:6])
                        pub_date = dt.strftime("%Y-%m-%d")
                    except (TypeError, ValueError):
                        pass

                # Tags
                tags = [t.get("term", "") for t in entry.get("tags", [])]

                item = FeedItem(
                    title=title,
                    url=link,
                    source_type="rsshub",
                    fetched_at=now_iso,
                    abstract=summary or "",
                    published_date=pub_date,
                    tags=tags + [route_label],
                    matched_keywords=[kw for kw in keywords if kw.lower() in text_lower],
                )
                items.append(item)

        self.logger.info(f"RSSHub returned {len(items)} items from {len(routes)} routes")
        return items[:max_results]

    def health_check(self) -> Dict[str, Any]:
        base_url = self.config.get("base_url", "https://rsshub.app")
        start = time.time()
        try:
            self.http.get_text(base_url, timeout=10)
            latency = int((time.time() - start) * 1000)
            return {"ok": True, "message": "RSSHub instance reachable", "latency_ms": latency}
        except Exception as e:
            latency = int((time.time() - start) * 1000)
            return {"ok": False, "message": str(e), "latency_ms": latency}
