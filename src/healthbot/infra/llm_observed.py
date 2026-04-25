from __future__ import annotations

from typing import Any

from opentelemetry import trace

from healthbot.core.settings import settings
from healthbot.observability.metrics import metrics

tracer = trace.get_tracer(__name__)


class ObservedLLM:
    """
    Thin wrapper around a LangChain chat model.

    Adds OpenTelemetry spans and local metrics around each LLM invocation
    without changing the model API used by the workflow.
    """

    def __init__(self, llm: Any, *, default_span_name: str = "llm.invoke") -> None:
        self._llm = llm
        self._default_span_name = default_span_name

    def invoke(self, messages: Any, *args: Any, span_name: str | None = None, **kwargs: Any) -> Any:
        effective_span_name = span_name or self._default_span_name

        with tracer.start_as_current_span(effective_span_name) as span:
            span.set_attribute("llm.provider", "openai")
            span.set_attribute("llm.model", settings.model_name)
            span.set_attribute("llm.message_count", _safe_len(messages))
            span.set_attribute("llm.prompt_size", len(str(messages)))

            try:
                response = self._llm.invoke(messages, *args, **kwargs)

                content = getattr(response, "content", "")
                span.set_attribute(
                    "llm.response_size",
                    len(content) if isinstance(content, str) else 0,
                )

                metrics.increment("llm.invoke.success")
                return response

            except Exception as exc:
                span.record_exception(exc)
                span.set_attribute("error", True)
                metrics.increment("llm.invoke.error")
                raise

    def bind_tools(self, *args: Any, **kwargs: Any) -> "ObservedLLM":
        """
        Preserve LangChain tool binding while keeping observation around invoke().
        """
        bound = self._llm.bind_tools(*args, **kwargs)
        return ObservedLLM(bound, default_span_name=self._default_span_name)

    def with_structured_output(self, *args: Any, **kwargs: Any) -> "ObservedLLM":
        """
        Preserve structured-output usage while keeping observation around invoke().
        """
        structured = self._llm.with_structured_output(*args, **kwargs)
        return ObservedLLM(structured, default_span_name=self._default_span_name)

    def __getattr__(self, name: str) -> Any:
        """
        Delegate unknown attributes/methods to the underlying LangChain model.
        """
        return getattr(self._llm, name)


def _safe_len(value: Any) -> int:
    try:
        return len(value)
    except TypeError:
        return 1