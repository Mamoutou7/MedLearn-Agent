from __future__ import annotations

from src.healthbot.core.logging import get_logger
from src.healthbot.observability.metrics import metrics
from src.healthbot.prompts.registry import get_prompt

logger = get_logger(__name__)


class PromptManager:
    """Central access point for prompt rendering and prompt-version observability."""

    def render(self, name: str, **kwargs):
        prompt = get_prompt(name)
        metrics.increment(f"prompt.render.{prompt.name}")
        logger.debug("Rendering prompt %s", prompt.full_name)
        return prompt.format_messages(**kwargs)