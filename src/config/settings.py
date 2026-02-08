"""Application settings loaded from environment variables.

Uses pydantic-settings BaseSettings to validate and load configuration.
All secrets come from environment variables or .env files — never hardcoded.
"""

import logging

from pydantic import ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)

# ---- Default Values ----

DEFAULT_OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_OUTPUT_DIR = "output"
DEFAULT_LOG_LEVEL = "INFO"
DEFAULT_ORCHESTRATOR_MODEL = "qwen3:latest"
DEFAULT_MEDICAL_MODEL = "MedAIBase/MedGemma1.0:4b"
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Required
    tavily_api_key: str

    # Optional with defaults
    ollama_base_url: str = DEFAULT_OLLAMA_BASE_URL
    output_dir: str = DEFAULT_OUTPUT_DIR
    log_level: str = DEFAULT_LOG_LEVEL
    orchestrator_model: str = DEFAULT_ORCHESTRATOR_MODEL
    medical_model: str = DEFAULT_MEDICAL_MODEL


def load_settings() -> Settings | None:
    """Load settings, returning None if validation fails.

    Logs a clear, actionable error message instead of letting
    raw Pydantic tracebacks reach the user.
    """
    try:
        return Settings()  # type: ignore[call-arg]
    except ValidationError as exc:
        logger.error(
            "Configuration error: %s. "
            "Ensure required environment variables are set. See .env.example.",
            exc,
        )
        return None


def configure_logging(settings: Settings) -> None:
    """Configure logging based on settings.log_level."""
    level = getattr(logging, settings.log_level.upper(), logging.INFO)
    logging.basicConfig(level=level, format=LOG_FORMAT, force=True)
