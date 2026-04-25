import time
import uuid
from collections.abc import Generator
from contextlib import contextmanager
from contextvars import ContextVar

from healthbot.core.logging import get_logger
from healthbot.observability.metrics import metrics

logger = get_logger(__name__)
request_id_var: ContextVar[str | None] = ContextVar("request_id", default=None)
span_id_var: ContextVar[str | None] = ContextVar("span_id", default=None)


def set_request_id(request_id: str | None) -> None:
    request_id_var.set(request_id)


def get_request_id() -> str | None:
    return request_id_var.get()


@contextmanager
def trace_span(name: str, **metadata) -> Generator[None]:
    start = time.perf_counter()
    request_id = get_request_id()
    span_id = uuid.uuid4().hex[:12]
    token = span_id_var.set(span_id)

    logger.info(
        "%s started | request_id=%s | span_id=%s | metadata=%s",
        name,
        request_id,
        span_id,
        metadata,
    )

    try:
        yield
    finally:
        duration_ms = (time.perf_counter() - start) * 1000
        metrics.increment(f"span.{name}.count")
        metrics.observe(f"span.{name}.duration_ms", duration_ms)
        logger.info(
            "%s finished | request_id=%s | span_id=%s | duration_ms=%.2f",
            name,
            request_id,
            span_id,
            duration_ms,
        )
        span_id_var.reset(token)
