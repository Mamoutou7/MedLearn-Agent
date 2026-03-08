from pydantic import BaseModel, Field


class SessionCreateResponse(BaseModel):
    session_id: str


class ChatRequest(BaseModel):
    session_id: str = Field(..., description="Active session identifier")
    question: str = Field(..., min_length=1, description="User health-related question")


class ChatResponse(BaseModel):
    session_id: str
    status: str
    answer: str | None = None
    interrupted: bool
    next_action: str | None = None
    summary: str | None = None
    quiz_question: str | None = None


class SessionHistoryResponse(BaseModel):
    session_id: str
    events: list[dict]
