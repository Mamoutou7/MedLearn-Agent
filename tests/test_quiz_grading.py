import pytest
from healthbot.services.quiz_service import QuizGradingService


def test_validate_answer_valid():
    service = QuizGradingService()

    assert service.validate_answer("A") is True
    assert service.validate_answer("b") is True
    assert service.validate_answer("C") is True


def test_validate_answer_invalid():
    service = QuizGradingService()

    assert service.validate_answer("Z") is False
    assert service.validate_answer("1") is False
    assert service.validate_answer("") is False


def test_grade_correct():
    service = QuizGradingService()

    result = service.grade("B", "B")

    assert result["is_correct"] is True
    assert result["score"] == 100


def test_grade_incorrect():
    service = QuizGradingService()

    result = service.grade("A", "C")

    assert result["is_correct"] is False
    assert result["score"] == 0
