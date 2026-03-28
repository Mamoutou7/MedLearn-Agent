"""Session-aware orchestration for the FastAPI layer."""

from __future__ import annotations

import uuid
from typing import Any

from langgraph.types import Command

from healthbot.core.logging import get_logger
from healthbot.core.settings import Settings, get_settings
from healthbot.observability.metrics import metrics
from healthbot.observability.tracing import trace_span
from healthbot.core.exceptions import (
    SessionBackendUnavailableError,
    WorkflowError,
)
from healthbot.repositories.session_repository import (
    InMemorySessionRepository,
    SessionNotFoundError,
    SessionRepository,
    SessionRepositoryError,
)
from healthbot.utils.get_interrupt_value import get_interrupt_value
from healthbot.workflow.workflow_builder import WorkflowBuilder

logger = get_logger(__name__)


class SessionService:
    """Manage agent sessions and LangGraph resumable interactions."""

    def __init__(
        self,
        session_repository: SessionRepository | None = None,
        settings: Settings | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self._session_repository = session_repository or InMemorySessionRepository()
        self._workflow_builder = WorkflowBuilder(settings=self.settings)
        self._graph = self._workflow_builder.build()

    def create_session(self) -> str:
        """Create and store a new conversation session identifier."""
        session_id = str(uuid.uuid4())

        try:
            self._session_repository.create_session(session_id)
        except SessionRepositoryError as exc:
            logger.exception("Failed to create session in configured backend")
            raise SessionBackendUnavailableError(
                "Session storage backend is unavailable.",
                context={"backend": self.settings.session_backend},
            ) from exc

        metrics.increment("session.created")
        logger.info("Created session %s", session_id)
        return session_id

    def list_sessions(self) -> list[str]:
        """Return all active session identifiers."""
        try:
            return self._session_repository.list_sessions()
        except SessionRepositoryError as exc:
            logger.exception("Failed to list sessions from configured backend")
            raise SessionBackendUnavailableError(
                "Session storage backend is unavailable.",
                context={"backend": self.settings.session_backend},
            ) from exc

    def ensure_session(self, session_id: str) -> None:
        """Validate that the session exists."""
        try:
            exists = self._session_repository.exists(session_id)
        except SessionRepositoryError as exc:
            logger.exception("Failed to check session existence")
            raise SessionBackendUnavailableError(
                "Session storage backend is unavailable.",
                context={"backend": self.settings.session_backend, "session_id": session_id},
            ) from exc

        if not exists:
            raise WorkflowError(f"Unknown session_id: {session_id}")

    def ask(self, session_id: str, question: str) -> dict:
        """Start a conversation turn for a given session."""
        self.ensure_session(session_id)
        with trace_span("session.ask", session_id=session_id):
            result = self._graph.invoke(
                {"question": question},
                config={"configurable": {"thread_id": session_id}},
            )
            payload = self._normalize_result(result)
            payload["session_id"] = session_id
            self._append_history(
                session_id,
                {"type": "ask", "question": question, "result": payload},
            )
            metrics.increment("session.ask.calls")
            return payload

    def approve_quiz(self, session_id: str, approved: bool) -> dict:
        """Resume the workflow after the quiz approval interrupt."""
        self.ensure_session(session_id)
        resume_value = "approve" if approved else "reject"
        with trace_span(
            "session.quiz_approval", session_id=session_id, approved=approved
        ):
            result = self._graph.invoke(
                Command(resume=resume_value),
                config={"configurable": {"thread_id": session_id}},
            )
            payload = self._normalize_result(result)
            payload["session_id"] = session_id
            self._append_history(
                session_id,
                {"type": "quiz_approval", "approved": approved, "result": payload},
            )
            metrics.increment("session.quiz_approval.calls")
            return payload

    def submit_quiz_answer(self, session_id: str, answer: str) -> dict:
        """Resume the workflow after the quiz answer interrupt."""
        self.ensure_session(session_id)
        with trace_span("session.quiz_answer", session_id=session_id):
            result = self._graph.invoke(
                Command(resume=answer),
                config={"configurable": {"thread_id": session_id}},
            )
            payload = self._normalize_result(result)
            payload["session_id"] = session_id
            self._append_history(
                session_id,
                {"type": "quiz_answer", "answer": answer, "result": payload},
            )
            metrics.increment("session.quiz_answer.calls")
            return payload

    def get_history(self, session_id: str) -> list[dict]:
        self.ensure_session(session_id)
        try:
            return self._session_repository.get_history(session_id)
        except SessionNotFoundError as exc:
            raise WorkflowError(
                f"Unknown session_id: {session_id}",
                context={"session_id": session_id},
            ) from exc
        except SessionRepositoryError as exc:
            logger.exception("Failed to fetch session history")
            raise SessionBackendUnavailableError(
                "Session storage backend is unavailable.",
                context={"backend": self.settings.session_backend, "session_id": session_id},
            ) from exc

    def close(self) -> None:
        """Release repository and workflow resources."""
        self._session_repository.close()
        self._workflow_builder.close()

    def _append_history(self, session_id: str, entry: dict) -> None:
        try:
            self._session_repository.append_event(session_id, entry)
        except SessionNotFoundError as exc:
            raise WorkflowError(
                f"Unknown session_id: {session_id}",
                context={"session_id": session_id},
            ) from exc
        except SessionRepositoryError as exc:
            logger.exception("Failed to append session history")
            raise SessionBackendUnavailableError(
                "Session storage backend is unavailable.",
                context={"backend": self.settings.session_backend, "session_id": session_id},
            ) from exc

    def _extract_last_message_content(self, result: dict) -> str | None:
        """
        Extract the last non-empty message content from a LangGraph result.
        """
        messages = result.get("messages", [])

        for message in reversed(messages):
            content = getattr(message, "content", None)
            if isinstance(content, str) and content.strip():
                return content.strip()

        return None

    def _normalize_result(self, result: dict) -> dict:
        """
        Normalize LangGraph output into an API-friendly payload.

        Rules:
        - If the workflow is interrupted, `answer` must stay None because there
          is no final answer yet.
        - Intermediate content should be exposed in `summary` or `quiz_question`.
        - If the workflow is completed, return the most useful final content,
          not the generic closing message.
        """
        if "__interrupt__" in result:
            interrupt_data = result["__interrupt__"]

            quiz_question = get_interrupt_value(interrupt_data, "quiz_question", None)
            full_summary = get_interrupt_value(interrupt_data, "full_summary", None)
            prompt_question = get_interrupt_value(interrupt_data, "question", None)

            next_action = "quiz_answer" if quiz_question else "quiz_approval"

            summary = (
                full_summary
                or prompt_question
                or self._extract_last_message_content(result)
            )

            return {
                "status": "interrupted",
                "answer": None,
                "interrupted": True,
                "next_action": next_action,
                "summary": summary,
                "quiz_question": quiz_question,
            }

        answer = self._extract_final_useful_message(result) or ""

        return {
            "status": "completed",
            "answer": answer,
            "interrupted": False,
            "next_action": None,
            "summary": None,
            "quiz_question": None,
        }

    def _extract_final_useful_message(self, result: dict) -> str | None:
        """
        Extract the most useful final message for API consumers.

        If the workflow ends with a generic closing message like
        'Thanks for using HealthBot!', return the previous meaningful
        assistant message instead.
        """
        messages = result.get("messages", [])
        generic_endings = {
            "Thanks for using HealthBot!",
            "Thanks for using HealthBot! ",
        }

        contents = []
        for message in messages:
            content = getattr(message, "content", None)
            if isinstance(content, str) and content.strip():
                contents.append(content.strip())

        if not contents:
            return None

        if contents[-1] in generic_endings and len(contents) >= 2:
            return contents[-2]

        return contents[-1]



    def ping(self) -> bool:
        repository = self._session_repository
        ping_method = getattr(repository, "ping", None)
        if callable(ping_method):
            return bool(ping_method())
        return True