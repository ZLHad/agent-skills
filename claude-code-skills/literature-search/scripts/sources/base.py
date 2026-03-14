"""Core data model and source interface for literature-search."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional
from datetime import datetime
import hashlib
import logging
import re


@dataclass
class PaperItem:
    """Academic paper metadata."""

    # Required
    title: str = ""
    url: str = ""
    source_type: str = ""  # "ieee" | "semantic_scholar" | "arxiv"
    fetched_at: str = ""

    # Core metadata
    authors: List[str] = field(default_factory=list)
    abstract: str = ""
    published_date: str = ""
    year: int = 0
    tags: List[str] = field(default_factory=list)

    # Identifiers
    doi: str = ""
    arxiv_id: str = ""

    # Publication info
    venue: str = ""  # Journal/conference name
    volume: str = ""
    number: str = ""
    pages: str = ""
    publisher: str = ""
    content_type: str = ""  # "journal" | "conference" | "early_access" | "preprint"

    # Metrics
    citation_count: int = -1
    tldr: str = ""

    # Aggregator-computed
    relevance_score: float = 0.0
    dedup_key: str = ""
    matched_keywords: List[str] = field(default_factory=list)
    search_round: str = ""

    def compute_dedup_key(self) -> str:
        if self.doi:
            self.dedup_key = f"doi:{self.doi.lower().strip()}"
        elif self.arxiv_id:
            self.dedup_key = f"arxiv:{self.arxiv_id.strip()}"
        else:
            normalized = self.title.lower().strip()
            normalized = "".join(c for c in normalized if c.isalnum() or c == " ")
            normalized = " ".join(normalized.split())
            self.dedup_key = f"title:{hashlib.sha256(normalized.encode()).hexdigest()[:16]}"
        return self.dedup_key

    def to_bibtex(self) -> str:
        """Generate BibTeX entry."""
        # Build cite key: FirstAuthorLastName + Year + first keyword word
        first_author = ""
        if self.authors:
            parts = self.authors[0].replace(",", " ").split()
            first_author = parts[-1] if parts else "Unknown"
            first_author = re.sub(r"[^a-zA-Z]", "", first_author)
        year = self.year or ""
        cite_key = f"{first_author}{year}"

        # Determine entry type
        if self.content_type == "conference":
            entry_type = "inproceedings"
        elif self.arxiv_id and not self.venue:
            entry_type = "article"
        else:
            entry_type = "article"

        # Format authors for BibTeX
        bib_authors = " and ".join(self.authors) if self.authors else "Unknown"

        lines = [f"@{entry_type}{{{cite_key},"]
        lines.append(f"  author    = {{{bib_authors}}},")
        lines.append(f"  title     = {{{self.title}}},")

        if entry_type == "inproceedings":
            lines.append(f"  booktitle = {{{self.venue}}},")
        elif self.venue:
            lines.append(f"  journal   = {{{self.venue}}},")
        elif self.arxiv_id:
            lines.append(f"  journal   = {{arXiv preprint arXiv:{self.arxiv_id}}},")

        if year:
            lines.append(f"  year      = {{{year}}},")
        if self.volume:
            lines.append(f"  volume    = {{{self.volume}}},")
        if self.number:
            lines.append(f"  number    = {{{self.number}}},")
        if self.pages:
            lines.append(f"  pages     = {{{self.pages}}},")
        if self.doi:
            lines.append(f"  doi       = {{{self.doi}}},")

        lines.append("}")
        return "\n".join(lines)

    def to_dict(self) -> dict:
        d = asdict(self)
        return {
            k: v
            for k, v in d.items()
            if v and v != -1 and v != 0 and v != 0.0 and v != []
        }


class PaperSource(ABC):
    """Abstract base class for academic paper sources."""

    name: str = ""

    def __init__(self, source_config: Dict[str, Any], http_client=None):
        self.config = source_config
        self.http = http_client
        self.logger = logging.getLogger(f"lit-search.{self.name}")

    @abstractmethod
    def search(
        self,
        keywords: List[str],
        max_results: int = 30,
        time_range: Optional[str] = None,
        **kwargs,
    ) -> List[PaperItem]:
        ...

    @abstractmethod
    def health_check(self) -> Dict[str, Any]:
        ...

    def is_enabled(self) -> bool:
        return self.config.get("enabled", True)
