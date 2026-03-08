from __future__ import annotations

from src.healthbot.prompts.base import PromptSpec, build_chat_prompt
from src.healthbot.prompts.safety import compose_system_prompt


HEALTH_VALIDATOR_PROMPT = PromptSpec(
    name="health_validator",
    version="v1",
    template=build_chat_prompt(
        [
            (
                "system",
                compose_system_prompt(
                    """
You are a strict topic classifier.

Task:
Determine whether the user question is related to health, medicine,
symptoms, diseases, treatments, prevention, hospitals, clinicians,
mental health, nutrition, wellness, or public health.

Output rules:
- Reply with ONLY: YES or NO
- YES = clearly health-related
- NO = not health-related
- Do not explain your answer
                    """,
                    """
Examples:
- What is diabetes? -> YES
- What causes HIV? -> YES
- What is a healthy diet? -> YES
- What is the capital of France? -> NO
- How do I install Python? -> NO
- Can stress affect sleep? -> YES
                    """,
                ),
            ),
            ("user", "{question}"),
        ]
    ),
)


def build_health_validator_messages(question: str):
    return HEALTH_VALIDATOR_PROMPT.format_messages(question=question)