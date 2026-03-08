from __future__ import annotations

from fastapi import APIRouter

from src.healthbot.observability.metrics import metrics

router = APIRouter(tags=["health"])


@router.get("/health")
async def healthcheck():
    """Liveness probe used by load balancers and orchestrators."""
    return {"status": "ok"}


@router.get("/ready")
async def readiness():
    """Readiness probe to signal whether the application is ready to serve traffic."""
    return {"status": "ready"}


@router.get("/metrics")
async def get_metrics():
    """Return a lightweight in-process metrics snapshot."""
    return metrics.snapshot()
