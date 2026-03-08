"""Application-wide exception handlers for FastAPI."""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.healthbot.core.exceptions import HealthBotError
from src.healthbot.core.logging import get_logger
from src.healthbot.observability.metrics import metrics

logger = get_logger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    """Register exception handlers for domain and unexpected errors."""

    @app.exception_handler(HealthBotError)
    async def handle_healthbot_error(request: Request, exc: HealthBotError):
        metrics.increment("http.errors.healthbot")
        logger.error("Handled HealthBotError on %s", request.url.path, exc_info=True)
        return JSONResponse(
            status_code=400,
            content={
                "error": exc.__class__.__name__,
                "detail": str(exc),
                "context": exc.context,
            },
        )

    @app.exception_handler(Exception)
    async def handle_unexpected_error(request: Request, exc: Exception):
        metrics.increment("http.errors.unexpected")
        logger.error("Unhandled exception on %s", request.url.path, exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "error": "InternalServerError",
                "detail": "Unexpected server error",
            },
        )
