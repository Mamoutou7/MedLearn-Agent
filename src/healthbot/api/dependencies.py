"""FastAPI dependency providers."""

from __future__ import annotations

from functools import lru_cache

from src.healthbot.core.logging import get_logger
from src.healthbot.core.settings import settings
from src.healthbot.repositories.redis_session_repository import RedisSessionRepository
from src.healthbot.repositories.session_repository import (
    InMemorySessionRepository,
    SessionRepository,
    SessionRepositoryError,
)
from src.healthbot.services.session_service import SessionService

logger = get_logger(__name__)


@lru_cache(maxsize=1)
def get_session_repository() -> SessionRepository:
    backend = settings.session_backend.lower().strip()

    if backend == "memory":
        logger.info("Using in-memory session repository")
        return InMemorySessionRepository()

    if backend == "redis":
        try:
            repository = RedisSessionRepository(
                redis_url=settings.redis_url,
                ttl_seconds=settings.session_ttl_seconds,
                key_prefix=settings.redis_key_prefix,
            )
            repository.ping()
            logger.info("Using Redis session repository | redis_url=%s", settings.redis_url)
            return repository
        except SessionRepositoryError:
            if settings.session_backend_fallback_enabled:
                logger.warning(
                    "Redis unavailable, falling back to in-memory session repository | redis_url=%s",
                    settings.redis_url,
                    exc_info=True,
                )
                return InMemorySessionRepository()
            raise

    raise ValueError(f"Unsupported session backend: {settings.session_backend}")


@lru_cache(maxsize=1)
def get_session_service() -> SessionService:
    return SessionService(session_repository=get_session_repository(), settings=settings)