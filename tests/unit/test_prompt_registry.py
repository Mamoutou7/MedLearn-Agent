from __future__ import annotations

import pytest

from healthbot.prompts.registry import get_prompt


def test_get_default_health_agent_prompt_version():
    prompt = get_prompt("health_agent")

    assert prompt.name == "health_agent"
    assert prompt.version == "v1"
    assert prompt.full_name == "health_agent:v1"


def test_get_specific_health_agent_prompt_version_v1():
    prompt = get_prompt("health_agent", version="v1")

    assert prompt.name == "health_agent"
    assert prompt.version == "v1"


def test_get_specific_health_agent_prompt_version_v2():
    prompt = get_prompt("health_agent", version="v2")

    assert prompt.name == "health_agent"
    assert prompt.version == "v2"


def test_unknown_prompt_version_raises_error():
    with pytest.raises(KeyError):
        get_prompt("health_agent", version="v999")


def test_unknown_prompt_name_raises_error():
    with pytest.raises(KeyError):
        get_prompt("unknown_prompt")