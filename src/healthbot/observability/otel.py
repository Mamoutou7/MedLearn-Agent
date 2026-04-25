from __future__ import annotations

from typing import Any

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from healthbot.core.logging import get_logger
from healthbot.core.settings import settings

logger = get_logger(__name__)


def _parser_headers(raw: str | None) -> dict[str, str]:
    if not raw:
        return {}

    headers: dict[str, str] = {}
    for item in raw.split(","):
        item = item.strip()
        if not item:
            continue
        key, value = item.split("=", 1)
        headers[key.strip()] = value.strip()
    return headers


def setup_otel(app: Any) -> None:
    """Initialize OpenTelemetry tracing and instrument the web stack."""
    if not settings.otel_enabled:
        logger.info("OpenTelemetry disabled")
        return

    if not settings.otel_exporter_otlp_endpoint:
        logger.warning("OpenTelemetry enabled but OTLP endpoint is missing;instrumentation skipped")
        return

    resource = Resource.create(
        {
            "service.name": settings.otel_service_name,
            "deployment.environment": settings.otel_environment,
        }
    )

    provider = TracerProvider(resource=resource)

    exporter = OTLPSpanExporter(
        endpoint=settings.otel_exporter_otlp_endpoint,
        headers=_parser_headers(settings.otel_exporter_otlp_headers),
    )

    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)

    FastAPIInstrumentor().instrument_app(app)
    HTTPXClientInstrumentor().instrument()

    logger.info(
        "OpenTelemetry initialized | service=%s | endpoint=%s | environment=%s ",
        settings.otel_service_name,
        settings.otel_exporter_otlp_endpoint,
        settings.otel_environment,
    )
