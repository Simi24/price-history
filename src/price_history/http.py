"""GET with an on-disk cache: every SerpApi call counts against the monthly quota, so answers are kept for a day."""

import hashlib
import json
import os
import time
import urllib.request
from pathlib import Path

CACHE_TTL_S = 24 * 3600
CACHE_DIR = Path(os.environ.get("PRICE_HISTORY_CACHE", Path.home() / ".cache" / "price-history"))


def _cache_path(key: str) -> Path:
    return CACHE_DIR / hashlib.sha1(key.encode()).hexdigest()


def get_json(url: str, cache_key: str | None = None, use_cache: bool = True) -> dict:
    """`cache_key` lets callers leave secrets (the API key) out of the cache key."""
    path = _cache_path(cache_key or url)
    if use_cache and path.exists() and time.time() - path.stat().st_mtime < CACHE_TTL_S:
        return json.loads(path.read_text(encoding="utf-8"))
    with urllib.request.urlopen(url, timeout=60) as r:
        body = r.read().decode("utf-8")
    payload = json.loads(body)
    if not payload.get("error"):
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        path.write_text(body, encoding="utf-8")
    return payload
