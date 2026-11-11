"""Google Shopping through SerpApi: `google_shopping` finds products, `google_product` returns stores and price history.

Every new call costs one search from the monthly quota (250 on the free plan): answers are cached for a day.
"""

import datetime as dt
import os
import urllib.parse

from price_history import http, key
from price_history.models import Listing, Offer, PricePoint, SearchResult

ENDPOINT = "https://serpapi.com/search.json"
ACCOUNT_ENDPOINT = "https://serpapi.com/account.json"
DEFAULT_COUNTRY = "us"
# Google `gl` country code -> (`hl` language, `location`)
COUNTRIES = {
    "us": ("en", "United States"),
    "uk": ("en", "United Kingdom"),
    "it": ("it", "Italy"),
    "de": ("de", "Germany"),
    "fr": ("fr", "France"),
    "es": ("es", "Spain"),
}


class SerpApiError(RuntimeError):
    """SerpApi answered with an error (quota exhausted, invalid key, unknown product...)."""


MissingKeyError = key.MissingKeyError


def api_key() -> str:
    return key.find()


def country(name: str | None = None) -> str:
    code = name or os.environ.get("PRICE_HISTORY_COUNTRY", DEFAULT_COUNTRY)
    if code not in COUNTRIES:
        raise ValueError(f"unknown country '{code}', available: {', '.join(COUNTRIES)}")
    return code


def _fetch(params: dict[str, str], code: str, use_cache: bool) -> dict:
    hl, location = COUNTRIES[code]
    query = {**params, "gl": "uk" if code == "uk" else code, "hl": hl, "location": location}
    cache_key = f"{ENDPOINT}?{urllib.parse.urlencode(query)}"
    payload = http.get_json(f"{cache_key}&{urllib.parse.urlencode({'api_key': api_key()})}", cache_key, use_cache)
    if payload.get("error"):
        raise SerpApiError(payload["error"])
    return payload


def parse_search(payload: dict, query: str, code: str) -> SearchResult:
    listings = [
        Listing(
            product_id=str(r["product_id"]),
            title=r.get("title", ""),
            price=r.get("extracted_price"),
            store=r.get("source", ""),
            multiple_sources=bool(r.get("multiple_sources")),
        )
        for r in payload.get("shopping_results") or []
        if r.get("product_id")
    ]
    return SearchResult(query=query, country=code, listings=listings)


def parse_offers(payload: dict) -> list[Offer]:
    stores = (payload.get("product_results") or {}).get("stores") or []
    return [Offer(store=s.get("name", ""), price=s.get("extracted_price"), url=s.get("link")) for s in stores]


def parse_history(payload: dict) -> dict[str, list[PricePoint]]:
    insights = (payload.get("product_results") or {}).get("price_insights") or {}
    return {
        s.get("name", ""): [
            PricePoint(date=dt.datetime.strptime(p["date"], "%b %d, %Y").date(), price=p["price"]) for p in s.get("prices") or []
        ]
        for s in insights.get("stores") or []
    }


def search(query: str, code: str | None = None, use_cache: bool = True) -> SearchResult:
    c = country(code)
    return parse_search(_fetch({"engine": "google_shopping", "q": query}, c, use_cache), query, c)


def product_payload(product_id: str, code: str | None = None, use_cache: bool = True) -> tuple[dict, str]:
    c = country(code)
    return _fetch({"engine": "google_product", "product_id": product_id}, c, use_cache), c


def credits() -> tuple[str | None, int | None, int | None]:
    """(plan, searches left, used this month). The account endpoint does not consume searches."""
    payload = http.get_json(f"{ACCOUNT_ENDPOINT}?{urllib.parse.urlencode({'api_key': api_key()})}", use_cache=False)
    if payload.get("error"):
        raise SerpApiError(payload["error"])
    return payload.get("plan_name"), payload.get("total_searches_left"), payload.get("this_month_usage")
