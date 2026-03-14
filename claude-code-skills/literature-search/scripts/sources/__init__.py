"""Source registry for literature-search."""

from .base import PaperItem, PaperSource

SOURCE_REGISTRY = {}


def _register_sources():
    try:
        from .ieee_xplore import IEEEXploreSource
        SOURCE_REGISTRY["ieee"] = IEEEXploreSource
    except ImportError:
        pass
    try:
        from .semantic_scholar import SemanticScholarSource
        SOURCE_REGISTRY["semantic_scholar"] = SemanticScholarSource
    except ImportError:
        pass
    try:
        from .arxiv_source import ArxivSource
        SOURCE_REGISTRY["arxiv"] = ArxivSource
    except ImportError:
        pass
    try:
        from .crossref_source import CrossrefSource
        SOURCE_REGISTRY["crossref"] = CrossrefSource
    except ImportError:
        pass


_register_sources()
