
from healthbot.services.quiz_service import (
    QuizService,
    QuizGradingService,
)


class FakeQuiz:
    def model_dump(self):
        return {
            "question": "What system does HIV attack?",
            "option_a": "Digestive system",
            "option_b": "Immune system",
            "option_c": "Respiratory system",
            "option_d": "Nervous system",
            "correct_answer": "B",
        }


class FakeLLM:
    def with_structured_output(self, schema):
        return self

    def invoke(self, messages):
        return FakeQuiz()


class FakeProvider:
    def get_model(self):
        return FakeLLM()


def test_quiz_pipeline():
    """
    Full quiz pipeline test:
    generation + grading
    """

    quiz_service = QuizService(FakeProvider())
    grading_service = QuizGradingService()

    summary = "HIV attacks the immune system."

    quiz = quiz_service.generate_quiz(summary)

    assert quiz["question"] is not None
    assert quiz["correct_answer"] == "B"

    user_answer = "B"

    result = grading_service.grade(user_answer, quiz["correct_answer"])

    assert result["is_correct"] is True
    assert result["score"] == 100
