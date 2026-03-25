"""
Application configuration module.

Centralizes environment loading for CLI, API and infrastructure.
"""

from __future__ import annotations

from functools import lru_cache
from typing import List

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class Settings(BaseSettings):
    """Typed application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    openai_api_key: str = Field(..., alias="OPENAI_API_KEY")
    tavily_api_key: str = Field(..., alias="TAVILY_API_KEY")
    model_name: str = Field(default="gpt-4o-mini", alias="MODEL_NAME")

    app_name: str = Field(default="MedLearn Agent", alias="APP_NAME")
    app_env: str = Field(default="development", alias="APP_ENV")
    debug: bool = Field(default=False, alias="DEBUG")
    api_host: str = Field(default="0.0.0.0", alias="API_HOST")
    api_port: int = Field(default=8000, alias="API_PORT")
    api_key: str | None = Field(default=None, alias="API_KEY")

    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    log_file: str = Field(default="logs/healthbot.log", alias="LOG_FILE")

    enable_metrics: bool = Field(default=True, alias="ENABLE_METRICS")
    enable_tracing: bool = Field(default=True, alias="ENABLE_TRACING")
    default_thread_prefix: str = Field(default="session", alias="DEFAULT_THREAD_PREFIX")
    allowed_origins_raw: str = Field(default="*", alias="ALLOWED_ORIGINS")

    session_backend: str = Field(default="redis", alias="SESSION_BACKEND")
    session_backend_fallback_enabled: bool = Field(
        default=True,
        alias="SESSION_BACKEND_FALLBACK_ENABLED",
    )
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")
    session_ttl_seconds: int = Field(default=86400, alias="SESSION_TTL_SECONDS")
    redis_key_prefix: str = Field(default="medlearn", alias="REDIS_KEY_PREFIX")

    checkpoint_backend: str = Field(default="sqlite", alias="CHECKPOINT_BACKEND")
    checkpoint_sqlite_path: str = Field(
        default=".data/langgraph_checkpoints.db",
        alias="CHECKPOINT_SQLITE_PATH",
    )
    checkpoint_postgres_url: str | None = Field(
        default=None,
        alias="CHECKPOINT_POSTGRES_URL",
    )

    @property
    def allowed_origins(self) -> List[str]:
        """Return CORS origins as a parsed list."""
        raw = self.allowed_origins_raw.strip()
        if raw == "*":
            return ["*"]
        return [item.strip() for item in raw.split(",") if item.strip()]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached settings instance."""
    return Settings()


settings = get_settings()