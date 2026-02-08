"""Ollama model client factories and error handling.

Provides factory functions for creating ChatOllama instances
for the orchestrator (Qwen3) and medical specialist (MedGemma) models.
Includes graceful degradation when MedGemma is unavailable.
"""

import logging

from langchain_ollama import ChatOllama

from src.config.settings import Settings

logger = logging.getLogger(__name__)

OLLAMA_NOT_RUNNING_MSG = (
    "Ollama connection failed. Ensure Ollama is running with `ollama serve` "
    "and the model is pulled."
)
OLLAMA_TIMEOUT_MSG = (
    "Ollama request timed out. The model may be loading or the request is too complex."
)


class ModelConnectionError(Exception):
    """Raised when an Ollama model connection or invocation fails."""


def create_orchestrator_llm(settings: Settings) -> ChatOllama:
    """Create a ChatOllama instance for the orchestrator model (Qwen3).

    The orchestrator supports function/tool calling and is used
    as the main agent model in the deep agent framework.
    """
    return ChatOllama(
        model=settings.orchestrator_model,
        base_url=settings.ollama_base_url,
    )


def create_medical_llm(settings: Settings) -> ChatOllama:
    """Create a ChatOllama instance for the medical model (MedGemma).

    MedGemma is used for medical text analysis only — it does NOT
    support tool calling and should never have tools bound to it.
    """
    return ChatOllama(
        model=settings.medical_model,
        base_url=settings.ollama_base_url,
    )


def create_medical_llm_with_fallback(
    settings: Settings,
    orchestrator_llm: ChatOllama,
) -> ChatOllama:
    """Create the medical LLM, falling back to orchestrator if unavailable.

    When MedGemma cannot be initialized, logs a warning and returns
    the orchestrator LLM as a fallback for medical analysis.
    """
    try:
        return create_medical_llm(settings)
    except Exception:
        logger.warning("MedGemma unavailable, medical analysis will use Qwen3 as fallback")
        return orchestrator_llm


def invoke_llm(llm: ChatOllama, prompt: str) -> object:
    """Invoke an Ollama LLM with error handling.

    Wraps connection and timeout errors into ModelConnectionError
    with actionable messages.
    """
    try:
        return llm.invoke(prompt)
    except ConnectionError as exc:
        logger.error("Ollama connection error: %s", exc)
        raise ModelConnectionError(OLLAMA_NOT_RUNNING_MSG) from exc
    except TimeoutError as exc:
        logger.error("Ollama request timed out: %s", exc)
        raise ModelConnectionError(OLLAMA_TIMEOUT_MSG) from exc
