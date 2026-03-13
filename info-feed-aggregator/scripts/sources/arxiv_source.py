"""arXiv source: search via Atom API, parse with feedparser."""

import re
from datetime import datetime
from typing import Dict, Any, List, Optional

import feedparser

from .base import InfoSource, FeedItem


class ArxivSource(InfoSource):
    name = "arxiv"

    def search(
        self,
        keywords: List[str],
        max_results: int = 20,
        time_range: Optional[str] = None,
        **kwargs,
    ) -> List[FeedItem]:
        base_url = self.config.get("base_url", "http://export.arxiv.org/api/query")
        # Fetch extra if time_range filtering will discard some
        extra = 10 if time_range else 0
        max_per_query = min(
            max_results + extra,
            self.config.get("max_results_per_query", 50),
        )
        # Sort: CLI `sort` kwarg overrides config
        sort_mode = kwargs.get("sort", "date")
        if sort_mode == "date":
            sort_by = "submittedDate"
            sort_order = "descending"
        else:
            sort_by = self.config.get("sort_by", "relevance")
            sort_order = self.config.get("sort_order", "descending")

        # Build query: combine keywords with AND
        query_parts = []
        for kw in keywords:
            kw = kw.strip()
            if " " in kw:
                # Multi-word keyword: search as phrase in title or abstract
                query_parts.append(f'all:"{kw}"')
            else:
                query_parts.append(f"all:{kw}")

        query_str = "+AND+".join(query_parts) if query_parts else "all:*"

        # Optional category filter
        categories = kwargs.get("categories")
        if categories:
            cat_query = "+OR+".join(f"cat:{c}" for c in categories)
            query_str = f"({query_str})+AND+({cat_query})"

        params = {
            "search_query": query_str,
            "start": 0,
            "max_results": max_per_query,
            "sortBy": sort_by,
            "sortOrder": sort_order,
        }

        self.logger.info(f"arXiv query: {query_str} (max={max_per_query})")

        try:
            text = self.http.get_text(base_url, params=params)
        except Exception as e:
            self.logger.error(f"arXiv request failed: {e}")
            return []

        feed = feedparser.parse(text)
        items = []
        now_iso = datetime.utcnow().isoformat() + "Z"

        for entry in feed.entries:
            arxiv_id = self._extract_arxiv_id(entry.get("id", ""))
            authors = [a.get("name", "") for a in entry.get("authors", [])]
            tags = [t.get("term", "") for t in entry.get("tags", [])]

            # Clean abstract: remove newlines and extra spaces
            abstract = entry.get("summary", "")
            abstract = re.sub(r"\s+", " ", abstract).strip()

            published = entry.get("published", "")
            # Normalize to ISO date
            if published:
                try:
                    dt = datetime.strptime(published, "%Y-%m-%dT%H:%M:%SZ")
                    published = dt.strftime("%Y-%m-%d")
                except ValueError:
                    pass

            # Find PDF link
            pdf_url = ""
            for link in entry.get("links", []):
                if link.get("type") == "application/pdf":
                    pdf_url = link.get("href", "")
                    break

            item = FeedItem(
                title=entry.get("title", "").replace("\n", " ").strip(),
                url=entry.get("id", ""),
                source_type="arxiv",
                fetched_at=now_iso,
                authors=authors,
                abstract=abstract,
                published_date=published,
                tags=tags,
                arxiv_id=arxiv_id,
                language="en",
            )

            # Extract DOI if present in links
            for link in entry.get("links", []):
                href = link.get("href", "")
                if "doi.org" in href:
                    item.doi = href.split("doi.org/")[-1]
                    break

            items.append(item)

        # Post-fetch time_range filter (arXiv API has no date range param)
        if time_range and items:
            items = self._filter_by_time(items, time_range)

        self.logger.info(f"arXiv returned {len(items)} items")
        return items[:max_results]

    @staticmethod
    def _filter_by_time(items: list, time_range: str) -> list:
        """Filter items by time_range (7d, 30d, 1y, etc.)."""
        from datetime import timedelta
        now = datetime.utcnow()
        days_map = {"1d": 1, "7d": 7, "30d": 30, "90d": 90, "1y": 365, "3y": 1095}
        days = days_map.get(time_range)
        if not days:
            return items
        cutoff = now - timedelta(days=days)
        filtered = []
        for item in items:
            if not item.published_date:
                filtered.append(item)  # Keep items without date
                continue
            try:
                pub = datetime.strptime(item.published_date[:10], "%Y-%m-%d")
                if pub >= cutoff:
                    filtered.append(item)
            except ValueError:
                filtered.append(item)
        return filtered

    def health_check(self) -> Dict[str, Any]:
        import time
        base_url = self.config.get("base_url", "http://export.arxiv.org/api/query")
        start = time.time()
        try:
            self.http.get_text(
                base_url,
                params={"search_query": "all:test", "max_results": 1},
                timeout=10,
            )
            latency = int((time.time() - start) * 1000)
            return {"ok": True, "message": "arXiv API reachable", "latency_ms": latency}
        except Exception as e:
            latency = int((time.time() - start) * 1000)
            return {"ok": False, "message": str(e), "latency_ms": latency}

    @staticmethod
    def _extract_arxiv_id(url: str) -> str:
        """Extract arXiv ID from URL like http://arxiv.org/abs/2403.12345v1."""
        match = re.search(r"(\d{4}\.\d{4,5})(v\d+)?$", url)
        if match:
            return match.group(1)
        # Older format: cs/0601001
        match = re.search(r"([a-z-]+/\d{7})", url)
        if match:
            return match.group(1)
        return ""
