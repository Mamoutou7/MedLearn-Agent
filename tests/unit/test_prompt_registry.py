import pytest

from healthbot.prompts.registry import (
    get_prompt,
    list_prompt_names,
    list_prompt_versions,
    list_prompts,
)


def test_get_prompt_uses_default_version():
    prompt = get_prompt("health_agent")

    assert prompt.name == "health_agent"
    assert prompt.version


def test_get_prompt_with_explicit_version():
    default_prompt = get_prompt("health_agent")
    prompt = get_prompt("health_agent", version=default_prompt.version)

    assert prompt.name == "health_agent"
    assert prompt.version == default_prompt.version


def test_get_unknown_prompt_raises_key_error():
    with pytest.raises(KeyError):
        get_prompt("unknown_prompt")


def test_get_unknown_prompt_version_raises_key_error():
    with pytest.raises(KeyError):
        get_prompt("health_agent", version="does-not-exist")


def test_list_prompt_names_contains_health_agent():
    assert "health_agent" in list_prompt_names()


def test_list_prompt_versions_contains_default_health_agent_version():
    prompt = get_prompt("health_agent")

    assert prompt.version in list_prompt_versions("health_agent")


def test_list_prompts_contains_full_prompt_name():
    prompt = get_prompt("health_agent")

    assert prompt.full_name in list_prompts()
