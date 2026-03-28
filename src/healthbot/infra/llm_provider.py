from __future__ import annotations

from langchain_openai import ChatOpenAI

from healthbot.core.exceptions import LLMServiceError
from healthbot.core.logging import get_logger
from healthbot.core.settings import settings
from healthbot.observability.metrics import metrics

logger = get_logger(__name__)


class LLMProvider:
    """
    Factory responsible for creating LLM instances.
    """

    def __init__(self):
        self._llm = None

    def get_model(self) -> ChatOpenAI:
        """
        Return configured ChatOpenAI instance.

        Returns
        -------
        ChatOpenAI
        """
        if self._llm is None:
            try:
                logger.info("Initializing LLM model=%s", settings.model_name)
                self._llm = ChatOpenAI(
                    model=settings.model_name,
                    temperature=0,
                    api_key=settings.openai_api_key,
                    base_url=settings.openai_base_url,
                    timeout=30,
                    max_retries=3,
                )
                metrics.increment("llm.provider.initialized")

            except Exception as exc:
                logger.exception("Failed to initialize ChatOpenAI")
                raise LLMServiceError("Could not initialize LLM provider") from exc

        return self._llm
