"""Session persistence contracts and implementations."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from typing import Protocol


@dataclass(slots=True)
class SessionRecord:
    """Persisted session metadata."""

    session_id: str
    created_at: float


class SessionRepository(Protocol):
    """Persistence contract for API sessions."""

    def create_session(self, session_id: str) -> None: ...

    def exists(self, session_id: str) -> bool: ...

    def list_sessions(self) -> list[str]: ...

    def append_event(self, session_id: str, entry: dict) -> None: ...

    def get_history(self, session_id: str) -> list[dict]: ...

    def close(self) -> None: ...


class JsonSerializer:
    """JSON helper shared by persistence implementations."""

    @staticmethod
    def dumps(value: dict) -> str:
        return json.dumps(value, ensure_ascii=False)

    @staticmethod
    def loads(value: str | bytes) -> dict:
        if isinstance(value, bytes):
            value = value.decode("utf-8")
        return json.loads(value)


class SessionRepositoryError(RuntimeError):
    """Raised when the configured session backend cannot be used."""


class SessionNotFoundError(KeyError):
    """Raised when a session id cannot be found in persistence."""


class SessionKeyBuilder:
    """Generate Redis keys in a single place."""

    def __init__(self, prefix: str = "medlearn") -> None:
        self.prefix = prefix

    def meta(self, session_id: str) -> str:
        return f"{self.prefix}:session:{session_id}:meta"

    def history(self, session_id: str) -> str:
        return f"{self.prefix}:session:{session_id}:history"

    def index(self) -> str:
        return f"{self.prefix}:sessions:index"


class InMemorySessionRepository:
    """Fallback repository kept for tests and local development."""

    def __init__(self) -> None:
        self._sessions: dict[str, SessionRecord] = {}
        self._history: dict[str, list[dict]] = {}

    def create_session(self, session_id: str) -> None:
        self._sessions[session_id] = SessionRecord(
            session_id=session_id,
            created_at=time.time(),
        )
        self._history[session_id] = []

    def exists(self, session_id: str) -> bool:
        return session_id in self._sessions

    def list_sessions(self) -> list[str]:
        return list(self._sessions.keys())

    def append_event(self, session_id: str, entry: dict) -> None:
        if session_id not in self._history:
            raise SessionNotFoundError(session_id)
        self._history[session_id].append(entry)

    def get_history(self, session_id: str) -> list[dict]:
        if session_id not in self._history:
            raise SessionNotFoundError(session_id)
        return list(self._history[session_id])

    def close(self) -> None:
        return None
