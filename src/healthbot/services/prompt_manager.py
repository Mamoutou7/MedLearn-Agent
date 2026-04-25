from __future__ import annotations

from typing import Any

from langchain_core.messages import BaseMessage
from opentelemetry import trace

from healthbot.core.logging import get_logger
from healthbot.observability.metrics import metrics
from healthbot.prompts.registry import get_prompt

logger = get_logger(__name__)
tracer = trace.get_tracer(__name__)


class PromptManager:
    """Central access point for prompt rendering and prompt-version observability."""

    def render(self, name: str, **kwargs: Any) -> list[BaseMessage]:
        """Render a registered prompt into LangChain messages.
        """
        prompt = get_prompt(name)

        with tracer.start_as_current_span("prompt.render") as span:
            span.set_attribute("prompt.name", prompt.name)
            span.set_attribute("prompt.version", prompt.version)
            span.set_attribute("prompt.full_name", prompt.full_name)
            span.set_attribute("prompt.variable_count", len(kwargs))

            metrics.increment(f"prompt.render.{prompt.name}")
            logger.debug("Rendering prompt %s", prompt.full_name)

            return prompt.format_messages(**kwargs)