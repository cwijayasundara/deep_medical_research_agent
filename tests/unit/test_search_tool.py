"""Unit tests for Tavily search tool — STORY-003.

Tests cover:
- AC-1: Search tool created with medical domain filtering
- AC-2: Search returns structured results
- AC-3: Search handles API errors gracefully
- AC-4: Domain filtering is configurable
"""

import logging
from unittest.mock import MagicMock, patch

import pytest


@pytest.mark.unit
class TestCreateSearchTool:
    """AC-1: Tavily search tool is created with medical domain filtering."""

    @patch("src.tools.search.TavilySearch")
    def test_creates_tavily_search_with_defaults(
        self,
        mock_tavily: MagicMock,
        settings_fixture: MagicMock,
    ) -> None:
        """Factory creates TavilySearch with default medical config."""
        from src.tools.search import (
            DEFAULT_MAX_RESULTS,
            DEFAULT_MEDICAL_DOMAINS,
            DEFAULT_SEARCH_DEPTH,
            create_search_tool,
        )

        create_search_tool(settings_fixture)

        mock_tavily.assert_called_once_with(
            max_results=DEFAULT_MAX_RESULTS,
            search_depth=DEFAULT_SEARCH_DEPTH,
            include_domains=DEFAULT_MEDICAL_DOMAINS,
            tavily_api_key=settings_fixture.tavily_api_key,
        )

    @patch("src.tools.search.TavilySearch")
    def test_default_max_results_is_five(
        self,
        mock_tavily: MagicMock,
        settings_fixture: MagicMock,
    ) -> None:
        """Default max_results is 5."""
        from src.tools.search import DEFAULT_MAX_RESULTS

        assert DEFAULT_MAX_RESULTS == 5

    @patch("src.tools.search.TavilySearch")
    def test_default_search_depth_is_advanced(
        self,
        mock_tavily: MagicMock,
        settings_fixture: MagicMock,
    ) -> None:
        """Default search_depth is 'advanced'."""
        from src.tools.search import DEFAULT_SEARCH_DEPTH

        assert DEFAULT_SEARCH_DEPTH == "advanced"

    @patch("src.tools.search.TavilySearch")
    def test_default_domains_include_trusted_sources(
        self,
        mock_tavily: MagicMock,
        settings_fixture: MagicMock,
    ) -> None:
        """Default domains include PubMed, Nature, Lancet, NEJM."""
        from src.tools.search import DEFAULT_MEDICAL_DOMAINS

        assert "pubmed.ncbi.nlm.nih.gov" in DEFAULT_MEDICAL_DOMAINS
        assert "nature.com" in DEFAULT_MEDICAL_DOMAINS
        assert "thelancet.com" in DEFAULT_MEDICAL_DOMAINS
        assert "nejm.org" in DEFAULT_MEDICAL_DOMAINS

    @patch("src.tools.search.TavilySearch")
    def test_returns_tavily_search_instance(
        self,
        mock_tavily: MagicMock,
        settings_fixture: MagicMock,
    ) -> None:
        """Factory returns the TavilySearch instance."""
        from src.tools.search import create_search_tool

        result = create_search_tool(settings_fixture)

        assert result is mock_tavily.return_value


@pytest.mark.unit
class TestSearchResultFormatting:
    """AC-2: Search returns structured results."""

    def test_format_results_produces_readable_string(self) -> None:
        """format_search_results creates LLM-consumable string."""
        from src.tools.search import format_search_results

        raw_results = {
            "results": [
                {
                    "title": "Cancer Immunotherapy Review",
                    "url": "https://pubmed.ncbi.nlm.nih.gov/12345",
                    "content": "A comprehensive review of cancer immunotherapy approaches.",
                },
                {
                    "title": "CRISPR in Oncology",
                    "url": "https://nature.com/articles/67890",
                    "content": "CRISPR gene editing shows promise in oncology.",
                },
            ]
        }

        formatted = format_search_results(raw_results)

        assert "Cancer Immunotherapy Review" in formatted
        assert "https://pubmed.ncbi.nlm.nih.gov/12345" in formatted
        assert "comprehensive review" in formatted
        assert "CRISPR in Oncology" in formatted

    def test_format_results_handles_empty_results(self) -> None:
        """format_search_results handles empty results gracefully."""
        from src.tools.search import format_search_results

        formatted = format_search_results({"results": []})

        assert "no results" in formatted.lower()

    def test_format_results_handles_missing_results_key(self) -> None:
        """format_search_results handles missing 'results' key."""
        from src.tools.search import format_search_results

        formatted = format_search_results({})

        assert "no results" in formatted.lower()


@pytest.mark.unit
class TestSearchErrorHandling:
    """AC-3: Search handles API errors gracefully."""

    def test_safe_search_returns_error_message_on_failure(
        self,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """safe_search returns error string instead of raising."""
        from src.tools.search import safe_search

        mock_tool = MagicMock()
        mock_tool.invoke.side_effect = Exception("Invalid API key")

        with caplog.at_level(logging.ERROR):
            result = safe_search(mock_tool, "cancer research")

        assert "error" in result.lower() or "failed" in result.lower()
        assert caplog.records

    def test_safe_search_logs_error_details(
        self,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """safe_search logs the exception at ERROR level."""
        from src.tools.search import safe_search

        mock_tool = MagicMock()
        mock_tool.invoke.side_effect = Exception("Rate limited")

        with caplog.at_level(logging.ERROR):
            safe_search(mock_tool, "test query")

        assert any(record.levelno == logging.ERROR for record in caplog.records)

    def test_safe_search_returns_formatted_results_on_success(self) -> None:
        """safe_search returns formatted results on success."""
        from src.tools.search import safe_search

        mock_tool = MagicMock()
        mock_tool.invoke.return_value = {
            "results": [
                {
                    "title": "Test Result",
                    "url": "https://example.com",
                    "content": "Test content.",
                }
            ]
        }

        result = safe_search(mock_tool, "test query")

        assert "Test Result" in result
        assert "https://example.com" in result


@pytest.mark.unit
class TestConfigurableDomains:
    """AC-4: Domain filtering is configurable."""

    @patch("src.tools.search.TavilySearch")
    def test_custom_domains_override_defaults(
        self,
        mock_tavily: MagicMock,
        settings_fixture: MagicMock,
    ) -> None:
        """Settings with custom domains uses them instead of defaults."""
        from src.tools.search import create_search_tool

        custom_domains = ["scholar.google.com", "arxiv.org"]
        settings_fixture.tavily_include_domains = custom_domains

        create_search_tool(settings_fixture)

        call_kwargs = mock_tavily.call_args[1]
        assert call_kwargs["include_domains"] == custom_domains

    @patch("src.tools.search.TavilySearch")
    def test_none_domains_uses_defaults(
        self,
        mock_tavily: MagicMock,
        settings_fixture: MagicMock,
    ) -> None:
        """Settings with None domains uses defaults."""
        from src.tools.search import DEFAULT_MEDICAL_DOMAINS, create_search_tool

        settings_fixture.tavily_include_domains = None

        create_search_tool(settings_fixture)

        call_kwargs = mock_tavily.call_args[1]
        assert call_kwargs["include_domains"] == DEFAULT_MEDICAL_DOMAINS
