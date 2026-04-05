"""IEEE Xplore source: web search via internal REST endpoint (no API key needed)."""

import time
import re
from datetime import datetime
from typing import Dict, Any, List, Optional

import requests

from .base import PaperSource, PaperItem


class IEEEXploreSource(PaperSource):
    name = "ieee"

    WEB_SEARCH_URL = "https://ieeexplore.ieee.org/rest/search"

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
        max_results: int = 30,
        time_range: Optional[str] = None,
        **kwargs,
    ) -> List[PaperItem]:
        max_per_query = min(max_results, self.config.get("max_results_per_query", 50))
        # match_mode: "all" -> AND of quoted phrases (strict); "any" -> OR (loose).
        # Default to "any" because IEEE Xplore treats concatenated quoted phrases as an
        # AND-of-exact-phrases match, which frequently returns 0 results when multiple
        # multi-word keywords are supplied. OR keeps recall high for exploratory search.
        match_mode = kwargs.get("match_mode", "any")
        if match_mode == "all":
            query_str = " ".join(f'"{kw}"' if " " in kw else kw for kw in keywords)
        else:
            parts = [f'"{kw}"' if " " in kw else kw for kw in keywords]
            query_str = f" OR ".join(parts) if len(parts) > 1 else (parts[0] if parts else "")
        sort = kwargs.get("sort", "relevance")
        journals_filter = kwargs.get("journals")
        self.logger.info(
            f"IEEE search: {query_str} (max={max_per_query}, sort={sort}, match={match_mode})"
        )

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
        elif sort == "citations":
            payload["sortType"] = "most-cited"
        else:
            payload["sortType"] = "most-relevant"

        # Year range filter
        if time_range:
            current_year = datetime.now().year
            year_map = {
                "1y": 1, "2y": 2, "3y": 3, "5y": 5, "10y": 10,
                "7d": 0, "30d": 0,
            }
            years_back = year_map.get(time_range, 0)
            if years_back > 0:
                payload["ranges"] = [f"{current_year - years_back}_{current_year}_Year"]
            elif time_range in ("7d", "30d"):
                payload["ranges"] = [f"{current_year}_{current_year}_Year"]

        # Journal filter
        if journals_filter:
            payload["matchPubs"] = True
            # Journals as publication title refinement
            # IEEE REST API supports "refinements" for filtering by publication
            payload["refinements"] = [
                f"PublicationTitle:{j}" for j in journals_filter[:5]
            ]

        try:
            session = requests.Session()
            session.headers.update(self.WEB_HEADERS)
            session.get(
                "https://ieeexplore.ieee.org/",
                timeout=10,
                headers={"User-Agent": self.WEB_HEADERS["User-Agent"]},
            )
            resp = session.post(
                self.WEB_SEARCH_URL, json=payload, timeout=20,
            )
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            self.logger.error(f"IEEE search failed: {e}")
            return []

        items = []
        now_iso = datetime.utcnow().isoformat() + "Z"

        for record in data.get("records", []):
            title = record.get("articleTitle", "")
            title = re.sub(r"</?highlight>", "", title)

            authors = []
            for a in record.get("authors", []):
                name = a.get("preferredName", "") or a.get("normalizedName", "")
                if name:
                    authors.append(name)

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

            abstract = record.get("abstract", "")
            abstract = re.sub(r"</?highlight>", "", abstract)

            # Fetch full abstract if truncated
            if article_number and abstract and abstract.rstrip().endswith("..."):
                full_abstract = self._fetch_full_abstract(session, article_number)
                if full_abstract:
                    abstract = full_abstract

            # Publication date & year
            pub_date = ""
            pub_year = 0
            pub_year_raw = record.get("publicationYear", "")
            pub_date_raw = record.get("publicationDate", "")
            if pub_date_raw:
                year_match = re.search(r"(\d{4})", pub_date_raw)
                if year_match:
                    pub_date = pub_date_raw
                    pub_year = int(year_match.group(1))
            if not pub_year and pub_year_raw:
                try:
                    pub_year = int(pub_year_raw)
                    if not pub_date:
                        pub_date = str(pub_year)
                except (ValueError, TypeError):
                    pass

            # Tags from index terms
            tags = []
            for term_type in ("ieee_terms", "author_terms", "mesh_terms"):
                terms_obj = record.get("indexTerms", record.get("meshTerms", {}))
                if isinstance(terms_obj, dict):
                    terms = terms_obj.get(term_type, {})
                    if isinstance(terms, dict):
                        tags.extend(terms.get("terms", []))
                    elif isinstance(terms, list):
                        tags.extend(terms)

            venue = record.get("publicationTitle", "")

            citation_count = -1
            if record.get("citationCount"):
                try:
                    citation_count = int(record["citationCount"])
                except (ValueError, TypeError):
                    pass

            # Content type
            content_type = "journal"
            ct = record.get("contentType", "").lower()
            if "conference" in ct:
                content_type = "conference"
            elif "early access" in ct.lower() if ct else False:
                content_type = "early_access"

            # Volume, number, pages
            volume = record.get("volume", "")
            number = record.get("issue", "")
            start_page = record.get("startPage", "")
            end_page = record.get("endPage", "")
            pages = f"{start_page}--{end_page}" if start_page and end_page else ""

            item = PaperItem(
                title=title,
                url=url,
                source_type="ieee",
                fetched_at=now_iso,
                authors=authors,
                abstract=abstract or "",
                published_date=pub_date,
                year=pub_year,
                tags=tags[:10],
                doi=doi,
                venue=venue,
                volume=str(volume),
                number=str(number),
                pages=pages,
                citation_count=citation_count,
                content_type=content_type,
                publisher="IEEE",
            )
            items.append(item)

        self.logger.info(f"IEEE search returned {len(items)} items")
        return items

    def _fetch_full_abstract(self, session, article_number: str) -> str:
        try:
            time.sleep(0.3)
            resp = session.get(
                f"https://ieeexplore.ieee.org/document/{article_number}/",
                timeout=10,
            )
            if resp.status_code == 200:
                meta_match = re.search(
                    r'<meta\s+(?:name|property)=["\'](?:description|twitter:description)["\']'
                    r'\s+content=["\']([^"]*?)["\']\s*/?>',
                    resp.text, re.IGNORECASE,
                )
                if meta_match:
                    abstract = meta_match.group(1).strip()
                    abstract = abstract.replace("&amp;", "&").replace("&lt;", "<")
                    abstract = abstract.replace("&gt;", ">").replace("&quot;", '"')
                    abstract = abstract.replace("&#034;", '"')
                    abstract = re.sub(
                        r'<inline-formula[^>]*>.*?<tex-math[^>]*>\$?(.*?)\$?</tex-math>.*?</inline-formula>',
                        r'$\1$', abstract, flags=re.DOTALL,
                    )
                    abstract = re.sub(r"<[^>]+>", "", abstract).strip()
                    if len(abstract) > 50:
                        return abstract
        except Exception as e:
            self.logger.debug(f"Failed to fetch abstract for {article_number}: {e}")
        return ""

    def health_check(self) -> Dict[str, Any]:
        import time as _time
        start = _time.time()
        try:
            resp = requests.get(
                "https://ieeexplore.ieee.org/",
                timeout=10,
                headers={"User-Agent": self.WEB_HEADERS["User-Agent"]},
            )
            resp.raise_for_status()
            latency = int((_time.time() - start) * 1000)
            return {"ok": True, "message": "IEEE Xplore reachable", "latency_ms": latency}
        except Exception as e:
            latency = int((_time.time() - start) * 1000)
            return {"ok": False, "message": str(e), "latency_ms": latency}
