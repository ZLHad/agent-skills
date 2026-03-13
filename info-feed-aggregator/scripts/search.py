#!/usr/bin/env python3
"""
Info Feed Aggregator — CLI entry point.

Usage:
    python3 search.py --keywords "LLM agent" "tool use" --max-results 20
    python3 search.py --profile daily_academic
    python3 search.py --keywords "AIGC" --sources arxiv semantic_scholar
    python3 search.py --keywords "movable antenna" --time-range 7d
    python3 search.py --health
    python3 search.py --list-profiles
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime

# Ensure scripts/ is on the path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

SKILL_DIR = os.path.dirname(SCRIPT_DIR)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Multi-source information feed aggregator"
    )

    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--keywords", nargs="+", help="Ad-hoc search keywords")
    mode.add_argument("--profile", type=str, help="Search profile name")
    mode.add_argument(
        "--health", action="store_true", help="Health check all enabled sources"
    )
    mode.add_argument(
        "--list-profiles", action="store_true", help="List available profiles"
    )

    parser.add_argument(
        "--sources", nargs="+", default=None, help="Override sources to query"
    )
    parser.add_argument(
        "--max-results",
        type=int,
        default=30,
        help="Max results per source per query (default: 30)",
    )
    parser.add_argument(
        "--time-range", type=str, default=None, help="Lookback: 1d, 7d, 30d, 1y"
    )
    parser.add_argument(
        "--sort",
        choices=["date", "relevance"],
        default="date",
        help="Sort order: date (newest first) or relevance (default: date)",
    )
    parser.add_argument(
        "--language", type=str, default=None, help="Report language: en, zh"
    )
    parser.add_argument(
        "--output-format",
        choices=["json", "markdown", "pdf", "both"],
        default="both",
        help="Output format (default: both = JSON + MD + PDF)",
    )
    parser.add_argument("--output-dir", type=str, default=None, help="Output directory")
    parser.add_argument("--config", type=str, default=None, help="Path to sources.json")
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Verbose logging"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Show config without executing"
    )

    return parser


def cmd_list_profiles():
    from utils.config_loader import list_profiles

    profiles_dir = os.path.join(SKILL_DIR, "config", "profiles")
    profiles = list_profiles(profiles_dir)
    if not profiles:
        print(json.dumps({"profiles": [], "message": "No profiles found"}, indent=2))
        return
    print(json.dumps({"profiles": profiles}, indent=2, ensure_ascii=False))


def cmd_health(config):
    from sources import SOURCE_REGISTRY
    from utils.http_client import HTTPClient

    http = HTTPClient(config.get("global", {}).get("http", {}))
    results = {}

    for source_name, source_cls in SOURCE_REGISTRY.items():
        source_config = config.get("sources", {}).get(source_name, {})
        source = source_cls(source_config, http)
        try:
            results[source_name] = source.health_check()
        except Exception as e:
            results[source_name] = {"ok": False, "message": str(e), "latency_ms": -1}

    print(json.dumps({"health": results}, indent=2, ensure_ascii=False))


def cmd_search(args, config):
    from sources import SOURCE_REGISTRY
    from utils.config_loader import load_profile, merge_config_with_args
    from utils.http_client import HTTPClient
    from aggregator import aggregate
    from reporter import generate_report

    # Load profile if specified
    profile = None
    if args.profile:
        profiles_dir = os.path.join(SKILL_DIR, "config", "profiles")
        profile = load_profile(args.profile, profiles_dir)

    effective = merge_config_with_args(config, profile, args)

    if args.dry_run:
        print(json.dumps(effective, indent=2, ensure_ascii=False))
        return

    http = HTTPClient(config.get("global", {}).get("http", {}))
    all_items = []
    sources_queried = []
    errors = []

    sources_to_use = effective.get("active_sources", [])
    topics = effective.get("topics", [])

    for source_name in sources_to_use:
        source_cls = SOURCE_REGISTRY.get(source_name)
        if not source_cls:
            errors.append(f"Unknown source: {source_name}")
            continue

        source_config = config.get("sources", {}).get(source_name, {})
        source = source_cls(source_config, http)

        if not source.is_enabled() and source_name not in (args.sources or []):
            logging.info(f"Source {source_name} disabled, skipping")
            continue

        sources_queried.append(source_name)

        for topic in topics:
            if not topic.get("enabled", True):
                continue

            try:
                sort_order = topic.get("sort", getattr(args, "sort", "date"))
                items = source.search(
                    keywords=topic.get("keywords", []),
                    max_results=topic.get("max_items", args.max_results),
                    time_range=topic.get("time_range", args.time_range),
                    categories=topic.get("categories"),
                    sort=sort_order,
                )
                for item in items:
                    item.matched_profile = topic.get("id", "adhoc")
                all_items.extend(items)
            except Exception as e:
                errors.append(f"{source_name}/{topic.get('id', '?')}: {e}")
                logging.error(f"Search failed for {source_name}: {e}")

    # Aggregate
    ranked = aggregate(all_items, topics)

    # Apply global max limit
    max_total = config.get("global", {}).get("max_total_items", 50)
    if len(ranked) > max_total:
        ranked = ranked[:max_total]

    # Generate report
    output_dir = args.output_dir or os.path.join(SKILL_DIR, "reports")
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    report_config = effective.get("report", {})
    output_files = generate_report(
        items=ranked,
        report_config=report_config,
        output_dir=output_dir,
        timestamp=timestamp,
        output_format=args.output_format,
    )

    # Print summary to stdout
    summary = {
        "status": "ok" if not errors else "partial",
        "total_fetched": len(all_items),
        "after_dedup": len(ranked),
        "sources_queried": sources_queried,
        "topics_searched": len(topics),
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

    if args.list_profiles:
        cmd_list_profiles()
        return

    # Load config
    from utils.config_loader import load_config

    config_path = args.config or os.path.join(SKILL_DIR, "config", "sources.json")
    if not os.path.exists(config_path):
        print(
            json.dumps(
                {"status": "error", "message": f"Config not found: {config_path}"}
            )
        )
        sys.exit(1)
    config = load_config(config_path)

    if args.health:
        cmd_health(config)
        return

    cmd_search(args, config)


if __name__ == "__main__":
    main()
