from __future__ import annotations

from unittest.mock import MagicMock, patch

from healthbot.infra.search_provider import SearchProvider


def test_search_provider_calls_tavily_client():
    fake_client = MagicMock()
    fake_client.search.return_value = {"results": []}

    with patch("healthbot.infra.search_provider.TavilyClient", return_value=fake_client):
        provider = SearchProvider(api_key="test-key")
        result = provider.search("anemia symptoms", search_depth="advanced", max_results=5)

    fake_client.search.assert_called_once_with(
        "anemia symptoms",
        search_depth="advanced",
        max_results=5,
    )
    assert result == {"results": []}