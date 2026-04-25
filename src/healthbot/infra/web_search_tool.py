from __future__ import annotations

from urllib.parse import urlparse

from langchain_core.tools import tool
from opentelemetry import trace

from healthbot.core.exceptions import ToolExecutionError
from healthbot.core.logging import get_logger
from healthbot.core.settings import settings
from healthbot.infra.search_provider import get_search_provider
from healthbot.observability.metrics import metrics

logger = get_logger(__name__)
tracer = trace.get_tracer(__name__)

SEARCH_DEPTH = "advanced"
MAX_RESULTS = 8

def _extract_domain(url: str | None) -> str | None:
    if not url:
        return None
    host = urlparse(url).netloc.lower()
    return host[4:] if host.startswith("www.") else host


def _is_trusted_domain(domain: str | None) -> bool:
    if not domain:
        return False
    return any(
        domain == trusted or domain.endswith(f".{trusted}")
        for trusted in settings.trusted_health_domains
    )


def _truncate_text(value: str | None, limit: int = 1200) -> str | None:
    if value is None:
        return None
    value = value.strip()
    if len(value) <= limit:
        return value
    return value[:limit].rstrip() + "..."


@tool
def web_search_tool(question: str) -> dict:
    """Search trusted web sources for health-related evidence."""
    logger.info("Running web search tool")

    if not question or not question.strip():
        raise ToolExecutionError("Web search question cannot be empty")

    with tracer.start_as_current_span("tool.web_search") as current_span:
        current_span.set_attribute("tool.name", "web_search_tool")
        current_span.set_attribute("question.length", len(question))
        current_span.set_attribute("search.max_results", MAX_RESULTS)
        current_span.set_attribute("search.depth", SEARCH_DEPTH)

        try:
            metrics.increment("tool.web_search.calls")
            client = get_search_provider()
            results = client.search(
                question,
                search_depth=SEARCH_DEPTH,
                max_results=MAX_RESULTS,
            )
        except Exception as exc:
            metrics.increment("tool.web_search.errors")
            current_span.record_exception(exc)
            current_span.set_attribute("error", True)
            logger.exception("Web search tool failed")
            raise ToolExecutionError("Web search execution failed") from exc

        if not isinstance(results, dict):
            raise ToolExecutionError("Search provider returned an invalid payload")

        raw_results = results.get("results", [])
        if not isinstance(raw_results, list):
            raise ToolExecutionError("Search provider returned invalid search results")

        current_span.set_attribute("search.raw_result_count", len(raw_results))

        curated_results = []

        for item in raw_results:
            domain = _extract_domain(item.get("url"))
            curated_results.append(
                {
                    "title": item.get("title"),
                    "url": item.get("url"),
                    "content": _truncate_text(item.get("content")),
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

        metrics.set_gauge("tool.web_search.last_trusted_result_count", trusted_count)
        metrics.set_gauge("tool.web_search.last_returned_result_count", returned_count)

        current_span.set_attribute("search.curated_result_count", len(curated_results))
        current_span.set_attribute("search.trusted_result_count", trusted_count)
        current_span.set_attribute("search.returned_result_count", returned_count)

        return {
            "query": question,
            "results": curated_results[: settings.source_result_limit],
            "trusted_result_count": trusted_count,
            "trusted_domains_considered": settings.trusted_health_domains,
        }