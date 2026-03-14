"""Semantic Scholar source: search via Graph API v1."""

import time
from datetime import datetime
from typing import Dict, Any, List, Optional

from .base import PaperSource, PaperItem


class SemanticScholarSource(PaperSource):
    name = "semantic_scholar"

    def search(
        self,
        keywords: List[str],
        max_results: int = 30,
        time_range: Optional[str] = None,
        **kwargs,
    ) -> List[PaperItem]:
        base_url = self.config.get("base_url", "https://api.semanticscholar.org/graph/v1")
        fields = self.config.get(
            "fields",
            "title,abstract,authors,year,citationCount,tldr,url,externalIds,"
            "publicationDate,venue,publicationVenue,journal",
        )
        max_per_query = min(max_results, self.config.get("max_results_per_query", 30))
        query_str = " ".join(keywords)
        sort_mode = kwargs.get("sort", "relevance")
        self.logger.info(f"S2 query: {query_str} (max={max_per_query})")

        headers = {}
        api_key = self.config.get("api_key", "")
        if api_key:
            headers["x-api-key"] = api_key

        # Year filter
        year_filter = ""
        if time_range:
            current_year = datetime.now().year
            year_map = {
                "7d": f"{current_year}", "30d": f"{current_year}",
                "1y": f"{current_year - 1}-{current_year}",
                "2y": f"{current_year - 2}-{current_year}",
                "3y": f"{current_year - 3}-{current_year}",
                "5y": f"{current_year - 5}-{current_year}",
                "10y": f"{current_year - 10}-{current_year}",
            }
            year_filter = year_map.get(time_range, "")

        params = {
            "query": query_str,
            "limit": max_per_query,
            "fields": fields,
        }
        if year_filter:
            params["year"] = year_filter
        if sort_mode == "date":
            params["sort"] = "publicationDate:desc"
        elif sort_mode == "citations":
            params["sort"] = "citationCount:desc"

        try:
            data = self.http.get_json(
                f"{base_url}/paper/search", params=params, headers=headers,
            )
        except Exception as e:
            self.logger.error(f"S2 request failed: {e}")
            return []

        items = []
        now_iso = datetime.utcnow().isoformat() + "Z"

        for paper in data.get("data", []):
            if not paper:
                continue

            authors = [a.get("name", "") for a in paper.get("authors", []) if a.get("name")]
            ext_ids = paper.get("externalIds", {}) or {}
            doi = ext_ids.get("DOI", "")
            arxiv_id = ext_ids.get("ArXiv", "")

            tldr_obj = paper.get("tldr")
            tldr = tldr_obj.get("text", "") if isinstance(tldr_obj, dict) else ""

            url = paper.get("url", "")
            if not url:
                paper_id = paper.get("paperId", "")
                if paper_id:
                    url = f"https://www.semanticscholar.org/paper/{paper_id}"

            pub_date = paper.get("publicationDate", "")
            year = paper.get("year", 0) or 0
            if not pub_date and year:
                pub_date = f"{year}-01-01"

            # Extract journal/venue info
            venue = paper.get("venue", "") or ""
            journal_info = paper.get("journal") or {}
            volume = ""
            pages = ""
            if isinstance(journal_info, dict):
                if not venue and journal_info.get("name"):
                    venue = journal_info["name"]
                volume = str(journal_info.get("volume", ""))
                raw_pages = journal_info.get("pages", "")
                if raw_pages:
                    pages = raw_pages.replace("-", "--")

            # Determine content type from publicationVenue
            content_type = "journal"
            pub_venue = paper.get("publicationVenue") or {}
            if isinstance(pub_venue, dict):
                vtype = pub_venue.get("type", "")
                if "conference" in vtype.lower():
                    content_type = "conference"

            item = PaperItem(
                title=paper.get("title", ""),
                url=url,
                source_type="semantic_scholar",
                fetched_at=now_iso,
                authors=authors,
                abstract=paper.get("abstract", "") or "",
                published_date=pub_date or "",
                year=year,
                doi=doi,
                arxiv_id=arxiv_id,
                venue=venue,
                volume=volume,
                pages=pages,
                citation_count=paper.get("citationCount", -1) or -1,
                tldr=tldr,
                content_type=content_type,
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
                headers=headers, timeout=10,
            )
            latency = int((time.time() - start) * 1000)
            return {"ok": True, "message": "Semantic Scholar API reachable", "latency_ms": latency}
        except Exception as e:
            latency = int((time.time() - start) * 1000)
            return {"ok": False, "message": str(e), "latency_ms": latency}
