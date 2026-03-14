#!/usr/bin/env python3
"""
Literature Search — CLI entry point for academic paper search.

Usage:
    python3 search.py --keywords "movable antenna" "beamforming" --max-results 30
    python3 search.py --keywords "RIS" --sources ieee --time-range 3y --sort relevance
    python3 search.py --keywords "deep reinforcement learning" "resource allocation" \
        --sources ieee semantic_scholar arxiv --sort citations --min-citations 10
    python3 search.py --health
    python3 search.py --merge results/file1.json results/file2.json -o results/merged
    python3 search.py --finalize results/merged.json --categories categories.json \
        --topic "AIGC inference in SAGIN"
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

SKILL_DIR = os.path.dirname(SCRIPT_DIR)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Academic literature search for writing Related Work / surveys"
    )

    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--keywords", nargs="+", help="Search keywords")
    mode.add_argument("--health", action="store_true", help="Health check all sources")
    mode.add_argument(
        "--merge", nargs="+", metavar="JSON_FILE",
        help="Merge multiple result JSON files (dedup & re-rank)",
    )
    mode.add_argument(
        "--finalize", type=str, metavar="JSON_FILE",
        help="Generate final organized report from a JSON result file + categories JSON",
    )

    parser.add_argument(
        "--sources", nargs="+", default=["ieee", "semantic_scholar", "arxiv"],
        help="Sources to query (default: ieee semantic_scholar arxiv)",
    )
    parser.add_argument(
        "--max-results", type=int, default=30,
        help="Max results per source (default: 30)",
    )
    parser.add_argument(
        "--time-range", type=str, default=None,
        help="Lookback: 1y, 2y, 3y, 5y, 10y (default: no limit)",
    )
    parser.add_argument(
        "--sort", choices=["date", "relevance", "citations"], default="relevance",
        help="Sort order (default: relevance)",
    )
    parser.add_argument(
        "--min-citations", type=int, default=0,
        help="Minimum citation count filter (default: 0)",
    )
    parser.add_argument(
        "--output-format", choices=["json", "markdown", "bibtex", "all"], default="all",
        help="Output format (default: all = JSON + MD + BibTeX)",
    )
    parser.add_argument("--output-dir", "-o", type=str, default=None, help="Output directory")
    parser.add_argument("--round-id", type=str, default=None, help="Label for this search round")
    parser.add_argument(
        "--categories", type=str, default=None,
        help="Path to categories JSON for --finalize (maps category names to paper indices or DOIs)",
    )
    parser.add_argument(
        "--topic", type=str, default="",
        help="Topic description for --finalize report header",
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")

    return parser


def cmd_health():
    from sources import SOURCE_REGISTRY
    from utils.http_client import HTTPClient

    http = HTTPClient()
    results = {}
    for name, cls in SOURCE_REGISTRY.items():
        source = cls({}, http)
        try:
            results[name] = source.health_check()
        except Exception as e:
            results[name] = {"ok": False, "message": str(e), "latency_ms": -1}

    print(json.dumps({"health": results}, indent=2, ensure_ascii=False))


def cmd_merge(files, args):
    from sources.base import PaperItem
    from aggregator import aggregate
    from reporter import generate_report

    all_items = []
    all_keywords = []

    for filepath in files:
        if not os.path.exists(filepath):
            print(json.dumps({"status": "error", "message": f"File not found: {filepath}"}))
            continue
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        kws = data.get("meta", {}).get("keywords", [])
        all_keywords.extend(kws)

        for p in data.get("papers", []):
            item = PaperItem(**{
                k: v for k, v in p.items()
                if k in PaperItem.__dataclass_fields__
            })
            all_items.append(item)

    # Deduplicate unique keywords
    all_keywords = list(dict.fromkeys(all_keywords))

    ranked = aggregate(all_items, all_keywords, min_citations=args.min_citations)

    output_dir = args.output_dir or os.path.join(SKILL_DIR, "results")
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    output_files = generate_report(
        items=ranked,
        output_dir=output_dir,
        timestamp=f"{timestamp}_merged",
        output_format=args.output_format,
        keywords=all_keywords,
    )

    summary = {
        "status": "ok",
        "total_input": len(all_items),
        "after_dedup": len(ranked),
        "merged_files": files,
        "output_files": output_files,
    }
    print(json.dumps(summary, indent=2, ensure_ascii=False))


def cmd_finalize(args):
    """Generate final organized report from a JSON result file + categories mapping."""
    from collections import OrderedDict
    from sources.base import PaperItem
    from reporter import generate_final_report

    source_path = args.finalize
    if not os.path.exists(source_path):
        print(json.dumps({"status": "error", "message": f"File not found: {source_path}"}))
        sys.exit(1)

    with open(source_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Load all papers
    all_papers = []
    # Handle both flat format (papers: [...]) and categorized format (categories: {...})
    if "papers" in data:
        for p in data["papers"]:
            item = PaperItem(**{
                k: v for k, v in p.items()
                if k in PaperItem.__dataclass_fields__
            })
            all_papers.append(item)
    elif "categories" in data:
        for cat_items in data["categories"].values():
            for p in cat_items:
                item = PaperItem(**{
                    k: v for k, v in p.items()
                    if k in PaperItem.__dataclass_fields__
                })
                all_papers.append(item)

    # Load categories mapping
    categories = OrderedDict()
    if args.categories and os.path.exists(args.categories):
        with open(args.categories, "r", encoding="utf-8") as f:
            cat_map = json.load(f)

        # cat_map format: {"Category Name": [doi1, doi2, ...] or [index1, index2, ...]}
        # Build lookup by DOI and title
        doi_lookup = {}
        title_lookup = {}
        for item in all_papers:
            if item.doi:
                doi_lookup[item.doi.lower()] = item
            if item.title:
                title_lookup[item.title.lower().strip()] = item

        for cat_name, identifiers in cat_map.items():
            cat_papers = []
            for ident in identifiers:
                if isinstance(ident, int):
                    # Index-based
                    if 0 <= ident < len(all_papers):
                        cat_papers.append(all_papers[ident])
                elif isinstance(ident, str):
                    # DOI or title match
                    found = doi_lookup.get(ident.lower())
                    if not found:
                        found = title_lookup.get(ident.lower().strip())
                    if found:
                        cat_papers.append(found)
            if cat_papers:
                categories[cat_name] = cat_papers
    else:
        # No categories file: group by search_round
        round_groups = OrderedDict()
        for item in all_papers:
            key = item.search_round or "Uncategorized"
            round_groups.setdefault(key, []).append(item)
        categories = round_groups

    output_dir = args.output_dir or os.path.join(SKILL_DIR, "results")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    output_files = generate_final_report(
        categories=categories,
        output_dir=output_dir,
        timestamp=timestamp,
        topic_description=args.topic,
    )

    summary = {
        "status": "ok",
        "total_papers": sum(len(v) for v in categories.values()),
        "categories": {k: len(v) for k, v in categories.items()},
        "output_files": output_files,
    }
    print(json.dumps(summary, indent=2, ensure_ascii=False))


def cmd_search(args):
    from sources import SOURCE_REGISTRY
    from utils.http_client import HTTPClient
    from aggregator import aggregate
    from reporter import generate_report

    http_config = {"timeout_sec": 30, "retry_max": 3, "min_interval_sec": 1}
    http = HTTPClient(http_config)

    all_items = []
    sources_queried = []
    errors = []

    for source_name in args.sources:
        source_cls = SOURCE_REGISTRY.get(source_name)
        if not source_cls:
            errors.append(f"Unknown source: {source_name}")
            continue

        source_config = {"enabled": True}
        if source_name == "ieee":
            source_config["max_results_per_query"] = 50
        elif source_name == "semantic_scholar":
            source_config["max_results_per_query"] = 30

        source = source_cls(source_config, http)
        sources_queried.append(source_name)

        try:
            items = source.search(
                keywords=args.keywords,
                max_results=args.max_results,
                time_range=args.time_range,
                sort=args.sort,
            )
            round_label = args.round_id or " + ".join(args.keywords)
            for item in items:
                item.search_round = round_label
            all_items.extend(items)
        except Exception as e:
            errors.append(f"{source_name}: {e}")
            logging.error(f"Search failed for {source_name}: {e}")

    ranked = aggregate(all_items, args.keywords, min_citations=args.min_citations)

    output_dir = args.output_dir or os.path.join(SKILL_DIR, "results")
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    output_files = generate_report(
        items=ranked,
        output_dir=output_dir,
        timestamp=timestamp,
        output_format=args.output_format,
        keywords=args.keywords,
    )

    summary = {
        "status": "ok" if not errors else "partial",
        "total_fetched": len(all_items),
        "after_dedup": len(ranked),
        "sources_queried": sources_queried,
        "keywords": args.keywords,
        "output_files": output_files,
    }
    if errors:
        summary["errors"] = errors

    print(json.dumps(summary, indent=2, ensure_ascii=False))


def main():
    parser = build_parser()
    args = parser.parse_args()

    level = logging.DEBUG if args.verbose else logging.WARNING
    logging.basicConfig(
        level=level, format="%(asctime)s [%(name)s] %(levelname)s: %(message)s"
    )

    if args.health:
        cmd_health()
        return

    if args.merge:
        cmd_merge(args.merge, args)
        return

    if args.finalize:
        cmd_finalize(args)
        return

    cmd_search(args)


if __name__ == "__main__":
    main()
