"""Generate reports from aggregated FeedItems in JSON, Markdown, and PDF."""

import json
import os
import logging
from datetime import datetime
from typing import List, Dict, Any

from sources.base import FeedItem
from utils.i18n import get_labels

logger = logging.getLogger("info-feed.reporter")

ACADEMIC_SOURCES = {"arxiv", "semantic_scholar", "ieee", "crossref"}
SOCIAL_SOURCES = {"wechat", "rsshub", "xiaohongshu"}


def generate_report(
    items: List[FeedItem],
    report_config: Dict[str, Any],
    output_dir: str,
    timestamp: str,
    output_format: str = "both",
) -> List[str]:
    """Generate output files. Returns list of generated file paths."""
    output_files = []
    language = report_config.get("language", "en")

    if output_format in ("json", "both"):
        path = os.path.join(output_dir, f"{timestamp}_feed.json")
        _write_json(items, report_config, path)
        output_files.append(path)

    if output_format in ("markdown", "both", "pdf"):
        md_path = os.path.join(output_dir, f"{timestamp}_feed.md")
        _write_markdown(items, report_config, md_path, language)
        output_files.append(md_path)

    if output_format in ("pdf", "both"):
        md_path = os.path.join(output_dir, f"{timestamp}_feed.md")
        pdf_path = os.path.join(output_dir, f"{timestamp}_feed.pdf")
        if not os.path.exists(md_path):
            _write_markdown(items, report_config, md_path, language)
        _write_pdf(md_path, pdf_path, language)
        output_files.append(pdf_path)

    return output_files


def _write_json(items: List[FeedItem], report_config: Dict, path: str):
    data = {
        "meta": {
            "generated_at": datetime.now().isoformat(),
            "total_items": len(items),
            "profile": report_config.get("profile_name", "adhoc"),
            "language": report_config.get("language", "en"),
        },
        "items": [item.to_dict() for item in items],
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    logger.info(f"JSON report: {path}")


def _split_by_category(items: List[FeedItem]):
    """Split items into academic papers and social/news articles."""
    academic = [i for i in items if i.source_type in ACADEMIC_SOURCES]
    social = [i for i in items if i.source_type not in ACADEMIC_SOURCES]
    return academic, social


def _write_markdown(
    items: List[FeedItem], report_config: Dict, path: str, language: str
):
    L = get_labels(language)
    group_by = report_config.get("group_by", "topic")
    title = report_config.get("title", L["report_title_default"])
    max_abstract = report_config.get("max_abstract_chars", 0)
    include_abstract = report_config.get("include_abstract", True)
    today = datetime.now().strftime("%Y-%m-%d %H:%M")

    lines = [f"# {title}\n"]

    # -- Cover info --
    lines.append(f"**{L['date']}**: {today}  ")

    profile_name = report_config.get("profile_name", "")
    if profile_name and profile_name != "adhoc":
        lines.append(f"**{L['profile']}**: {profile_name}  ")

    source_counts: Dict[str, int] = {}
    for item in items:
        source_counts[item.source_type] = source_counts.get(item.source_type, 0) + 1
    source_str = ", ".join(f"`{s}`({c})" for s, c in sorted(source_counts.items()))
    lines.append(f"**{L['sources']}**: {source_str}  ")
    lines.append(f"**{L['total']}**: {len(items)} {L['items']}  \n")
    lines.append("---\n")

    # -- Executive Summary placeholder --
    lines.append(f"\n## {L['executive_summary']}\n")
    lines.append("<!-- EXECUTIVE_SUMMARY -->\n")
    lines.append("---\n")

    # -- Split by category --
    academic, social = _split_by_category(items)

    # -- Academic Papers --
    if academic:
        lines.append(f"\n## {L['academic_papers']}({len(academic)})\n")

        if group_by == "topic":
            groups: Dict[str, List[FeedItem]] = {}
            for item in academic:
                key = item.matched_profile or "other"
                groups.setdefault(key, []).append(item)

            for topic_id, topic_items in groups.items():
                lines.append(f"\n### {topic_id} ({len(topic_items)})\n")
                for i, item in enumerate(topic_items, 1):
                    lines.append(
                        _format_academic_item(item, i, L, max_abstract, include_abstract)
                    )
        else:
            for i, item in enumerate(academic, 1):
                lines.append(
                    _format_academic_item(item, i, L, max_abstract, include_abstract)
                )

    # -- News & Insights --
    if social:
        lines.append(f"\n## {L['news_insights']}({len(social)})\n")
        for i, item in enumerate(social, 1):
            lines.append(
                _format_social_item(item, i, L, max_abstract, include_abstract)
            )

    # -- Footer --
    lines.append("\n---\n")
    lines.append(f"*{L['generated_by']} {today}*\n")

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    logger.info(f"Markdown report: {path}")


def _format_academic_item(
    item: FeedItem, index: int, L: dict, max_abstract: int, include_abstract: bool
) -> str:
    """Format an academic paper as Markdown."""
    parts = [f"#### {index}. [{item.title}]({item.url})\n"]

    meta = []
    if item.authors:
        authors_str = ", ".join(item.authors[:5])
        if len(item.authors) > 5:
            authors_str += f" et al. ({len(item.authors)})"
        meta.append(f"**{L['authors']}**: {authors_str}")
    if item.published_date:
        meta.append(f"**{L['pub_date']}**: {item.published_date}")
    meta.append(f"**{L['source']}**: `{item.source_type}`")
    if item.venue:
        meta.append(f"**{L['venue']}**: {item.venue}")
    if item.citation_count > 0:
        meta.append(f"**{L['citations']}**: {item.citation_count}")

    parts.append(" | ".join(meta) + "  \n")

    if include_abstract and item.abstract:
        abstract = item.abstract
        if max_abstract > 0 and len(abstract) > max_abstract:
            abstract = abstract[:max_abstract].rsplit(" ", 1)[0] + "..."
        parts.append(f"> {abstract}\n")

    if item.tldr:
        parts.append(f"**{L['tldr']}**: {item.tldr}  \n")

    score_stars = "★" * int(item.relevance_score * 5) + "☆" * (
        5 - int(item.relevance_score * 5)
    )
    score_line = f"{L['relevance']}: {score_stars} ({item.relevance_score:.2f})"
    if item.matched_keywords:
        score_line += f" | {L['matched_keywords']}: {', '.join(item.matched_keywords)}"
    parts.append(f"*{score_line}*\n")

    return "\n".join(parts)


def _format_social_item(
    item: FeedItem, index: int, L: dict, max_abstract: int, include_abstract: bool
) -> str:
    """Format a social/news article as Markdown."""
    parts = [f"#### {index}. [{item.title}]({item.url})\n"]

    meta = []
    # Extract account name from tags (wechat parser: tags[0]="wechat", tags[1]=account)
    account = ""
    if item.tags:
        for t in item.tags:
            if t not in ("wechat", "xiaohongshu", "rsshub"):
                account = t
                break
    if account:
        meta.append(f"**{L['account']}**: {account}")
    if item.published_date:
        meta.append(f"**{L['pub_date']}**: {item.published_date}")
    meta.append(f"**{L['source']}**: `{item.source_type}`")

    parts.append(" | ".join(meta) + "  \n")

    if include_abstract and item.abstract:
        abstract = item.abstract
        if max_abstract > 0 and len(abstract) > max_abstract:
            abstract = abstract[:max_abstract].rsplit(" ", 1)[0] + "..."
        parts.append(f"> {abstract}\n")

    # Engagement stats
    engagement = []
    if item.likes > 0:
        engagement.append(f"{L['likes']}: {item.likes}")
    if item.comments_count > 0:
        engagement.append(f"{L['comments']}: {item.comments_count}")
    if item.shares > 0:
        engagement.append(f"{L['shares']}: {item.shares}")
    if engagement:
        parts.append(f"*{' | '.join(engagement)}*  \n")

    score_stars = "★" * int(item.relevance_score * 5) + "☆" * (
        5 - int(item.relevance_score * 5)
    )
    score_line = f"{L['relevance']}: {score_stars} ({item.relevance_score:.2f})"
    if item.matched_keywords:
        score_line += f" | {L['matched_keywords']}: {', '.join(item.matched_keywords)}"
    parts.append(f"*{score_line}*\n")

    return "\n".join(parts)


def _write_pdf(md_path: str, pdf_path: str, language: str = "en"):
    """Render Markdown to PDF via pandoc + xelatex (render_pdf.py)."""
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        render_script = os.path.join(script_dir, "render_pdf.py")

        import subprocess
        result = subprocess.run(
            ["python3", render_script, "-i", md_path, "-o", pdf_path, "-l", language],
            capture_output=True, text=True,
        )
        if result.returncode != 0:
            logger.error(f"PDF generation failed: {result.stderr}")
        else:
            logger.info(f"PDF report: {pdf_path}")
    except Exception as e:
        logger.error(f"PDF generation failed: {e}")
