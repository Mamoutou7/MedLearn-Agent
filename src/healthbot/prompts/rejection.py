from __future__ import annotations

from healthbot.prompts.base import PromptSpec, build_chat_prompt
from healthbot.prompts.safety import compose_system_prompt

TOPIC_REJECTION_V1 = PromptSpec(
    name="topic_rejection",
    version="v1",
    description="Rejects non-health questions politely.",
    template=build_chat_prompt(
        [
            (
                "system",
                """
You are HealthBot, a health education assistant.

The user's request is not related to health education.

You must:
- politely refuse the non-health request
- explicitly say: "I can only help with health-related educational topics."
- do not answer the non-health request
- do not provide code, technical explanations, or non-health content
- invite the user to ask a health-related question

Keep the answer short.
                """.strip(),
            ),
            ("user", "{question}"),
        ]
    ),
)


TOPIC_REJECTION_V2 = PromptSpec(
    name="topic_rejection",
    version="v2",
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

REJECTION_PROMPT = TOPIC_REJECTION_V1


def build_rejection_messages(question: str):
    return REJECTION_PROMPT.format_messages(question=question)
