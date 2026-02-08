# STORY-009: Reports API Endpoints

## Story
As a **user**, I want API endpoints to list and retrieve my saved research reports, so that the frontend can display my research history.

## Expertise
backend

## Story Points
2

## Dependencies
- STORY-006 (Report persistence service)
- STORY-007 (FastAPI application)

## Acceptance Criteria

### AC-1: List reports endpoint returns all saved reports
- **Given** 3 saved research reports in the output directory
- **When** `GET /api/reports` is called
- **Then** a JSON array is returned with metadata for each report (id, query, timestamp, filename)
- **And** reports are sorted by timestamp descending (newest first)

### AC-2: Get report endpoint returns full report content
- **Given** a saved report with id "2026-02-08_cancer-immunotherapy-advances"
- **When** `GET /api/reports/2026-02-08_cancer-immunotherapy-advances` is called
- **Then** the full report is returned with metadata and content
- **And** content type is JSON with the markdown body in a `content` field

### AC-3: Missing report returns 404
- **Given** no report with id "nonexistent-report"
- **When** `GET /api/reports/nonexistent-report` is called
- **Then** a `404 Not Found` response is returned
- **And** the error follows RFC 7807 format

### AC-4: Empty reports directory returns empty list
- **Given** no saved reports in the output directory
- **When** `GET /api/reports` is called
- **Then** an empty JSON array `[]` is returned with `200 OK`

## Technical Notes
- Module: `src/api/routes/reports.py`
- Pydantic schemas: `ReportSummary(id, query, timestamp)` and `ReportDetail(id, query, timestamp, content, models_used)`
- Reuse `ReportService` from STORY-006
