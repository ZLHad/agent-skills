"""HTTP client with retry, rate limiting, and timeout support."""

import time
import logging
from typing import Dict, Any, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger("info-feed.http")


class HTTPClient:
    """Thin wrapper around requests.Session with retry and rate limiting."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        cfg = config or {}
        self.timeout = cfg.get("timeout_sec", 30)
        self.retry_max = cfg.get("retry_max", 3)
        self.retry_base = cfg.get("retry_base_sec", 2)
        self.min_interval = cfg.get("min_interval_sec", 1)
        self._last_request_time = 0.0

        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "info-feed-aggregator/1.0 (academic research tool)"
        })

        retry = Retry(
            total=self.retry_max,
            backoff_factor=self.retry_base,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"],
        )
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

    def _rate_limit(self):
        """Enforce minimum interval between requests."""
        if self.min_interval > 0:
            elapsed = time.time() - self._last_request_time
            if elapsed < self.min_interval:
                time.sleep(self.min_interval - elapsed)
        self._last_request_time = time.time()

    def get(
        self,
        url: str,
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        timeout: Optional[int] = None,
    ) -> requests.Response:
        """GET request with rate limiting and retry."""
        self._rate_limit()
        logger.debug(f"GET {url} params={params}")
        resp = self.session.get(
            url,
            params=params,
            headers=headers,
            timeout=timeout or self.timeout,
        )
        resp.raise_for_status()
        return resp

    def get_json(
        self,
        url: str,
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        timeout: Optional[int] = None,
    ) -> Any:
        """GET request, return parsed JSON."""
        resp = self.get(url, params=params, headers=headers, timeout=timeout)
        return resp.json()

    def get_text(
        self,
        url: str,
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        timeout: Optional[int] = None,
    ) -> str:
        """GET request, return response text."""
        resp = self.get(url, params=params, headers=headers, timeout=timeout)
        return resp.text
