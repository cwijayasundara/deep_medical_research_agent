# STORY-002: Ollama Model Clients

## Story
As a **developer**, I want wrapper clients for the Qwen3 and MedGemma Ollama models, so that other components can invoke them with consistent interfaces and error handling.

## Expertise
backend

## Story Points
3

## Dependencies
- STORY-001 (Settings and configuration)

## Acceptance Criteria

### AC-1: Qwen3 client initializes with tool-calling support
- **Given** Ollama is running with `qwen3:latest` pulled
- **When** the Qwen3 client is created via `create_orchestrator_llm(settings)`
- **Then** a `ChatOllama` instance is returned configured for `qwen3:latest`
- **And** it supports `bind_tools()` for function calling

### AC-2: MedGemma client initializes for text completion
- **Given** Ollama is running with `MedAIBase/MedGemma1.0:4b` pulled
- **When** the MedGemma client is created via `create_medical_llm(settings)`
- **Then** a `ChatOllama` instance is returned configured for `MedAIBase/MedGemma1.0:4b`
- **And** it does NOT attempt to bind tools (MedGemma does not support tool calling)

### AC-3: Connection errors are handled gracefully
- **Given** Ollama is not running or a model is not pulled
- **When** a client attempts to invoke the model
- **Then** a `ModelConnectionError` is raised with an actionable message (e.g., "Ollama is not running. Start it with `ollama serve`")
- **And** the error is logged at ERROR level

### AC-4: MedGemma unavailability triggers graceful degradation
- **Given** MedGemma is not available but Qwen3 is
- **When** the medical client factory is called
- **Then** a warning is logged: "MedGemma unavailable, medical analysis will use Qwen3 as fallback"
- **And** the factory returns the Qwen3 client as a fallback

## Technical Notes
- Module: `src/models/clients.py`
- Use `ChatOllama` from `langchain_ollama`
- Define model name constants: `ORCHESTRATOR_MODEL = "qwen3:latest"`, `MEDICAL_MODEL = "MedAIBase/MedGemma1.0:4b"`
- Wrap all Ollama calls in try/except with specific exception types
