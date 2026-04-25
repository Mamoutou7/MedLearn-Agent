from __future__ import annotations

from urllib.parse import urlparse

from langchain_core.tools import tool
from opentelemetry import trace

from healthbot.core.exceptions import ToolExecutionError
from healthbot.core.logging import get_logger
from healthbot.core.settings import settings
from healthbot.domain.evidence import EvidencePack, EvidenceSource
from healthbot.infra.search_provider import get_search_provider
from healthbot.observability.metrics import metrics

logger = get_logger(__name__)
tracer = trace.get_tracer(__name__)

MAX_RESULTS = 8
SEARCH_DEPTH = "advanced"


def _extract_domain(url: str | None) -> str:
    if not url:
        return ""
    host = urlparse(url).netloc.lower()
    return host[4:] if host.startswith("www.") else host


def _is_trusted_domain(domain: str | None) -> bool:
    if not domain:
        return False
    return any(
        domain == trusted or domain.endswith(f".{trusted}")
        for trusted in settings.trusted_health_domains
    )


def _truncate_text(value: str | None, limit: int = 1200) -> str:
    if not value:
        return ""
    value = value.strip()
    if len(value) <= limit:
        return value
    return value[:limit].rstrip() + "..."


def _build_evidence_pack(question: str, raw_results: list[dict]) -> EvidencePack:
    sources: list[EvidenceSource] = []

    for item in raw_results:
        url = item.get("url") or ""
        domain = _extract_domain(url)

        sources.append(
            EvidenceSource(
                title=item.get("title") or "Untitled source",
                url=url,
                domain=domain,
                content=_truncate_text(item.get("content")),
                score=item.get("score"),
                trusted_source=_is_trusted_domain(domain),
            )
        )

    sources.sort(
        key=lambda source: (
            source.trusted_source,
            source.score if source.score is not None else 0.0,
        ),
        reverse=True,
    )

    return EvidencePack(query=question, sources=sources)


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
            current_span.record_exception(exc)
            current_span.set_attribute("error", True)
            logger.exception("Web search tool failed")
            raise ToolExecutionError("Web search execution failed") from exc

        if not isinstance(results, dict):
            raise ToolExecutionError("Search provider returned an invalid payload")

        raw_results = results.get("results", [])
        if not isinstance(raw_results, list):
            raise ToolExecutionError("Search provider returned invalid search results")

        evidence_pack = _build_evidence_pack(question, raw_results)
        top_sources = evidence_pack.top_sources(settings.source_result_limit)

        trusted_count = len(evidence_pack.trusted_sources)
        returned_count = len(top_sources)

        metrics.set_gauge("tool.web_search.last_trusted_result_count", trusted_count)
        metrics.set_gauge("tool.web_search.last_returned_result_count", returned_count)

        current_span.set_attribute("search.raw_result_count", len(raw_results))
        current_span.set_attribute("search.curated_result_count", len(evidence_pack.sources))
        current_span.set_attribute("search.trusted_result_count", trusted_count)
        current_span.set_attribute("search.returned_result_count", returned_count)

        return {
            "query": evidence_pack.query,
            "results": [
                {
                    "title": source.title,
                    "url": source.url,
                    "content": source.content,
                    "score": source.score,
                    "domain": source.domain,
                    "trusted_source": source.trusted_source,
                }
                for source in top_sources
            ],
            "trusted_domains_considered": settings.trusted_health_domains,
        }
