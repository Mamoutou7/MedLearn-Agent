from __future__ import annotations

from urllib.parse import urlparse

from langchain_core.tools import tool
from opentelemetry import trace

from healthbot.core.exceptions import ToolExecutionError
from healthbot.core.logging import get_logger
from healthbot.core.settings import settings
from healthbot.infra.search_provider import get_search_provider
from healthbot.observability.metrics import metrics
from healthbot.observability.tracing import trace_span

logger = get_logger(__name__)
tracer = trace.get_tracer(__name__)

def _extract_domain(url: str | None) -> str | None:
    if not url:
        return None
    host = urlparse(url).netloc.lower()
    return host[4:] if host.startswith("www.") else host


def _is_trusted_domain(domain: str | None) -> bool:
    if not domain:
        return False
    for trusted in settings.trusted_health_domains:
        if domain == trusted or domain.endswith(f".{trusted}"):
            return True
    return False


@tool
def web_search_tool(question: str) -> dict:
    """Search trusted web sources for health-related evidence."""
    logger.info("Running web search tool")

    with tracer.start_as_current_span("tool.web_search") as current_span:
        current_span.set_attribute("tool.name", "web_search_tool")
        current_span.set_attribute("question.length", len(question))
        current_span.set_attribute("search.max_results", 8)
        current_span.set_attribute("search.depth", "advanced")

        try:
            metrics.increment("tool.web_search.calls")
            client = get_search_provider()
            results = client.search(
                question,
                search_depth="advanced",
                max_results=8,
            )
        except Exception as exc:
            current_span.record_exception(exc)
            current_span.set_attribute("error", True)
            logger.exception("Web search tool failed")
            raise ToolExecutionError("Web search execution failed") from exc

        raw_results = results.get("results", [])
        current_span.set_attribute("search.raw_result_count", len(raw_results))

        curated_results = []

        for item in raw_results:
            domain = _extract_domain(item.get("url"))
            curated_results.append(
                {
                    "title": item.get("title"),
                    "url": item.get("url"),
                    "content": item.get("content"),
                    "score": item.get("score"),
                    "domain": domain,
                    "trusted_source": _is_trusted_domain(domain),
                }
            )

        curated_results.sort(
            key=lambda item: (item["trusted_source"], item.get("score") or 0),
            reverse=True,
        )

        trusted_count = sum(1 for item in curated_results if item["trusted_source"])
        returned_count = min(len(curated_results), settings.source_result_limit)

        metrics.set_gauge("tool.web_search.trusted_results", trusted_count)

        current_span.set_attribute("search.trusted_result_count", trusted_count)
        current_span.set_attribute("search.returned_result_count", returned_count)

        return {
            "query": question,
            "results": curated_results[: settings.source_result_limit],
            "trusted_domains_considered": settings.trusted_health_domains,
        }