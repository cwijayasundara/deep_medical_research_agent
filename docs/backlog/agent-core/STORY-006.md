# STORY-006: Report Persistence Service

## Story
As a **user**, I want my research reports saved as markdown files, so that I can review past research sessions without re-running queries.

## Expertise
backend

## Story Points
2

## Dependencies
- STORY-001 (Settings with OUTPUT_DIR)

## Acceptance Criteria

### AC-1: Reports are saved with timestamp and topic slug
- **Given** a completed research report with query "Cancer immunotherapy advances"
- **When** the report is saved via `save_report(query, content)`
- **Then** a file is created at `{OUTPUT_DIR}/2026-02-08_cancer-immunotherapy-advances.md`
- **And** the filename uses the current date and a slugified query

### AC-2: Report files include metadata header
- **Given** a research report being saved
- **When** the file is written
- **Then** it includes a YAML front matter block with:
  - `query`: the original query
  - `timestamp`: ISO 8601 timestamp
  - `models_used`: list of models (e.g., ["qwen3:latest", "MedGemma1.0:4b"])
  - `sources_count`: number of sources consulted

### AC-3: Saved reports can be listed
- **Given** multiple saved reports in the output directory
- **When** `list_reports()` is called
- **Then** a list of report metadata is returned (filename, query, timestamp)
- **And** the list is sorted by timestamp descending (newest first)

### AC-4: A specific report can be retrieved
- **Given** a saved report with a known filename
- **When** `get_report(report_id)` is called
- **Then** the full report content is returned including metadata
- **And** a `ReportNotFoundError` is raised if the file does not exist

### AC-5: Output directory is created if it doesn't exist
- **Given** the configured `OUTPUT_DIR` does not exist
- **When** `save_report()` is called
- **Then** the directory is created automatically
- **And** the report is saved successfully

## Technical Notes
- Module: `src/services/report_service.py`
- Use `python-slugify` for generating filename slugs
- Define `MAX_SLUG_LENGTH = 80` constant
- Define `REPORT_DATE_FORMAT = "%Y-%m-%d"` constant
- YAML front matter parsing with a simple custom parser (avoid heavy deps)
