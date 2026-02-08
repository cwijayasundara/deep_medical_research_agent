"""Research API endpoint with Server-Sent Events streaming.

Provides a POST /research endpoint that streams research progress
from the deep research agent via SSE, then auto-saves the report.
"""

import logging
from collections.abc import Generator
from typing import Any

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from langchain_core.messages import HumanMessage
from langgraph.graph.state import CompiledStateGraph
from pydantic import BaseModel, field_validator

from src.config.settings import Settings
from src.services.report_service import save_report

logger = logging.getLogger(__name__)

# ---- Constants ----

EVENT_TYPE_PROGRESS = "progress"
EVENT_TYPE_RESULT = "result"
EVENT_TYPE_ERROR = "error"
SSE_CONTENT_TYPE = "text/event-stream"


# ---- Pydantic Schemas ----


class ResearchRequest(BaseModel):
    """Request body for the research endpoint."""

    query: str

    @field_validator("query")
    @classmethod
    def query_must_not_be_empty(cls, v: str) -> str:
        """Validate that query is not empty or whitespace."""
        if not v.strip():
            msg = "Query must not be empty"
            raise ValueError(msg)
        return v


class StreamEvent(BaseModel):
    """A single SSE event payload."""

    type: str
    data: str
    filename: str | None = None


# ---- SSE Helpers ----


def _format_sse_event(event: StreamEvent) -> str:
    """Format a StreamEvent as an SSE data line."""
    return f"data: {event.model_dump_json()}\n\n"


def _extract_final_content(result: dict[str, Any]) -> str:
    """Extract the final text content from the agent result."""
    messages = result.get("messages", [])
    if messages:
        last_message = messages[-1]
        return str(getattr(last_message, "content", str(last_message)))
    return ""


# ---- Stream Generator ----


def _research_stream_generator(
    query: str,
    agent: CompiledStateGraph[Any, Any],
    settings: Settings,
) -> Generator[str, None, None]:
    """Generate SSE events from the research agent stream.

    Yields progress events during research, a result event with
    the final report, and saves the report to disk.
    """
    yield _format_sse_event(StreamEvent(type=EVENT_TYPE_PROGRESS, data="Starting research..."))

    try:
        final_content = ""
        for chunk in agent.stream({"messages": [HumanMessage(content=query)]}):
            final_content = _extract_final_content(chunk)

        if not final_content:
            final_content = "No results produced by the research agent."

        report_path = save_report(
            query=query,
            content=final_content,
            output_dir=settings.output_dir,
            models_used=[settings.orchestrator_model, settings.medical_model],
        )

        yield _format_sse_event(
            StreamEvent(
                type=EVENT_TYPE_RESULT,
                data=final_content,
                filename=report_path.name,
            )
        )

    except Exception as exc:
        logger.error("Research failed for query '%s': %s", query, exc)
        yield _format_sse_event(StreamEvent(type=EVENT_TYPE_ERROR, data=f"Research failed: {exc}"))


# ---- Router Factory ----


def create_research_router(
    settings: Settings,
    agent: CompiledStateGraph[Any, Any],
) -> APIRouter:
    """Create the research API router with the agent bound."""
    router = APIRouter()

    @router.post("/research")
    def start_research(request: ResearchRequest) -> StreamingResponse:
        """Start a research session, streaming SSE progress events."""
        logger.info("Research request received: %s", request.query)
        return StreamingResponse(
            _research_stream_generator(request.query, agent, settings),
            media_type=SSE_CONTENT_TYPE,
        )

    return router
