from __future__ import annotations

API_PREFIX = "/api/v1"


def test_create_session_route(test_client):
    response = test_client.post(f"{API_PREFIX}/sessions")

    assert response.status_code == 201

    data = response.json()
    assert "session_id" in data
    assert isinstance(data["session_id"], str)
    assert data["session_id"]


def test_get_session_history_route_returns_empty_history_initially(test_client):
    create_response = test_client.post(f"{API_PREFIX}/sessions")
    assert create_response.status_code == 201
    session_id = create_response.json()["session_id"]

    response = test_client.get(f"{API_PREFIX}/sessions/{session_id}")
    assert response.status_code == 200

    data = response.json()
    assert data["session_id"] == session_id

    history = (
        data.get("history")
        or data.get("events")
        or data.get("messages")
        or data.get("items")
        or []
    )
    assert history == []


def test_chat_route_returns_interrupted_payload_for_quiz_flow(test_client):
    class FakeSessionService:
        def ask(self, session_id: str, question: str):
            return {
                "status": "interrupted",
                "interrupted": True,
                "next_action": "quiz_approval",
                "session_id": session_id,
                "question": question,
                "summary": "Diabetes is a chronic condition that affects blood sugar.",
            }

    from healthbot.api.app import app
    from healthbot.api.dependencies import get_session_service

    app.dependency_overrides[get_session_service] = lambda: FakeSessionService()

    try:
        response = test_client.post(
            f"{API_PREFIX}/chat",
            json={
                "session_id": "session-123",
                "question": "What is diabetes?",
            },
        )

        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "interrupted"
        assert data["interrupted"] is True
        assert data["next_action"] == "quiz_approval"
        assert data["session_id"] == "session-123"
        assert "blood sugar" in data["summary"]
    finally:
        app.dependency_overrides.clear()


def test_submit_quiz_approval_route(test_client):
    class FakeSessionService:
        def approve_quiz(self, session_id: str, approved: bool):
            if approved:
                return {
                    "status": "interrupted",
                    "interrupted": True,
                    "next_action": "quiz_answer",
                    "session_id": session_id,
                    "quiz_question": (
                        "What hormone is most directly involved in lowering blood sugar?\n\n"
                        "A) Cortisol\n"
                        "B) Insulin\n"
                        "C) Adrenaline\n"
                        "D) Thyroxine"
                    ),
                }

            return {
                "status": "completed",
                "interrupted": False,
                "session_id": session_id,
                "answer": "Okay, no quiz this time.",
            }

    from healthbot.api.app import app
    from healthbot.api.dependencies import get_session_service

    app.dependency_overrides[get_session_service] = lambda: FakeSessionService()

    try:
        response = test_client.post(
            f"{API_PREFIX}/quiz/approval",
            json={"session_id": "session-123", "approved": True},
        )

        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "interrupted"
        assert data["interrupted"] is True
        assert data["next_action"] == "quiz_answer"
        assert data["session_id"] == "session-123"
        assert "Insulin" in data["quiz_question"]
    finally:
        app.dependency_overrides.clear()


def test_submit_quiz_answer_route(test_client):
    class FakeSessionService:
        def submit_quiz_answer(self, session_id: str, answer: str):
            return {
                "status": "completed",
                "interrupted": False,
                "session_id": session_id,
                "answer": f"Received answer {answer}. Correct!",
            }

    from healthbot.api.app import app
    from healthbot.api.dependencies import get_session_service

    app.dependency_overrides[get_session_service] = lambda: FakeSessionService()

    try:
        response = test_client.post(
            f"{API_PREFIX}/quiz/answer",
            json={"session_id": "session-123", "answer": "B"},
        )

        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "completed"
        assert data["interrupted"] is False
        assert data["session_id"] == "session-123"
        assert "Correct!" in data["answer"]
    finally:
        app.dependency_overrides.clear()


def test_health_route(test_client):
    response = test_client.get(f"{API_PREFIX}/health")

    assert response.status_code == 200

    data = response.json()
    assert "status" in data


def test_ready_route_reports_backend_error_when_health_check_fails(test_client):
    class FakeSessionService:
        def health_check(self):
            raise RuntimeError("backend unavailable")

    from healthbot.api.app import app
    from healthbot.api.dependencies import get_session_service

    app.dependency_overrides[get_session_service] = lambda: FakeSessionService()

    try:
        response = test_client.get(f"{API_PREFIX}/ready")

        assert response.status_code == 503

        data = response.json()
        assert data["status"] == "not_ready"
    finally:
        app.dependency_overrides.clear()


def test_get_session_history_route_uses_service_history(test_client):
    class FakeSessionService:
        def get_history(self, session_id: str):
            return [
                {"type": "ask", "question": "What is asthma?"},
                {"type": "quiz_approval", "approved": True},
            ]

    from healthbot.api.app import app
    from healthbot.api.dependencies import get_session_service

    app.dependency_overrides[get_session_service] = lambda: FakeSessionService()

    try:
        response = test_client.get(f"{API_PREFIX}/sessions/session-xyz")
        assert response.status_code == 200

        data = response.json()
        assert data["session_id"] == "session-xyz"

        history = (
                data.get("history")
                or data.get("events")
                or data.get("messages")
                or data.get("items")
        )
        assert history is not None
        assert len(history) == 2
        assert history[0]["type"] == "ask"
        assert history[1]["type"] == "quiz_approval"
    finally:
        app.dependency_overrides.clear()