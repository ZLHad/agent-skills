"""Semantic Scholar source: search via Graph API v1."""

import time
from datetime import datetime
from typing import Dict, Any, List, Optional

from .base import InfoSource, FeedItem


class SemanticScholarSource(InfoSource):
    name = "semantic_scholar"

    def search(
        self,
        keywords: List[str],
        max_results: int = 20,
        time_range: Optional[str] = None,
        **kwargs,
    ) -> List[FeedItem]:
        base_url = self.config.get("base_url", "https://api.semanticscholar.org/graph/v1")
        fields = self.config.get(
            "fields",
            "title,abstract,authors,year,citationCount,tldr,url,externalIds,publicationDate,venue",
        )
        max_per_query = min(
            max_results,
            self.config.get("max_results_per_query", 30),
        )

        query_str = " ".join(keywords)
        self.logger.info(f"S2 query: {query_str} (max={max_per_query})")

        headers = {}
        api_key = self.config.get("api_key", "")
        if api_key:
            headers["x-api-key"] = api_key

        # Build year filter from time_range
        year_filter = ""
        if time_range:
            current_year = datetime.now().year
            if time_range in ("1d", "7d", "30d"):
                year_filter = str(current_year)
            elif time_range == "1y":
                year_filter = f"{current_year - 1}-{current_year}"
            elif time_range == "3y":
                year_filter = f"{current_year - 3}-{current_year}"

        # Sort mode
        sort_mode = kwargs.get("sort", "date")

        params = {
            "query": query_str,
            "limit": max_per_query,
            "fields": fields,
        }
        if year_filter:
            params["year"] = year_filter
        # S2 supports sort by publicationDate or citationCount
        if sort_mode == "date":
            params["sort"] = "publicationDate:desc"
        elif sort_mode == "relevance":
            pass  # Default S2 sort is relevance

        try:
            data = self.http.get_json(
                f"{base_url}/paper/search",
                params=params,
                headers=headers,
            )
        except Exception as e:
            self.logger.error(f"S2 request failed: {e}")
            return []

        items = []
        now_iso = datetime.utcnow().isoformat() + "Z"

        for paper in data.get("data", []):
            if not paper:
                continue

            # Extract authors
            authors = []
            for a in paper.get("authors", []):
                name = a.get("name", "")
                if name:
                    authors.append(name)

            # Extract external IDs
            ext_ids = paper.get("externalIds", {}) or {}
            doi = ext_ids.get("DOI", "")
            arxiv_id = ext_ids.get("ArXiv", "")

            # TL;DR
            tldr_obj = paper.get("tldr")
            tldr = ""
            if tldr_obj and isinstance(tldr_obj, dict):
                tldr = tldr_obj.get("text", "")

            # Build URL
            url = paper.get("url", "")
            if not url:
                paper_id = paper.get("paperId", "")
                if paper_id:
                    url = f"https://www.semanticscholar.org/paper/{paper_id}"

            pub_date = paper.get("publicationDate", "")
            if not pub_date and paper.get("year"):
                pub_date = f"{paper['year']}-01-01"

            item = FeedItem(
                title=paper.get("title", ""),
                url=url,
                source_type="semantic_scholar",
                fetched_at=now_iso,
                authors=authors,
                abstract=paper.get("abstract", "") or "",
                published_date=pub_date or "",
                doi=doi,
                arxiv_id=arxiv_id,
                venue=paper.get("venue", "") or "",
                citation_count=paper.get("citationCount", -1) or -1,
                tldr=tldr,
                language="en",
            )
            items.append(item)

        self.logger.info(f"S2 returned {len(items)} items")
        return items

    def health_check(self) -> Dict[str, Any]:
        base_url = self.config.get("base_url", "https://api.semanticscholar.org/graph/v1")
        headers = {}
        api_key = self.config.get("api_key", "")
        if api_key:
            headers["x-api-key"] = api_key

        start = time.time()
        try:
            self.http.get_json(
                f"{base_url}/paper/search",
                params={"query": "test", "limit": 1, "fields": "title"},
                headers=headers,
                timeout=10,
            )
            latency = int((time.time() - start) * 1000)
            return {"ok": True, "message": "Semantic Scholar API reachable", "latency_ms": latency}
        except Exception as e:
            latency = int((time.time() - start) * 1000)
            return {"ok": False, "message": str(e), "latency_ms": latency}
