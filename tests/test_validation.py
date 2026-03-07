from unittest.mock import MagicMock
from healthbot.services.health_validator import HealthValidator


class FakeLLM:
    def __init__(self, response):
        self.response = response

    def invoke(self, messages):
        return self.response


class FakeProvider:
    def __init__(self, response):
        self.response = response

    def get_model(self):
        return FakeLLM(self.response)


def test_health_question_valid():
    """
    Should return True for a health-related question.
    """

    mock_response = MagicMock()
    mock_response.content = "YES"

    validator = HealthValidator(FakeProvider(mock_response))

    result = validator.validate("What is diabetes?")

    assert result["health_topic"] is True


def test_health_question_invalid():
    """
    Should return False for a non-health question.
    """

    mock_response = MagicMock()
    mock_response.content = "NO"

    validator = HealthValidator(FakeProvider(mock_response))

    result = validator.validate("What is the capital of France?")

    assert result["health_topic"] is False


def test_health_validation_error():
    """
    Should handle LLM failure gracefully.
    """

    class ErrorLLM:
        def invoke(self, messages):
            raise Exception("LLM error")

    class ErrorProvider:
        def get_model(self):
            return ErrorLLM()

    validator = HealthValidator(ErrorProvider())

    result = validator.validate("What is diabetes?")

    assert result["health_topic"] is False