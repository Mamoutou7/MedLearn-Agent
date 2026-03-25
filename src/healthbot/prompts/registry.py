from __future__ import annotations

from src.healthbot.prompts.base import PromptSpec
from src.healthbot.prompts.health_agent import (
    HEALTH_AGENT_PROMPT,
    WELCOME_PROMPT,
)
from src.healthbot.prompts.health_validator import HEALTH_VALIDATOR_PROMPT
from src.healthbot.prompts.quiz_generation import QUIZ_GENERATION_PROMPT
from src.healthbot.prompts.quiz_explanation import QUIZ_EXPLANATION_PROMPT
from src.healthbot.prompts.rejection import REJECTION_PROMPT


PROMPT_REGISTRY: dict[str, PromptSpec] = {
    HEALTH_VALIDATOR_PROMPT.name: HEALTH_VALIDATOR_PROMPT,
    HEALTH_AGENT_PROMPT.name: HEALTH_AGENT_PROMPT,
    WELCOME_PROMPT.name: WELCOME_PROMPT,
    QUIZ_GENERATION_PROMPT.name: QUIZ_GENERATION_PROMPT,
    QUIZ_EXPLANATION_PROMPT.name: QUIZ_EXPLANATION_PROMPT,
    REJECTION_PROMPT.name: REJECTION_PROMPT,
}


def get_prompt(name: str) -> PromptSpec:
    """
    Return a registered prompt definition.

    Raises
    ------
    KeyError
        If the prompt name is unknown.
    """
    try:
        return PROMPT_REGISTRY[name]
    except KeyError as exc:
        available = ", ".join(sorted(PROMPT_REGISTRY))
        raise KeyError(f"Unknown prompt '{name}'. Available: {available}") from exc