"""Crossref source: search via REST API for DOI metadata enrichment."""

import time
from datetime import datetime
from typing import Dict, Any, List, Optional

from .base import PaperSource, PaperItem


class CrossrefSource(PaperSource):
    name = "crossref"

    def search(
        self,
        keywords: List[str],
        max_results: int = 20,
        time_range: Optional[str] = None,
        **kwargs,
    ) -> List[PaperItem]:
        base_url = self.config.get("base_url", "https://api.crossref.org/works")
        max_per_query = min(max_results, self.config.get("max_results_per_query", 20))
        query_str = " ".join(keywords)
        sort = kwargs.get("sort", "relevance")
        self.logger.info(f"Crossref query: {query_str} (max={max_per_query})")

        params = {
            "query": query_str,
            "rows": max_per_query,
        }

        mailto = self.config.get("mailto", "")
        if mailto:
            params["mailto"] = mailto

        if sort == "date":
            params["sort"] = "published"
            params["order"] = "desc"
        elif sort == "citations":
            params["sort"] = "is-referenced-by-count"
            params["order"] = "desc"
        else:
            params["sort"] = "relevance"

        # Year filter
        if time_range:
            current_year = datetime.now().year
            year_map = {
                "1y": 1, "2y": 2, "3y": 3, "5y": 5, "10y": 10,
            }
            years_back = year_map.get(time_range)
            if years_back:
                params["filter"] = f"from-pub-date:{current_year - years_back}"

        try:
            data = self.http.get_json(base_url, params=params)
        except Exception as e:
            self.logger.error(f"Crossref request failed: {e}")
            return []

        items = []
        now_iso = datetime.utcnow().isoformat() + "Z"

        for work in data.get("message", {}).get("items", []):
            title_list = work.get("title", [])
            title = title_list[0] if title_list else ""

            authors = []
            for a in work.get("author", []):
                given = a.get("given", "")
                family = a.get("family", "")
                if given and family:
                    authors.append(f"{given} {family}")
                elif family:
                    authors.append(family)

            doi = work.get("DOI", "")
            url = f"https://doi.org/{doi}" if doi else ""

            # Publication date
            pub_date = ""
            year = 0
            date_parts = work.get("published-print", work.get("published-online", {}))
            if isinstance(date_parts, dict):
                parts = date_parts.get("date-parts", [[]])
                if parts and parts[0]:
                    year = parts[0][0] if len(parts[0]) > 0 else 0
                    month = parts[0][1] if len(parts[0]) > 1 else 1
                    day = parts[0][2] if len(parts[0]) > 2 else 1
                    pub_date = f"{year}-{month:02d}-{day:02d}"

            venue_list = work.get("container-title", [])
            venue = venue_list[0] if venue_list else ""

            volume = work.get("volume", "")
            issue = work.get("issue", "")
            page = work.get("page", "").replace("-", "--")

            abstract = work.get("abstract", "")
            # Crossref abstracts are sometimes HTML
            if abstract:
                import re
                abstract = re.sub(r"<[^>]+>", "", abstract).strip()

            citation_count = work.get("is-referenced-by-count", -1)
            if citation_count is None:
                citation_count = -1

            # Content type
            content_type = "journal"
            cr_type = work.get("type", "")
            if "proceedings" in cr_type:
                content_type = "conference"

            item = PaperItem(
                title=title,
                url=url,
                source_type="crossref",
                fetched_at=now_iso,
                authors=authors,
                abstract=abstract,
                published_date=pub_date,
                year=year,
                doi=doi,
                venue=venue,
                volume=str(volume),
                number=str(issue),
                pages=page,
                citation_count=citation_count,
                content_type=content_type,
                publisher=work.get("publisher", ""),
            )
            items.append(item)

        self.logger.info(f"Crossref returned {len(items)} items")
        return items

    def health_check(self) -> Dict[str, Any]:
        base_url = self.config.get("base_url", "https://api.crossref.org/works")
        start = time.time()
        try:
            self.http.get_json(
                base_url,
                params={"query": "test", "rows": 1},
                timeout=10,
            )
            latency = int((time.time() - start) * 1000)
            return {"ok": True, "message": "Crossref API reachable", "latency_ms": latency}
        except Exception as e:
            latency = int((time.time() - start) * 1000)
            return {"ok": False, "message": str(e), "latency_ms": latency}
