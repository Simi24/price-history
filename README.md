# price-history

Is that discount real? price-history pulls the **price history by store** and the current offers from Google Shopping, and judges a price against what the product actually sold for — built to be driven by an LLM agent. It ships as a CLI with compact text or JSON output, an agent skill, and an optional MCP server.

```text
$ price-history --country it product 6140211472744474228 --price 299.99
Robot Aspirapolvere Lavapavimenti roborock Qrevo S Pro (it, EUR) · range 370 €-590 €
Deal: 299.99 [NEW LOW] (-14% vs 90d low) · all-time low 349.99 · 90d low 349.99 · typical 90d 479.99
History by store:
- Amazon.it - Seller: low 349.99 · high 589.99 · last 589.99 · 90d low 349.99 (2026-04-25 → 2026-10-27, 13 points)
    Jun 27 390, Jul 13 590, Aug 24 370, Sep 06 590, Sep 07 370, Sep 08 590, Sep 11 370, Sep 16 590, Oct 08 350, Oct 27 590
```

The store advertised that 299.99 as "-49%" against 589.99. The history shows the product bounces between 589.99 and promotions at 350-390: the real discount is about 15-20%, and the price is still a new low.

## How it works

[SerpApi](https://serpapi.com/) returns Google Shopping as JSON. `google_shopping` finds the product and its id; `google_product` returns the stores selling it and, under `price_insights`, a dated price series per store. price-history summarizes each store (low, high, last, 90-day low) and gives a verdict:

| verdict | meaning |
|---|---|
| `new_low` | lower than any price in the history |
| `great` | within 5% of the lowest price of the last 90 days |
| `fair` | at or below the typical (median) price of the last 90 days |
| `high` | above the typical price |

Caveats: Google's current offers can lag a few days behind the stores (pass the price you see with `--price`), and only stores tracked by Google appear.

Each search or product call costs one SerpApi search (250 a month on the free plan). Answers are cached on disk for 24 hours (`~/.cache/price-history`, or `PRICE_HISTORY_CACHE`); the cache key never contains the API key.

## Install

```bash
uv tool install git+https://github.com/Simi24/price-history
mkdir -p ~/.config/price-history && echo "<your SerpApi key>" > ~/.config/price-history/serpapi_key
chmod 600 ~/.config/price-history/serpapi_key
export PRICE_HISTORY_COUNTRY=it   # optional: us, uk, it, de, fr, es (default us)
```

`SERPAPI_KEY` in the environment works too.

## Usage

```bash
price-history search "roborock qrevo s pro" --min-price 200
price-history product 6140211472744474228 --price 299.99
price-history credits
```

## Agent skill

`skills/price-history/SKILL.md` tells an agent when to use the tool and how to read a history. For Claude Code:

```bash
git clone https://github.com/Simi24/price-history
ln -s "$PWD/price-history/skills/price-history" ~/.claude/skills/price-history
```

It pairs with [amazon-scout](https://github.com/Simi24/amazon-scout) and [ali-scout](https://github.com/Simi24/ali-scout): they find the options, price-history tells whether the price is good.

## MCP server (optional)

```bash
uv tool install "price-history[mcp] @ git+https://github.com/Simi24/price-history"
```

```json
{
  "mcpServers": {
    "price-history": { "command": "price-history-mcp", "env": { "PRICE_HISTORY_COUNTRY": "it" } }
  }
}
```

Tools: `search_products`, `product_history`.

## Development

```bash
uv sync
uv run pytest
uv run ruff check . && uv run ruff format .
```

Tests run offline against saved fixtures in `tests/fixtures/`.

## Disclaimer

Not affiliated with Google or SerpApi. Data comes from SerpApi under its terms of service.

## License

MIT
