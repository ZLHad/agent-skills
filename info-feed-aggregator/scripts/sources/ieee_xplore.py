"""IEEE Xplore source: web search via internal REST endpoint (no API key needed)."""

import time
import json
import re
from datetime import datetime
from typing import Dict, Any, List, Optional

import requests

from .base import InfoSource, FeedItem


class IEEEXploreSource(InfoSource):
    name = "ieee"

    # Internal REST endpoint used by IEEE Xplore web frontend
    WEB_SEARCH_URL = "https://ieeexplore.ieee.org/rest/search"
    # Official API endpoint (fallback, requires API key)
    API_SEARCH_URL = "https://ieeexploreapi.ieee.org/api/v1/search/articles"

    WEB_HEADERS = {
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ),
        "Referer": "https://ieeexplore.ieee.org/search/searchresult.jsp",
        "Origin": "https://ieeexplore.ieee.org",
    }

    def search(
        self,
        keywords: List[str],
        max_results: int = 20,
        time_range: Optional[str] = None,
        **kwargs,
    ) -> List[FeedItem]:
        method = self.config.get("method", "web")
        if method == "api":
            return self._search_api(keywords, max_results, time_range, **kwargs)
        else:
            return self._search_web(keywords, max_results, time_range, **kwargs)

    def _search_web(
        self,
        keywords: List[str],
        max_results: int,
        time_range: Optional[str] = None,
        **kwargs,
    ) -> List[FeedItem]:
        """Search via IEEE Xplore internal REST endpoint (no API key)."""
        max_per_query = min(max_results, self.config.get("max_results_per_query", 50))
        query_str = " ".join(f'"{kw}"' if " " in kw else kw for kw in keywords)
        sort = kwargs.get("sort", "date")
        self.logger.info(f"IEEE web search: {query_str} (max={max_per_query}, sort={sort})")

        payload = {
            "newsearch": True,
            "queryText": query_str,
            "highlight": True,
            "returnFacets": ["ALL"],
            "returnType": "SEARCH",
            "matchPubs": True,
            "rowsPerPage": max_per_query,
            "pageNumber": 1,
        }

        # Sort order
        if sort == "date":
            payload["sortType"] = "newest"
        else:
            payload["sortType"] = "most-cited"

        # Year range filter
        if time_range:
            current_year = datetime.now().year
            if time_range in ("7d", "30d"):
                payload["ranges"] = [f"{current_year}_{current_year}_Year"]
            elif time_range in ("1y",):
                payload["ranges"] = [f"{current_year - 1}_{current_year}_Year"]
            elif time_range in ("3y",):
                payload["ranges"] = [f"{current_year - 3}_{current_year}_Year"]

        try:
            # Use a session to handle cookies
            session = requests.Session()
            session.headers.update(self.WEB_HEADERS)
            # Visit homepage to get initial cookies
            session.get(
                "https://ieeexplore.ieee.org/",
                timeout=10,
                headers={"User-Agent": self.WEB_HEADERS["User-Agent"]},
            )
            resp = session.post(
                self.WEB_SEARCH_URL,
                json=payload,
                timeout=15,
            )
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            self.logger.error(f"IEEE web search failed: {e}")
            return []

        items = []
        now_iso = datetime.utcnow().isoformat() + "Z"

        for record in data.get("records", []):
            title = record.get("articleTitle", "")
            # Strip highlight tags
            title = re.sub(r"</?highlight>", "", title)

            # Authors
            authors = []
            for a in record.get("authors", []):
                name = a.get("preferredName", "") or a.get("normalizedName", "")
                if name:
                    authors.append(name)

            # DOI & URL
            doi = record.get("doi", "")
            html_link = record.get("htmlLink", "")
            article_number = record.get("articleNumber", "")
            if doi:
                url = f"https://doi.org/{doi}"
            elif html_link:
                url = f"https://ieeexplore.ieee.org{html_link}"
            elif article_number:
                url = f"https://ieeexplore.ieee.org/document/{article_number}/"
            else:
                url = ""

            # Abstract (search endpoint returns truncated text)
            abstract = record.get("abstract", "")
            abstract = re.sub(r"</?highlight>", "", abstract)

            # Fetch full abstract from article detail endpoint if truncated
            if article_number and abstract and abstract.rstrip().endswith("..."):
                full_abstract = self._fetch_full_abstract(session, article_number)
                if full_abstract:
                    abstract = full_abstract

            # Publication date
            pub_date = ""
            pub_year = record.get("publicationYear", "")
            pub_date_raw = record.get("publicationDate", "")
            if pub_date_raw:
                # Format varies: "2024", "Jan. 2024", "15-18 March 2024", etc.
                try:
                    # Try to extract year-month
                    year_match = re.search(r"(\d{4})", pub_date_raw)
                    if year_match:
                        pub_date = pub_date_raw
                except Exception:
                    pass
            if not pub_date and pub_year:
                pub_date = str(pub_year)

            # Tags from index terms
            tags = []
            if record.get("meshTerms"):
                tags.extend(record.get("meshTerms", {}).get("terms", []))

            # Venue
            venue = record.get("publicationTitle", "")

            # Citation count
            citation_count = -1
            if record.get("citationCount"):
                try:
                    citation_count = int(record["citationCount"])
                except (ValueError, TypeError):
                    pass

            item = FeedItem(
                title=title,
                url=url,
                source_type="ieee",
                fetched_at=now_iso,
                authors=authors,
                abstract=abstract or "",
                published_date=pub_date,
                tags=tags[:10],
                doi=doi,
                venue=venue,
                citation_count=citation_count,
                language="en",
            )
            items.append(item)

        self.logger.info(f"IEEE web search returned {len(items)} items")
        return items

    def _fetch_full_abstract(self, session: requests.Session, article_number: str) -> str:
        """Fetch full abstract from IEEE article page meta description."""
        try:
            time.sleep(0.3)  # Rate limit
            resp = session.get(
                f"https://ieeexplore.ieee.org/document/{article_number}/",
                timeout=10,
            )
            if resp.status_code == 200:
                # Extract from meta description tag (contains full abstract)
                meta_match = re.search(
                    r'<meta\s+(?:name|property)=["\'](?:description|twitter:description)["\']'
                    r'\s+content=["\']([^"]*?)["\']\s*/?>',
                    resp.text,
                    re.IGNORECASE,
                )
                if meta_match:
                    abstract = meta_match.group(1).strip()
                    # Decode HTML entities
                    abstract = abstract.replace("&amp;", "&").replace("&lt;", "<")
                    abstract = abstract.replace("&gt;", ">").replace("&quot;", '"')
                    abstract = abstract.replace("&#034;", '"')
                    # Extract LaTeX math from inline-formula tags
                    abstract = re.sub(
                        r'<inline-formula[^>]*>.*?<tex-math[^>]*>\$?(.*?)\$?</tex-math>.*?</inline-formula>',
                        r'$\1$', abstract, flags=re.DOTALL,
                    )
                    # Remove any remaining HTML/XML tags
                    abstract = re.sub(r"<[^>]+>", "", abstract).strip()
                    if len(abstract) > 50:
                        return abstract
        except Exception as e:
            self.logger.debug(f"Failed to fetch full abstract for {article_number}: {e}")
        return ""

    def _search_api(
        self,
        keywords: List[str],
        max_results: int,
        time_range: Optional[str] = None,
    ) -> List[FeedItem]:
        """Fallback: search via official IEEE API (requires API key)."""
        api_key = self.config.get("api_key", "")
        if not api_key:
            self.logger.warning("IEEE API key not configured, trying web method")
            return self._search_web(keywords, max_results, time_range)

        base_url = self.config.get("base_url", self.API_SEARCH_URL)
        max_per_query = min(max_results, self.config.get("max_results_per_query", 25))
        query_str = " AND ".join(f'"{kw}"' if " " in kw else kw for kw in keywords)

        params = {
            "apikey": api_key,
            "querytext": query_str,
            "max_records": max_per_query,
            "sort_field": "article_date",
            "sort_order": "desc",
        }

        if time_range:
            current_year = datetime.now().year
            if time_range in ("1d", "7d", "30d"):
                params["start_year"] = current_year
                params["end_year"] = current_year

        try:
            data = self.http.get_json(base_url, params=params)
        except Exception as e:
            self.logger.error(f"IEEE API request failed: {e}")
            return []

        items = []
        now_iso = datetime.utcnow().isoformat() + "Z"

        for article in data.get("articles", []):
            authors = []
            for a in article.get("authors", {}).get("authors", []):
                name = a.get("full_name", "")
                if name:
                    authors.append(name)

            doi = article.get("doi", "")
            url = f"https://doi.org/{doi}" if doi else article.get("html_url", "")

            pub_date = article.get("publication_date", "")
            if not pub_date:
                pub_year = article.get("publication_year", "")
                if pub_year:
                    pub_date = f"{pub_year}"

            tags = []
            for term_type in ("ieee_terms", "author_terms"):
                terms = article.get("index_terms", {}).get(term_type, {}).get("terms", [])
                tags.extend(terms)

            item = FeedItem(
                title=article.get("title", ""),
                url=url,
                source_type="ieee",
                fetched_at=now_iso,
                authors=authors,
                abstract=article.get("abstract", ""),
                published_date=pub_date,
                tags=tags[:10],
                doi=doi,
                venue=article.get("publication_title", ""),
                citation_count=article.get("citing_paper_count", -1) or -1,
                language="en",
            )
            items.append(item)

        self.logger.info(f"IEEE API returned {len(items)} items")
        return items

    def health_check(self) -> Dict[str, Any]:
        method = self.config.get("method", "web")

        if method == "api":
            api_key = self.config.get("api_key", "")
            if not api_key:
                return {"ok": False, "message": "API key not configured", "latency_ms": 0}
            start = time.time()
            try:
                self.http.get_json(
                    self.API_SEARCH_URL,
                    params={"apikey": api_key, "querytext": "test", "max_records": 1},
                    timeout=10,
                )
                latency = int((time.time() - start) * 1000)
                return {"ok": True, "message": "IEEE API reachable", "latency_ms": latency}
            except Exception as e:
                latency = int((time.time() - start) * 1000)
                return {"ok": False, "message": str(e), "latency_ms": latency}
        else:
            # Web method health check
            start = time.time()
            try:
                resp = requests.get(
                    "https://ieeexplore.ieee.org/",
                    timeout=10,
                    headers={"User-Agent": self.WEB_HEADERS["User-Agent"]},
                )
                resp.raise_for_status()
                latency = int((time.time() - start) * 1000)
                return {"ok": True, "message": "IEEE Xplore web reachable", "latency_ms": latency}
            except Exception as e:
                latency = int((time.time() - start) * 1000)
                return {"ok": False, "message": str(e), "latency_ms": latency}
