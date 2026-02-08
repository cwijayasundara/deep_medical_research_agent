"""Medical expert consultation tool using MedGemma.

Provides a function that sends medical queries to the MedGemma model
for domain-specific analysis, with fallback to Qwen3 and a disclaimer.
"""

import logging

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage

logger = logging.getLogger(__name__)

# ---- Constants ----

MEDICAL_QUERY_TIMEOUT_SECONDS = 120

MEDICAL_SYSTEM_PROMPT = (
    "You are a medical research assistant with expertise in clinical medicine, "
    "pharmacology, pathology, and biomedical sciences. Provide thorough, "
    "evidence-based analysis of medical topics. Cite relevant research when "
    "possible. Be precise with medical terminology. Do not provide clinical "
    "diagnoses or treatment recommendations — focus on research-level analysis."
)

MEDICAL_DISCLAIMER = (
    "Disclaimer: This analysis is for research purposes only "
    "and does not constitute medical advice."
)

FALLBACK_WARNING = (
    "Note: Medical specialist model unavailable. Analysis provided by general-purpose model.\n\n"
)

TIMEOUT_ERROR_MSG = (
    "Medical analysis timed out. The query may be too complex. "
    "Try breaking it into smaller, more specific questions."
)


def consult_medical_expert(
    query: str,
    medical_llm: BaseChatModel,
    fallback_llm: BaseChatModel,
) -> str:
    """Consult the medical expert model for domain-specific analysis.

    Sends the query to MedGemma with a medical system prompt.
    Falls back to the orchestrator LLM if MedGemma is unavailable.
    Always appends a medical disclaimer.
    """
    messages: list[BaseMessage] = [
        SystemMessage(content=MEDICAL_SYSTEM_PROMPT),
        HumanMessage(content=query),
    ]

    try:
        response = medical_llm.invoke(messages)
        return _format_response(str(response.content))
    except TimeoutError:
        return _handle_timeout(query, fallback_llm, messages)
    except Exception:
        return _handle_fallback(query, fallback_llm, messages)


def _handle_fallback(
    query: str,
    fallback_llm: BaseChatModel,
    messages: list[BaseMessage],
) -> str:
    """Handle MedGemma failure by falling back to Qwen3."""
    logger.warning("Medical model unavailable for query '%s', using fallback", query)
    try:
        response = fallback_llm.invoke(messages)
        return FALLBACK_WARNING + str(response.content) + "\n\n" + MEDICAL_DISCLAIMER
    except TimeoutError as exc:
        logger.error("Fallback model timed out for query '%s': %s", query, exc)
        return TIMEOUT_ERROR_MSG
    except Exception as exc:
        logger.error("Fallback model failed for query '%s': %s", query, exc)
        return f"Medical analysis failed: {exc}\n\n{MEDICAL_DISCLAIMER}"


def _handle_timeout(
    query: str,
    fallback_llm: BaseChatModel,
    messages: list[BaseMessage],
) -> str:
    """Handle timeout from medical model, try fallback."""
    logger.warning("Medical model timed out for query '%s', trying fallback", query)
    try:
        response = fallback_llm.invoke(messages)
        return FALLBACK_WARNING + str(response.content) + "\n\n" + MEDICAL_DISCLAIMER
    except TimeoutError as exc:
        logger.error("Both models timed out for query '%s': %s", query, exc)
        return TIMEOUT_ERROR_MSG
    except Exception as exc:
        logger.error("Fallback model failed for query '%s': %s", query, exc)
        return TIMEOUT_ERROR_MSG


def _format_response(content: str) -> str:
    """Format a successful medical response with disclaimer."""
    return content + "\n\n" + MEDICAL_DISCLAIMER
