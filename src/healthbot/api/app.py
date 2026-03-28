from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from healthbot.api.dependencies import get_session_service
from healthbot.api.middleware.error_handler import register_exception_handlers
from healthbot.api.middleware.request_logging import RequestLoggingMiddleware
from healthbot.api.routes import chat, health, quiz
from healthbot.core.logging import configure_logging
from healthbot.core.settings import settings

configure_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    service = get_session_service()
    try:
        yield
    finally:
        service.close()


app = FastAPI(
    title="MedLearn Agent API",
    version="1.0.0",
    description="AI health learning agent powered by LangGraph and FastAPI.",
    lifespan=lifespan,
)

if settings.is_production and settings.allowed_origins == ["*"]:
    raise ValueError("Wildcard CORS is not allowed in production")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=False if settings.allowed_origins == ["*"] else True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(RequestLoggingMiddleware)

register_exception_handlers(app)

app.include_router(health.router, prefix="/api/v1")
app.include_router(chat.router, prefix="/api/v1")
app.include_router(quiz.router, prefix="/api/v1")