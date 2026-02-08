# STORY-001: Project Configuration and Dependencies

## Story
As a **developer**, I want the project dependencies and configuration properly set up, so that all team members can install and run the project consistently.

## Expertise
backend / infra

## Story Points
2

## Dependencies
None (foundation story)

## Acceptance Criteria

### AC-1: Python dependencies are defined
- **Given** the project repository is cloned
- **When** a developer runs `make build`
- **Then** all runtime dependencies are installed: `deepagents`, `langchain-ollama`, `langchain-tavily`, `fastapi`, `uvicorn`, `pydantic-settings`

### AC-2: Settings class loads configuration from environment
- **Given** a `.env` file with `TAVILY_API_KEY`, `OLLAMA_BASE_URL`, `OUTPUT_DIR`, `LOG_LEVEL`
- **When** the `Settings` class is instantiated
- **Then** all values are loaded from environment variables with sensible defaults
- **And** missing required keys (TAVILY_API_KEY) raise a clear validation error

### AC-3: Settings validation fails gracefully
- **Given** no `.env` file and no environment variables set
- **When** the application attempts to load settings
- **Then** a clear, actionable error message is logged (not a raw Pydantic traceback)

### AC-4: Logging is configured at startup
- **Given** a `LOG_LEVEL` environment variable set to "DEBUG"
- **When** the application starts
- **Then** logging is configured with the specified level
- **And** all modules use `logging.getLogger(__name__)`

## Technical Notes
- Use `pydantic-settings` for `BaseSettings` class
- Define constants for default values (e.g., `DEFAULT_OLLAMA_BASE_URL`, `DEFAULT_OUTPUT_DIR`)
- Update `.env.example` with all required/optional variables
- Update `requirements.txt` with all runtime dependencies
