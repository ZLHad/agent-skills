"""Merge, deduplicate, score, and rank FeedItems from multiple sources."""

import logging
from datetime import datetime, timezone
from typing import List, Dict, Any

from sources.base import FeedItem

logger = logging.getLogger("info-feed.aggregator")


def aggregate(
    items: List[FeedItem], topics: List[Dict[str, Any]]
) -> List[FeedItem]:
    """Full aggregation pipeline: dedup -> score -> rank."""
    # Compute dedup keys
    for item in items:
        item.compute_dedup_key()

    # Deduplicate
    deduped = _deduplicate(items)
    logger.info(f"Dedup: {len(items)} -> {len(deduped)} items")

    # Collect all keywords from topics
    all_keywords = []
    for topic in topics:
        all_keywords.extend(topic.get("keywords", []))

    # Score
    for item in deduped:
        item.relevance_score = _compute_relevance(item, all_keywords)

    # Rank by relevance descending
    ranked = sorted(deduped, key=lambda x: x.relevance_score, reverse=True)
    return ranked


def _normalize_title(title: str) -> str:
    """Normalize title for dedup comparison."""
    t = title.lower().strip()
    t = "".join(c for c in t if c.isalnum() or c == " ")
    return " ".join(t.split())


def _merge_items(base: FeedItem, other: FeedItem) -> None:
    """Merge metadata from `other` into `base` (fill gaps only)."""
    if not base.tldr and other.tldr:
        base.tldr = other.tldr
    if base.citation_count == -1 and other.citation_count != -1:
        base.citation_count = other.citation_count
    if not base.doi and other.doi:
        base.doi = other.doi
    if not base.arxiv_id and other.arxiv_id:
        base.arxiv_id = other.arxiv_id
    if not base.venue and other.venue:
        base.venue = other.venue
    if not base.abstract and other.abstract:
        base.abstract = other.abstract


def _deduplicate(items: List[FeedItem]) -> List[FeedItem]:
    """Group by dedup_key + title similarity. Keep version with most metadata."""
    seen: Dict[str, FeedItem] = {}
    # Secondary index: normalized title -> dedup_key (for cross-source dedup)
    title_index: Dict[str, str] = {}

    for item in items:
        key = item.dedup_key
        norm_title = _normalize_title(item.title)

        # Check if this title was already seen under a different dedup_key
        if norm_title in title_index and title_index[norm_title] != key:
            # Same paper, different IDs (e.g., arXiv ID vs DOI)
            key = title_index[norm_title]

        if key not in seen:
            seen[key] = item
            if norm_title:
                title_index[norm_title] = key
        else:
            existing = seen[key]
            new_fields = len(item.to_dict())
            old_fields = len(existing.to_dict())

            if new_fields > old_fields:
                _merge_items(item, existing)
                seen[key] = item
            else:
                _merge_items(existing, item)

    return list(seen.values())


def _compute_relevance(item: FeedItem, keywords: List[str]) -> float:
    """Compute relevance score (0.0 to 1.0).

    Components:
    - Keyword match ratio (0-0.6)
    - Recency boost (0-0.2)
    - Quality signals (0-0.2)
    """
    score = 0.0
    search_text = f"{item.title} {item.abstract}".lower()

    # Keyword matching (0.0-0.6)
    if keywords:
        matches = 0
        matched = []
        for kw in keywords:
            kw_lower = kw.lower().strip('"')
            if kw_lower in search_text:
                # Exact match for the full keyword
                matches += 1
                matched.append(kw)
            elif " " in kw_lower:
                # Multi-word keyword: check if all words appear individually
                words = kw_lower.split()
                if all(w in search_text for w in words):
                    matches += 0.8  # Slightly less credit than exact match
                    matched.append(kw)
        keyword_ratio = matches / len(keywords)
        score += min(keyword_ratio * 0.6, 0.6)
        item.matched_keywords = matched

    # Recency boost (0.0-0.2)
    if item.published_date:
        try:
            pub_date = datetime.fromisoformat(
                item.published_date.replace("Z", "+00:00")
            )
            now = datetime.now(timezone.utc)
            if pub_date.tzinfo is None:
                from datetime import timezone as tz
                pub_date = pub_date.replace(tzinfo=tz.utc)
            days_old = (now - pub_date).days
            if days_old <= 1:
                score += 0.20
            elif days_old <= 7:
                score += 0.15
            elif days_old <= 30:
                score += 0.10
            else:
                score += 0.05
        except (ValueError, TypeError):
            score += 0.05
    else:
        score += 0.05

    # Quality signals (0.0-0.2)
    if item.abstract and len(item.abstract) > 50:
        score += 0.05
    if item.tldr:
        score += 0.05
    if item.citation_count > 0:
        score += min(item.citation_count / 100, 0.05)
    if item.authors:
        score += 0.05

    return min(round(score, 3), 1.0)
