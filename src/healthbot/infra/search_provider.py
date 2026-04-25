"""Search provider abstraction for Tavily-backed web retrieval."""

from __future__ import annotations

from tavily import TavilyClient

from healthbot.core.settings import settings


class SearchProvider:
    """Singleton-style provider for Tavily search client."""

    def __init__(self, api_key: str) -> None:
        self._client = TavilyClient(api_key=api_key)

    def search(self, query: str, *, search_depth: str = "advanced", max_results: int = 8) -> dict:
        return self._client.search(
            query,
            search_depth=search_depth,
            max_results=max_results,
        )


_search_provider: SearchProvider | None = None


def get_search_provider() -> SearchProvider:
    """Return a lazily initialized shared search provider."""
    global _search_provider

    if _search_provider is None:
        _search_provider = SearchProvider(api_key=settings.tavily_api_key)

    return _search_provider
