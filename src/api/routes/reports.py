"""Reports API endpoints for listing and retrieving saved research reports.

Provides GET /reports and GET /reports/{report_id} endpoints
backed by the report persistence service.
"""

import logging
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.config.settings import Settings
from src.services.report_service import (
    FRONT_MATTER_DELIMITER,
    ReportNotFoundError,
    get_report,
    list_reports,
)
from src.services.report_service import _parse_front_matter as parse_front_matter

logger = logging.getLogger(__name__)

# ---- Constants ----

REPORT_FILE_EXTENSION = ".md"
HTTP_404_NOT_FOUND = 404


# ---- Pydantic Schemas ----


class ReportSummary(BaseModel):
    """Summary metadata for a report in the list view."""

    id: str
    query: str
    timestamp: str


class ReportDetail(BaseModel):
    """Full report with metadata and content."""

    id: str
    query: str
    timestamp: str
    content: str
    models_used: list[str] | None = None


# ---- Helpers ----


def _filename_to_id(filename: str) -> str:
    """Convert a report filename to its ID (stem without extension)."""
    return Path(filename).stem


def _id_to_filename(report_id: str) -> str:
    """Convert a report ID to its filename (with .md extension)."""
    return f"{report_id}{REPORT_FILE_EXTENSION}"


def _extract_body(raw_text: str) -> str:
    """Extract the markdown body from a report, stripping front matter."""
    if not raw_text.startswith(f"{FRONT_MATTER_DELIMITER}\n"):
        return raw_text

    try:
        end_idx = raw_text.index(f"\n{FRONT_MATTER_DELIMITER}\n", len(FRONT_MATTER_DELIMITER))
        return raw_text[end_idx + len(FRONT_MATTER_DELIMITER) + 2 :]
    except ValueError:
        return raw_text


# ---- Router Factory ----


def create_reports_router(settings: Settings) -> APIRouter:
    """Create the reports API router."""
    router = APIRouter()

    @router.get("/reports", response_model=list[ReportSummary])
    def list_all_reports() -> list[ReportSummary]:
        """List all saved research reports with metadata."""
        logger.info("Listing reports from %s", settings.output_dir)
        raw_reports = list_reports(settings.output_dir)
        return [
            ReportSummary(
                id=_filename_to_id(r["filename"]),
                query=r["query"],
                timestamp=r["timestamp"],
            )
            for r in raw_reports
        ]

    @router.get("/reports/{report_id}", response_model=ReportDetail)
    def get_report_by_id(report_id: str) -> ReportDetail:
        """Retrieve a full report by its ID."""
        logger.info("Retrieving report: %s", report_id)
        filename = _id_to_filename(report_id)

        try:
            raw_content = get_report(filename, settings.output_dir)
        except ReportNotFoundError:
            logger.warning("Report not found: %s", report_id)
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND,
                detail=f"Report not found: {report_id}",
            ) from None

        metadata = parse_front_matter(raw_content)
        body = _extract_body(raw_content)

        return ReportDetail(
            id=report_id,
            query=metadata.get("query", ""),
            timestamp=metadata.get("timestamp", ""),
            content=body,
            models_used=None,
        )

    return router
