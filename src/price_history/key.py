"""SerpApi key: one shared file for every SerpApi-based tool, plus the SERPAPI_KEY environment variable.

Lookup order: SERPAPI_KEY, then ~/.config/serpapi/key (shared), then the legacy per-tool file.
"""

import getpass
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
import webbrowser
from pathlib import Path

SHARED_FILE = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "serpapi" / "key"
LEGACY_FILE = Path.home() / ".config" / "price-history" / "serpapi_key"
SIGNUP_URL = "https://serpapi.com/users/sign_up"
KEY_PAGE_URL = "https://serpapi.com/manage-api-key"
ACCOUNT_ENDPOINT = "https://serpapi.com/account.json"


class MissingKeyError(RuntimeError):
    """No SerpApi key configured."""


def find() -> str:
    if key := os.environ.get("SERPAPI_KEY", "").strip():
        return key
    for path in (SHARED_FILE, LEGACY_FILE):
        if path.exists() and (key := path.read_text().strip()):
            return key
    raise MissingKeyError("missing SerpApi key: run `price-history setup`, or set SERPAPI_KEY")


def account(key: str) -> dict:
    """The account endpoint does not consume searches: it doubles as a key check."""
    try:
        with urllib.request.urlopen(f"{ACCOUNT_ENDPOINT}?{urllib.parse.urlencode({'api_key': key})}", timeout=30) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        return json.loads(e.read() or b"{}") or {"error": f"HTTP {e.code}"}


def save(key: str) -> Path:
    SHARED_FILE.parent.mkdir(parents=True, exist_ok=True)
    SHARED_FILE.write_text(key + "\n")
    SHARED_FILE.chmod(0o600)
    return SHARED_FILE


def setup(key: str | None = None, open_browser: bool = True) -> str:
    """Interactive when no key is given: open the SerpApi pages, read the key without echoing it, check it, save it."""
    if key is None:
        if not sys.stdin.isatty():
            raise MissingKeyError("no terminal to read the key from: pass it with `setup --key <key>` or set SERPAPI_KEY")
        print(f"1. Create a free SerpApi account (250 searches a month): {SIGNUP_URL}")
        print(f"2. Copy your API key from: {KEY_PAGE_URL}")
        if open_browser:
            webbrowser.open(SIGNUP_URL)
        key = getpass.getpass("3. Paste the key here (hidden): ").strip()
    info = account(key)
    if info.get("error"):
        raise MissingKeyError(f"SerpApi rejected the key: {info['error']}")
    path = save(key)
    return f"Key saved to {path} · {info.get('plan_name')}: {info.get('total_searches_left')} searches left"
