"""
Health topic validation service.
"""

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage

from src.healthbot.infra.llm_provider import LLMProvider
from src.healthbot.core.logging import get_logger
from src.healthbot.core.exceptions import ValidationError

logger = get_logger(__name__)

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
        logger.info("Validating user question")
        prompt = ChatPromptTemplate.from_messages(
            [(
            "system",
            """You are a health topic classifier.

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
        ])

        try:
            response = self.llm.invoke(
                prompt.format_messages(question=question)
            )
            decision = response.content.strip().upper()

            logger.debug(f"LLM decision: {decision}")

            is_health = decision in ["YES", "Y", "TRUE", "HEALTH-RELATED"]

            if is_health:
                logger.info("Question validated as health-related")
                return {
                    "messages": [AIMessage(content="Health topic validated")],
                    "health_topic": True,
                    "question": question
                }

            logger.warning("Non-health question detected")
            return {
                "messages": [AIMessage(content="Only health topics allowed.")],
                "health_topic": False,
                "question": question
            }

        except Exception as e:
            logger.error(
                "Health validation failed",
                exc_info=True
            )
            raise ValidationError(
                "Health validation failed"
            ) from e

            # return {
            #     "messages": [AIMessage(content="Validation error occurred.")],
            #     "health_topic": False,
            #     "question": question
            # }