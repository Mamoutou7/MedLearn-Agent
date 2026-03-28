from __future__ import annotations

from fastapi import APIRouter, Depends, Response
from fastapi.responses import JSONResponse

from healthbot.api.dependencies import get_session_service
from healthbot.api.security import require_api_key
from healthbot.observability.metrics import metrics
from healthbot.services.session_service import SessionService

router = APIRouter(tags=["health"])


@router.get("/health")
async def healthcheck():
    return {"status": "ok"}


@router.get("/ready")
async def readiness(session_service: SessionService = Depends(get_session_service)):
    checks = {"session_backend": "ok", "checkpointer": "ok"}

    try:
        session_service.ping()
    except Exception:
        checks["session_backend"] = "error"
        return JSONResponse(
            status_code=503,
            content={"status": "not_ready", "checks": checks},
        )

    return {"status": "ready", "checks": checks}


@router.get("/metrics", dependencies=[Depends(require_api_key)])
async def get_metrics():
    return metrics.snapshot()


@router.get("/metrics/prometheus", dependencies=[Depends(require_api_key)])
async def get_prometheus_metrics():
    return Response(
        content=metrics.render_prometheus(),
        media_type="text/plain; version=0.0.4",
    )