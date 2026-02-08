"""Unit tests for FastAPI application and health endpoint — STORY-007.

Tests cover:
- AC-1: FastAPI app initializes with CORS and settings
- AC-2: Health endpoint returns status with model info
- AC-3: Health endpoint handles Ollama unavailability (degraded)
- AC-4: Startup errors handled cleanly (missing TAVILY_API_KEY)
"""

from unittest.mock import patch

import pytest

from tests.conftest import make_mock_settings

# ---- AC-1: FastAPI app initializes with CORS and settings ----


@pytest.mark.unit
class TestAppInitialization:
    """AC-1: FastAPI app initializes with CORS and settings."""

    def test_app_is_fastapi_instance(self) -> None:
        """The app module exposes a FastAPI instance."""
        from src.api.app import create_app

        with (
            patch("src.api.app.load_settings", return_value=make_mock_settings()),
            patch("src.api.app.configure_logging"),
            patch("src.api.app.create_research_agent"),
        ):
            app = create_app()

        assert app is not None

    def test_cors_allows_frontend_origin(self) -> None:
        """CORS is configured to allow the frontend origin."""
        from src.api.app import FRONTEND_ORIGIN, create_app

        with (
            patch("src.api.app.load_settings", return_value=make_mock_settings()),
            patch("src.api.app.configure_logging"),
            patch("src.api.app.create_research_agent"),
        ):
            app = create_app()

        cors_found = False
        for middleware in app.user_middleware:
            if "CORSMiddleware" in str(middleware.cls):
                cors_found = True
                assert FRONTEND_ORIGIN in middleware.kwargs.get("allow_origins", [])
        assert cors_found, "CORSMiddleware not found on app"

    def test_frontend_origin_constant(self) -> None:
        """FRONTEND_ORIGIN constant is defined correctly."""
        from src.api.app import FRONTEND_ORIGIN

        assert FRONTEND_ORIGIN == "http://localhost:5173"


# ---- AC-2: Health endpoint returns status ----


@pytest.mark.unit
class TestHealthEndpoint:
    """AC-2: Health endpoint returns status with model info."""

    def test_health_returns_200(self) -> None:
        """GET /api/health returns 200 OK."""
        from fastapi.testclient import TestClient

        from src.api.app import create_app

        with (
            patch("src.api.app.load_settings", return_value=make_mock_settings()),
            patch("src.api.app.configure_logging"),
            patch("src.api.app.create_research_agent"),
            patch("src.api.app._check_ollama_connectivity", return_value=True),
        ):
            app = create_app()
            client = TestClient(app)
            response = client.get("/api/health")

        assert response.status_code == 200

    def test_health_returns_healthy_status(self) -> None:
        """Health response includes status: healthy when Ollama is available."""
        from fastapi.testclient import TestClient

        from src.api.app import create_app

        with (
            patch("src.api.app.load_settings", return_value=make_mock_settings()),
            patch("src.api.app.configure_logging"),
            patch("src.api.app.create_research_agent"),
            patch("src.api.app._check_ollama_connectivity", return_value=True),
        ):
            app = create_app()
            client = TestClient(app)
            data = client.get("/api/health").json()

        assert data["status"] == "healthy"

    def test_health_returns_model_info(self) -> None:
        """Health response includes model names."""
        from fastapi.testclient import TestClient

        from src.api.app import create_app

        with (
            patch("src.api.app.load_settings", return_value=make_mock_settings()),
            patch("src.api.app.configure_logging"),
            patch("src.api.app.create_research_agent"),
            patch("src.api.app._check_ollama_connectivity", return_value=True),
        ):
            app = create_app()
            client = TestClient(app)
            data = client.get("/api/health").json()

        assert data["models"]["orchestrator"] == "qwen3:latest"
        assert data["models"]["medical"] == "MedAIBase/MedGemma1.0:4b"

    def test_health_route_mounted_under_api_prefix(self) -> None:
        """Health endpoint is at /api/health, not /health."""
        from fastapi.testclient import TestClient

        from src.api.app import create_app

        with (
            patch("src.api.app.load_settings", return_value=make_mock_settings()),
            patch("src.api.app.configure_logging"),
            patch("src.api.app.create_research_agent"),
            patch("src.api.app._check_ollama_connectivity", return_value=True),
        ):
            app = create_app()
            client = TestClient(app)
            assert client.get("/api/health").status_code == 200
            assert client.get("/health").status_code == 404


# ---- AC-3: Degraded health when Ollama is unavailable ----


@pytest.mark.unit
class TestHealthDegradedMode:
    """AC-3: Health endpoint handles Ollama unavailability."""

    def test_returns_degraded_when_ollama_down(self) -> None:
        """Health returns degraded status when Ollama connectivity check fails."""
        from fastapi.testclient import TestClient

        from src.api.app import create_app

        with (
            patch("src.api.app.load_settings", return_value=make_mock_settings()),
            patch("src.api.app.configure_logging"),
            patch("src.api.app.create_research_agent"),
            patch("src.api.app._check_ollama_connectivity", return_value=False),
        ):
            app = create_app()
            client = TestClient(app)
            data = client.get("/api/health").json()

        assert data["status"] == "degraded"

    def test_degraded_returns_200_not_500(self) -> None:
        """Degraded health still returns 200 OK, not 500."""
        from fastapi.testclient import TestClient

        from src.api.app import create_app

        with (
            patch("src.api.app.load_settings", return_value=make_mock_settings()),
            patch("src.api.app.configure_logging"),
            patch("src.api.app.create_research_agent"),
            patch("src.api.app._check_ollama_connectivity", return_value=False),
        ):
            app = create_app()
            client = TestClient(app)
            response = client.get("/api/health")

        assert response.status_code == 200

    def test_degraded_shows_unavailable_models(self) -> None:
        """Degraded health shows models as unavailable."""
        from fastapi.testclient import TestClient

        from src.api.app import create_app

        with (
            patch("src.api.app.load_settings", return_value=make_mock_settings()),
            patch("src.api.app.configure_logging"),
            patch("src.api.app.create_research_agent"),
            patch("src.api.app._check_ollama_connectivity", return_value=False),
        ):
            app = create_app()
            client = TestClient(app)
            data = client.get("/api/health").json()

        assert data["models"]["orchestrator"] == "unavailable"
        assert data["models"]["medical"] == "unavailable"


# ---- AC-4: Startup errors handled cleanly ----


@pytest.mark.unit
class TestStartupErrorHandling:
    """AC-4: Startup errors are handled cleanly."""

    def test_create_app_raises_on_missing_settings(self) -> None:
        """create_app raises SystemExit when settings cannot be loaded."""
        from src.api.app import create_app

        with (
            patch("src.api.app.load_settings", return_value=None),
            pytest.raises(SystemExit),
        ):
            create_app()

    def test_create_app_logs_error_on_missing_settings(
        self,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """create_app logs an error when settings fail to load."""
        import logging

        from src.api.app import create_app

        with (
            patch("src.api.app.load_settings", return_value=None),
            caplog.at_level(logging.ERROR),
            pytest.raises(SystemExit),
        ):
            create_app()

        assert any(record.levelno == logging.ERROR for record in caplog.records)


# ---- Constants ----


@pytest.mark.unit
class TestAppConstants:
    """Verify application constants."""

    def test_api_prefix_defined(self) -> None:
        """API_PREFIX constant is defined."""
        from src.api.app import API_PREFIX

        assert API_PREFIX == "/api"

    def test_status_healthy_constant(self) -> None:
        """STATUS_HEALTHY constant is defined."""
        from src.api.app import STATUS_HEALTHY

        assert STATUS_HEALTHY == "healthy"

    def test_status_degraded_constant(self) -> None:
        """STATUS_DEGRADED constant is defined."""
        from src.api.app import STATUS_DEGRADED

        assert STATUS_DEGRADED == "degraded"

    def test_model_unavailable_constant(self) -> None:
        """MODEL_UNAVAILABLE constant is defined."""
        from src.api.app import MODEL_UNAVAILABLE

        assert MODEL_UNAVAILABLE == "unavailable"
