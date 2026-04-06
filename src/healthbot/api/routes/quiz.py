from __future__ import annotations

from fastapi import APIRouter, Depends

from healthbot.api.dependencies import get_session_service
from healthbot.api.schemas.quiz_schema import (
    QuizAnswerRequest,
    QuizApprovalRequest,
    QuizWorkflowResponse,
)
from healthbot.services.session_service import SessionService

router = APIRouter(prefix="/quiz", tags=["quiz"])


@router.post("/approval", response_model=QuizWorkflowResponse)
async def submit_quiz_approval(
    payload: QuizApprovalRequest,
    session_service: SessionService = Depends(get_session_service),
):
    """Resume the e2e after the user approves or rejects the quiz."""
    result = session_service.approve_quiz(payload.session_id, payload.approved)
    return QuizWorkflowResponse(**result)


@router.post("/answer", response_model=QuizWorkflowResponse)
async def submit_quiz_answer(
    payload: QuizAnswerRequest,
    session_service: SessionService = Depends(get_session_service),
):
    """Resume the e2e after the user submits the quiz answer."""
    result = session_service.submit_quiz_answer(
        payload.session_id, payload.answer.upper()
    )
    return QuizWorkflowResponse(**result)
