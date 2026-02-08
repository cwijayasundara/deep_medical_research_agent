# STORY-008: Research API Endpoint with Streaming

## Story
As a **frontend developer**, I want a `POST /api/research` endpoint that streams research progress, so that the UI can show real-time updates as the agent works.

## Expertise
backend

## Story Points
5

## Dependencies
- STORY-005 (Research agent assembly)
- STORY-006 (Report persistence)
- STORY-007 (FastAPI application)

## Acceptance Criteria

### AC-1: Research endpoint accepts a query and streams progress
- **Given** a valid research query in the request body `{"query": "CRISPR gene therapy advances"}`
- **When** `POST /api/research` is called
- **Then** the response is a `text/event-stream` (Server-Sent Events)
- **And** events are streamed as the agent progresses: planning, searching, analyzing, synthesizing

### AC-2: Stream events have a consistent format
- **Given** a streaming research session
- **When** events are emitted
- **Then** each event has the format: `{"type": "progress|result|error", "data": "..."}`
- **And** progress events include the current step description
- **And** the final result event contains the complete markdown report

### AC-3: Report is automatically saved after completion
- **Given** the agent completes a research session
- **When** the final result is produced
- **Then** the report is saved via the report persistence service
- **And** the saved report's filename is included in the final event

### AC-4: Invalid requests return proper error responses
- **Given** an empty or missing query in the request body
- **When** `POST /api/research` is called
- **Then** a `422 Unprocessable Entity` response is returned with validation details
- **And** the error follows RFC 7807 problem detail format

### AC-5: Agent errors are streamed as error events
- **Given** the agent encounters an unrecoverable error during research
- **When** the error occurs
- **Then** an error event is streamed: `{"type": "error", "data": "Research failed: ..."}`
- **And** the stream is closed gracefully
- **And** the error is logged at ERROR level

## Technical Notes
- Module: `src/api/routes/research.py`
- Use `StreamingResponse` with `text/event-stream` media type
- Pydantic schema: `ResearchRequest(query: str)` and `StreamEvent(type: str, data: str)`
- Use async generator to yield SSE events from the agent's LangGraph stream
