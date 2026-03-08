from __future__ import annotations

from src.healthbot.prompts.base import PromptSpec, build_chat_prompt
from src.healthbot.prompts.safety import (
    GLOBAL_MEDICAL_SAFETY_RULES,
    compose_system_prompt,
)


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
- If web_search_tool is available, use it only when additional evidence is needed.
- When possible, include practical next steps the user can discuss with a clinician.
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


def build_health_agent_messages(question: str):
    return HEALTH_AGENT_PROMPT.format_messages(question=question)


def build_welcome_messages(question: str):
    return WELCOME_PROMPT.format_messages(question=question)