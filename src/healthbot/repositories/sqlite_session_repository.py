"""SQLite-backed session repository for persistent local and production-safe state."""

from __future__ import annotations

import os
import sqlite3
import threading
import time

from healthbot.repositories.session_repository import (
    JsonSerializer,
    SessionNotFoundError,
    SessionRepositoryError,
)


class SQLiteSessionRepository:
    """Persist session metadata and API-visible history in SQLite."""

    def __init__(self, database_path: str) -> None:
        self._database_path = database_path
        db_dir = os.path.dirname(database_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)

        try:
            self._conn = sqlite3.connect(database_path, check_same_thread=False)
            self._conn.row_factory = sqlite3.Row
            self._lock = threading.Lock()
            self._serializer = JsonSerializer()
            self._configure_connection()
            self._initialize()
        except sqlite3.Error as exc:
            raise SessionRepositoryError(
                f"Failed to initialize SQLite session repository at {database_path!r}: {exc}"
            ) from exc

    def _configure_connection(self) -> None:
        """Configure SQLite connection pragmas."""
        with self._conn:
            self._conn.execute("PRAGMA foreign_keys = ON")

    def _initialize(self) -> None:
        with self._conn:
            self._conn.execute(
                """
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    created_at REAL NOT NULL
                )
                """
            )
            self._conn.execute(
                """
                CREATE TABLE IF NOT EXISTS session_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    created_at REAL NOT NULL,
                    FOREIGN KEY(session_id) REFERENCES sessions(session_id) ON DELETE CASCADE
                )
                """
            )
            self._conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_session_events_session_id
                ON session_events(session_id, id)
                """
            )

    def create_session(self, session_id: str) -> None:
        try:
            with self._lock, self._conn:
                self._conn.execute(
                    "INSERT OR IGNORE INTO sessions(session_id, created_at) VALUES (?, ?)",
                    (session_id, time.time()),
                )
        except sqlite3.Error as exc:
            raise SessionRepositoryError(f"Failed to create session {session_id!r}: {exc}") from exc

    def exists(self, session_id: str) -> bool:
        try:
            with self._lock:
                row = self._conn.execute(
                    "SELECT 1 FROM sessions WHERE session_id = ? LIMIT 1",
                    (session_id,),
                ).fetchone()
            return row is not None
        except sqlite3.Error as exc:
            raise SessionRepositoryError(f"Failed to check session {session_id!r}: {exc}") from exc

    def list_sessions(self) -> list[str]:
        try:
            with self._lock:
                rows = self._conn.execute(
                    "SELECT session_id FROM sessions ORDER BY created_at ASC"
                ).fetchall()
            return [str(row[0]) for row in rows]
        except sqlite3.Error as exc:
            raise SessionRepositoryError(f"Failed to list sessions: {exc}") from exc

    def append_event(self, session_id: str, entry: dict) -> None:
        """Append an event to a session history.

        Relies on SQLite foreign key enforcement to validate the session existence,
        avoiding a separate SELECT/exists() call before INSERT.
        """
        payload = self._serializer.dumps(entry)

        try:
            with self._lock, self._conn:
                self._conn.execute(
                    """
                    INSERT INTO session_events(session_id, payload, created_at)
                    VALUES (?, ?, ?)
                    """,
                    (session_id, payload, time.time()),
                )
        except sqlite3.IntegrityError as exc:
            # Foreign key violation -> session_id does not exist
            raise SessionNotFoundError(session_id) from exc
        except sqlite3.Error as exc:
            raise SessionRepositoryError(
                f"Failed to append event for {session_id!r}: {exc}"
            ) from exc

    def get_history(self, session_id: str) -> list[dict]:
        if not self.exists(session_id):
            raise SessionNotFoundError(session_id)

        try:
            with self._lock:
                rows = self._conn.execute(
                    """
                    SELECT payload
                    FROM session_events
                    WHERE session_id = ?
                    ORDER BY id ASC
                    """,
                    (session_id,),
                ).fetchall()
            return [self._serializer.loads(str(row[0])) for row in rows]
        except sqlite3.Error as exc:
            raise SessionRepositoryError(f"Failed to load history for {session_id!r}: {exc}") from exc

    def ping(self) -> bool:
        try:
            with self._lock:
                self._conn.execute("SELECT 1").fetchone()
            return True
        except sqlite3.Error as exc:
            raise SessionRepositoryError(f"SQLite health check failed: {exc}") from exc

    def close(self) -> None:
        self._conn.close()