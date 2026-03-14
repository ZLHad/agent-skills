"""arXiv source: search via Atom API, parse with feedparser."""

import re
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

import feedparser

from .base import PaperSource, PaperItem


class ArxivSource(PaperSource):
    name = "arxiv"

    def search(
        self,
        keywords: List[str],
        max_results: int = 30,
        time_range: Optional[str] = None,
        **kwargs,
    ) -> List[PaperItem]:
        base_url = self.config.get("base_url", "http://export.arxiv.org/api/query")
        extra = 10 if time_range else 0
        max_per_query = min(
            max_results + extra,
            self.config.get("max_results_per_query", 50),
        )
        sort_mode = kwargs.get("sort", "relevance")
        if sort_mode == "date":
            sort_by, sort_order = "submittedDate", "descending"
        else:
            sort_by, sort_order = "relevance", "descending"

        # Build query
        query_parts = []
        for kw in keywords:
            kw = kw.strip()
            if " " in kw:
                query_parts.append(f'all:"{kw}"')
            else:
                query_parts.append(f"all:{kw}")
        query_str = "+AND+".join(query_parts) if query_parts else "all:*"

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

            abstract = entry.get("summary", "")
            abstract = re.sub(r"\s+", " ", abstract).strip()

            published = entry.get("published", "")
            year = 0
            if published:
                try:
                    dt = datetime.strptime(published, "%Y-%m-%dT%H:%M:%SZ")
                    published = dt.strftime("%Y-%m-%d")
                    year = dt.year
                except ValueError:
                    pass

            # DOI from links
            doi = ""
            for link in entry.get("links", []):
                href = link.get("href", "")
                if "doi.org" in href:
                    doi = href.split("doi.org/")[-1]
                    break

            item = PaperItem(
                title=entry.get("title", "").replace("\n", " ").strip(),
                url=entry.get("id", ""),
                source_type="arxiv",
                fetched_at=now_iso,
                authors=authors,
                abstract=abstract,
                published_date=published,
                year=year,
                tags=tags,
                arxiv_id=arxiv_id,
                doi=doi,
                content_type="preprint",
            )
            items.append(item)

        # Post-fetch time filter
        if time_range and items:
            items = self._filter_by_time(items, time_range)

        self.logger.info(f"arXiv returned {len(items)} items")
        return items[:max_results]

    @staticmethod
    def _filter_by_time(items: list, time_range: str) -> list:
        now = datetime.utcnow()
        days_map = {
            "7d": 7, "30d": 30, "1y": 365, "2y": 730,
            "3y": 1095, "5y": 1825, "10y": 3650,
        }
        days = days_map.get(time_range)
        if not days:
            return items
        cutoff = now - timedelta(days=days)
        filtered = []
        for item in items:
            if not item.published_date:
                filtered.append(item)
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
        match = re.search(r"(\d{4}\.\d{4,5})(v\d+)?$", url)
        if match:
            return match.group(1)
        match = re.search(r"([a-z-]+/\d{7})", url)
        if match:
            return match.group(1)
        return ""
