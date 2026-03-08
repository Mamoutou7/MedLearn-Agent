from __future__ import annotations

from fastapi import APIRouter, Depends, status

from src.healthbot.api.dependencies import get_session_service
from src.healthbot.api.schemas.chat_schema import (
    ChatRequest,
    ChatResponse,
    SessionCreateResponse,
    SessionHistoryResponse,
)
from src.healthbot.services.session_service import SessionService

router = APIRouter(tags=["chat"])


@router.post(
    "/sessions",
    response_model=SessionCreateResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_session(
    session_service: SessionService = Depends(get_session_service),
):
    """Create a new chat session and return its identifier."""
    return SessionCreateResponse(session_id=session_service.create_session())


@router.get("/sessions/{session_id}", response_model=SessionHistoryResponse)
async def get_session_history(
    session_id: str,
    session_service: SessionService = Depends(get_session_service),
):
    """Return the API-visible interaction history for one session."""
    return SessionHistoryResponse(
        session_id=session_id, events=session_service.get_history(session_id)
    )


@router.post("/chat", response_model=ChatResponse)
async def chat(
    payload: ChatRequest,
    session_service: SessionService = Depends(get_session_service),
):
    """Send a user question to the HealthBot workflow."""
    result = session_service.ask(payload.session_id, payload.question)
    return ChatResponse(**result)
