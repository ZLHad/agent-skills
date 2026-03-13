"""Crossref source: search via REST API (free, no auth required)."""

import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

from .base import InfoSource, FeedItem


class CrossrefSource(InfoSource):
    name = "crossref"

    def search(
        self,
        keywords: List[str],
        max_results: int = 20,
        time_range: Optional[str] = None,
        **kwargs,
    ) -> List[FeedItem]:
        base_url = self.config.get("base_url", "https://api.crossref.org/works")
        mailto = self.config.get("mailto", "")
        max_per_query = min(
            max_results,
            self.config.get("max_results_per_query", 20),
        )

        query_str = " ".join(keywords)
        self.logger.info(f"Crossref query: {query_str} (max={max_per_query})")

        params = {
            "query": query_str,
            "rows": max_per_query,
            "sort": "published",
            "order": "desc",
            "select": "DOI,title,author,abstract,published,container-title,is-referenced-by-count,URL,subject,type",
        }

        if mailto:
            params["mailto"] = mailto

        # Date filter
        if time_range:
            now = datetime.now()
            days_map = {"1d": 1, "7d": 7, "30d": 30}
            days = days_map.get(time_range, 30)
            from_date = (now - timedelta(days=days)).strftime("%Y-%m-%d")
            params["filter"] = f"from-pub-date:{from_date}"

        try:
            data = self.http.get_json(base_url, params=params)
        except Exception as e:
            self.logger.error(f"Crossref request failed: {e}")
            return []

        items = []
        now_iso = datetime.utcnow().isoformat() + "Z"

        message = data.get("message", {})
        for work in message.get("items", []):
            # Title
            titles = work.get("title", [])
            title = titles[0] if titles else ""

            # Authors
            authors = []
            for a in work.get("author", []):
                given = a.get("given", "")
                family = a.get("family", "")
                if given and family:
                    authors.append(f"{given} {family}")
                elif family:
                    authors.append(family)

            # DOI
            doi = work.get("DOI", "")
            url = f"https://doi.org/{doi}" if doi else work.get("URL", "")

            # Date
            pub_date = ""
            published = work.get("published", {})
            date_parts = published.get("date-parts", [[]])
            if date_parts and date_parts[0]:
                parts = date_parts[0]
                if len(parts) >= 3:
                    pub_date = f"{parts[0]}-{parts[1]:02d}-{parts[2]:02d}"
                elif len(parts) >= 2:
                    pub_date = f"{parts[0]}-{parts[1]:02d}-01"
                elif len(parts) >= 1:
                    pub_date = f"{parts[0]}-01-01"

            # Venue
            containers = work.get("container-title", [])
            venue = containers[0] if containers else ""

            # Tags/subjects
            tags = work.get("subject", [])

            # Abstract (Crossref sometimes has it with JATS tags)
            abstract = work.get("abstract", "")
            if abstract:
                import re
                abstract = re.sub(r"<[^>]+>", "", abstract).strip()

            item = FeedItem(
                title=title,
                url=url,
                source_type="crossref",
                fetched_at=now_iso,
                authors=authors,
                abstract=abstract,
                published_date=pub_date,
                tags=tags[:10],
                doi=doi,
                venue=venue,
                citation_count=work.get("is-referenced-by-count", -1) or -1,
                language="en",
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
