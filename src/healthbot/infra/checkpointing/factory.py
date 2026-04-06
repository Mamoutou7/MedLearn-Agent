"""Factory for LangGraph checkpoint backends."""

from __future__ import annotations

import os
from contextlib import AbstractContextManager
from typing import Any

from healthbot.core.logging import get_logger
from healthbot.core.settings import Settings

logger = get_logger(__name__)


class CheckpointerFactoryError(RuntimeError):
    """Raised when the configured checkpoint backend cannot be created."""


class CheckpointerHandle(AbstractContextManager):
    """Wrap a checkpointer and keep the owning context alive."""

    def __init__(self, resource: Any, owner: AbstractContextManager[Any] | None = None):
        self.resource = resource
        self._owner = owner

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False

    def close(self) -> None:
        if self._owner is not None:
            self._owner.__exit__(None, None, None)
            self._owner = None


def build_checkpointer(settings: Settings) -> CheckpointerHandle:
    """Create the configured LangGraph checkpoint saver."""
    backend = settings.checkpoint_backend.lower().strip()

    if backend == "memory":
        from langgraph.checkpoint.memory import MemorySaver

        logger.warning("Using in-memory LangGraph checkpointer; state is not persistent")
        return CheckpointerHandle(MemorySaver())

    if backend == "sqlite":
        try:
            from langgraph.checkpoint.sqlite import SqliteSaver
        except ImportError as exc:
            raise CheckpointerFactoryError(
                "SQLite checkpoint backend requires `langgraph-checkpoint-sqlite`."
            ) from exc

        db_path = settings.checkpoint_sqlite_path
        db_dir = os.path.dirname(db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)

        owner = SqliteSaver.from_conn_string(db_path)
        resource = owner.__enter__()
        return CheckpointerHandle(resource=resource, owner=owner)

    if backend == "postgres":
        if not settings.checkpoint_postgres_url:
            raise CheckpointerFactoryError(
                "CHECKPOINT_POSTGRES_URL must be configured for postgres checkpoints."
            )

        try:
            from langgraph.checkpoint.postgres import PostgresSaver
        except ImportError as exc:
            raise CheckpointerFactoryError(
                "Postgres checkpoint backend requires `langgraph-checkpoint-postgres`."
            ) from exc

        owner = PostgresSaver.from_conn_string(settings.checkpoint_postgres_url)
        resource = owner.__enter__()
        resource.setup()
        return CheckpointerHandle(resource=resource, owner=owner)

    raise CheckpointerFactoryError(f"Unsupported checkpoint backend: {backend}")