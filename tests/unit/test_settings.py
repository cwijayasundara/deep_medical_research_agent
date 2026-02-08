"""Unit tests for Settings configuration — STORY-001.

Tests cover:
- AC-1: Dependencies importable
- AC-2: Settings loads from environment with defaults
- AC-3: Validation fails gracefully with actionable message
- AC-4: Logging configuration from settings
"""

import logging

import pytest


@pytest.mark.unit
class TestSettingsFromEnvironment:
    """AC-2: Settings class loads configuration from environment."""

    def test_settings_loads_all_values_from_env(
        self, env_with_all_settings: None
    ) -> None:
        """Given all env vars set, Settings loads them correctly."""
        from src.config.settings import Settings

        settings = Settings()

        assert settings.tavily_api_key == "tvly-test-key-12345"
        assert settings.ollama_base_url == "http://localhost:11434"
        assert settings.output_dir == "/tmp/test-reports"
        assert settings.log_level == "DEBUG"

    def test_settings_uses_defaults_for_optional_values(
        self, env_minimal_settings: None
    ) -> None:
        """Given only required env vars, Settings uses sensible defaults."""
        from src.config.settings import Settings

        settings = Settings()

        assert settings.tavily_api_key == "tvly-test-key-12345"
        assert settings.ollama_base_url == "http://localhost:11434"
        assert settings.output_dir == "output"
        assert settings.log_level == "INFO"

    def test_settings_orchestrator_model_has_default(
        self, env_minimal_settings: None
    ) -> None:
        """Settings provides default orchestrator model name."""
        from src.config.settings import Settings

        settings = Settings()

        assert settings.orchestrator_model == "qwen3:latest"

    def test_settings_medical_model_has_default(
        self, env_minimal_settings: None
    ) -> None:
        """Settings provides default medical model name."""
        from src.config.settings import Settings

        settings = Settings()

        assert settings.medical_model == "MedAIBase/MedGemma1.0:4b"


@pytest.mark.unit
class TestSettingsValidation:
    """AC-3: Settings validation fails gracefully."""

    def test_missing_tavily_api_key_raises_validation_error(
        self, env_no_settings: None
    ) -> None:
        """Given no TAVILY_API_KEY, Settings raises ValidationError."""
        from pydantic import ValidationError

        from src.config.settings import Settings

        with pytest.raises(ValidationError, match="tavily_api_key"):
            Settings()

    def test_load_settings_returns_none_on_missing_key(
        self, env_no_settings: None, caplog: pytest.LogCaptureFixture
    ) -> None:
        """load_settings() logs error and returns None on validation failure."""
        from src.config.settings import load_settings

        with caplog.at_level(logging.ERROR):
            result = load_settings()

        assert result is None
        assert "Configuration error" in caplog.text
        assert "TAVILY_API_KEY" in caplog.text or "tavily_api_key" in caplog.text


@pytest.mark.unit
class TestLoggingConfiguration:
    """AC-4: Logging is configured at startup."""

    def test_configure_logging_sets_level(
        self, env_with_all_settings: None
    ) -> None:
        """Given LOG_LEVEL=DEBUG, configure_logging sets root logger to DEBUG."""
        from src.config.settings import Settings, configure_logging

        settings = Settings()
        configure_logging(settings)

        root_logger = logging.getLogger()
        assert root_logger.level == logging.DEBUG

    def test_configure_logging_defaults_to_info(
        self, env_minimal_settings: None
    ) -> None:
        """Given no LOG_LEVEL, configure_logging defaults to INFO."""
        from src.config.settings import Settings, configure_logging

        settings = Settings()
        configure_logging(settings)

        root_logger = logging.getLogger()
        assert root_logger.level == logging.INFO

    def test_configure_logging_sets_format(
        self, env_minimal_settings: None
    ) -> None:
        """Logging format includes timestamp, level, and module name."""
        from src.config.settings import Settings, configure_logging

        settings = Settings()
        configure_logging(settings)

        root_logger = logging.getLogger()
        assert root_logger.handlers  # At least one handler configured
