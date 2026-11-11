"""From raw price points to per-store summaries and a deal verdict.

The strikethrough price shown by stores is often a launch list price, or the price a product bounces back to
between promotions. The history answers the real question: is this price low compared with what it actually sold for?
"""

import datetime as dt
import statistics

from price_history.models import DealCheck, PricePoint, StoreHistory, Verdict

WINDOW_DAYS = 90
GREAT_MARGIN = 0.05


def summarize(store: str, points: list[PricePoint], today: dt.date) -> StoreHistory:
    points = sorted(points, key=lambda p: p.date)
    recent = [p.price for p in points if (today - p.date).days <= WINDOW_DAYS]
    return StoreHistory(
        store=store,
        points=points,
        low=min(p.price for p in points),
        high=max(p.price for p in points),
        last=points[-1].price,
        low_90d=min(recent) if recent else None,
    )


def check(price: float, history: list[StoreHistory], today: dt.date) -> DealCheck:
    if not history:
        return DealCheck(
            price=price,
            verdict=Verdict.UNKNOWN,
            all_time_low=None,
            low_90d=None,
            typical_90d=None,
            vs_low_90d_pct=None,
            note="no price history",
        )
    all_time_low = min(h.low for h in history)
    recent = [p.price for h in history for p in h.points if (today - p.date).days <= WINDOW_DAYS]
    low_90d = min(recent) if recent else None
    typical = statistics.median(recent) if recent else None
    vs_low = round((price - low_90d) / low_90d * 100, 1) if low_90d else None

    if price < all_time_low:
        verdict, note = Verdict.NEW_LOW, "lower than any price in the history"
    elif low_90d is not None and price <= low_90d * (1 + GREAT_MARGIN):
        verdict, note = Verdict.GREAT, "at or near the lowest price of the last 90 days"
    elif typical is not None and price <= typical:
        verdict, note = Verdict.FAIR, "at or below the typical price of the last 90 days"
    else:
        verdict, note = Verdict.HIGH, "above the typical price of the last 90 days"
    return DealCheck(
        price=price,
        verdict=verdict,
        all_time_low=all_time_low,
        low_90d=low_90d,
        typical_90d=typical,
        vs_low_90d_pct=vs_low,
        note=note,
    )
