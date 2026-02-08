"""FastAPI application with health check endpoint.

Provides the main application factory with CORS configuration,
settings validation, and an Ollama-aware health check.
"""

import logging
import sys

import httpx
from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config.settings import Settings, configure_logging, load_settings

logger = logging.getLogger(__name__)

# ---- Constants ----

FRONTEND_ORIGIN = "http://localhost:5173"
API_PREFIX = "/api"
STATUS_HEALTHY = "healthy"
STATUS_DEGRADED = "degraded"
MODEL_UNAVAILABLE = "unavailable"
OLLAMA_HEALTH_TIMEOUT_SECONDS = 5


def _check_ollama_connectivity(base_url: str) -> bool:
    """Check whether Ollama is reachable."""
    try:
        response = httpx.get(base_url, timeout=OLLAMA_HEALTH_TIMEOUT_SECONDS)
        return response.status_code == 200
    except httpx.HTTPError:
        return False


def _build_health_response(settings: Settings, ollama_available: bool) -> dict[str, object]:
    """Build the health check response payload."""
    if ollama_available:
        return {
            "status": STATUS_HEALTHY,
            "models": {
                "orchestrator": settings.orchestrator_model,
                "medical": settings.medical_model,
            },
        }
    return {
        "status": STATUS_DEGRADED,
        "models": {
            "orchestrator": MODEL_UNAVAILABLE,
            "medical": MODEL_UNAVAILABLE,
        },
    }


def _create_health_router(settings: Settings) -> APIRouter:
    """Create the health check API router."""
    router = APIRouter()

    @router.get("/health")
    def health_check() -> dict[str, object]:
        """Return application health status with model availability."""
        ollama_available = _check_ollama_connectivity(settings.ollama_base_url)
        return _build_health_response(settings, ollama_available)

    return router


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

    Loads settings, configures CORS and logging, and mounts
    the health check endpoint under /api.
    """
    settings = load_settings()
    if settings is None:
        logger.error("Failed to load settings. Ensure TAVILY_API_KEY is set. See .env.example.")
        sys.exit(1)

    configure_logging(settings)
    logger.info("Starting application with orchestrator=%s", settings.orchestrator_model)

    app = FastAPI(title="Deep Medical Research Agent")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[FRONTEND_ORIGIN],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    health_router = _create_health_router(settings)
    app.include_router(health_router, prefix=API_PREFIX)

    return app
