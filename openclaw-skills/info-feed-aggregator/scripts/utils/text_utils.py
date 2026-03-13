"""Text utilities for title normalization, abstract truncation, language detection."""

import re
import hashlib
import unicodedata


def normalize_title(title: str) -> str:
    """Normalize a title for dedup comparison.

    - Lowercase
    - Strip leading/trailing whitespace
    - Collapse multiple whitespace to single space
    - Remove common prefixes like "[PDF]", "(PDF)", etc.
    - Strip non-alphanumeric chars (keep CJK)
    """
    if not title:
        return ""
    t = title.strip().lower()
    # Remove common noise prefixes
    t = re.sub(r"^\[pdf\]\s*", "", t, flags=re.IGNORECASE)
    t = re.sub(r"^\(pdf\)\s*", "", t, flags=re.IGNORECASE)
    # Collapse whitespace
    t = re.sub(r"\s+", " ", t)
    return t.strip()


def title_hash(title: str) -> str:
    """SHA-256 hex digest of the normalized title."""
    return hashlib.sha256(normalize_title(title).encode("utf-8")).hexdigest()


def truncate_abstract(text: str, max_chars: int = 500, ellipsis: str = "...") -> str:
    """Truncate text to max_chars, breaking at word/sentence boundary if possible."""
    if not text or len(text) <= max_chars:
        return text or ""

    truncated = text[:max_chars]

    # Try to break at last sentence boundary
    for sep in ["。", ". ", "！", "! ", "？", "? "]:
        idx = truncated.rfind(sep)
        if idx > max_chars * 0.5:
            return truncated[: idx + len(sep)].strip()

    # Try to break at last word boundary (space)
    idx = truncated.rfind(" ")
    if idx > max_chars * 0.5:
        return truncated[:idx].strip() + ellipsis

    return truncated.strip() + ellipsis


def strip_html(text: str) -> str:
    """Remove HTML tags from text."""
    if not text:
        return ""
    clean = re.sub(r"<[^>]+>", "", text)
    # Decode common HTML entities
    clean = clean.replace("&amp;", "&")
    clean = clean.replace("&lt;", "<")
    clean = clean.replace("&gt;", ">")
    clean = clean.replace("&quot;", '"')
    clean = clean.replace("&#39;", "'")
    clean = clean.replace("&nbsp;", " ")
    return clean.strip()


def detect_language(text: str) -> str:
    """Simple heuristic language detection: 'zh' if CJK chars > 20%, else 'en'."""
    if not text:
        return "en"
    cjk_count = 0
    total = 0
    for ch in text:
        if ch.isspace():
            continue
        total += 1
        if _is_cjk(ch):
            cjk_count += 1
    if total == 0:
        return "en"
    return "zh" if cjk_count / total > 0.2 else "en"


def _is_cjk(char: str) -> bool:
    """Check if a character is CJK."""
    cp = ord(char)
    # CJK Unified Ideographs
    if 0x4E00 <= cp <= 0x9FFF:
        return True
    # CJK Unified Ideographs Extension A
    if 0x3400 <= cp <= 0x4DBF:
        return True
    # CJK Unified Ideographs Extension B
    if 0x20000 <= cp <= 0x2A6DF:
        return True
    # CJK Compatibility Ideographs
    if 0xF900 <= cp <= 0xFAFF:
        return True
    return False


def format_authors(authors: list, max_display: int = 3) -> str:
    """Format author list: 'A, B, C et al. (N)' if too many."""
    if not authors:
        return ""
    if len(authors) <= max_display:
        return ", ".join(authors)
    shown = ", ".join(authors[:max_display])
    return f"{shown} et al. ({len(authors)})"
