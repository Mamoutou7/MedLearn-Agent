from __future__ import annotations

from src.healthbot.prompts.base import PromptSpec, build_chat_prompt
from src.healthbot.prompts.safety import (
    GLOBAL_MEDICAL_SAFETY_RULES,
    QUIZ_SAFETY_RULES,
    compose_system_prompt,
)


QUIZ_GENERATION_PROMPT = PromptSpec(
    name="quiz_generation",
    version="v1",
    template=build_chat_prompt(
        [
            (
                "system",
                compose_system_prompt(
                    GLOBAL_MEDICAL_SAFETY_RULES,
                    QUIZ_SAFETY_RULES,
                    """
Generate exactly ONE multiple-choice quiz question from the provided health summary.

Requirements:
- The question must assess understanding of the summary.
- Provide exactly 4 answer choices: A, B, C, D.
- Only one answer must be correct.
- All distractors must be plausible but clearly wrong.
- Use plain language suitable for patients.
- Do not ask about facts missing from the summary.
- Prefer conceptual understanding over memorization.
                    """,
                    """
Example:

Summary:
"Diabetes is a condition where blood sugar levels are too high."

Expected structure:
Question: What is the main problem in diabetes?
A: Low blood pressure
B: High blood sugar
C: Weak muscles
D: Poor vision
Correct Answer: B
                    """,
                ),
            ),
            ("user", "{summary}"),
        ]
    ),
)


def build_quiz_generation_messages(summary: str):
    return QUIZ_GENERATION_PROMPT.format_messages(summary=summary)