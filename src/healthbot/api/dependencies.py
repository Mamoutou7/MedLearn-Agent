"""FastAPI dependency providers."""

from functools import lru_cache

from src.healthbot.core.settings import settings
from src.healthbot.repositories.session_repository import InMemorySessionRepository, SessionRepository
from src.healthbot.repositories.redis_session_repository import RedisSessionRepository
from src.healthbot.services.session_service import SessionService


@lru_cache(maxsize=1)
def get_session_repository() -> SessionRepository:
    backend = settings.session_backend.lower().strip()

    if backend == "memory":
        return InMemorySessionRepository()

    if backend == "redis":
        return RedisSessionRepository(
            redis_url=settings.redis_url,
            ttl_seconds=settings.session_ttl_seconds,
            key_prefix=settings.redis_key_prefix,
        )

    raise ValueError(f"Unsupported session backend: {settings.session_backend}")


@lru_cache(maxsize=1)
def get_session_service() -> SessionService:
    return SessionService(session_repository=get_session_repository(), settings=settings)