"""Compact text output, readable by a person and by an LLM without wasting tokens."""

from price_history.models import Product, SearchResult

_VERDICT = {"new_low": "NEW LOW", "great": "GREAT", "fair": "FAIR", "high": "HIGH", "unknown": "?"}


def search(r: SearchResult) -> str:
    lines = [f"Google Shopping ({r.country}) '{r.query}'"]
    for item in r.listings:
        price = f"{item.price:.2f}" if item.price is not None else "n/a"
        stores = " · several stores" if item.multiple_sources else ""
        lines.append(f"- [{item.product_id}] {item.title} | {price} at {item.store}{stores}")
    return "\n".join(lines)


def product(p: Product) -> str:
    lines = [f"{p.title} ({p.country}, {p.currency or '?'}) · range {p.price_range or 'n/a'}"]
    if p.deal:
        d = p.deal
        parts = [f"all-time low {d.all_time_low:.2f}" if d.all_time_low else "", f"90d low {d.low_90d:.2f}" if d.low_90d else ""]
        parts.append(f"typical 90d {d.typical_90d:.2f}" if d.typical_90d else "")
        delta = f" ({d.vs_low_90d_pct:+.0f}% vs 90d low)" if d.vs_low_90d_pct is not None else ""
        lines.append(f"Deal: {d.price:.2f} [{_VERDICT[d.verdict]}]{delta} · " + " · ".join(s for s in parts if s) + f" — {d.note}")
    lines.append("Offers now (may lag a few days):")
    lines += [f"- {o.store}: {o.price:.2f}" if o.price is not None else f"- {o.store}: n/a" for o in p.offers]
    lines.append("History by store:")
    for h in p.history:
        span = f"{h.points[0].date} → {h.points[-1].date}, {len(h.points)} points"
        low_90d = f" · 90d low {h.low_90d:.2f}" if h.low_90d is not None else ""
        lines.append(f"- {h.store}: low {h.low:.2f} · high {h.high:.2f} · last {h.last:.2f}{low_90d} ({span})")
        lines.append("    " + ", ".join(f"{pt.date:%b %d} {pt.price:.0f}" for pt in h.points[-10:]))
    return "\n".join(lines)
