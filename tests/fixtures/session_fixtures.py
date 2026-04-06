from __future__ import annotations

import pytest


@pytest.fixture
def sample_session_id() -> str:
    return "session-test-123"


@pytest.fixture
def sample_history_entry() -> dict:
    return {"type": "ask", "question": "What is flu?"}
