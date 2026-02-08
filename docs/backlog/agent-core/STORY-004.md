# STORY-004: Medical Expert Consultation Tool

## Story
As a **researcher**, I want the agent to consult a medical AI specialist for domain-specific analysis, so that research outputs have expert-level medical understanding.

## Expertise
backend

## Story Points
3

## Dependencies
- STORY-002 (Ollama model clients)

## Acceptance Criteria

### AC-1: Medical consultation tool accepts a query and returns analysis
- **Given** MedGemma is available via Ollama
- **When** the `consult_medical_expert` tool is invoked with a medical query
- **Then** the query is sent to MedGemma with a medical system prompt
- **And** the response includes the medical analysis plus a disclaimer

### AC-2: Disclaimer is always appended
- **Given** any invocation of the medical consultation tool
- **When** MedGemma returns a response
- **Then** the output ends with: "Disclaimer: This analysis is for research purposes only and does not constitute medical advice."

### AC-3: Fallback to Qwen3 when MedGemma is unavailable
- **Given** MedGemma is not available (Ollama not serving it)
- **When** the medical consultation tool is invoked
- **Then** the query is sent to Qwen3 instead
- **And** a warning is prepended: "Note: Medical specialist model unavailable. Analysis provided by general-purpose model."
- **And** the fallback is logged at WARNING level

### AC-4: Timeout handling for long medical queries
- **Given** a complex medical query that takes longer than the timeout
- **When** the model call exceeds `MEDICAL_QUERY_TIMEOUT_SECONDS`
- **Then** a timeout error is returned with an actionable message
- **And** the timeout is logged at ERROR level

## Technical Notes
- Module: `src/tools/medical.py`
- The tool is a plain Python function (not a LangChain `@tool` — deepagents accepts plain functions)
- Define `MEDICAL_SYSTEM_PROMPT` constant with instructions for medical analysis
- Define `MEDICAL_DISCLAIMER` constant
- Define `MEDICAL_QUERY_TIMEOUT_SECONDS = 120`
- The tool receives the LLM clients via closure or dependency injection
