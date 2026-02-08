"""Deep research agent assembly.

Creates a LangGraph-based research agent that plans multi-step research,
searches the web via Tavily, and consults MedGemma for medical analysis.
"""

import logging
from functools import partial
from typing import Any

from deepagents import create_deep_agent
from langchain_core.language_models import BaseChatModel
from langchain_core.tools import BaseTool, tool
from langgraph.graph.state import CompiledStateGraph

from src.config.settings import Settings
from src.models.clients import create_medical_llm_with_fallback, create_orchestrator_llm
from src.tools.medical import consult_medical_expert
from src.tools.search import create_search_tool

logger = logging.getLogger(__name__)

# ---- Constants ----

AGENT_NAME = "medical-research-agent"
MAX_AGENT_ITERATIONS = 20

RESEARCH_SYSTEM_PROMPT = (
    "You are a medical research agent. Your role is to conduct thorough, "
    "evidence-based research on medical and biomedical topics.\n\n"
    "## Research Workflow\n"
    "1. Break the research question into sub-questions\n"
    "2. Search for relevant information using the search tool\n"
    "3. Consult the medical expert tool for domain-specific analysis\n"
    "4. Synthesize findings into a structured report\n\n"
    "## Output Format\n"
    "Your final output MUST be a markdown-formatted report containing:\n"
    "- **Title**: A clear title for the research report\n"
    "- **Research Query**: The original question being investigated\n"
    "- **Executive Summary**: A concise overview of key findings (2-3 paragraphs)\n"
    "- **Key Findings**: Numbered list of the most important discoveries, "
    "with citations and sources where available\n"
    "- **Detailed Analysis**: In-depth discussion of the topic\n"
    "- **Sources Consulted**: List of all sources referenced\n"
    "- **Disclaimer**: Always include the medical disclaimer at the end\n\n"
    "## Important Rules\n"
    "- You are a RESEARCH assistant only. You do NOT provide clinical diagnosis "
    "or treatment recommendations.\n"
    "- If a user asks for a diagnosis, treatment plan, or medical advice, "
    "you MUST decline and explain that you provide research information only.\n"
    "- Always suggest that users consult a qualified healthcare professional "
    "for medical decisions.\n"
    "- Cite sources for all claims. Prefer peer-reviewed sources.\n"
    "- Include the medical disclaimer in every report: "
    "'This analysis is for research purposes only and does not constitute medical advice.'\n"
)


def _build_medical_tool(
    medical_llm: BaseChatModel,
    fallback_llm: BaseChatModel,
) -> BaseTool:
    """Build a LangChain tool that wraps consult_medical_expert."""
    bound = partial(consult_medical_expert, medical_llm=medical_llm, fallback_llm=fallback_llm)

    @tool
    def consult_medical_expert_tool(query: str) -> str:
        """Consult the medical specialist model for domain-specific medical analysis.

        Use this tool when you need expert medical knowledge, analysis of
        medical conditions, pharmacology, pathology, or biomedical topics.
        The tool sends queries to a specialized medical AI model.
        """
        return bound(query=query)

    return consult_medical_expert_tool


def create_research_agent(settings: Settings) -> CompiledStateGraph[Any, Any]:
    """Create the deep research agent with search and medical tools.

    Assembles a LangGraph agent using create_deep_agent with:
    - Qwen3 as the orchestrator model (supports tool calling)
    - Tavily search tool for web research
    - Medical consultation tool backed by MedGemma with Qwen3 fallback
    """
    orchestrator_llm = create_orchestrator_llm(settings)
    medical_llm = create_medical_llm_with_fallback(settings, orchestrator_llm)
    search_tool = create_search_tool(settings)
    medical_tool = _build_medical_tool(
        medical_llm=medical_llm,
        fallback_llm=orchestrator_llm,
    )

    logger.info("Creating research agent '%s' with Qwen3 orchestrator", AGENT_NAME)

    return create_deep_agent(
        model=orchestrator_llm,
        tools=[search_tool, medical_tool],
        system_prompt=RESEARCH_SYSTEM_PROMPT,
        name=AGENT_NAME,
    )
