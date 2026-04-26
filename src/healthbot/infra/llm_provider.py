from __future__ import annotations

from langchain_openai import ChatOpenAI

from healthbot.core.exceptions import LLMServiceError
from healthbot.core.logging import get_logger
from healthbot.core.settings import settings
from healthbot.infra.llm_observed import ObservedLLM
from healthbot.observability.metrics import metrics

logger = get_logger(__name__)


class LLMProvider:
    """
    Factory responsible for creating LLM instances.
    """

    def __init__(self):
        self._llm = None
        self._judge_llm = None

    def get_model(self) -> ObservedLLM:
        """
        Return configured and observed ChatOpenAI instance for application generation.
        """
        if self._llm is None:
            try:
                logger.info(
                    "Initializing LLM model=%s base_url=%s",
                    settings.model_name,
                    settings.openai_base_url,
                )

                raw_llm = ChatOpenAI(
                    model=settings.model_name,
                    temperature=0,
                    api_key=settings.openai_api_key,
                    base_url=settings.openai_base_url,
                    timeout=30,
                    max_retries=3,
                )

                self._llm = ObservedLLM(
                    raw_llm,
                    model_name=settings.model_name,
                    default_span_name="llm.invoke",
                    metric_prefix="llm.invoke",
                )
                metrics.increment("llm.provider.initialized")

            except Exception as exc:
                logger.exception("Failed to initialize ChatOpenAI")
                raise LLMServiceError("Could not initialize LLM provider") from exc

        return self._llm

    def get_judge_model(self) -> ObservedLLM:
        """
        Return configured and observed ChatOpenAI instance for LLM-as-judge evaluation.
        """
        if self._judge_llm is None:
            try:
                logger.info(
                    "Initializing judge LLM model=%s base_url=%s",
                    settings.judge_model_name,
                    settings.openai_base_url,
                )

                raw_judge_llm = ChatOpenAI(
                    model=settings.judge_model_name,
                    temperature=0,
                    api_key=settings.openai_api_key,
                    base_url=settings.openai_base_url,
                    timeout=30,
                    max_retries=3,
                )

                self._judge_llm = ObservedLLM(
                    raw_judge_llm,
                    model_name=settings.judge_model_name,
                    default_span_name="llm.judge",
                    metric_prefix="llm.judge",
                )
                metrics.increment("llm.judge_provider.initialized")

            except Exception as exc:
                logger.exception("Failed to initialize judge ChatOpenAI")
                raise LLMServiceError("Could not initialize judge LLM provider") from exc

        return self._judge_llm
