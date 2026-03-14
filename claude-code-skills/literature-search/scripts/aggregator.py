"""Merge, deduplicate, score, and rank PaperItems from multiple sources."""

import logging
from datetime import datetime, timezone
from typing import List, Dict, Any

from sources.base import PaperItem

logger = logging.getLogger("lit-search.aggregator")


def aggregate(
    items: List[PaperItem], keywords: List[str],
    min_citations: int = 0,
) -> List[PaperItem]:
    """Full aggregation pipeline: dedup -> score -> filter -> rank."""
    for item in items:
        item.compute_dedup_key()

    deduped = _deduplicate(items)
    logger.info(f"Dedup: {len(items)} -> {len(deduped)} items")

    for item in deduped:
        item.relevance_score = _compute_relevance(item, keywords)

    # Filter by min citations
    if min_citations > 0:
        deduped = [
            i for i in deduped
            if i.citation_count >= min_citations or i.citation_count == -1
        ]

    ranked = sorted(deduped, key=lambda x: x.relevance_score, reverse=True)
    return ranked


def _normalize_title(title: str) -> str:
    t = title.lower().strip()
    t = "".join(c for c in t if c.isalnum() or c == " ")
    return " ".join(t.split())


def _merge_items(base: PaperItem, other: PaperItem) -> None:
    """Merge metadata from other into base (fill gaps only)."""
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
    if not base.volume and other.volume:
        base.volume = other.volume
    if not base.pages and other.pages:
        base.pages = other.pages
    if base.year == 0 and other.year != 0:
        base.year = other.year


def _deduplicate(items: List[PaperItem]) -> List[PaperItem]:
    seen: Dict[str, PaperItem] = {}
    title_index: Dict[str, str] = {}

    for item in items:
        key = item.dedup_key
        norm_title = _normalize_title(item.title)

        if norm_title in title_index and title_index[norm_title] != key:
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


def _compute_relevance(item: PaperItem, keywords: List[str]) -> float:
    """Compute relevance score (0.0 to 1.0).

    Components:
    - Keyword match ratio (0-0.5)
    - Recency boost (0-0.15)
    - Citation boost (0-0.15)
    - Quality signals (0-0.2)
    """
    score = 0.0
    search_text = f"{item.title} {item.abstract}".lower()

    # Keyword matching (0.0-0.5)
    if keywords:
        matches = 0
        matched = []
        for kw in keywords:
            kw_lower = kw.lower().strip('"')
            if kw_lower in search_text:
                matches += 1
                matched.append(kw)
            elif " " in kw_lower:
                words = kw_lower.split()
                if all(w in search_text for w in words):
                    matches += 0.8
                    matched.append(kw)
        keyword_ratio = matches / len(keywords)
        score += min(keyword_ratio * 0.5, 0.5)
        item.matched_keywords = matched

    # Recency boost (0.0-0.15)
    if item.published_date:
        try:
            pub_str = item.published_date[:10]
            pub_date = datetime.strptime(pub_str, "%Y-%m-%d")
            pub_date = pub_date.replace(tzinfo=timezone.utc)
            now = datetime.now(timezone.utc)
            days_old = (now - pub_date).days
            if days_old <= 180:
                score += 0.15
            elif days_old <= 365:
                score += 0.12
            elif days_old <= 730:
                score += 0.08
            else:
                score += 0.04
        except (ValueError, TypeError):
            score += 0.04
    else:
        score += 0.04

    # Citation boost (0.0-0.15)
    if item.citation_count > 0:
        if item.citation_count >= 100:
            score += 0.15
        elif item.citation_count >= 50:
            score += 0.12
        elif item.citation_count >= 20:
            score += 0.09
        elif item.citation_count >= 5:
            score += 0.06
        else:
            score += 0.03

    # Quality signals (0.0-0.2)
    if item.abstract and len(item.abstract) > 100:
        score += 0.05
    if item.tldr:
        score += 0.03
    if item.authors:
        score += 0.02
    if item.doi:
        score += 0.03
    if item.venue:
        score += 0.04
    if item.content_type in ("journal",):
        score += 0.03

    return min(round(score, 3), 1.0)
