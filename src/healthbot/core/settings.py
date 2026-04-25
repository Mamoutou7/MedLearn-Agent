"""
Application configuration module.

Centralizes environment loading for CLI, API and infrastructure.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from dotenv import load_dotenv
from pydantic import Field, field_validator
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
    openai_base_url: str | None = Field(default=None, alias="OPENAI_BASE_URL")
    model_name: str = Field(default="gpt-4o-mini", alias="MODEL_NAME")
    judge_model_name: str = Field(default="gpt-4o-mini", alias="JUDGE_MODEL_NAME")

    app_name: str = Field(default="MedLearn Agent", alias="APP_NAME")
    app_env: Literal["development", "staging", "production", "test"] = Field(
        default="development",
        alias="APP_ENV",
    )
    debug: bool = Field(default=False, alias="DEBUG")
    api_host: str = Field(default="0.0.0.0", alias="API_HOST")
    api_port: int = Field(default=8000, alias="API_PORT")
    api_key: str | None = Field(default="your_api_key", alias="API_KEY")

    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO",
        alias="LOG_LEVEL",
    )
    log_file: str = Field(default="logs/healthbot.log", alias="LOG_FILE")

    enable_metrics: bool = Field(default=True, alias="ENABLE_METRICS")
    enable_tracing: bool = Field(default=True, alias="ENABLE_TRACING")
    default_thread_prefix: str = Field(default="session", alias="DEFAULT_THREAD_PREFIX")
    allowed_origins_raw: str = Field(default="*", alias="ALLOWED_ORIGINS")

    session_backend: Literal["memory", "redis", "sqlite"] = Field(
        default="redis",
        alias="SESSION_BACKEND",
    )
    session_backend_fallback_enabled: bool = Field(
        default=True,
        alias="SESSION_BACKEND_FALLBACK_ENABLED",
    )
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")
    redis_key_prefix: str = Field(default="medlearn", alias="REDIS_KEY_PREFIX")
    session_ttl_seconds: int = Field(default=86400, alias="SESSION_TTL_SECONDS")
    session_sqlite_path: str = Field(default=".data/sessions.db", alias="SESSION_SQLITE_PATH")

    checkpoint_backend: Literal["memory", "redis", "sqlite"] = Field(
        default="sqlite",
        alias="CHECKPOINT_BACKEND",
    )
    checkpoint_sqlite_path: str = Field(
        default=".data/langgraph_checkpoints.db",
        alias="CHECKPOINT_SQLITE_PATH",
    )
    checkpoint_postgres_url: str | None = Field(
        default=None,
        alias="CHECKPOINT_POSTGRES_URL",
    )

    observability_backend: Literal["local", "prometheus_text"] = Field(
        default="prometheus_text",
        alias="OBSERVABILITY_BACKEND",
    )

    trusted_health_domains_raw: str = Field(
        default=(
            "cdc.gov,who.int,nih.gov,medlineplus.gov,nhs.uk,mayoclinic.org,"
            "clevelandclinic.org,nice.org.uk,msdmanuals.com"
        ),
        alias="TRUSTED_HEALTH_DOMAINS",
    )
    source_result_limit: int = Field(default=5, alias="SOURCE_RESULT_LIMIT")

    # OpenTelemetry
    otel_enabled: bool = Field(default=False, alias="OTEL_ENABLED")
    otel_service_name: str = Field(default="otel", alias="OTEL_SERVICE_NAME")
    otel_exporter_otlp_endpoint: str | None = Field(
        default=None,
        alias="OTEL_EXPORTER_OTLP_ENDPOINT",
    )
    otel_exporter_otlp_headers: str | None = Field(
        default=None,
        alias="OTEL_EXPORTER_OTLP_HEADERS",
    )
    otel_environment: str = Field(default="development", alias="OTEL_ENVIRONMENT")

    @field_validator("redis_key_prefix")
    @classmethod
    def validate_redis_key_prefix(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("REDIS_KEY_PREFIX cannot be empty")
        return value

    @field_validator("session_ttl_seconds")
    @classmethod
    def validate_session_ttl_seconds(cls, value: int) -> int:
        if value < 0:
            raise ValueError("SESSION_TTL_SECONDS must be >= 0")
        return value

    @field_validator("source_result_limit")
    @classmethod
    def validate_source_result_limit(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("SOURCE_RESULT_LIMIT must be > 0")
        return value

    @field_validator("openai_base_url")
    @classmethod
    def normalize_openai_base_url(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        return value.rstrip("/") if value else None

    @property
    def allowed_origins(self) -> list[str]:
        """Return allowed CORS origins as a parsed list."""
        raw = self.allowed_origins_raw.strip()
        if raw == "*":
            return ["*"]
        return [item.strip() for item in raw.split(",") if item.strip()]

    @property
    def trusted_health_domains(self) -> list[str]:
        """Return trusted health domains as a normalized list."""
        return [
            item.strip().lower()
            for item in self.trusted_health_domains_raw.split(",")
            if item.strip()
        ]

    @property
    def is_production(self) -> bool:
        """Whether the app runs in production mode."""
        return self.app_env == "production"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached settings instance."""
    return Settings()


settings = get_settings()
