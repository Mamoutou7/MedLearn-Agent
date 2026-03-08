from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.healthbot.api.middleware.error_handler import register_exception_handlers
from src.healthbot.api.middleware.request_logging import RequestLoggingMiddleware
from src.healthbot.api.routes import chat, health, quiz
from src.healthbot.core.logging import configure_logging
from src.healthbot.core.settings import settings

configure_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application startup and shutdown events.

    This is the right place to initialize shared resources such as:
    - DB clients
    - Redis connections
    - external telemetry
    - cached workflow instances
    """
    yield


app = FastAPI(
    title="MedLearn Agent API",
    version="1.0.0",
    description="AI health learning agent powered by LangGraph and FastAPI.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(RequestLoggingMiddleware)

register_exception_handlers(app)

app.include_router(health.router, prefix="/api/v1")
app.include_router(chat.router, prefix="/api/v1")
app.include_router(quiz.router, prefix="/api/v1")
