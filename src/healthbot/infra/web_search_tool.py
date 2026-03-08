"""
External tool for retrieving health information from the web.
"""

from __future__ import annotations

from typing import Dict

from langchain_core.tools import tool
from tavily import TavilyClient

from src.healthbot.core.exceptions import ToolExecutionError
from src.healthbot.core.logging import get_logger
from src.healthbot.core.settings import settings
from src.healthbot.observability.metrics import metrics
from src.healthbot.observability.tracing import trace_span

logger = get_logger(__name__)


@tool
def web_search_tool(question: str) -> Dict:
    """
    Perform a web search for medical information.

    Parameters
    ----------
    question : str
        User question related to health.

    Returns
    -------
    Dict
        Tavily search results.
    """
    try:
        with trace_span("tool.web_search"):
            logger.info("Executing web search tool")
            client = TavilyClient(api_key=settings.tavily_api_key)
            metrics.increment("tool.web_search.calls")
    except Exception as exc:
        logger.exception("Web search tool failed")
        raise ToolExecutionError("Web search execution failed") from exc
    return client.search(question)
