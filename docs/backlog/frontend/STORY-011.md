# STORY-011: Research Query Input and Streaming Results

## Story
As a **user**, I want to type a medical research question and see the agent's progress in real-time, so that I know the agent is working and can follow its research process.

## Expertise
frontend

## Story Points
5

## Dependencies
- STORY-008 (Research API with streaming)
- STORY-010 (React project setup)

## Acceptance Criteria

### AC-1: Research query input is functional
- **Given** the research page is loaded
- **When** the user types a query and clicks "Research" (or presses Enter)
- **Then** the query is sent to `POST /api/research`
- **And** the input is disabled while research is in progress
- **And** a "Stop" button appears to cancel the request

### AC-2: Streaming progress is displayed
- **Given** a research query has been submitted
- **When** SSE progress events arrive from the backend
- **Then** each progress step is displayed in a progress log area (e.g., "Planning research...", "Searching for papers...", "Analyzing with medical expert...")
- **And** a loading spinner or animation is shown

### AC-3: Final report is rendered as markdown
- **Given** the agent completes research and sends the result event
- **When** the result is received
- **Then** the markdown report is rendered with proper formatting (headings, lists, links, code blocks)
- **And** the progress log collapses or moves to a secondary position
- **And** the input is re-enabled

### AC-4: Errors are displayed to the user
- **Given** the agent encounters an error during research
- **When** an error event is received
- **Then** an error message is displayed in the UI (not a raw JSON dump)
- **And** the input is re-enabled so the user can try again

## Technical Notes
- Components: `ResearchInput.tsx`, `ProgressLog.tsx`, `ReportViewer.tsx`
- Use `EventSource` or `fetch` with `ReadableStream` for SSE consumption
- Use a markdown rendering library (e.g., `react-markdown`) for report display
- State management: React `useState` + `useReducer` (no Redux needed)
