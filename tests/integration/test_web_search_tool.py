from __future__ import annotations

from unittest.mock import patch

from healthbot.infra.web_search_tool import web_search_tool


class FakeSearchProvider:
    def search(self, query: str, *, search_depth: str = "advanced", max_results: int = 8) -> dict:
        return {
            "results": [
                {
                    "title": "Random Blog",
                    "url": "https://example-blog.com/post",
                    "content": "blog content",
                    "score": 0.95,
                },
                {
                    "title": "CDC Page",
                    "url": "https://www.cdc.gov/anemia",
                    "content": "cdc content",
                    "score": 0.80,
                },
                {
                    "title": "WHO Page",
                    "url": "https://www.who.int/news-room/example",
                    "content": "who content",
                    "score": 0.75,
                },
            ]
        }


def test_web_search_tool_prioritizes_trusted_domains():
    with patch("healthbot.infra.web_search_tool.get_search_provider",
               return_value=FakeSearchProvider()
               ):
        result = web_search_tool.invoke(
            {"question": "iron deficiency anemia symptoms"}
        )

    assert result["query"] == "iron deficiency anemia symptoms"
    assert len(result["results"]) >= 1

    first = result["results"][0]
    second = result["results"][1]

    assert first["trusted_source"] is True
    assert second["trusted_source"] is True
    assert first["domain"] in {"cdc.gov", "who.int"}
    assert second["domain"] in {"cdc.gov", "who.int"}


def test_web_search_tool_enriches_results_with_domain_and_trust_flag():
    with patch("healthbot.infra.web_search_tool.get_search_provider",
               return_value=FakeSearchProvider()
               ):
        result = web_search_tool.invoke(
            {"question": "measles prevention"}
        )

    domains = [item["domain"] for item in result["results"]]
    trust_flags = [item["trusted_source"] for item in result["results"]]

    assert "cdc.gov" in domains
    assert "who.int" in domains
    assert any(flag is True for flag in trust_flags)
    assert any(flag is False for flag in trust_flags)