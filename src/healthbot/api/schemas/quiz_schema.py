from pydantic import BaseModel, Field


class QuizApprovalRequest(BaseModel):
    """Payload used to approve or reject quiz generation."""

    session_id: str = Field(..., description="Active session identifier")
    approved: bool = Field(..., description="Whether the user wants to take the quiz")


class QuizAnswerRequest(BaseModel):
    """Payload used to submit a quiz answer."""

    session_id: str = Field(..., description="Active session identifier")
    answer: str = Field(..., min_length=1, max_length=1, description="Quiz answer: A, B, C, or D")


class QuizWorkflowResponse(BaseModel):
    """
    Response returned after quiz approval or answer submission.

    `answer` is nullable because interrupted workflows do not yet have
    a final answer.
    """

    session_id: str
    status: str
    answer: str | None = None
    interrupted: bool
    next_action: str | None = None
    summary: str | None = None
    quiz_question: str | None = None
