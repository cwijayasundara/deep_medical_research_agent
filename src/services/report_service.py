"""Report persistence service for saving and retrieving research reports.

Saves markdown reports with YAML front matter metadata, supports
listing and retrieving saved reports by filename.
"""

import logging
from datetime import UTC, datetime
from pathlib import Path

from slugify import slugify

logger = logging.getLogger(__name__)

# ---- Constants ----

MAX_SLUG_LENGTH = 80
REPORT_DATE_FORMAT = "%Y-%m-%d"
FRONT_MATTER_DELIMITER = "---"


class ReportNotFoundError(Exception):
    """Raised when a requested report file does not exist."""


def _now() -> datetime:
    """Return the current UTC datetime. Patchable for testing."""
    return datetime.now(tz=UTC)


def _build_filename(query: str, timestamp: datetime) -> str:
    """Build a report filename from the query and timestamp."""
    date_str = timestamp.strftime(REPORT_DATE_FORMAT)
    slug = slugify(query, max_length=MAX_SLUG_LENGTH)
    return f"{date_str}_{slug}.md"


def _build_front_matter(
    query: str,
    timestamp: datetime,
    models_used: list[str] | None = None,
    sources_count: int = 0,
) -> str:
    """Build YAML front matter string for a report."""
    lines = [
        FRONT_MATTER_DELIMITER,
        f"query: {query}",
        f"timestamp: {timestamp.isoformat()}",
    ]

    if models_used:
        lines.append("models_used:")
        for model in models_used:
            lines.append(f"  - {model}")
    else:
        lines.append("models_used: []")

    lines.append(f"sources_count: {sources_count}")
    lines.append(FRONT_MATTER_DELIMITER)

    return "\n".join(lines) + "\n"


def _parse_front_matter(text: str) -> dict[str, str]:
    """Parse simple YAML front matter from a report file."""
    result: dict[str, str] = {}

    if not text.startswith(f"{FRONT_MATTER_DELIMITER}\n"):
        return result

    # Find closing delimiter
    end_idx = text.index(f"\n{FRONT_MATTER_DELIMITER}\n", len(FRONT_MATTER_DELIMITER))
    front_matter_text = text[len(FRONT_MATTER_DELIMITER) + 1 : end_idx]

    for line in front_matter_text.split("\n"):
        line = line.strip()
        if ": " in line and not line.startswith("- "):
            key, value = line.split(": ", 1)
            result[key] = value

    return result


def save_report(
    query: str,
    content: str,
    output_dir: str,
    models_used: list[str] | None = None,
    sources_count: int = 0,
) -> Path:
    """Save a research report as a markdown file with YAML front matter.

    Creates the output directory if it doesn't exist. Returns the
    path to the saved file.
    """
    timestamp = _now()
    filename = _build_filename(query, timestamp)
    dir_path = Path(output_dir)
    dir_path.mkdir(parents=True, exist_ok=True)

    front_matter = _build_front_matter(
        query=query,
        timestamp=timestamp,
        models_used=models_used,
        sources_count=sources_count,
    )

    file_path = dir_path / filename
    file_path.write_text(front_matter + content)
    logger.info("Report saved: %s", file_path)

    return file_path


def list_reports(output_dir: str) -> list[dict[str, str]]:
    """List all saved reports with metadata, sorted newest first.

    Returns a list of dicts with filename, query, and timestamp.
    Only includes .md files with valid front matter.
    """
    dir_path = Path(output_dir)

    if not dir_path.exists():
        return []

    reports: list[dict[str, str]] = []
    for md_file in dir_path.glob("*.md"):
        try:
            text = md_file.read_text()
            metadata = _parse_front_matter(text)
            if metadata:
                reports.append(
                    {
                        "filename": md_file.name,
                        "query": metadata.get("query", ""),
                        "timestamp": metadata.get("timestamp", ""),
                    }
                )
        except Exception:
            logger.warning("Failed to parse report: %s", md_file.name)

    reports.sort(key=lambda r: r["timestamp"], reverse=True)
    return reports


def get_report(report_id: str, output_dir: str) -> str:
    """Retrieve a report's full content by filename.

    Raises ReportNotFoundError if the file does not exist.
    """
    file_path = Path(output_dir) / report_id

    if not file_path.exists():
        raise ReportNotFoundError(f"Report not found: {report_id}")

    return file_path.read_text()
