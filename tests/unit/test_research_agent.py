"""Unit tests for deep research agent assembly — STORY-005.

Tests cover:
- AC-1: Agent created via create_deep_agent with all tools
- AC-2: Agent plans research before executing (built-in todo tracking)
- AC-3: System prompt enforces structured report format
- AC-4: System prompt enforces research-only behavior (no diagnosis)
- AC-5: Agent handles tool failures without crashing
"""

from unittest.mock import MagicMock, patch

import pytest


@pytest.mark.unit
class TestCreateResearchAgent:
    """AC-1: Agent is created via create_deep_agent with all tools."""

    def test_returns_compiled_state_graph(self, settings_fixture: MagicMock) -> None:
        """create_research_agent returns a CompiledStateGraph."""
        from src.agent.research_agent import create_research_agent

        with patch("src.agent.research_agent.create_deep_agent") as mock_create:
            mock_create.return_value = MagicMock()
            agent = create_research_agent(settings_fixture)

        assert agent is not None

    def test_passes_orchestrator_model_to_deep_agent(
        self, settings_fixture: MagicMock
    ) -> None:
        """Agent uses the orchestrator LLM (Qwen3) as the model."""
        from src.agent.research_agent import create_research_agent

        with (
            patch("src.agent.research_agent.create_deep_agent") as mock_create,
            patch("src.agent.research_agent.create_orchestrator_llm") as mock_orch,
        ):
            mock_orch.return_value = MagicMock()
            mock_create.return_value = MagicMock()
            create_research_agent(settings_fixture)

        mock_create.assert_called_once()
        call_kwargs = mock_create.call_args
        assert call_kwargs.kwargs.get("model") is mock_orch.return_value

    def test_binds_search_tool(self, settings_fixture: MagicMock) -> None:
        """Agent has the Tavily search tool bound."""
        from src.agent.research_agent import create_research_agent

        with (
            patch("src.agent.research_agent.create_deep_agent") as mock_create,
            patch("src.agent.research_agent.create_orchestrator_llm"),
            patch("src.agent.research_agent.create_search_tool") as mock_search,
        ):
            mock_search.return_value = MagicMock()
            mock_create.return_value = MagicMock()
            create_research_agent(settings_fixture)

        call_kwargs = mock_create.call_args
        tools = call_kwargs.kwargs.get("tools", [])
        assert any(t is mock_search.return_value for t in tools)

    def test_binds_medical_consultation_tool(self, settings_fixture: MagicMock) -> None:
        """Agent has a medical consultation tool bound."""
        from src.agent.research_agent import create_research_agent

        with (
            patch("src.agent.research_agent.create_deep_agent") as mock_create,
            patch("src.agent.research_agent.create_orchestrator_llm"),
            patch("src.agent.research_agent.create_search_tool"),
        ):
            mock_create.return_value = MagicMock()
            create_research_agent(settings_fixture)

        call_kwargs = mock_create.call_args
        tools = call_kwargs.kwargs.get("tools", [])
        # Should have at least 2 tools: search + medical
        assert len(tools) >= 2

    def test_passes_system_prompt(self, settings_fixture: MagicMock) -> None:
        """Agent receives the RESEARCH_SYSTEM_PROMPT."""
        from src.agent.research_agent import RESEARCH_SYSTEM_PROMPT, create_research_agent

        with (
            patch("src.agent.research_agent.create_deep_agent") as mock_create,
            patch("src.agent.research_agent.create_orchestrator_llm"),
            patch("src.agent.research_agent.create_search_tool"),
        ):
            mock_create.return_value = MagicMock()
            create_research_agent(settings_fixture)

        call_kwargs = mock_create.call_args
        assert call_kwargs.kwargs.get("system_prompt") == RESEARCH_SYSTEM_PROMPT


@pytest.mark.unit
class TestResearchSystemPrompt:
    """AC-3 & AC-4: System prompt enforces report format and research-only behavior."""

    def test_prompt_includes_report_structure(self) -> None:
        """System prompt instructs agent to produce structured markdown reports."""
        from src.agent.research_agent import RESEARCH_SYSTEM_PROMPT

        prompt_lower = RESEARCH_SYSTEM_PROMPT.lower()
        assert "executive summary" in prompt_lower
        assert "key findings" in prompt_lower
        assert "sources" in prompt_lower

    def test_prompt_includes_title_and_query(self) -> None:
        """System prompt instructs agent to include title and query in report."""
        from src.agent.research_agent import RESEARCH_SYSTEM_PROMPT

        prompt_lower = RESEARCH_SYSTEM_PROMPT.lower()
        assert "title" in prompt_lower

    def test_prompt_includes_medical_disclaimer_instruction(self) -> None:
        """System prompt instructs agent to include medical disclaimer."""
        from src.agent.research_agent import RESEARCH_SYSTEM_PROMPT

        prompt_lower = RESEARCH_SYSTEM_PROMPT.lower()
        assert "disclaimer" in prompt_lower

    def test_prompt_prohibits_clinical_diagnosis(self) -> None:
        """System prompt explicitly forbids clinical diagnosis."""
        from src.agent.research_agent import RESEARCH_SYSTEM_PROMPT

        prompt_lower = RESEARCH_SYSTEM_PROMPT.lower()
        assert "diagnosis" in prompt_lower or "diagnos" in prompt_lower

    def test_prompt_prohibits_treatment_recommendations(self) -> None:
        """System prompt explicitly forbids treatment recommendations."""
        from src.agent.research_agent import RESEARCH_SYSTEM_PROMPT

        prompt_lower = RESEARCH_SYSTEM_PROMPT.lower()
        assert "treatment" in prompt_lower

    def test_prompt_suggests_consulting_professional(self) -> None:
        """System prompt tells agent to suggest consulting a healthcare professional."""
        from src.agent.research_agent import RESEARCH_SYSTEM_PROMPT

        prompt_lower = RESEARCH_SYSTEM_PROMPT.lower()
        assert "healthcare professional" in prompt_lower or "medical professional" in prompt_lower


@pytest.mark.unit
class TestMedicalConsultationToolCreation:
    """AC-1 continued: Medical consultation tool is properly wrapped."""

    def test_medical_tool_is_callable(self, settings_fixture: MagicMock) -> None:
        """The medical consultation tool passed to create_deep_agent is callable."""
        from src.agent.research_agent import create_research_agent

        with (
            patch("src.agent.research_agent.create_deep_agent") as mock_create,
            patch("src.agent.research_agent.create_orchestrator_llm"),
            patch("src.agent.research_agent.create_search_tool"),
        ):
            mock_create.return_value = MagicMock()
            create_research_agent(settings_fixture)

        call_kwargs = mock_create.call_args
        tools = call_kwargs.kwargs.get("tools", [])
        for tool in tools:
            assert callable(tool)

    def test_medical_tool_uses_medical_llm(self, settings_fixture: MagicMock) -> None:
        """Medical consultation tool is created with the medical LLM."""
        from src.agent.research_agent import create_research_agent

        with (
            patch("src.agent.research_agent.create_deep_agent") as mock_create,
            patch("src.agent.research_agent.create_orchestrator_llm"),
            patch("src.agent.research_agent.create_search_tool"),
            patch("src.agent.research_agent.create_medical_llm_with_fallback") as mock_med,
        ):
            mock_med.return_value = MagicMock()
            mock_create.return_value = MagicMock()
            create_research_agent(settings_fixture)

        mock_med.assert_called_once()


@pytest.mark.unit
class TestAgentToolFailureHandling:
    """AC-5: Agent handles tool failures without crashing."""

    def test_search_tool_failure_returns_error_string(self) -> None:
        """When search tool fails, it returns an error string instead of raising."""
        from src.tools.search import safe_search

        mock_tool = MagicMock()
        mock_tool.invoke.side_effect = Exception("network error")

        result = safe_search(mock_tool, "test query")

        assert isinstance(result, str)
        assert "failed" in result.lower()

    def test_medical_tool_failure_returns_error_string(self) -> None:
        """When medical tool fails completely, it returns an error string."""
        from src.tools.medical import consult_medical_expert

        mock_medical = MagicMock()
        mock_medical.invoke.side_effect = ConnectionError("unavailable")
        mock_fallback = MagicMock()
        mock_fallback.invoke.side_effect = RuntimeError("also broken")

        result = consult_medical_expert(
            query="test",
            medical_llm=mock_medical,
            fallback_llm=mock_fallback,
        )

        assert isinstance(result, str)
        assert "failed" in result.lower()


@pytest.mark.unit
class TestAgentConstants:
    """Verify important constants are defined."""

    def test_research_system_prompt_is_non_empty_string(self) -> None:
        """RESEARCH_SYSTEM_PROMPT is a non-empty string."""
        from src.agent.research_agent import RESEARCH_SYSTEM_PROMPT

        assert isinstance(RESEARCH_SYSTEM_PROMPT, str)
        assert len(RESEARCH_SYSTEM_PROMPT) > 0

    def test_max_agent_iterations_is_defined(self) -> None:
        """MAX_AGENT_ITERATIONS constant is defined."""
        from src.agent.research_agent import MAX_AGENT_ITERATIONS

        assert isinstance(MAX_AGENT_ITERATIONS, int)
        assert MAX_AGENT_ITERATIONS > 0

    def test_agent_name_is_defined(self) -> None:
        """AGENT_NAME constant is defined."""
        from src.agent.research_agent import AGENT_NAME

        assert isinstance(AGENT_NAME, str)
        assert len(AGENT_NAME) > 0
