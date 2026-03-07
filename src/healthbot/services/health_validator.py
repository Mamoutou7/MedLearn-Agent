"""
Health topic validation service.
"""

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage
from src.healthbot.infra.llm_provider import LLMProvider


class HealthValidator:
    """
    Service responsible for validating if a question
    is related to health.
    """

    def __init__(self, llm_provider: LLMProvider):
        self.llm = llm_provider.get_model()

    def validate(self, question: str) -> dict:
        """
        Validate a user question.
        """
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """You are a classifier.

        Determine if a question is related to health, medicine, diseases,
        symptoms, treatments, hospitals, doctors, or wellness.

        Rules:
        - Reply ONLY with YES or NO
        - YES → medical or health topic
        - NO → anything else

        Examples:
        What is diabetes? → YES
        What causes HIV? → YES
        What is a healthy diet? → YES
        What is the capital of France? → NO
        How to install Python? → NO
        """
                ),
                ("user", "{question}")
            ]
        )

        try:
            response = self.llm.invoke(
                prompt.format_messages(question=question)
            )
            decision = response.content.strip().upper()
            is_health = decision in ["YES", "Y", "TRUE", "HEALTH-RELATED"]

            if is_health:
                return {
                    "messages": [AIMessage(content="Health topic validated")],
                    "health_topic": True,
                    "question": question
                }

            return {
                "messages": [AIMessage(content="Only health topics allowed.")],
                "health_topic": False,
                "question": question
            }

        except Exception as e:
            print(f"Validation error: {e}")

            return {
                "messages": [AIMessage(content="Validation error occurred.")],
                "health_topic": False,
                "question": question
            }


if __name__ == "__main__":
    health_validator = HealthValidator(LLMProvider())

    result = health_validator.validate("What is AIDS?")
    print(result)