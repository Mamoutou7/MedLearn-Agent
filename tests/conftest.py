# ruff: noqa: E402, I001

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"

for path in (str(PROJECT_ROOT), str(SRC_DIR)):
    if path not in sys.path:
        sys.path.insert(0, path)

DEFAULT_TEST_ENV = {
    "OPENAI_API_KEY": "test-openai-key",
    "TAVILY_API_KEY": "test-tavily-key",
    "OPENAI_BASE_URL": "https://api.openai.com/v1",
    "MODEL_NAME": "gpt-4o-mini",
    "APP_ENV": "test",
    "DEBUG": "false",
    "API_KEY": "test-api-key",
    "ENABLE_METRICS": "false",
    "ENABLE_TRACING": "false",
    "SESSION_BACKEND": "memory",
    "CHECKPOINT_BACKEND": "memory",
    "SESSION_BACKEND_FALLBACK_ENABLED": "true",
    "SOURCE_RESULT_LIMIT": "5",
    "REDIS_URL": "redis://localhost:6379/15",
    "REDIS_KEY_PREFIX": "medlearn-test",
}

for key, value in DEFAULT_TEST_ENV.items():
    os.environ.setdefault(key, value)

from healthbot.api.dependencies import get_session_repository, get_session_service
from healthbot.core.settings import Settings, get_settings
import healthbot.infra.search_provider as search_provider_module
from healthbot.observability.metrics import metrics
from healthbot.repositories.session_repository import InMemorySessionRepository
from healthbot.repositories.sqlite_session_repository import SQLiteSessionRepository


def _safe_cache_clear(obj) -> None:
    cache_clear = getattr(obj, "cache_clear", None)
    if callable(cache_clear):
        cache_clear()


def _reset_settings_cache() -> None:
    _safe_cache_clear(get_settings)


def _reset_dependency_caches() -> None:
    _safe_cache_clear(get_session_repository)
    _safe_cache_clear(get_session_service)


def _reset_search_provider_singleton() -> None:
    if hasattr(search_provider_module, "_search_provider"):
        search_provider_module._search_provider = None


def _reset_metrics_registry() -> None:
    for attr in ("_counters", "_timers", "_gauges"):
        value = getattr(metrics, attr, None)
        if hasattr(value, "clear"):
            value.clear()


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line("markers", "unit: unit tests")
    config.addinivalue_line("markers", "integration: integration tests")
    config.addinivalue_line("markers", "regression: regression tests")
    config.addinivalue_line("markers", "e2e: end-to-end tests")
    config.addinivalue_line("markers", "slow: slow tests")


@pytest.fixture(scope="session")
def test_env() -> dict[str, str]:
    return dict(DEFAULT_TEST_ENV)


@pytest.fixture
def test_settings(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Settings:
    sqlite_sessions = tmp_path / "sessions.db"
    sqlite_checkpoints = tmp_path / "checkpoints.db"

    overrides = {
        "OPENAI_API_KEY": "test-openai-key",
        "TAVILY_API_KEY": "test-tavily-key",
        "OPENAI_BASE_URL": "https://api.openai.com/v1",
        "MODEL_NAME": "gpt-4o-mini",
        "APP_ENV": "test",
        "DEBUG": "false",
        "API_KEY": "test-api-key",
        "ENABLE_METRICS": "false",
        "ENABLE_TRACING": "false",
        "SESSION_BACKEND": "memory",
        "CHECKPOINT_BACKEND": "memory",
        "SESSION_BACKEND_FALLBACK_ENABLED": "true",
        "SESSION_SQLITE_PATH": str(sqlite_sessions),
        "CHECKPOINT_SQLITE_PATH": str(sqlite_checkpoints),
        "SOURCE_RESULT_LIMIT": "5",
        "REDIS_URL": "redis://localhost:6379/15",
        "REDIS_KEY_PREFIX": "medlearn-test",
    }

    for key, value in overrides.items():
        monkeypatch.setenv(key, value)

    _reset_settings_cache()
    _reset_dependency_caches()
    _reset_search_provider_singleton()

    return Settings()


@pytest.fixture(autouse=True)
def isolate_global_state():
    _reset_settings_cache()
    _reset_dependency_caches()
    _reset_search_provider_singleton()
    _reset_metrics_registry()

    yield

    _reset_settings_cache()
    _reset_dependency_caches()
    _reset_search_provider_singleton()
    _reset_metrics_registry()


@pytest.fixture
def in_memory_session_repo() -> InMemorySessionRepository:
    repo = InMemorySessionRepository()
    yield repo
    close = getattr(repo, "close", None)
    if callable(close):
        close()


@pytest.fixture
def sqlite_session_repo(tmp_path: Path) -> SQLiteSessionRepository:
    db_path = tmp_path / "test_sessions.db"
    repo = SQLiteSessionRepository(str(db_path))
    yield repo
    close = getattr(repo, "close", None)
    if callable(close):
        close()


@pytest.fixture
def test_client(
    test_settings: Settings,
    in_memory_session_repo: InMemorySessionRepository,
) -> TestClient:
    from healthbot.api.app import app
    from healthbot.api.dependencies import get_session_service
    from healthbot.services.session_service import SessionService

    service = SessionService(
        session_repository=in_memory_session_repo,
        settings=test_settings,
    )

    app.dependency_overrides[get_session_service] = lambda: service

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()

    close = getattr(service, "close", None)
    if callable(close):
        close()


class FakeLLM:
    def invoke(self, messages, *args, **kwargs):
        from langchain_core.messages import AIMessage

        return AIMessage(content="Stub response")

    def with_structured_output(self, schema, *args, **kwargs):
        class _Structured:
            def invoke(self, messages, *args, **kwargs):
                class _FakeModel:
                    def model_dump(self):
                        schema_name = getattr(schema, "__name__", "")
                        if schema_name == "QuizQuestion":
                            return {
                                "question": "Which organ pumps blood through the body?",
                                "option_a": "Liver",
                                "option_b": "Heart",
                                "option_c": "Kidney",
                                "option_d": "Lung",
                                "correct_answer": "B",
                            }
                        return {
                            "explanation": "The heart pumps blood through the body.",
                            "key_concepts": "heart, circulation",
                            "citations": "Educational summary",
                            "learning_tips": "Review cardiovascular basics.",
                        }

                return _FakeModel()

        return _Structured()


class FakeLLMProvider:
    def get_model(self):
        return FakeLLM()


@pytest.fixture
def fake_llm_provider() -> FakeLLMProvider:
    return FakeLLMProvider()
