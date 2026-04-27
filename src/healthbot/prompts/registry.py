from __future__ import annotations

from healthbot.prompts.base import PromptSpec
from healthbot.prompts.health_agent import (
    HEALTH_AGENT_PROMPT,
    HEALTH_AGENT_PROMPT_V2,
    WELCOME_PROMPT,
)
from healthbot.prompts.health_validator import HEALTH_VALIDATOR_PROMPT
from healthbot.prompts.quiz_explanation import QUIZ_EXPLANATION_PROMPT
from healthbot.prompts.quiz_generation import QUIZ_GENERATION_PROMPT
from healthbot.prompts.rejection import REJECTION_PROMPT

PromptKey = tuple[str, str]


PROMPT_REGISTRY: dict[PromptKey, PromptSpec] = {
    (HEALTH_VALIDATOR_PROMPT.name, HEALTH_VALIDATOR_PROMPT.version): HEALTH_VALIDATOR_PROMPT,
    (HEALTH_AGENT_PROMPT.name, HEALTH_AGENT_PROMPT.version): HEALTH_AGENT_PROMPT,
    (HEALTH_AGENT_PROMPT_V2.name, HEALTH_AGENT_PROMPT_V2.version): HEALTH_AGENT_PROMPT_V2,
    (WELCOME_PROMPT.name, WELCOME_PROMPT.version): WELCOME_PROMPT,
    (QUIZ_GENERATION_PROMPT.name, QUIZ_GENERATION_PROMPT.version): QUIZ_GENERATION_PROMPT,
    (QUIZ_EXPLANATION_PROMPT.name, QUIZ_EXPLANATION_PROMPT.version): QUIZ_EXPLANATION_PROMPT,
    (REJECTION_PROMPT.name, REJECTION_PROMPT.version): REJECTION_PROMPT,
}


DEFAULT_PROMPT_VERSIONS: dict[str, str] = {
    HEALTH_VALIDATOR_PROMPT.name: HEALTH_VALIDATOR_PROMPT.version,
    HEALTH_AGENT_PROMPT.name: HEALTH_AGENT_PROMPT.version,
    WELCOME_PROMPT.name: WELCOME_PROMPT.version,
    QUIZ_GENERATION_PROMPT.name: QUIZ_GENERATION_PROMPT.version,
    QUIZ_EXPLANATION_PROMPT.name: QUIZ_EXPLANATION_PROMPT.version,
    REJECTION_PROMPT.name: REJECTION_PROMPT.version,
}


def get_prompt(name: str, version: str | None = None) -> PromptSpec:
    """Fetch a prompt by logical name and optional version.

    If version is omitted, the default version for that prompt name is used.
    """
    resolved_version = version or DEFAULT_PROMPT_VERSIONS.get(name)

    if resolved_version is None:
        available_names = ", ".join(sorted(DEFAULT_PROMPT_VERSIONS))
        raise KeyError(
            f"No default prompt version configured for '{name}'. "
            f"Available prompts: {available_names}"
        )

    key = (name, resolved_version)

    try:
        return PROMPT_REGISTRY[key]
    except KeyError as exc:
        available_names = list_prompt_versions(name)
        raise KeyError(
            f"No prompt registered for {name}:{resolved_version}. "
            f"Available prompts: {available_names}"
        ) from exc


def list_prompt_names() -> list[str]:
    """Return all registered logical prompt names."""
    return sorted({name for name, _version in PROMPT_REGISTRY})


def list_prompt_versions(name: str) -> list[str]:
    """Return all registered versions for a given prompt name."""
    return sorted(version for prompt_name, version in PROMPT_REGISTRY if prompt_name == name)


def list_prompts() -> list[str]:
    """Return all registered prompt full names."""
    return sorted(f"{name}:{version}" for name, version in PROMPT_REGISTRY)
