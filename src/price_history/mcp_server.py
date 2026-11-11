"""MCP server (stdio) on top of the same functions as the CLI. Needs the extra: uv sync --extra mcp."""

from fastmcp import FastMCP

from price_history import product, serpapi
from price_history.models import Product, SearchResult

mcp = FastMCP("price-history")


@mcp.tool
def search_products(query: str, min_price: float | None = None, limit: int = 10, country: str | None = None) -> SearchResult:
    """Find a product on Google Shopping and get its product_id (costs one SerpApi search). Use min_price to drop
    accessories and spare parts. Prefer listings with multiple_sources: they carry the history of several stores."""
    result = serpapi.search(query, country)
    listings = [item for item in result.listings if min_price is None or (item.price or 0) >= min_price]
    return result.model_copy(update={"listings": listings[:limit]})


@mcp.tool
def product_history(product_id: str, price: float | None = None, country: str | None = None) -> Product:
    """Current offers, price history by store and a deal verdict for `price` (or the cheapest current offer):
    new_low, great (within 5% of the 90-day low), fair (at or below the typical 90-day price), high.
    Costs one SerpApi search. Google's current offers can lag a few days behind the stores."""
    return product.product(product_id, country, price)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
