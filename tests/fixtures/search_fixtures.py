from __future__ import annotations

import pytest


@pytest.fixture
def tavily_search_payload() -> dict:
    return {
        "results": [
            {
                "title": "CDC Page",
                "url": "https://www.cdc.gov/anemia",
                "content": "cdc content",
                "score": 0.8,
            },
            {
                "title": "WHO Page",
                "url": "https://www.who.int/news-room/example",
                "content": "who content",
                "score": 0.75,
            },
        ]
    }
