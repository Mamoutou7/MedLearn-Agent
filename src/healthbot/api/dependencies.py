"""FastAPI dependency providers."""

from functools import lru_cache

from src.healthbot.services.session_service import SessionService


@lru_cache(maxsize=1)
def get_session_service() -> SessionService:
    """Return a singleton session service for the API process."""
    return SessionService()
