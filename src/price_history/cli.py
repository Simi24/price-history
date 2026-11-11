"""price-history: Google Shopping price history and store offers, with a deal verdict — through SerpApi.

  price-history [--country it] search "<query>" [--min-price N] [--limit N] [--json]
  price-history [--country it] product <product_id> [--price 299.99] [--json]
  price-history credits
  price-history setup [--key <key>] [--no-browser]

search and product cost one SerpApi search each (cached for 24 hours); credits and setup are free.
The verdict compares a price (given with --price, or the cheapest current offer) with the history:
new_low < all-time low, great = within 5% of the 90-day low, fair = at or below the typical 90-day price, high = above.
The SerpApi key comes from SERPAPI_KEY or ~/.config/serpapi/key (written by `setup`, shared with other
SerpApi tools); the default country from
PRICE_HISTORY_COUNTRY (us otherwise).
"""

import argparse
import sys

from price_history import key, product, render, serpapi


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--country", choices=serpapi.COUNTRIES, help="Google Shopping country")
    p.add_argument("--no-cache", action="store_true", help="ignore the 24-hour cache (costs a search)")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("search", help="find the product and its id (1 SerpApi search)")
    s.add_argument("query")
    s.add_argument("--min-price", type=float, help="drop accessories and spare parts below this price")
    s.add_argument("--limit", type=int, default=10)
    s.add_argument("--json", action="store_true")

    d = sub.add_parser("product", help="offers, history by store and deal verdict (1 SerpApi search)")
    d.add_argument("product_id")
    d.add_argument("--price", type=float, help="price to judge, e.g. the one seen on Amazon")
    d.add_argument("--json", action="store_true")

    sub.add_parser("credits", help="remaining SerpApi searches (free)")

    st = sub.add_parser("setup", help="save and check the SerpApi key (free)")
    st.add_argument("--key", help="the key, for non-interactive setup (otherwise it is asked without echo)")
    st.add_argument("--no-browser", action="store_true", help="do not open the SerpApi sign-up page")
    return p.parse_args()


def run(args: argparse.Namespace) -> str:
    use_cache = not args.no_cache
    match args.cmd:
        case "search":
            result = serpapi.search(args.query, args.country, use_cache)
            listings = [item for item in result.listings if args.min_price is None or (item.price or 0) >= args.min_price]
            result = result.model_copy(update={"listings": listings[: args.limit]})
            return result.model_dump_json(indent=1) if args.json else render.search(result)
        case "product":
            result = product.product(args.product_id, args.country, args.price, use_cache)
            return result.model_dump_json(indent=1) if args.json else render.product(result)
        case "setup":
            return key.setup(args.key, open_browser=not args.no_browser)
        case _:
            plan, left, used = serpapi.credits()
            return f"SerpApi {plan}: {left} searches left ({used} used this month)"


def main() -> None:
    args = parse_args()
    try:
        print(run(args))
    except (serpapi.MissingKeyError, serpapi.SerpApiError, ValueError) as e:
        print(f"price-history: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
