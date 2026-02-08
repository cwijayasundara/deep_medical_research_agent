# STORY-007: FastAPI Application and Health Endpoint

## Story
As a **developer**, I want a FastAPI application with a health check endpoint, so that the frontend and other clients can verify the backend is running.

## Expertise
backend

## Story Points
2

## Dependencies
- STORY-001 (Settings and configuration)

## Acceptance Criteria

### AC-1: FastAPI app initializes with CORS and settings
- **Given** the application is started with `uvicorn`
- **When** the app starts
- **Then** CORS is configured to allow the frontend origin (`http://localhost:5173`)
- **And** settings are loaded and validated at startup
- **And** logging is configured

### AC-2: Health endpoint returns status
- **Given** the application is running
- **When** `GET /api/health` is called
- **Then** it returns `200 OK` with `{"status": "healthy", "models": {"orchestrator": "qwen3:latest", "medical": "MedGemma1.0:4b"}}`

### AC-3: Health endpoint checks Ollama connectivity
- **Given** Ollama is not running
- **When** `GET /api/health` is called
- **Then** it returns `200 OK` with `{"status": "degraded", "models": {"orchestrator": "unavailable", "medical": "unavailable"}}`
- **And** does NOT return 500 (health checks should not crash)

### AC-4: Startup errors are handled cleanly
- **Given** a missing `TAVILY_API_KEY`
- **When** the application attempts to start
- **Then** a clear error message is logged
- **And** the application exits with a non-zero status code

## Technical Notes
- Module: `src/api/app.py`
- Use FastAPI lifespan for initialization
- Define `FRONTEND_ORIGIN = "http://localhost:5173"` constant
- Mount routes under `/api` prefix
