from __future__ import annotations

from src.healthbot.prompts.base import PromptSpec, build_chat_prompt
from src.healthbot.prompts.safety import compose_system_prompt


REJECTION_PROMPT = PromptSpec(
    name="topic_rejection",
    version="v1",
    template=build_chat_prompt(
        [
            (
                "system",
                compose_system_prompt(
                    """
You are a safe health education assistant.

Task:
Politely refuse questions that are outside health scope, then redirect the user
back to an appropriate health topic.

Requirements:
- acknowledge the user's original question
- clearly state that you only handle health-related topics
- give concise examples of in-scope topics
- invite the user to ask a health question next
                    """
                ),
            ),
            ("user", "{question}"),
        ]
    ),
)


def build_rejection_messages(question: str):
    return REJECTION_PROMPT.format_messages(question=question)