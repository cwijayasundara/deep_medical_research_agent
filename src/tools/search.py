"""Tavily web search tool with medical domain filtering.

Provides a factory for creating a TavilySearch tool configured for
medical research, plus helpers for formatting results and error handling.
"""

import logging
from typing import Any

from langchain_tavily import TavilySearch

from src.config.settings import Settings

logger = logging.getLogger(__name__)

# ---- Constants ----

DEFAULT_MAX_RESULTS = 5
DEFAULT_SEARCH_DEPTH = "advanced"
DEFAULT_MEDICAL_DOMAINS = [
    "pubmed.ncbi.nlm.nih.gov",
    "nature.com",
    "thelancet.com",
    "nejm.org",
    "who.int",
    "nih.gov",
    "bmj.com",
    "jamanetwork.com",
]
NO_RESULTS_MESSAGE = "Search returned no results for the query."


def create_search_tool(settings: Settings) -> TavilySearch:
    """Create a TavilySearch tool configured for medical research.

    Uses custom domain list from settings if provided,
    otherwise falls back to DEFAULT_MEDICAL_DOMAINS.
    """
    domains = settings.tavily_include_domains or DEFAULT_MEDICAL_DOMAINS

    return TavilySearch(
        max_results=DEFAULT_MAX_RESULTS,
        search_depth=DEFAULT_SEARCH_DEPTH,
        include_domains=domains,
        tavily_api_key=settings.tavily_api_key,
    )


def format_search_results(raw_results: dict[str, Any]) -> str:
    """Format raw Tavily search results into an LLM-consumable string.

    Each result is formatted with title, URL, and content snippet.
    Returns a 'no results' message if results are empty.
    """
    results = raw_results.get("results", [])

    if not results:
        return NO_RESULTS_MESSAGE

    formatted_parts = []
    for i, result in enumerate(results, start=1):
        title = result.get("title", "Untitled")
        url = result.get("url", "")
        content = result.get("content", "")
        formatted_parts.append(f"[{i}] {title}\n    URL: {url}\n    {content}")

    return "\n\n".join(formatted_parts)


def safe_search(tool: TavilySearch, query: str) -> str:
    """Invoke the search tool with error handling.

    Returns formatted results on success, or an error message
    string on failure (never raises).
    """
    try:
        raw_results = tool.invoke({"query": query})
        return format_search_results(raw_results)
    except Exception as exc:
        logger.error("Tavily search failed for query '%s': %s", query, exc)
        return f"Search failed: {exc}. Please try again or refine your query."
