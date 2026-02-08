# STORY-012: Research History Sidebar

## Story
As a **user**, I want to see a list of my past research sessions in a sidebar, so that I can quickly revisit previous research without re-running queries.

## Expertise
frontend

## Story Points
3

## Dependencies
- STORY-009 (Reports API endpoints)
- STORY-010 (React project setup)

## Acceptance Criteria

### AC-1: Sidebar displays list of past reports
- **Given** the backend has 5 saved research reports
- **When** the frontend loads
- **Then** the sidebar shows a list of reports with query title and date
- **And** reports are sorted by date (newest first)

### AC-2: Clicking a report loads its content
- **Given** the sidebar is showing a list of reports
- **When** the user clicks on a report entry
- **Then** the full report content is fetched from `GET /api/reports/{id}`
- **And** it is rendered in the main content area as formatted markdown

### AC-3: Empty state is handled
- **Given** no saved research reports exist
- **When** the sidebar loads
- **Then** a message is shown: "No research history yet. Start by asking a question!"

### AC-4: New research appears in sidebar after completion
- **Given** the user just completed a research query
- **When** the report is saved and the result event is received
- **Then** the new report appears at the top of the sidebar list without a page refresh

## Technical Notes
- Component: `HistorySidebar.tsx`
- Fetch reports on mount via `GET /api/reports`
- Use `ReportViewer.tsx` (from STORY-011) to display selected reports
- Consider optimistic update for AC-4 (add to local state immediately)
