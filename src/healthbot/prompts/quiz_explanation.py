from __future__ import annotations

from healthbot.prompts.base import PromptSpec, build_chat_prompt
from healthbot.prompts.safety import (
    GLOBAL_MEDICAL_SAFETY_RULES,
    QUIZ_SAFETY_RULES,
    compose_system_prompt,
)


QUIZ_EXPLANATION_PROMPT = PromptSpec(
    name="quiz_explanation",
    version="v1",
    template=build_chat_prompt(
        [
            (
                "system",
                compose_system_prompt(
                    GLOBAL_MEDICAL_SAFETY_RULES,
                    QUIZ_SAFETY_RULES,
                    """
You are a medical educator helping a patient learn from a quiz result.

Produce a clear explanation that:
1. explains why the correct answer is correct
2. briefly explains why the user's answer is correct or incorrect
3. highlights the most important concepts from the summary
4. includes supporting information grounded in the summary
5. gives one or two simple learning tips

Style rules:
- keep it supportive
- avoid blame
- use simple patient-friendly language
- do not add unsupported medical claims
                    """,
                ),
            ),
            (
                "user",
                """
Create a structured explanation for the following quiz result.

Question: {quiz_question}
User Answer: {user_answer}
Correct Answer: {correct_answer}
Was Correct: {is_correct}
Health Summary: {summary}
                """,
            ),
        ]
    ),
)


def build_quiz_explanation_messages(
    quiz_question: str,
    user_answer: str,
    correct_answer: str,
    is_correct: bool,
    summary: str,
):
    return QUIZ_EXPLANATION_PROMPT.format_messages(
        quiz_question=quiz_question,
        user_answer=user_answer,
        correct_answer=correct_answer,
        is_correct=is_correct,
        summary=summary,
    )