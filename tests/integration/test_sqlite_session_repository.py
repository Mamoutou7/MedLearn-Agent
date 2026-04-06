from __future__ import annotations

from pathlib import Path

import pytest

from healthbot.repositories.session_repository import SessionNotFoundError
from healthbot.repositories.sqlite_session_repository import SQLiteSessionRepository


def test_create_session_and_exists(tmp_path: Path):
    db_path = tmp_path / "sessions.db"
    repository = SQLiteSessionRepository(str(db_path))

    repository.create_session("session-1")

    assert repository.exists("session-1") is True
    assert repository.exists("missing-session") is False
    repository.close()

def test_append_event_and_get_history(tmp_path: Path):
    db_path = tmp_path / "sessions.db"
    repository = SQLiteSessionRepository(str(db_path))

    repository.create_session("session-1")
    repository.append_event("session-1", {"role": "user", "content": "Hello"})
    repository.append_event("session-1", {"role": "assistant", "content": "Hi there"})

    history = repository.get_history("session-1")

    assert len(history) == 2
    assert history[0]["role"] == "user"
    assert history[0]["content"] == "Hello"
    assert history[1]["role"] == "assistant"
    assert history[1]["content"] == "Hi there"

    repository.close()

def test_append_event_raises_for_missing_session(tmp_path: Path):
    db_path = tmp_path / "sessions.db"
    repository = SQLiteSessionRepository(str(db_path))

    with pytest.raises(SessionNotFoundError):
        repository.append_event("missing-session", {"role": "user", "content": "Hello"})


def test_get_history_raises_for_missing_session(tmp_path: Path):
    db_path = tmp_path / "sessions.db"
    repository = SQLiteSessionRepository(str(db_path))

    with pytest.raises(SessionNotFoundError):
        repository.get_history("missing-session")


def test_list_sessions_returns_created_sessions_in_order(tmp_path: Path):
    db_path = tmp_path / "sessions.db"
    repository = SQLiteSessionRepository(str(db_path))

    repository.create_session("session-1")
    repository.create_session("session-2")

    sessions = repository.list_sessions()

    assert sessions == ["session-1", "session-2"]


def test_ping_returns_true(tmp_path: Path):
    db_path = tmp_path / "sessions.db"
    repository = SQLiteSessionRepository(str(db_path))

    assert repository.ping() is True


def test_session_persists_across_repository_instances(tmp_path: Path):
    db_path = tmp_path / "sessions.db"

    repository1 = SQLiteSessionRepository(str(db_path))
    repository1.create_session("session-1")
    repository1.append_event("session-1", {"role": "user", "content": "Persistent hello"})
    repository1.close()

    repository2 = SQLiteSessionRepository(str(db_path))

    assert repository2.exists("session-1") is True
    history = repository2.get_history("session-1")
    assert len(history) == 1
    assert history[0]["content"] == "Persistent hello"


def test_foreign_keys_are_enforced(tmp_path: Path):
    db_path = tmp_path / "sessions.db"
    repository = SQLiteSessionRepository(str(db_path))

    with pytest.raises(SessionNotFoundError):
        repository.append_event("unknown-session", {"role": "assistant", "content": "No session"})