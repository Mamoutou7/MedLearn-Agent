from __future__ import annotations

import pytest

from healthbot.services.prompt_experiment_resolver import PromptExperimentResolver


def test_prompt_experiment_resolver_is_deterministic(monkeypatch):
    monkeypatch.setattr(
        "healthbot.services.prompt_experiment_resolver.settings.prompt_ab_testing_enabled",
        True,
    )

    resolver = PromptExperimentResolver()

    assignment_1 = resolver.resolve(
        prompt_name="health_agent",
        session_id="session-123",
        default_version="v1",
        weights_raw="v1:50,v2:50",
    )

    assignment_2 = resolver.resolve(
        prompt_name="health_agent",
        session_id="session-123",
        default_version="v1",
        weights_raw="v1:50,v2:50",
    )

    assert assignment_1.version == assignment_2.version
    assert assignment_1.bucket == assignment_2.bucket


def test_prompt_experiment_resolver_returns_default_when_disabled(monkeypatch):
    monkeypatch.setattr(
        "healthbot.services.prompt_experiment_resolver.settings.prompt_ab_testing_enabled",
        False,
    )

    resolver = PromptExperimentResolver()

    assignment = resolver.resolve(
        prompt_name="health_agent",
        session_id="session-123",
        default_version="v1",
        weights_raw="v1:50,v2:50",
    )

    assert assignment.version == "v1"
    assert assignment.experiment_enabled is False
    assert assignment.bucket == -1


def test_prompt_experiment_resolver_can_assign_v2(monkeypatch):
    monkeypatch.setattr(
        "healthbot.services.prompt_experiment_resolver.settings.prompt_ab_testing_enabled",
        True,
    )

    resolver = PromptExperimentResolver()

    assignment = resolver.resolve(
        prompt_name="health_agent",
        session_id="session-123",
        default_version="v1",
        weights_raw="v1:0,v2:100",
    )

    assert assignment.version == "v2"
    assert assignment.experiment_enabled is True


def test_prompt_experiment_resolver_rejects_invalid_weights(monkeypatch):
    monkeypatch.setattr(
        "healthbot.services.prompt_experiment_resolver.settings.prompt_ab_testing_enabled",
        True,
    )

    resolver = PromptExperimentResolver()

    with pytest.raises(ValueError):
        resolver.resolve(
            prompt_name="health_agent",
            session_id="session-123",
            default_version="v1",
            weights_raw="v1:80,v2:10",
        )