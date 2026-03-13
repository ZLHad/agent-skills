"""Load and merge configuration files."""

import json
import os
import re
from typing import Dict, Any, Optional, List


def load_config(config_path: str) -> Dict[str, Any]:
    """Load sources.json, resolving ${ENV_VAR} placeholders."""
    with open(config_path, "r", encoding="utf-8") as f:
        raw = f.read()

    # Resolve ${ENV_VAR} placeholders
    def _resolve_env(match):
        var_name = match.group(1)
        return os.environ.get(var_name, "")

    resolved = re.sub(r"\$\{(\w+)\}", _resolve_env, raw)
    return json.loads(resolved)


def load_profile(
    profile_name: str, profiles_dir: str
) -> Dict[str, Any]:
    """Load a search profile by name from the profiles directory."""
    profile_path = os.path.join(profiles_dir, f"{profile_name}.json")
    if not os.path.exists(profile_path):
        raise FileNotFoundError(
            f"Profile '{profile_name}' not found at {profile_path}"
        )
    with open(profile_path, "r", encoding="utf-8") as f:
        return json.load(f)


def list_profiles(profiles_dir: str) -> List[Dict[str, str]]:
    """List all available profiles with name and description."""
    profiles = []
    if not os.path.isdir(profiles_dir):
        return profiles
    for fname in sorted(os.listdir(profiles_dir)):
        if not fname.endswith(".json"):
            continue
        fpath = os.path.join(profiles_dir, fname)
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                data = json.load(f)
            profiles.append({
                "name": data.get("profile_name", fname.replace(".json", "")),
                "description": data.get("description", ""),
                "file": fname,
            })
        except (json.JSONDecodeError, IOError):
            continue
    return profiles


def merge_config_with_args(
    config: Dict[str, Any],
    profile: Optional[Dict[str, Any]],
    args,
) -> Dict[str, Any]:
    """Merge sources.json config with profile and CLI args into effective config.

    Returns a dict with keys: active_sources, topics, report, global.
    """
    effective = {
        "global": config.get("global", {}),
        "active_sources": [],
        "topics": [],
        "report": {},
    }

    # Determine active sources
    if args.sources:
        effective["active_sources"] = args.sources
    elif profile and "sources_override" in profile:
        effective["active_sources"] = profile["sources_override"]
    else:
        # Use all enabled sources from config
        effective["active_sources"] = [
            name
            for name, src_cfg in config.get("sources", {}).items()
            if src_cfg.get("enabled", False)
        ]

    # Determine topics
    if profile and "topics" in profile:
        effective["topics"] = profile["topics"]
    elif hasattr(args, "keywords") and args.keywords:
        # Build a synthetic single topic from CLI keywords
        effective["topics"] = [
            {
                "id": "adhoc",
                "name": "Ad-hoc Search",
                "enabled": True,
                "keywords": args.keywords,
                "time_range": args.time_range,
                "max_items": args.max_results,
            }
        ]

    # Report config
    if profile and "report" in profile:
        effective["report"] = profile["report"]

    # CLI overrides
    if hasattr(args, "language") and args.language:
        effective["report"]["language"] = args.language
    if hasattr(args, "max_results") and args.max_results:
        for topic in effective["topics"]:
            if "max_items" not in topic:
                topic["max_items"] = args.max_results

    if profile:
        effective["report"]["profile_name"] = profile.get("profile_name", "")

    return effective
