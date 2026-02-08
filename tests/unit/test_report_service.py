"""Unit tests for report persistence service — STORY-006.

Tests cover:
- AC-1: Reports saved with timestamp and topic slug
- AC-2: Report files include YAML front matter metadata
- AC-3: Saved reports can be listed (sorted newest first)
- AC-4: A specific report can be retrieved (with ReportNotFoundError)
- AC-5: Output directory is created if it doesn't exist
"""

from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import patch

import pytest

# ---- AC-1: Reports saved with timestamp and topic slug ----


@pytest.mark.unit
class TestSaveReport:
    """AC-1: Reports are saved with timestamp and topic slug."""

    def test_creates_file_with_date_and_slug(self, tmp_path: Path) -> None:
        """save_report creates a file named {date}_{slug}.md."""
        from src.services.report_service import save_report

        fake_now = datetime(2026, 2, 8, 14, 30, 0, tzinfo=UTC)
        with patch("src.services.report_service._now", return_value=fake_now):
            path = save_report(
                query="Cancer immunotherapy advances",
                content="# Report\nSome content",
                output_dir=str(tmp_path),
            )

        assert path.name == "2026-02-08_cancer-immunotherapy-advances.md"
        assert path.exists()

    def test_slugifies_complex_query(self, tmp_path: Path) -> None:
        """Queries with special characters are slugified properly."""
        from src.services.report_service import save_report

        fake_now = datetime(2026, 1, 15, 10, 0, 0, tzinfo=UTC)
        with patch("src.services.report_service._now", return_value=fake_now):
            path = save_report(
                query="What are the effects of COVID-19 on the heart?",
                content="# Report",
                output_dir=str(tmp_path),
            )

        assert "what-are-the-effects-of-covid-19-on-the-heart" in path.name
        assert path.name.startswith("2026-01-15_")

    def test_truncates_long_slugs(self, tmp_path: Path) -> None:
        """Slugs longer than MAX_SLUG_LENGTH are truncated."""
        from src.services.report_service import MAX_SLUG_LENGTH, save_report

        long_query = "a " * 100  # Very long query
        fake_now = datetime(2026, 3, 1, 0, 0, 0, tzinfo=UTC)
        with patch("src.services.report_service._now", return_value=fake_now):
            path = save_report(
                query=long_query,
                content="# Report",
                output_dir=str(tmp_path),
            )

        # Slug portion (after date and underscore) should not exceed MAX_SLUG_LENGTH
        slug_part = path.stem.split("_", 1)[1]
        assert len(slug_part) <= MAX_SLUG_LENGTH

    def test_returns_path_object(self, tmp_path: Path) -> None:
        """save_report returns a Path to the created file."""
        from src.services.report_service import save_report

        fake_now = datetime(2026, 2, 8, 0, 0, 0, tzinfo=UTC)
        with patch("src.services.report_service._now", return_value=fake_now):
            path = save_report(
                query="test query",
                content="# Report",
                output_dir=str(tmp_path),
            )

        assert isinstance(path, Path)

    def test_file_content_includes_report_body(self, tmp_path: Path) -> None:
        """The saved file contains the report content."""
        from src.services.report_service import save_report

        content = "# My Report\n\nDetailed analysis here."
        fake_now = datetime(2026, 2, 8, 0, 0, 0, tzinfo=UTC)
        with patch("src.services.report_service._now", return_value=fake_now):
            path = save_report(
                query="test query",
                content=content,
                output_dir=str(tmp_path),
            )

        file_text = path.read_text()
        assert "Detailed analysis here." in file_text


# ---- AC-2: Report files include metadata header ----


@pytest.mark.unit
class TestReportMetadataHeader:
    """AC-2: Report files include YAML front matter metadata."""

    def test_includes_yaml_front_matter(self, tmp_path: Path) -> None:
        """Saved report starts with YAML front matter delimiters."""
        from src.services.report_service import save_report

        fake_now = datetime(2026, 2, 8, 14, 30, 0, tzinfo=UTC)
        with patch("src.services.report_service._now", return_value=fake_now):
            path = save_report(
                query="test query",
                content="# Report",
                output_dir=str(tmp_path),
            )

        text = path.read_text()
        assert text.startswith("---\n")
        assert "\n---\n" in text[3:]  # closing delimiter

    def test_front_matter_contains_query(self, tmp_path: Path) -> None:
        """Front matter includes the original query."""
        from src.services.report_service import save_report

        fake_now = datetime(2026, 2, 8, 14, 30, 0, tzinfo=UTC)
        with patch("src.services.report_service._now", return_value=fake_now):
            path = save_report(
                query="Cancer immunotherapy advances",
                content="# Report",
                output_dir=str(tmp_path),
            )

        text = path.read_text()
        assert "query: Cancer immunotherapy advances" in text

    def test_front_matter_contains_iso_timestamp(self, tmp_path: Path) -> None:
        """Front matter includes an ISO 8601 timestamp."""
        from src.services.report_service import save_report

        fake_now = datetime(2026, 2, 8, 14, 30, 0, tzinfo=UTC)
        with patch("src.services.report_service._now", return_value=fake_now):
            path = save_report(
                query="test",
                content="# Report",
                output_dir=str(tmp_path),
            )

        text = path.read_text()
        assert "timestamp: 2026-02-08T14:30:00" in text

    def test_front_matter_contains_models_used(self, tmp_path: Path) -> None:
        """Front matter includes the models_used list."""
        from src.services.report_service import save_report

        fake_now = datetime(2026, 2, 8, 0, 0, 0, tzinfo=UTC)
        with patch("src.services.report_service._now", return_value=fake_now):
            path = save_report(
                query="test",
                content="# Report",
                output_dir=str(tmp_path),
                models_used=["qwen3:latest", "MedGemma1.0:4b"],
            )

        text = path.read_text()
        assert "models_used:" in text
        assert "qwen3:latest" in text
        assert "MedGemma1.0:4b" in text

    def test_front_matter_contains_sources_count(self, tmp_path: Path) -> None:
        """Front matter includes the sources_count."""
        from src.services.report_service import save_report

        fake_now = datetime(2026, 2, 8, 0, 0, 0, tzinfo=UTC)
        with patch("src.services.report_service._now", return_value=fake_now):
            path = save_report(
                query="test",
                content="# Report",
                output_dir=str(tmp_path),
                sources_count=5,
            )

        text = path.read_text()
        assert "sources_count: 5" in text


# ---- AC-3: Saved reports can be listed ----


@pytest.mark.unit
class TestListReports:
    """AC-3: Saved reports can be listed."""

    def test_returns_list_of_report_metadata(self, tmp_path: Path) -> None:
        """list_reports returns a list of metadata dicts."""
        from src.services.report_service import list_reports, save_report

        fake_now = datetime(2026, 2, 8, 10, 0, 0, tzinfo=UTC)
        with patch("src.services.report_service._now", return_value=fake_now):
            save_report(query="test query", content="# Report", output_dir=str(tmp_path))

        reports = list_reports(output_dir=str(tmp_path))

        assert len(reports) == 1
        assert "filename" in reports[0]
        assert "query" in reports[0]
        assert "timestamp" in reports[0]

    def test_sorted_newest_first(self, tmp_path: Path) -> None:
        """Reports are sorted by timestamp descending (newest first)."""
        from src.services.report_service import list_reports, save_report

        with patch(
            "src.services.report_service._now",
            return_value=datetime(2026, 1, 1, 0, 0, 0, tzinfo=UTC),
        ):
            save_report(query="older query", content="# Old", output_dir=str(tmp_path))

        with patch(
            "src.services.report_service._now",
            return_value=datetime(2026, 2, 15, 0, 0, 0, tzinfo=UTC),
        ):
            save_report(query="newer query", content="# New", output_dir=str(tmp_path))

        reports = list_reports(output_dir=str(tmp_path))

        assert len(reports) == 2
        assert reports[0]["query"] == "newer query"
        assert reports[1]["query"] == "older query"

    def test_returns_empty_list_when_no_reports(self, tmp_path: Path) -> None:
        """list_reports returns an empty list when no reports exist."""
        from src.services.report_service import list_reports

        reports = list_reports(output_dir=str(tmp_path))

        assert reports == []

    def test_ignores_non_markdown_files(self, tmp_path: Path) -> None:
        """list_reports only includes .md files."""
        from src.services.report_service import list_reports, save_report

        fake_now = datetime(2026, 2, 8, 0, 0, 0, tzinfo=UTC)
        with patch("src.services.report_service._now", return_value=fake_now):
            save_report(query="test", content="# Report", output_dir=str(tmp_path))

        # Create a non-markdown file
        (tmp_path / "notes.txt").write_text("not a report")

        reports = list_reports(output_dir=str(tmp_path))

        assert len(reports) == 1


# ---- AC-4: A specific report can be retrieved ----


@pytest.mark.unit
class TestGetReport:
    """AC-4: A specific report can be retrieved."""

    def test_returns_full_report_content(self, tmp_path: Path) -> None:
        """get_report returns the full file content."""
        from src.services.report_service import get_report, save_report

        fake_now = datetime(2026, 2, 8, 0, 0, 0, tzinfo=UTC)
        with patch("src.services.report_service._now", return_value=fake_now):
            path = save_report(
                query="test query",
                content="# Detailed Report\n\nBody here.",
                output_dir=str(tmp_path),
            )

        result = get_report(report_id=path.name, output_dir=str(tmp_path))

        assert "Detailed Report" in result
        assert "Body here." in result

    def test_raises_report_not_found_error(self, tmp_path: Path) -> None:
        """get_report raises ReportNotFoundError for missing files."""
        from src.services.report_service import ReportNotFoundError, get_report

        with pytest.raises(ReportNotFoundError):
            get_report(report_id="nonexistent.md", output_dir=str(tmp_path))

    def test_returned_content_includes_metadata(self, tmp_path: Path) -> None:
        """get_report includes the YAML front matter in the returned content."""
        from src.services.report_service import get_report, save_report

        fake_now = datetime(2026, 2, 8, 14, 0, 0, tzinfo=UTC)
        with patch("src.services.report_service._now", return_value=fake_now):
            path = save_report(
                query="metadata test",
                content="# Report",
                output_dir=str(tmp_path),
            )

        result = get_report(report_id=path.name, output_dir=str(tmp_path))

        assert "query: metadata test" in result


# ---- AC-5: Output directory created if missing ----


@pytest.mark.unit
class TestOutputDirectoryCreation:
    """AC-5: Output directory is created if it doesn't exist."""

    def test_creates_output_dir_when_missing(self, tmp_path: Path) -> None:
        """save_report creates the output directory if it doesn't exist."""
        from src.services.report_service import save_report

        new_dir = tmp_path / "reports" / "nested"
        assert not new_dir.exists()

        fake_now = datetime(2026, 2, 8, 0, 0, 0, tzinfo=UTC)
        with patch("src.services.report_service._now", return_value=fake_now):
            path = save_report(
                query="test",
                content="# Report",
                output_dir=str(new_dir),
            )

        assert new_dir.exists()
        assert path.exists()

    def test_works_when_dir_already_exists(self, tmp_path: Path) -> None:
        """save_report works normally when the output dir already exists."""
        from src.services.report_service import save_report

        fake_now = datetime(2026, 2, 8, 0, 0, 0, tzinfo=UTC)
        with patch("src.services.report_service._now", return_value=fake_now):
            path = save_report(
                query="test",
                content="# Report",
                output_dir=str(tmp_path),
            )

        assert path.exists()


# ---- Constants ----


@pytest.mark.unit
class TestReportServiceConstants:
    """Verify important constants are defined."""

    def test_max_slug_length_is_80(self) -> None:
        """MAX_SLUG_LENGTH is defined as 80."""
        from src.services.report_service import MAX_SLUG_LENGTH

        assert MAX_SLUG_LENGTH == 80

    def test_report_date_format_defined(self) -> None:
        """REPORT_DATE_FORMAT is defined."""
        from src.services.report_service import REPORT_DATE_FORMAT

        assert REPORT_DATE_FORMAT == "%Y-%m-%d"
