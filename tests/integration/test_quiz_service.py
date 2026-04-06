
from healthbot.services.quiz_service import QuizService


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


class FakeLLMProvider:
    def get_model(self):
        return FakeLLM()


def test_generate_quiz():
    service = QuizService(FakeLLMProvider())

    summary = "HIV attacks the immune system."

    quiz = service.generate_quiz(summary)

    assert quiz["question"] is not None
    assert quiz["correct_answer"] in {"A", "B", "C", "D"}
    assert len(quiz) == 6
