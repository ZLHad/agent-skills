"""Core data model and source interface for info-feed-aggregator."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional
from datetime import datetime
import hashlib
import logging


@dataclass
class FeedItem:
    """Universal information item across all sources.

    Academic and social sources share the same flat structure.
    Unused fields are left empty/default and stripped in to_dict().
    """

    # Required fields (every source MUST populate these)
    title: str = ""
    url: str = ""
    source_type: str = ""  # "arxiv" | "semantic_scholar" | "ieee" | "crossref" | "rsshub" | "wechat" | "xiaohongshu"
    fetched_at: str = ""   # ISO 8601

    # Common optional fields
    authors: List[str] = field(default_factory=list)
    abstract: str = ""
    published_date: str = ""  # ISO 8601 (best effort)
    tags: List[str] = field(default_factory=list)
    language: str = ""        # "en", "zh", etc.

    # Academic-specific (empty for social sources)
    doi: str = ""
    arxiv_id: str = ""
    venue: str = ""           # Journal/conference name
    citation_count: int = -1  # -1 = unknown
    tldr: str = ""            # Semantic Scholar TL;DR

    # Social-specific (empty for academic sources)
    likes: int = -1
    comments_count: int = -1
    shares: int = -1
    media_urls: List[str] = field(default_factory=list)

    # Aggregator-computed fields
    relevance_score: float = 0.0
    dedup_key: str = ""
    matched_keywords: List[str] = field(default_factory=list)
    matched_profile: str = ""

    def compute_dedup_key(self) -> str:
        """Generate a fingerprint for deduplication.

        Priority: DOI > arXiv ID > normalized title hash.
        """
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

    def to_dict(self) -> dict:
        """Serialize to dict, omitting empty/default fields for compact JSON."""
        d = asdict(self)
        return {
            k: v
            for k, v in d.items()
            if v and v != -1 and v != 0.0 and v != []
        }


class InfoSource(ABC):
    """Abstract base class for all information sources.

    Each concrete source MUST implement:
    - name (class attribute): unique source identifier
    - search(): fetch items matching a query
    - health_check(): verify connectivity/credentials
    """

    name: str = ""

    def __init__(self, source_config: Dict[str, Any], http_client=None):
        self.config = source_config
        self.http = http_client
        self.logger = logging.getLogger(f"info-feed.{self.name}")

    @abstractmethod
    def search(
        self,
        keywords: List[str],
        max_results: int = 20,
        time_range: Optional[str] = None,
        **kwargs,
    ) -> List[FeedItem]:
        """Fetch items matching the given keywords.

        Args:
            keywords: Search terms. Combination logic is source-specific.
            max_results: Maximum items to return.
            time_range: Lookback window ("1d", "7d", "30d").

        Returns:
            List of FeedItem instances.
        """
        ...

    @abstractmethod
    def health_check(self) -> Dict[str, Any]:
        """Verify source reachability and credentials.

        Returns:
            {"ok": bool, "message": str, "latency_ms": int}
        """
        ...

    def is_enabled(self) -> bool:
        return self.config.get("enabled", False)
