"""Tracing helpers for API requests and internal agent operations."""

from __future__ import annotations

import time
from contextlib import contextmanager
from contextvars import ContextVar
from typing import Generator

from src.healthbot.core.logging import get_logger
from src.healthbot.observability.metrics import metrics

logger = get_logger(__name__)
request_id_var: ContextVar[str | None] = ContextVar("request_id", default=None)


def set_request_id(request_id: str | None) -> None:
    """Attach the current request identifier to the active context."""
    request_id_var.set(request_id)


def get_request_id() -> str | None:
    """Return the active request identifier if any."""
    return request_id_var.get()


@contextmanager
def trace_span(name: str, **metadata) -> Generator[None, None, None]:
    """Trace a logical operation and emit duration metrics and logs."""
    start = time.perf_counter()
    request_id = get_request_id()
    logger.info("%s started | request_id=%s | metadata=%s", name, request_id, metadata)
    try:
        yield
    finally:
        duration_ms = (time.perf_counter() - start) * 1000
        metrics.increment(f"span.{name}.count")
        metrics.observe(f"span.{name}.duration_ms", duration_ms)
        logger.info(
            "%s finished | request_id=%s | duration_ms=%.2f",
            name,
            request_id,
            duration_ms,
        )
