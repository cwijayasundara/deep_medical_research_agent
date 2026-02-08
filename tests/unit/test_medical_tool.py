"""Unit tests for medical expert consultation tool — STORY-004.

Tests cover:
- AC-1: Medical consultation accepts query, returns analysis with system prompt
- AC-2: Disclaimer is always appended
- AC-3: Fallback to Qwen3 when MedGemma unavailable
- AC-4: Timeout handling for long queries
"""

import logging
from unittest.mock import MagicMock

import pytest


@pytest.mark.unit
class TestConsultMedicalExpert:
    """AC-1: Medical consultation tool accepts query and returns analysis."""

    def test_sends_query_to_medical_llm(self) -> None:
        """consult_medical_expert sends the query to the medical LLM."""
        from src.tools.medical import consult_medical_expert

        mock_medical_llm = MagicMock()
        mock_medical_llm.invoke.return_value = MagicMock(content="Analysis result")

        consult_medical_expert(
            query="What causes migraines?",
            medical_llm=mock_medical_llm,
            fallback_llm=MagicMock(),
        )

        mock_medical_llm.invoke.assert_called_once()

    def test_includes_medical_system_prompt(self) -> None:
        """The call to the LLM includes a medical system prompt."""
        from src.tools.medical import MEDICAL_SYSTEM_PROMPT, consult_medical_expert

        mock_medical_llm = MagicMock()
        mock_medical_llm.invoke.return_value = MagicMock(content="Analysis")

        consult_medical_expert(
            query="What causes migraines?",
            medical_llm=mock_medical_llm,
            fallback_llm=MagicMock(),
        )

        call_args = mock_medical_llm.invoke.call_args[0][0]
        # Should be a list of messages containing the system prompt
        system_content = str(call_args)
        assert MEDICAL_SYSTEM_PROMPT in system_content or "medical" in system_content.lower()

    def test_returns_string_response(self) -> None:
        """consult_medical_expert returns a string."""
        from src.tools.medical import consult_medical_expert

        mock_medical_llm = MagicMock()
        mock_medical_llm.invoke.return_value = MagicMock(content="Detailed analysis")

        result = consult_medical_expert(
            query="What causes migraines?",
            medical_llm=mock_medical_llm,
            fallback_llm=MagicMock(),
        )

        assert isinstance(result, str)
        assert "Detailed analysis" in result


@pytest.mark.unit
class TestMedicalDisclaimer:
    """AC-2: Disclaimer is always appended."""

    def test_disclaimer_appended_to_successful_response(self) -> None:
        """Response always ends with the medical disclaimer."""
        from src.tools.medical import MEDICAL_DISCLAIMER, consult_medical_expert

        mock_medical_llm = MagicMock()
        mock_medical_llm.invoke.return_value = MagicMock(content="Analysis text")

        result = consult_medical_expert(
            query="test query",
            medical_llm=mock_medical_llm,
            fallback_llm=MagicMock(),
        )

        assert result.endswith(MEDICAL_DISCLAIMER)

    def test_disclaimer_constant_matches_spec(self) -> None:
        """MEDICAL_DISCLAIMER matches the specification text."""
        from src.tools.medical import MEDICAL_DISCLAIMER

        expected = (
            "Disclaimer: This analysis is for research purposes only "
            "and does not constitute medical advice."
        )
        assert expected == MEDICAL_DISCLAIMER

    def test_disclaimer_appended_on_fallback(self) -> None:
        """Disclaimer is appended even when using fallback model."""
        from src.tools.medical import MEDICAL_DISCLAIMER, consult_medical_expert

        mock_medical_llm = MagicMock()
        mock_medical_llm.invoke.side_effect = ConnectionError("unavailable")
        mock_fallback = MagicMock()
        mock_fallback.invoke.return_value = MagicMock(content="Fallback analysis")

        result = consult_medical_expert(
            query="test query",
            medical_llm=mock_medical_llm,
            fallback_llm=mock_fallback,
        )

        assert result.endswith(MEDICAL_DISCLAIMER)


@pytest.mark.unit
class TestFallbackToQwen3:
    """AC-3: Fallback to Qwen3 when MedGemma unavailable."""

    def test_uses_fallback_when_medical_raises_connection_error(
        self,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """Falls back to Qwen3 when MedGemma raises ConnectionError."""
        from src.tools.medical import consult_medical_expert

        mock_medical_llm = MagicMock()
        mock_medical_llm.invoke.side_effect = ConnectionError("Connection refused")
        mock_fallback = MagicMock()
        mock_fallback.invoke.return_value = MagicMock(content="Fallback result")

        with caplog.at_level(logging.WARNING):
            result = consult_medical_expert(
                query="test query",
                medical_llm=mock_medical_llm,
                fallback_llm=mock_fallback,
            )

        mock_fallback.invoke.assert_called_once()
        assert "Fallback result" in result

    def test_fallback_prepends_warning_note(self) -> None:
        """Fallback response includes a warning note about model unavailability."""
        from src.tools.medical import FALLBACK_WARNING, consult_medical_expert

        mock_medical_llm = MagicMock()
        mock_medical_llm.invoke.side_effect = Exception("model not found")
        mock_fallback = MagicMock()
        mock_fallback.invoke.return_value = MagicMock(content="Fallback analysis")

        result = consult_medical_expert(
            query="test query",
            medical_llm=mock_medical_llm,
            fallback_llm=mock_fallback,
        )

        assert result.startswith(FALLBACK_WARNING)

    def test_fallback_logs_warning(
        self,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """Fallback is logged at WARNING level."""
        from src.tools.medical import consult_medical_expert

        mock_medical_llm = MagicMock()
        mock_medical_llm.invoke.side_effect = Exception("unavailable")
        mock_fallback = MagicMock()
        mock_fallback.invoke.return_value = MagicMock(content="result")

        with caplog.at_level(logging.WARNING):
            consult_medical_expert(
                query="test query",
                medical_llm=mock_medical_llm,
                fallback_llm=mock_fallback,
            )

        assert any(record.levelno == logging.WARNING for record in caplog.records)

    def test_fallback_warning_constant_matches_spec(self) -> None:
        """FALLBACK_WARNING matches the specification text."""
        from src.tools.medical import FALLBACK_WARNING

        expected = (
            "Note: Medical specialist model unavailable. "
            "Analysis provided by general-purpose model.\n\n"
        )
        assert expected == FALLBACK_WARNING


@pytest.mark.unit
class TestTimeoutHandling:
    """AC-4: Timeout handling for long medical queries."""

    def test_timeout_returns_actionable_error_message(
        self,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """Timeout returns a clear error message, not an exception."""
        from src.tools.medical import consult_medical_expert

        mock_medical_llm = MagicMock()
        mock_medical_llm.invoke.side_effect = TimeoutError("Request timed out")
        mock_fallback = MagicMock()
        mock_fallback.invoke.side_effect = TimeoutError("Fallback also timed out")

        with caplog.at_level(logging.ERROR):
            result = consult_medical_expert(
                query="very complex query",
                medical_llm=mock_medical_llm,
                fallback_llm=mock_fallback,
            )

        assert isinstance(result, str)
        assert "timed out" in result.lower() or "timeout" in result.lower()

    def test_timeout_logged_at_error_level(
        self,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """Timeout is logged at ERROR level."""
        from src.tools.medical import consult_medical_expert

        mock_medical_llm = MagicMock()
        mock_medical_llm.invoke.side_effect = TimeoutError("timed out")
        mock_fallback = MagicMock()
        mock_fallback.invoke.side_effect = TimeoutError("also timed out")

        with caplog.at_level(logging.ERROR):
            consult_medical_expert(
                query="test",
                medical_llm=mock_medical_llm,
                fallback_llm=mock_fallback,
            )

        assert any(record.levelno == logging.ERROR for record in caplog.records)

    def test_timeout_constant_is_defined(self) -> None:
        """MEDICAL_QUERY_TIMEOUT_SECONDS is defined as 120."""
        from src.tools.medical import MEDICAL_QUERY_TIMEOUT_SECONDS

        assert MEDICAL_QUERY_TIMEOUT_SECONDS == 120

    def test_timeout_with_successful_fallback(self) -> None:
        """When medical times out but fallback succeeds, returns fallback result."""
        from src.tools.medical import FALLBACK_WARNING, consult_medical_expert

        mock_medical_llm = MagicMock()
        mock_medical_llm.invoke.side_effect = TimeoutError("timed out")
        mock_fallback = MagicMock()
        mock_fallback.invoke.return_value = MagicMock(content="Fallback analysis")

        result = consult_medical_expert(
            query="test",
            medical_llm=mock_medical_llm,
            fallback_llm=mock_fallback,
        )

        assert result.startswith(FALLBACK_WARNING)
        assert "Fallback analysis" in result

    def test_timeout_fallback_general_error(self) -> None:
        """When medical times out and fallback raises non-timeout, returns error."""
        from src.tools.medical import consult_medical_expert

        mock_medical_llm = MagicMock()
        mock_medical_llm.invoke.side_effect = TimeoutError("timed out")
        mock_fallback = MagicMock()
        mock_fallback.invoke.side_effect = RuntimeError("unexpected error")

        result = consult_medical_expert(
            query="test",
            medical_llm=mock_medical_llm,
            fallback_llm=mock_fallback,
        )

        assert "timed out" in result.lower() or "timeout" in result.lower()


@pytest.mark.unit
class TestFallbackEdgeCases:
    """Additional edge cases for fallback paths."""

    def test_fallback_timeout_returns_timeout_msg(self) -> None:
        """When medical fails and fallback times out, returns timeout message."""
        from src.tools.medical import consult_medical_expert

        mock_medical_llm = MagicMock()
        mock_medical_llm.invoke.side_effect = ConnectionError("unavailable")
        mock_fallback = MagicMock()
        mock_fallback.invoke.side_effect = TimeoutError("fallback timed out")

        result = consult_medical_expert(
            query="test",
            medical_llm=mock_medical_llm,
            fallback_llm=mock_fallback,
        )

        assert "timed out" in result.lower() or "timeout" in result.lower()

    def test_fallback_general_error_returns_failure_msg(self) -> None:
        """When both medical and fallback fail, returns failure message."""
        from src.tools.medical import MEDICAL_DISCLAIMER, consult_medical_expert

        mock_medical_llm = MagicMock()
        mock_medical_llm.invoke.side_effect = ConnectionError("unavailable")
        mock_fallback = MagicMock()
        mock_fallback.invoke.side_effect = RuntimeError("also broken")

        result = consult_medical_expert(
            query="test",
            medical_llm=mock_medical_llm,
            fallback_llm=mock_fallback,
        )

        assert "failed" in result.lower()
        assert result.endswith(MEDICAL_DISCLAIMER)
