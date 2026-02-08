"""Shared test fixtures.

Add fixtures here when the same setup appears in 3+ test files.
See .claude/skills/testing/SKILL.md for fixture patterns.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

# ---- Marker registration ----
# Markers are configured in pyproject.toml [tool.pytest.ini_options].


# ---- Settings fixtures ----


@pytest.fixture()
def env_with_all_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    """Set all required and optional environment variables for Settings."""
    monkeypatch.setenv("TAVILY_API_KEY", "tvly-test-key-12345")
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://localhost:11434")
    monkeypatch.setenv("OUTPUT_DIR", "/tmp/test-reports")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")


@pytest.fixture()
def env_minimal_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    """Set only the required environment variables for Settings."""
    monkeypatch.setenv("TAVILY_API_KEY", "tvly-test-key-12345")


@pytest.fixture()
def env_no_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    """Clear all settings-related environment variables."""
    for key in ("TAVILY_API_KEY", "OLLAMA_BASE_URL", "OUTPUT_DIR", "LOG_LEVEL"):
        monkeypatch.delenv(key, raising=False)


# ---- Mock Settings fixture ----

TEST_TAVILY_API_KEY = "tvly-test-key-12345"
TEST_OLLAMA_BASE_URL = "http://localhost:11434"
TEST_OUTPUT_DIR = "/tmp/test-reports"
TEST_LOG_LEVEL = "INFO"
TEST_ORCHESTRATOR_MODEL = "qwen3:latest"
TEST_MEDICAL_MODEL = "MedAIBase/MedGemma1.0:4b"


@pytest.fixture()
def settings_fixture() -> MagicMock:
    """Create a mock Settings object with default test values."""
    settings = MagicMock()
    settings.tavily_api_key = TEST_TAVILY_API_KEY
    settings.ollama_base_url = TEST_OLLAMA_BASE_URL
    settings.output_dir = TEST_OUTPUT_DIR
    settings.log_level = TEST_LOG_LEVEL
    settings.orchestrator_model = TEST_ORCHESTRATOR_MODEL
    settings.medical_model = TEST_MEDICAL_MODEL
    settings.tavily_include_domains = None
    return settings
