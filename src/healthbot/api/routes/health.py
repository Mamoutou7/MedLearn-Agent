from __future__ import annotations

from fastapi import APIRouter, Response

from src.healthbot.core.settings import settings
from src.healthbot.observability.metrics import metrics

router = APIRouter(tags=["health"])


@router.get("/health")
async def healthcheck():
    """Liveness probe used by load balancers and orchestrators."""
    return {"status": "ok"}


@router.get("/ready")
async def readiness():
    """Readiness probe to signal whether the application is ready to serve traffic."""
    return {
        "status": "ready",
        "session_backend": settings.session_backend,
        "checkpoint_backend": settings.checkpoint_backend,
        "observability_backend": settings.observability_backend,
    }


@router.get("/metrics")
async def get_metrics():
    """Return a lightweight in-process metrics snapshot."""
    return metrics.snapshot()


@router.get("/metrics/prometheus")
async def get_prometheus_metrics():
    """Return metrics in Prometheus text exposition format."""
    return Response(
        content=metrics.render_prometheus(),
        media_type="text/plain; version=0.0.4",
    )