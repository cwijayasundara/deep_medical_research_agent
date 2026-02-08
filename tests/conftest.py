"""Shared test fixtures.

Add fixtures here when the same setup appears in 3+ test files.
See .claude/skills/testing/SKILL.md for fixture patterns.
"""

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
