"""
Health topic validation service.
"""

from __future__ import annotations

from langchain_core.messages import AIMessage

from healthbot.core.logging import get_logger
from healthbot.infra.llm_provider import LLMProvider
from healthbot.observability.metrics import metrics
from healthbot.observability.tracing import trace_span
from healthbot.prompts.health_validator import build_health_validator_messages

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

        try:
            with trace_span("health.validate"):
                metrics.increment("health.validate.calls")
                response = self.llm.invoke(build_health_validator_messages(question))
                decision = response.content.strip().upper()
                logger.debug(f"LLM decision: {decision}")

                is_health = decision in ["YES", "Y", "TRUE", "HEALTH-RELATED"]

                if is_health:
                    logger.info("Question validated as health-related")
                    return {
                        "messages": [AIMessage(content="Health topic validated")],
                        "health_topic": True,
                        "question": question,
                    }

                logger.warning("Non-health question detected")
                return {
                    "messages": [AIMessage(content="Only health topics allowed.")],
                    "health_topic": False,
                    "question": question,
                }

        except Exception:
            logger.exception("Health validation failed")
            metrics.increment("health.validate.errors")
            return {
                "messages": [AIMessage(content="Validation error occurred.")],
                "health_topic": False,
                "question": question,
            }
