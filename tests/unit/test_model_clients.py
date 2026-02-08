"""Unit tests for Ollama model clients — STORY-002.

Tests cover:
- AC-1: Qwen3 orchestrator client with tool-calling support
- AC-2: MedGemma medical client for text completion
- AC-3: Connection errors handled gracefully with ModelConnectionError
- AC-4: MedGemma unavailability triggers fallback to Qwen3
"""

import logging
from unittest.mock import MagicMock, patch

import pytest


@pytest.mark.unit
class TestCreateOrchestratorLlm:
    """AC-1: Qwen3 client initializes with tool-calling support."""

    @patch("src.models.clients.ChatOllama")
    def test_creates_chat_ollama_with_orchestrator_model(
        self,
        mock_chat_ollama: MagicMock,
        settings_fixture: MagicMock,
    ) -> None:
        """Factory creates ChatOllama configured for qwen3:latest."""
        from src.models.clients import create_orchestrator_llm

        create_orchestrator_llm(settings_fixture)

        mock_chat_ollama.assert_called_once_with(
            model="qwen3:latest",
            base_url="http://localhost:11434",
        )

    @patch("src.models.clients.ChatOllama")
    def test_returns_chat_ollama_instance(
        self,
        mock_chat_ollama: MagicMock,
        settings_fixture: MagicMock,
    ) -> None:
        """Factory returns the ChatOllama instance."""
        from src.models.clients import create_orchestrator_llm

        result = create_orchestrator_llm(settings_fixture)

        assert result is mock_chat_ollama.return_value

    @patch("src.models.clients.ChatOllama")
    def test_uses_model_from_settings(
        self,
        mock_chat_ollama: MagicMock,
        settings_fixture: MagicMock,
    ) -> None:
        """Factory uses the orchestrator_model from settings."""
        settings_fixture.orchestrator_model = "qwen3:8b"

        from src.models.clients import create_orchestrator_llm

        create_orchestrator_llm(settings_fixture)

        mock_chat_ollama.assert_called_once_with(
            model="qwen3:8b",
            base_url="http://localhost:11434",
        )


@pytest.mark.unit
class TestCreateMedicalLlm:
    """AC-2: MedGemma client initializes for text completion."""

    @patch("src.models.clients.ChatOllama")
    def test_creates_chat_ollama_with_medical_model(
        self,
        mock_chat_ollama: MagicMock,
        settings_fixture: MagicMock,
    ) -> None:
        """Factory creates ChatOllama configured for MedGemma."""
        from src.models.clients import create_medical_llm

        create_medical_llm(settings_fixture)

        mock_chat_ollama.assert_called_once_with(
            model="MedAIBase/MedGemma1.0:4b",
            base_url="http://localhost:11434",
        )

    @patch("src.models.clients.ChatOllama")
    def test_returns_chat_ollama_instance(
        self,
        mock_chat_ollama: MagicMock,
        settings_fixture: MagicMock,
    ) -> None:
        """Factory returns the ChatOllama instance."""
        from src.models.clients import create_medical_llm

        result = create_medical_llm(settings_fixture)

        assert result is mock_chat_ollama.return_value

    @patch("src.models.clients.ChatOllama")
    def test_uses_model_from_settings(
        self,
        mock_chat_ollama: MagicMock,
        settings_fixture: MagicMock,
    ) -> None:
        """Factory uses the medical_model from settings."""
        settings_fixture.medical_model = "MedAIBase/MedGemma1.5:4b"

        from src.models.clients import create_medical_llm

        create_medical_llm(settings_fixture)

        mock_chat_ollama.assert_called_once_with(
            model="MedAIBase/MedGemma1.5:4b",
            base_url="http://localhost:11434",
        )


@pytest.mark.unit
class TestModelConnectionError:
    """AC-3: Connection errors are handled gracefully."""

    def test_model_connection_error_exists(self) -> None:
        """ModelConnectionError is a defined exception class."""
        from src.models.clients import ModelConnectionError

        assert issubclass(ModelConnectionError, Exception)

    def test_model_connection_error_stores_message(self) -> None:
        """ModelConnectionError stores an actionable message."""
        from src.models.clients import ModelConnectionError

        error = ModelConnectionError("Ollama is not running. Start it with `ollama serve`")

        assert "Ollama is not running" in str(error)

    @patch("src.models.clients.ChatOllama")
    def test_invoke_wraps_connection_error(
        self,
        mock_chat_ollama: MagicMock,
        settings_fixture: MagicMock,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """invoke_llm wraps connection errors into ModelConnectionError."""
        from src.models.clients import ModelConnectionError, invoke_llm

        mock_llm = MagicMock()
        mock_llm.invoke.side_effect = ConnectionError("Connection refused")

        with (
            caplog.at_level(logging.ERROR),
            pytest.raises(ModelConnectionError, match="Ollama"),
        ):
            invoke_llm(mock_llm, "test prompt")

        assert "ERROR" in caplog.text or caplog.records

    @patch("src.models.clients.ChatOllama")
    def test_invoke_wraps_timeout_error(
        self,
        mock_chat_ollama: MagicMock,
        settings_fixture: MagicMock,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """invoke_llm wraps timeout errors into ModelConnectionError."""
        from src.models.clients import ModelConnectionError, invoke_llm

        mock_llm = MagicMock()
        mock_llm.invoke.side_effect = TimeoutError("Request timed out")

        with (
            caplog.at_level(logging.ERROR),
            pytest.raises(ModelConnectionError, match="timed out"),
        ):
            invoke_llm(mock_llm, "test prompt")

    @patch("src.models.clients.ChatOllama")
    def test_invoke_returns_response_on_success(
        self,
        mock_chat_ollama: MagicMock,
        settings_fixture: MagicMock,
    ) -> None:
        """invoke_llm returns the model response on success."""
        from src.models.clients import invoke_llm

        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "Medical analysis result"
        mock_llm.invoke.return_value = mock_response

        result = invoke_llm(mock_llm, "What causes headaches?")

        assert result is mock_response


@pytest.mark.unit
class TestMedicalLlmFallback:
    """AC-4: MedGemma unavailability triggers graceful degradation."""

    @patch("src.models.clients.ChatOllama")
    def test_fallback_returns_orchestrator_when_medical_fails(
        self,
        mock_chat_ollama: MagicMock,
        settings_fixture: MagicMock,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """When MedGemma init fails, fallback returns the orchestrator LLM."""
        from src.models.clients import create_medical_llm_with_fallback

        orchestrator_llm = MagicMock()
        # First call (medical) raises, second call would be orchestrator
        mock_chat_ollama.side_effect = [Exception("Model not found"), orchestrator_llm]

        with caplog.at_level(logging.WARNING):
            result = create_medical_llm_with_fallback(settings_fixture, orchestrator_llm)

        assert result is orchestrator_llm

    @patch("src.models.clients.ChatOllama")
    def test_fallback_logs_warning(
        self,
        mock_chat_ollama: MagicMock,
        settings_fixture: MagicMock,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """When MedGemma init fails, a warning is logged."""
        from src.models.clients import create_medical_llm_with_fallback

        orchestrator_llm = MagicMock()
        mock_chat_ollama.side_effect = Exception("Model not found")

        with caplog.at_level(logging.WARNING):
            create_medical_llm_with_fallback(settings_fixture, orchestrator_llm)

        assert "MedGemma unavailable" in caplog.text
        assert "fallback" in caplog.text.lower() or "Qwen3" in caplog.text

    @patch("src.models.clients.ChatOllama")
    def test_fallback_returns_medical_when_available(
        self,
        mock_chat_ollama: MagicMock,
        settings_fixture: MagicMock,
    ) -> None:
        """When MedGemma is available, fallback returns the medical LLM."""
        from src.models.clients import create_medical_llm_with_fallback

        medical_llm = MagicMock()
        orchestrator_llm = MagicMock()
        mock_chat_ollama.return_value = medical_llm

        result = create_medical_llm_with_fallback(settings_fixture, orchestrator_llm)

        assert result is medical_llm
