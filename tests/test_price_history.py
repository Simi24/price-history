import datetime as dt
import json
from pathlib import Path

import pytest

from price_history import analysis, product, serpapi
from price_history.models import PricePoint, Verdict

FIXTURES = Path(__file__).parent / "fixtures"
TODAY = dt.date(2026, 11, 11)


def load(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def test_search_listings() -> None:
    result = serpapi.parse_search(load("search.json"), "roborock saros 10r", "it")
    assert result.listings
    first = result.listings[0]
    assert first.product_id
    assert any(item.multiple_sources for item in result.listings)


def test_history_parsed_by_store() -> None:
    history = serpapi.parse_history(load("product_multi.json"))
    assert set(history) == {"MediaWorld - Marketplace MediaWorld IT", "ManoMano.it", "Techinn.com"}
    assert history["MediaWorld - Marketplace MediaWorld IT"][0] == PricePoint(date=dt.date(2026, 3, 24), price=1208.89)


def test_amazon_history_is_a_sawtooth() -> None:
    p = product.build(load("product.json"), "6140211472744474228", "it", 299.99, TODAY)
    amazon = p.history[0]
    assert amazon.low == 349.99
    assert amazon.high == 589.99
    assert p.deal is not None
    assert p.deal.verdict == Verdict.NEW_LOW
    assert p.deal.all_time_low == 349.99


def test_cheapest_offer_is_judged_by_default() -> None:
    p = product.build(load("product_multi.json"), "11596626893787107707", "it", None, TODAY)
    assert p.deal is not None
    assert p.deal.price == 762.0
    assert len(p.history) == 3


def _history(*prices: float) -> list:
    points = [PricePoint(date=TODAY - dt.timedelta(days=10 * i), price=price) for i, price in enumerate(prices)]
    return [analysis.summarize("Store", points, TODAY)]


@pytest.mark.parametrize(
    ("price", "verdict"),
    [(90.0, Verdict.NEW_LOW), (102.0, Verdict.GREAT), (110.0, Verdict.FAIR), (130.0, Verdict.HIGH)],
)
def test_verdicts(price: float, verdict: Verdict) -> None:
    assert analysis.check(price, _history(100, 120, 110, 125, 100), TODAY).verdict == verdict


def test_no_history_is_unknown() -> None:
    assert analysis.check(100.0, [], TODAY).verdict == Verdict.UNKNOWN


def test_unknown_country() -> None:
    with pytest.raises(ValueError):
        serpapi.country("xx")
