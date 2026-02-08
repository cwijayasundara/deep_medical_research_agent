"""Unit tests for reports API endpoints — STORY-009.

Tests cover:
- AC-1: List reports endpoint returns all saved reports
- AC-2: Get report endpoint returns full report content
- AC-3: Missing report returns 404
- AC-4: Empty reports directory returns empty list
"""

from unittest.mock import patch

import pytest

from tests.conftest import TEST_OUTPUT_DIR, make_mock_settings


def _create_reports_app():
    """Create a test app with the reports router mounted."""
    from fastapi import FastAPI

    from src.api.routes.reports import create_reports_router

    settings = make_mock_settings()
    app = FastAPI()
    router = create_reports_router(settings=settings)
    app.include_router(router, prefix="/api")
    return app


# ---- AC-1: List reports endpoint returns all saved reports ----


@pytest.mark.unit
class TestListReportsEndpoint:
    """AC-1: List reports endpoint returns all saved reports."""

    def test_get_reports_returns_200(self) -> None:
        """GET /api/reports returns 200 OK."""
        from fastapi.testclient import TestClient

        app = _create_reports_app()
        client = TestClient(app)

        with patch("src.api.routes.reports.list_reports", return_value=[]):
            response = client.get("/api/reports")

        assert response.status_code == 200

    def test_get_reports_returns_json_array(self) -> None:
        """GET /api/reports returns a JSON array."""
        from fastapi.testclient import TestClient

        mock_reports = [
            {
                "filename": "2026-02-08_crispr-advances.md",
                "query": "CRISPR advances",
                "timestamp": "2026-02-08T14:30:00+00:00",
            },
            {
                "filename": "2026-02-07_cancer-immunotherapy.md",
                "query": "cancer immunotherapy",
                "timestamp": "2026-02-07T10:00:00+00:00",
            },
        ]

        app = _create_reports_app()
        client = TestClient(app)

        with patch("src.api.routes.reports.list_reports", return_value=mock_reports):
            response = client.get("/api/reports")

        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2

    def test_reports_contain_required_metadata(self) -> None:
        """Each report in the list has id, query, and timestamp fields."""
        from fastapi.testclient import TestClient

        mock_reports = [
            {
                "filename": "2026-02-08_crispr-advances.md",
                "query": "CRISPR advances",
                "timestamp": "2026-02-08T14:30:00+00:00",
            },
        ]

        app = _create_reports_app()
        client = TestClient(app)

        with patch("src.api.routes.reports.list_reports", return_value=mock_reports):
            response = client.get("/api/reports")

        report = response.json()[0]
        assert "id" in report
        assert "query" in report
        assert "timestamp" in report

    def test_report_id_is_filename_without_extension(self) -> None:
        """Report id is the filename stem (without .md extension)."""
        from fastapi.testclient import TestClient

        mock_reports = [
            {
                "filename": "2026-02-08_crispr-advances.md",
                "query": "CRISPR advances",
                "timestamp": "2026-02-08T14:30:00+00:00",
            },
        ]

        app = _create_reports_app()
        client = TestClient(app)

        with patch("src.api.routes.reports.list_reports", return_value=mock_reports):
            response = client.get("/api/reports")

        report = response.json()[0]
        assert report["id"] == "2026-02-08_crispr-advances"

    def test_reports_sorted_newest_first(self) -> None:
        """Reports are sorted by timestamp descending (newest first)."""
        from fastapi.testclient import TestClient

        mock_reports = [
            {
                "filename": "2026-02-08_newer-report.md",
                "query": "newer report",
                "timestamp": "2026-02-08T14:30:00+00:00",
            },
            {
                "filename": "2026-02-07_older-report.md",
                "query": "older report",
                "timestamp": "2026-02-07T10:00:00+00:00",
            },
            {
                "filename": "2026-02-06_oldest-report.md",
                "query": "oldest report",
                "timestamp": "2026-02-06T08:00:00+00:00",
            },
        ]

        app = _create_reports_app()
        client = TestClient(app)

        with patch("src.api.routes.reports.list_reports", return_value=mock_reports):
            response = client.get("/api/reports")

        data = response.json()
        timestamps = [r["timestamp"] for r in data]
        assert timestamps == sorted(timestamps, reverse=True)

    def test_list_reports_calls_service_with_output_dir(self) -> None:
        """list_reports is called with the settings output_dir."""
        from fastapi.testclient import TestClient

        app = _create_reports_app()
        client = TestClient(app)

        with patch("src.api.routes.reports.list_reports", return_value=[]) as mock_list:
            client.get("/api/reports")

        mock_list.assert_called_once_with(TEST_OUTPUT_DIR)


# ---- AC-2: Get report endpoint returns full report content ----


@pytest.mark.unit
class TestGetReportEndpoint:
    """AC-2: Get report endpoint returns full report content."""

    def test_get_report_returns_200(self) -> None:
        """GET /api/reports/{report_id} returns 200 OK."""
        from fastapi.testclient import TestClient

        report_content = "---\nquery: cancer\ntimestamp: 2026-02-08T14:30:00+00:00\n---\n# Report"

        app = _create_reports_app()
        client = TestClient(app)

        with patch("src.api.routes.reports.get_report", return_value=report_content):
            response = client.get("/api/reports/2026-02-08_cancer-immunotherapy-advances")

        assert response.status_code == 200

    def test_get_report_returns_json_with_content(self) -> None:
        """Response is JSON with a 'content' field containing the markdown body."""
        from fastapi.testclient import TestClient

        report_content = (
            "---\nquery: cancer immunotherapy\ntimestamp: 2026-02-08T14:30:00+00:00\n---\n"
            "# Cancer Report\n\nFindings here."
        )

        app = _create_reports_app()
        client = TestClient(app)

        with patch("src.api.routes.reports.get_report", return_value=report_content):
            response = client.get("/api/reports/2026-02-08_cancer-immunotherapy-advances")

        data = response.json()
        assert "content" in data
        assert "Cancer Report" in data["content"]

    def test_get_report_returns_metadata(self) -> None:
        """Response includes id, query, and timestamp metadata."""
        from fastapi.testclient import TestClient

        report_content = (
            "---\nquery: cancer immunotherapy\ntimestamp: 2026-02-08T14:30:00+00:00\n---\n"
            "# Report content"
        )

        app = _create_reports_app()
        client = TestClient(app)

        with patch("src.api.routes.reports.get_report", return_value=report_content):
            response = client.get("/api/reports/2026-02-08_cancer-immunotherapy-advances")

        data = response.json()
        assert data["id"] == "2026-02-08_cancer-immunotherapy-advances"
        assert data["query"] == "cancer immunotherapy"
        assert data["timestamp"] == "2026-02-08T14:30:00+00:00"

    def test_get_report_calls_service_with_filename(self) -> None:
        """get_report is called with the report_id + .md extension."""
        from fastapi.testclient import TestClient

        report_content = "---\nquery: test\ntimestamp: 2026-02-08T14:30:00+00:00\n---\nContent"

        app = _create_reports_app()
        client = TestClient(app)

        with patch("src.api.routes.reports.get_report", return_value=report_content) as mock_get:
            client.get("/api/reports/2026-02-08_test")

        mock_get.assert_called_once_with("2026-02-08_test.md", TEST_OUTPUT_DIR)


# ---- AC-3: Missing report returns 404 ----


@pytest.mark.unit
class TestMissingReport:
    """AC-3: Missing report returns 404."""

    def test_missing_report_returns_404(self) -> None:
        """GET /api/reports/{nonexistent_id} returns 404."""
        from fastapi.testclient import TestClient

        from src.services.report_service import ReportNotFoundError

        app = _create_reports_app()
        client = TestClient(app)

        with patch(
            "src.api.routes.reports.get_report",
            side_effect=ReportNotFoundError("Report not found: nonexistent-report.md"),
        ):
            response = client.get("/api/reports/nonexistent-report")

        assert response.status_code == 404

    def test_missing_report_error_has_detail(self) -> None:
        """404 response includes an error detail message."""
        from fastapi.testclient import TestClient

        from src.services.report_service import ReportNotFoundError

        app = _create_reports_app()
        client = TestClient(app)

        with patch(
            "src.api.routes.reports.get_report",
            side_effect=ReportNotFoundError("Report not found: nonexistent-report.md"),
        ):
            response = client.get("/api/reports/nonexistent-report")

        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()


# ---- AC-4: Empty reports directory returns empty list ----


@pytest.mark.unit
class TestEmptyReportsDirectory:
    """AC-4: Empty reports directory returns empty list."""

    def test_empty_directory_returns_200(self) -> None:
        """GET /api/reports with no reports returns 200."""
        from fastapi.testclient import TestClient

        app = _create_reports_app()
        client = TestClient(app)

        with patch("src.api.routes.reports.list_reports", return_value=[]):
            response = client.get("/api/reports")

        assert response.status_code == 200

    def test_empty_directory_returns_empty_array(self) -> None:
        """GET /api/reports with no reports returns []."""
        from fastapi.testclient import TestClient

        app = _create_reports_app()
        client = TestClient(app)

        with patch("src.api.routes.reports.list_reports", return_value=[]):
            response = client.get("/api/reports")

        assert response.json() == []


# ---- Pydantic schemas ----


@pytest.mark.unit
class TestReportsSchemas:
    """Verify Pydantic schemas for reports API."""

    def test_report_summary_schema_exists(self) -> None:
        """ReportSummary Pydantic model is defined."""
        from src.api.routes.reports import ReportSummary

        summary = ReportSummary(
            id="2026-02-08_test",
            query="test query",
            timestamp="2026-02-08T14:30:00+00:00",
        )
        assert summary.id == "2026-02-08_test"
        assert summary.query == "test query"

    def test_report_detail_schema_exists(self) -> None:
        """ReportDetail Pydantic model is defined."""
        from src.api.routes.reports import ReportDetail

        detail = ReportDetail(
            id="2026-02-08_test",
            query="test query",
            timestamp="2026-02-08T14:30:00+00:00",
            content="# Report\n\nContent here.",
        )
        assert detail.id == "2026-02-08_test"
        assert detail.content == "# Report\n\nContent here."

    def test_report_detail_has_optional_models_used(self) -> None:
        """ReportDetail includes optional models_used field."""
        from src.api.routes.reports import ReportDetail

        detail = ReportDetail(
            id="2026-02-08_test",
            query="test",
            timestamp="2026-02-08T14:30:00+00:00",
            content="content",
            models_used=["qwen3:latest", "MedGemma1.0:4b"],
        )
        assert detail.models_used == ["qwen3:latest", "MedGemma1.0:4b"]
