"""
External tool for retrieving health information from the web.
"""

from typing import Dict
from langchain_core.tools import tool
from tavily import TavilyClient
from src.healthbot.core.settings import settings

@tool
def med_web_search(question: str) -> Dict:
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
    client = TavilyClient(api_key=settings.tavily_api_key)

    return client.search(question)