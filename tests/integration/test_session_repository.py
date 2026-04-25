from healthbot.repositories.session_repository import (
    InMemorySessionRepository,
    SessionNotFoundError,
)
from healthbot.repositories.sqlite_session_repository import SQLiteSessionRepository


def test_in_memory_session_repository_roundtrip():
    repo = InMemorySessionRepository()

    repo.create_session("abc")
    repo.append_event("abc", {"type": "ask", "question": "What is flu?"})

    assert repo.exists("abc") is True
    assert repo.list_sessions() == ["abc"]
    assert repo.get_history("abc") == [{"type": "ask", "question": "What is flu?"}]


def test_in_memory_session_repository_rejects_unknown_session():
    repo = InMemorySessionRepository()

    try:
        repo.append_event("missing", {"type": "ask"})
        raise AssertionError("Expected SessionNotFoundError")
    except SessionNotFoundError:
        pass


def test_sqlite_session_repository_roundtrip(tmp_path):
    repo = SQLiteSessionRepository(str(tmp_path / "sessions.db"))

    repo.create_session("abc")
    repo.append_event("abc", {"type": "ask", "question": "What is flu?"})

    assert repo.exists("abc") is True
    assert repo.get_history("abc") == [{"type": "ask", "question": "What is flu?"}]
