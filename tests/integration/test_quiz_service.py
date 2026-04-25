from __future__ import annotations

import pytest

from healthbot.core.exceptions import QuizGenerationError
from healthbot.services.quiz_service import QuizService


class FakeQuiz:
    def model_dump(self):
        return {
            "question": "Which virus attacks the immune system?",
            "option_a": "HIV",
            "option_b": "Flu",
            "option_c": "Measles",
            "option_d": "Chickenpox",
            "correct_answer": "A",
        }


class FakeLLM:
    def with_structured_output(self, schema, *args, **kwargs):
        return self

    def invoke(self, messages, *args, **kwargs):
        return FakeQuiz()


class FakeLLMProvider:
    def get_model(self):
        return FakeLLM()


def test_generate_quiz():
    service = QuizService(FakeLLMProvider())

    summary = "HIV attacks the immune system."

    quiz = service.generate_quiz(summary)

    assert quiz["question"] == "Which virus attacks the immune system?"
    assert quiz["option_a"] == "HIV"
    assert quiz["correct_answer"] == "A"


def test_generate_quiz_requires_summary():
    service = QuizService(FakeLLMProvider())

    with pytest.raises(QuizGenerationError):
        service.generate_quiz("")
