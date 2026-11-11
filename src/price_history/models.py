"""Models returned by price-history: they are also the JSON contract for agents."""

import datetime as dt
from enum import StrEnum

from pydantic import BaseModel


class Listing(BaseModel):
    """A Google Shopping search result. `product_id` opens the history; `multiple_sources` means several stores."""

    product_id: str
    title: str
    price: float | None
    store: str
    multiple_sources: bool


class SearchResult(BaseModel):
    query: str
    country: str
    listings: list[Listing]


class PricePoint(BaseModel):
    date: dt.date
    price: float


class StoreHistory(BaseModel):
    store: str
    points: list[PricePoint]
    low: float
    high: float
    last: float
    low_90d: float | None


class Offer(BaseModel):
    store: str
    price: float | None
    url: str | None


class Verdict(StrEnum):
    NEW_LOW = "new_low"  # below every price in the history
    GREAT = "great"  # within 5% of the 90-day low
    FAIR = "fair"  # at or below the typical 90-day price
    HIGH = "high"  # above the typical 90-day price
    UNKNOWN = "unknown"  # no history


class DealCheck(BaseModel):
    price: float
    verdict: Verdict
    all_time_low: float | None
    low_90d: float | None
    typical_90d: float | None  # median of the last 90 days across stores
    vs_low_90d_pct: float | None
    note: str


class Product(BaseModel):
    product_id: str
    title: str
    country: str
    currency: str | None
    price_range: str | None
    offers: list[Offer]
    history: list[StoreHistory]
    deal: DealCheck | None
