---
name: price-history
description: Price history by store and current offers from Google Shopping, with a verdict on whether a price is actually a deal. Use it when the user asks whether a discount is real, whether to buy now or wait, what a product normally costs, or where it is cheapest across stores ("is this a good deal?", "is the discount real?", "price history of X", "what does X usually cost?").
---

# price-history

## Setup (only if the command is missing)

- `price-history` not found: propose `uv tool install git+https://github.com/Simi24/price-history` and wait for the person to agree.
- Exit code 2 with "missing SerpApi key": the person must create a free SerpApi account (250 searches a month) and run `price-history setup` in their own terminal, which reads the key without echoing it and saves it to `~/.config/serpapi/key`. Never ask them to paste the key into the chat.
- Default country: set `PRICE_HISTORY_COUNTRY` (e.g. `it`) or pass the option on each call.

## Commands

```bash
price-history search "<query>" [--min-price N] [--limit 10] [--json]   # 1 search: find the product_id
price-history product <product_id> [--price 299.99] [--json]          # 1 search: offers, history, verdict
price-history credits                                                  # free
```

## Flow

1. `search` with the precise model name and `--min-price` set to roughly half the expected price: generic queries return accessories and spare parts first.
2. Pick a listing **with "several stores"**: it carries the history of more stores. The same product often appears under several product ids (one per store); if the first has a thin history, try another.
3. `product <id> --price <price seen in the store>` and read the verdict:

| verdict | meaning |
|---|---|
| `new_low` | lower than any price in the history |
| `great` | within 5% of the lowest price of the last 90 days |
| `fair` | at or below the typical (median) price of the last 90 days |
| `high` | above the typical price: likely better to wait for a promotion |
| `unknown` | no history for this product |

## Reading the history

- **The strikethrough price lies.** It is often the launch list price, or the price the product bounces back to between promotions (a "sawtooth": 589 → 370 → 589 → 350). The real discount is against the recent lows and the typical price, not against the strikethrough.
- **Current offers can lag a few days** behind the stores: always pass the price you actually see with `--price`, and trust the store's own page (or amazon-scout / ali-scout) for the current price.
- Only stores tracked by Google appear: a store can be missing from the history even if it sells the product.
- Each `search` and `product` costs one SerpApi search (250 a month on the free plan, possibly shared with other tools). Answers are cached for 24 hours.
