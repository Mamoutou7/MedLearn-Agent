from __future__ import annotations

from typing import Any

from langgraph.graph.message import MessagesState


class WorkflowState(MessagesState):
    """
    State object passed between LangGraph workflow nodes.

    This state contains all data required for the health education workflow:
    - user question
    - health-topic validation
    - retrieved grounding sources
    - quiz flow state
    - final grading state
    """

    # Core conversation state
    question: str
    health_topic: bool = True
    answer: str = ""

    # Grounding / retrieval state
    sources: list[dict[str, Any]] = []
    source_query: str = ""
    grounding_used: bool = False

    # Quiz state
    quiz_question: str = ""
    quiz_options: dict[str, str] = {}
    quiz_correct_answer: str = ""
    user_quiz_answer: str = ""
    quiz_approved: bool = False
    quiz_generated: bool = False
    quiz_graded: bool = False

    # Quiz grading state
    is_correct: bool = False
    score: int = 0

    # Safety state
    safety_short_circuit: bool = False
    safety_category: str = ""
    safety_severity: str = ""