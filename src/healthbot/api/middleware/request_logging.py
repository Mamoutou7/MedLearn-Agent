"""Request logging middleware for FastAPI."""

from __future__ import annotations

import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware

from healthbot.core.logging import get_logger
from healthbot.observability.metrics import metrics
from healthbot.observability.tracing import set_request_id

logger = get_logger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Attach request ids and log duration for every HTTP call."""

    async def dispatch(self, request, call_next):
        request_id = str(uuid.uuid4())
        set_request_id(request_id)
        start = time.perf_counter()

        try:
            response = await call_next(request)
        except Exception:
            duration_ms = (time.perf_counter() - start) * 1000
            metrics.increment("http.requests.total")
            metrics.increment("http.requests.failed")
            metrics.observe("http.request.duration_ms", duration_ms)
            logger.exception(
                "HTTP request failed | request_id=%s | method=%s | path=%s | duration_ms=%.2f",
                request_id,
                request.method,
                request.url.path,
                duration_ms,
            )
            raise

        duration_ms = (time.perf_counter() - start) * 1000
        response.headers["X-Request-ID"] = request_id
        metrics.increment("http.requests.total")
        metrics.observe("http.request.duration_ms", duration_ms)

        logger.info(
            "HTTP request processed | request_id=%s | "
            "method=%s | path=%s | status_code=%s | duration_ms=%.2f",
            request_id,
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
        )
        return response
