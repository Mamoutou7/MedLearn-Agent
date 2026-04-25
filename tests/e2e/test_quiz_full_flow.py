from __future__ import annotations

from dataclasses import dataclass

from langchain_core.messages import AIMessage
from langgraph.types import Command

from healthbot.core.settings import Settings
from healthbot.repositories.session_repository import InMemorySessionRepository
from healthbot.services.session_service import SessionService


@dataclass
class FakeInterrupt:
    value: dict


class FakeGraph:
    def invoke(self, payload, config=None, *args, **kwargs):
        if isinstance(payload, dict):
            return {
                "__interrupt__": [
                    FakeInterrupt(
                        value={
                            "question": "Would you like a short quiz?",
                            "full_summary": "Diabetes is a chronic condition "
                            "that affects blood sugar.",
                        }
                    )
                ],
                "messages": [
                    AIMessage(content="Diabetes is a chronic condition that affects blood sugar.")
                ],
            }

        if isinstance(payload, Command) and payload.resume == "approve":
            return {
                "__interrupt__": [
                    FakeInterrupt(
                        value={
                            "quiz_question": (
                                "What hormone is most directly involved "
                                "in lowering blood sugar?\n\n"
                                "A) Cortisol\n"
                                "B) Insulin\n"
                                "C) Adrenaline\n"
                                "D) Thyroxine"
                            )
                        }
                    )
                ],
                "messages": [
                    AIMessage(
                        content=(
                            "What hormone is most directly involved in lowering blood sugar?\n\n"
                            "A) Cortisol\n"
                            "B) Insulin\n"
                            "C) Adrenaline\n"
                            "D) Thyroxine"
                        )
                    )
                ],
            }

        if isinstance(payload, Command) and payload.resume == "B":
            return {
                "messages": [
                    AIMessage(content=("🎉 Correct!\nYour answer B is correct.\nScore: 100%")),
                    AIMessage(content="Thanks for using HealthBot!"),
                ]
            }

        if isinstance(payload, Command) and payload.resume == "reject":
            return {
                "messages": [
                    AIMessage(content="Okay, no quiz this time."),
                    AIMessage(content="Thanks for using HealthBot!"),
                ]
            }

        raise AssertionError(f"Unexpected payload: {payload!r}")


class FakeWorkflowBuilder:
    def __init__(self, settings=None):
        self.settings = settings

    def build(self):
        return FakeGraph()

    def close(self):
        return None


def build_test_settings() -> Settings:
    return Settings(
        OPENAI_API_KEY="test-openai-key",
        TAVILY_API_KEY="test-tavily-key",
        APP_ENV="test",
        SESSION_BACKEND="memory",
        CHECKPOINT_BACKEND="memory",
        ENABLE_METRICS=False,
        ENABLE_TRACING=False,
    )


def test_session_service_full_quiz_flow(monkeypatch):
    monkeypatch.setattr(
        "healthbot.services.session_service.WorkflowBuilder",
        FakeWorkflowBuilder,
    )

    service = SessionService(
        session_repository=InMemorySessionRepository(),
        settings=build_test_settings(),
    )

    session_id = service.create_session()

    ask_result = service.ask(session_id, "What is diabetes?")
    assert ask_result["status"] == "interrupted"
    assert ask_result["interrupted"] is True
    assert ask_result["next_action"] == "quiz_approval"
    assert "blood sugar" in (ask_result["summary"] or "")

    approval_result = service.approve_quiz(session_id, approved=True)
    assert approval_result["status"] == "interrupted"
    assert approval_result["interrupted"] is True
    assert approval_result["next_action"] == "quiz_answer"
    assert "Insulin" in (approval_result["quiz_question"] or "")

    answer_result = service.submit_quiz_answer(session_id, "B")
    assert answer_result["status"] == "completed"
    assert answer_result["interrupted"] is False
    assert answer_result["answer"] is not None
    assert "Correct!" in answer_result["answer"]

    history = service.get_history(session_id)
    assert len(history) == 3
    assert history[0]["type"] == "ask"
    assert history[1]["type"] == "quiz_approval"
    assert history[2]["type"] == "quiz_answer"


def test_session_service_quiz_rejection_flow(monkeypatch):
    monkeypatch.setattr(
        "healthbot.services.session_service.WorkflowBuilder",
        FakeWorkflowBuilder,
    )

    service = SessionService(
        session_repository=InMemorySessionRepository(),
        settings=build_test_settings(),
    )

    session_id = service.create_session()

    ask_result = service.ask(session_id, "What is hypertension?")
    assert ask_result["next_action"] == "quiz_approval"

    rejection_result = service.approve_quiz(session_id, approved=False)
    assert rejection_result["status"] == "completed"
    assert rejection_result["interrupted"] is False
    assert rejection_result["answer"] == "Okay, no quiz this time."
