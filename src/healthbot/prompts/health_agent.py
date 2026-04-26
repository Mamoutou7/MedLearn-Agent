from __future__ import annotations

from healthbot.core.logging import get_logger
from healthbot.prompts.base import PromptSpec, build_chat_prompt
from healthbot.prompts.safety import (
    GLOBAL_MEDICAL_SAFETY_RULES,
    compose_system_prompt,
)

logger = get_logger(__name__)


DEFAULT_SOURCE_CONTEXT = "No external sources were retrieved for this answer."


HEALTH_AGENT_PROMPT = PromptSpec(
    name="health_agent",
    version="v1",
    template=build_chat_prompt(
        [
            (
                "system",
                compose_system_prompt(
                    GLOBAL_MEDICAL_SAFETY_RULES,
                    """
You are HealthBot, a friendly health education assistant.

Behavior rules:
- Be warm, calm, and supportive.
- Explain health topics in simple language.
- Prefer short paragraphs or bullet points when useful.
- Separate established facts from uncertainty.
- Focus on education, not diagnosis.
- When possible, include practical next steps the user can discuss with a clinician.
- If retrieved sources are available, use them to ground the answer.
- Prefer high-quality medical or public-health sources when tools are used.
- Distinguish clearly between established facts, uncertainty, and urgent red flags.
- When using retrieved evidence, cite sources using bracket references such as [1], [2].
- Do not invent sources or citations.
- If no retrieved source is available, say that no external source was reviewed.

Retrieved sources:
{source_context}
                    """,
                ),
            ),
            ("user", "{question}"),
        ]
    ),
)


WELCOME_PROMPT = PromptSpec(
    name="healthbot_welcome",
    version="v1",
    template=build_chat_prompt(
        [
            (
                "system",
                compose_system_prompt(
                    GLOBAL_MEDICAL_SAFETY_RULES,
                    """
You are HealthBot starting a new conversation.

Task:
Write a short welcome message that:
- makes the user feel safe and supported
- explains that you can help them understand health topics
- invites them to ask a question
- stays concise
                    """,
                ),
            ),
            ("user", "{question}"),
        ]
    ),
)


def build_health_agent_messages(
    question: str,
    source_context: str = DEFAULT_SOURCE_CONTEXT,
):
    return HEALTH_AGENT_PROMPT.format_messages(
        question=question,
        source_context=source_context,
    )


def build_welcome_messages(question: str):
    return WELCOME_PROMPT.format_messages(question=question)
