"""Product view: current offers, per-store history and, given a price, the deal verdict."""

import datetime as dt

from price_history import analysis, serpapi
from price_history.models import Product


def build(payload: dict, product_id: str, code: str, price: float | None, today: dt.date) -> Product:
    results = payload.get("product_results") or {}
    offers = serpapi.parse_offers(payload)
    history = [analysis.summarize(store, points, today) for store, points in serpapi.parse_history(payload).items() if points]
    # Without an explicit price, judge the cheapest current offer.
    target = price if price is not None else min((o.price for o in offers if o.price), default=None)
    return Product(
        product_id=product_id,
        title=results.get("title", ""),
        country=code,
        currency=(results.get("price_insights") or {}).get("currency"),
        price_range=results.get("price_range"),
        offers=offers,
        history=history,
        deal=analysis.check(target, history, today) if target is not None else None,
    )


def product(product_id: str, code: str | None = None, price: float | None = None, use_cache: bool = True) -> Product:
    payload, c = serpapi.product_payload(product_id, code, use_cache)
    return build(payload, product_id, c, price, dt.date.today())
