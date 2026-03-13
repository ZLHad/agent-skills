"""Source registry for info-feed-aggregator."""

from .arxiv_source import ArxivSource

# Register all available sources. Add new sources here as they are implemented.
SOURCE_REGISTRY = {
    "arxiv": ArxivSource,
}

# Deferred imports for optional sources to avoid import errors
# when their dependencies are not installed.

def _register_optional():
    """Register sources that may not be available."""
    try:
        from .semantic_scholar import SemanticScholarSource
        SOURCE_REGISTRY["semantic_scholar"] = SemanticScholarSource
    except ImportError:
        pass
    try:
        from .ieee_xplore import IEEEXploreSource
        SOURCE_REGISTRY["ieee"] = IEEEXploreSource
    except ImportError:
        pass
    try:
        from .crossref_source import CrossrefSource
        SOURCE_REGISTRY["crossref"] = CrossrefSource
    except ImportError:
        pass
    try:
        from .rsshub import RSSHubSource
        SOURCE_REGISTRY["rsshub"] = RSSHubSource
    except ImportError:
        pass
    try:
        from .wechat_rss import WeChatRSSSource
        SOURCE_REGISTRY["wechat"] = WeChatRSSSource
    except ImportError:
        pass
    try:
        from .xiaohongshu import XiaohongshuSource
        SOURCE_REGISTRY["xiaohongshu"] = XiaohongshuSource
    except ImportError:
        pass

_register_optional()
