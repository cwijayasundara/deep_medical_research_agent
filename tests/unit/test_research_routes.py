"""Unit tests for research API endpoint with streaming — STORY-008.

Tests cover:
- AC-1: Research endpoint accepts query and streams SSE progress
- AC-2: Stream events have consistent format
- AC-3: Report auto-saved after completion
- AC-4: Invalid requests return 422
- AC-5: Agent errors streamed as error events
"""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from tests.conftest import make_mock_settings


def _create_test_app():
    """Create a test app with mocked dependencies."""
    from fastapi import FastAPI

    from src.api.routes.research import create_research_router

    settings = make_mock_settings()
    mock_agent = MagicMock()
    app = FastAPI()
    router = create_research_router(settings=settings, agent=mock_agent)
    app.include_router(router, prefix="/api")
    return app


# ---- AC-1: Research endpoint accepts query and streams progress ----


@pytest.mark.unit
class TestResearchEndpointStreaming:
    """AC-1: Research endpoint accepts a query and streams progress."""

    def test_post_research_returns_200(self) -> None:
        """POST /api/research with valid query returns 200."""
        from fastapi.testclient import TestClient

        from src.api.routes.research import create_research_router

        settings = make_mock_settings()
        mock_agent = MagicMock()
        # Mock stream to yield one result event
        mock_agent.stream.return_value = iter(
            [{"messages": [MagicMock(content="Final report content")]}]
        )

        app = __import__("fastapi", fromlist=["FastAPI"]).FastAPI()
        router = create_research_router(settings=settings, agent=mock_agent)
        app.include_router(router, prefix="/api")

        client = TestClient(app)
        with patch("src.api.routes.research.save_report"):
            response = client.post("/api/research", json={"query": "CRISPR gene therapy advances"})

        assert response.status_code == 200

    def test_response_content_type_is_event_stream(self) -> None:
        """Response has text/event-stream content type."""
        from fastapi.testclient import TestClient

        from src.api.routes.research import create_research_router

        settings = make_mock_settings()
        mock_agent = MagicMock()
        mock_agent.stream.return_value = iter([{"messages": [MagicMock(content="Report")]}])

        app = __import__("fastapi", fromlist=["FastAPI"]).FastAPI()
        router = create_research_router(settings=settings, agent=mock_agent)
        app.include_router(router, prefix="/api")

        client = TestClient(app)
        with patch("src.api.routes.research.save_report"):
            response = client.post("/api/research", json={"query": "test query"})

        assert "text/event-stream" in response.headers.get("content-type", "")


# ---- AC-2: Stream events have a consistent format ----


@pytest.mark.unit
class TestStreamEventFormat:
    """AC-2: Stream events have a consistent format."""

    def test_events_are_valid_sse_format(self) -> None:
        """Each streamed line follows SSE data: format."""
        from fastapi.testclient import TestClient

        from src.api.routes.research import create_research_router

        settings = make_mock_settings()
        mock_agent = MagicMock()
        mock_agent.stream.return_value = iter(
            [
                {"messages": [MagicMock(content="Final report")]},
            ]
        )

        app = __import__("fastapi", fromlist=["FastAPI"]).FastAPI()
        router = create_research_router(settings=settings, agent=mock_agent)
        app.include_router(router, prefix="/api")

        client = TestClient(app)
        with patch("src.api.routes.research.save_report") as mock_save:
            mock_save.return_value = Path("/tmp/2026-02-08_test.md")
            response = client.post("/api/research", json={"query": "test"})

        lines = [line for line in response.text.strip().split("\n") if line.startswith("data:")]
        assert len(lines) > 0

        for line in lines:
            json_str = line.removeprefix("data: ").strip()
            event = json.loads(json_str)
            assert "type" in event
            assert "data" in event
            assert event["type"] in ("progress", "result", "error")

    def test_final_event_is_result_type(self) -> None:
        """The last event in the stream is a result event."""
        from fastapi.testclient import TestClient

        from src.api.routes.research import create_research_router

        settings = make_mock_settings()
        mock_agent = MagicMock()
        mock_agent.stream.return_value = iter(
            [
                {"messages": [MagicMock(content="Complete report")]},
            ]
        )

        app = __import__("fastapi", fromlist=["FastAPI"]).FastAPI()
        router = create_research_router(settings=settings, agent=mock_agent)
        app.include_router(router, prefix="/api")

        client = TestClient(app)
        with patch("src.api.routes.research.save_report") as mock_save:
            mock_save.return_value = Path("/tmp/2026-02-08_test.md")
            response = client.post("/api/research", json={"query": "test"})

        data_lines = [
            line for line in response.text.strip().split("\n") if line.startswith("data:")
        ]
        last_line = data_lines[-1]
        last_event = json.loads(last_line.removeprefix("data: ").strip())
        assert last_event["type"] == "result"

    def test_result_event_contains_report_content(self) -> None:
        """The result event data contains the markdown report."""
        from fastapi.testclient import TestClient

        from src.api.routes.research import create_research_router

        settings = make_mock_settings()
        mock_agent = MagicMock()
        mock_agent.stream.return_value = iter(
            [
                {"messages": [MagicMock(content="# Research Report\n\nFindings here.")]},
            ]
        )

        app = __import__("fastapi", fromlist=["FastAPI"]).FastAPI()
        router = create_research_router(settings=settings, agent=mock_agent)
        app.include_router(router, prefix="/api")

        client = TestClient(app)
        with patch("src.api.routes.research.save_report") as mock_save:
            mock_save.return_value = Path("/tmp/2026-02-08_test.md")
            response = client.post("/api/research", json={"query": "test"})

        data_lines = [
            line for line in response.text.strip().split("\n") if line.startswith("data:")
        ]
        result_events = [
            json.loads(line.removeprefix("data: ").strip())
            for line in data_lines
            if '"type": "result"' in line or '"type":"result"' in line
        ]

        # At least one result event should exist
        assert len(result_events) >= 1
        # Find the result event (may parse all to be safe)
        result_event = next(e for e in result_events if e["type"] == "result")
        assert "Research Report" in result_event["data"]


# ---- AC-3: Report is auto-saved after completion ----


@pytest.mark.unit
class TestReportAutoSave:
    """AC-3: Report is automatically saved after completion."""

    def test_save_report_called_after_completion(self) -> None:
        """save_report is called with the query and report content."""
        from fastapi.testclient import TestClient

        from src.api.routes.research import create_research_router

        settings = make_mock_settings()
        mock_agent = MagicMock()
        mock_agent.stream.return_value = iter(
            [
                {"messages": [MagicMock(content="Report content")]},
            ]
        )

        app = __import__("fastapi", fromlist=["FastAPI"]).FastAPI()
        router = create_research_router(settings=settings, agent=mock_agent)
        app.include_router(router, prefix="/api")

        client = TestClient(app)
        with patch("src.api.routes.research.save_report") as mock_save:
            mock_save.return_value = Path("/tmp/2026-02-08_test.md")
            client.post("/api/research", json={"query": "CRISPR advances"})

        mock_save.assert_called_once()
        call_kwargs = mock_save.call_args
        assert call_kwargs.kwargs.get("query") == "CRISPR advances" or (
            call_kwargs.args and call_kwargs.args[0] == "CRISPR advances"
        )

    def test_result_event_includes_filename(self) -> None:
        """The result event includes the saved report filename."""
        from fastapi.testclient import TestClient

        from src.api.routes.research import create_research_router

        settings = make_mock_settings()
        mock_agent = MagicMock()
        mock_agent.stream.return_value = iter(
            [
                {"messages": [MagicMock(content="Report")]},
            ]
        )

        app = __import__("fastapi", fromlist=["FastAPI"]).FastAPI()
        router = create_research_router(settings=settings, agent=mock_agent)
        app.include_router(router, prefix="/api")

        client = TestClient(app)
        with patch("src.api.routes.research.save_report") as mock_save:
            mock_save.return_value = Path("/tmp/2026-02-08_crispr-advances.md")
            response = client.post("/api/research", json={"query": "test"})

        data_lines = [
            line for line in response.text.strip().split("\n") if line.startswith("data:")
        ]
        result_events = [json.loads(line.removeprefix("data: ").strip()) for line in data_lines]
        result_event = next(e for e in result_events if e["type"] == "result")
        assert "2026-02-08_crispr-advances.md" in result_event.get("filename", "")


# ---- AC-4: Invalid requests return 422 ----


@pytest.mark.unit
class TestInvalidRequests:
    """AC-4: Invalid requests return proper error responses."""

    def test_empty_query_returns_422(self) -> None:
        """POST with empty query returns 422."""
        from fastapi.testclient import TestClient

        app = _create_test_app()
        client = TestClient(app)
        response = client.post("/api/research", json={"query": ""})

        assert response.status_code == 422

    def test_missing_query_returns_422(self) -> None:
        """POST with missing query field returns 422."""
        from fastapi.testclient import TestClient

        app = _create_test_app()
        client = TestClient(app)
        response = client.post("/api/research", json={})

        assert response.status_code == 422

    def test_no_body_returns_422(self) -> None:
        """POST with no body returns 422."""
        from fastapi.testclient import TestClient

        app = _create_test_app()
        client = TestClient(app)
        response = client.post("/api/research")

        assert response.status_code == 422


# ---- AC-5: Agent errors streamed as error events ----


@pytest.mark.unit
class TestAgentErrorStreaming:
    """AC-5: Agent errors are streamed as error events."""

    def test_agent_error_produces_error_event(self) -> None:
        """When agent.stream raises, an error event is streamed."""
        from fastapi.testclient import TestClient

        from src.api.routes.research import create_research_router

        settings = make_mock_settings()
        mock_agent = MagicMock()
        mock_agent.stream.side_effect = RuntimeError("Agent crashed")

        app = __import__("fastapi", fromlist=["FastAPI"]).FastAPI()
        router = create_research_router(settings=settings, agent=mock_agent)
        app.include_router(router, prefix="/api")

        client = TestClient(app)
        response = client.post("/api/research", json={"query": "test"})

        assert response.status_code == 200  # SSE stream still 200
        data_lines = [
            line for line in response.text.strip().split("\n") if line.startswith("data:")
        ]
        events = [json.loads(line.removeprefix("data: ").strip()) for line in data_lines]
        error_events = [e for e in events if e["type"] == "error"]
        assert len(error_events) >= 1
        assert (
            "failed" in error_events[0]["data"].lower()
            or "error" in error_events[0]["data"].lower()
        )

    def test_error_event_logged_at_error_level(
        self,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """Agent errors are logged at ERROR level."""
        import logging

        from fastapi.testclient import TestClient

        from src.api.routes.research import create_research_router

        settings = make_mock_settings()
        mock_agent = MagicMock()
        mock_agent.stream.side_effect = RuntimeError("Agent crashed")

        app = __import__("fastapi", fromlist=["FastAPI"]).FastAPI()
        router = create_research_router(settings=settings, agent=mock_agent)
        app.include_router(router, prefix="/api")

        client = TestClient(app)
        with caplog.at_level(logging.ERROR):
            client.post("/api/research", json={"query": "test"})

        assert any(record.levelno == logging.ERROR for record in caplog.records)


# ---- Pydantic schemas ----


@pytest.mark.unit
class TestResearchSchemas:
    """Verify Pydantic request/response schemas."""

    def test_research_request_schema_exists(self) -> None:
        """ResearchRequest Pydantic model is defined."""
        from src.api.routes.research import ResearchRequest

        req = ResearchRequest(query="test query")
        assert req.query == "test query"

    def test_research_request_rejects_empty_query(self) -> None:
        """ResearchRequest rejects empty string queries."""
        from pydantic import ValidationError

        from src.api.routes.research import ResearchRequest

        with pytest.raises(ValidationError):
            ResearchRequest(query="")

    def test_stream_event_schema_exists(self) -> None:
        """StreamEvent Pydantic model is defined."""
        from src.api.routes.research import StreamEvent

        event = StreamEvent(type="progress", data="Searching...")
        assert event.type == "progress"
        assert event.data == "Searching..."

    def test_stream_event_types(self) -> None:
        """StreamEvent type field accepts progress, result, and error."""
        from src.api.routes.research import StreamEvent

        for event_type in ("progress", "result", "error"):
            event = StreamEvent(type=event_type, data="test")
            assert event.type == event_type
