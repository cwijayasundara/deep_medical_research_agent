# Deep Medical Research Agent

AI-powered medical research agent that plans and executes multi-step research using web search and specialized medical AI. Built with LangChain Deep Agents, Qwen3 (orchestrator), and MedGemma (medical specialist), all running locally via Ollama.

## Architecture

```
User Query
    |
    v
+-------------+    SSE Stream    +------------------+
|  React UI   | <--------------> |  FastAPI Backend  |
|  :5173      |    POST /api/    |  :8000            |
+-------------+    research      +--------+---------+
                                          |
                                          v
                                +-----------------------+
                                |  Deep Research Agent   |
                                |  (LangGraph loop)      |
                                +--+------+------+------+
                                   |      |      |
                          +--------+      |      +--------+
                          v               v               v
                   +-----------+  +------------+  +----------+
                   |  Tavily   |  |  MedGemma  |  |  Report  |
                   |  Search   |  |  Expert    |  |  Storage |
                   |  (HTTPS)  |  |  (Ollama)  |  |  (files) |
                   +-----------+  +------------+  +----------+
```

The agent receives a research query, creates a multi-step plan, searches the web via Tavily, consults MedGemma for medical analysis, and produces a comprehensive markdown report — all streamed to the frontend in real time via Server-Sent Events.

## Prerequisites

- **Python 3.12+**
- **Node.js 18+** and npm
- **Ollama** — local LLM server ([install guide](https://ollama.ai))
- **Tavily API key** — sign up at [tavily.com](https://tavily.com) (free tier available)

## Setup

### 1. Clone the repository

```bash
git clone <your-repo-url> deep-medical-research-agent
cd deep-medical-research-agent
```

### 2. Pull required Ollama models

```bash
# Orchestrator model (tool-calling capable)
ollama pull qwen3:latest

# Medical specialist model
ollama pull MedAIBase/MedGemma1.0:4b
```

Verify Ollama is running:

```bash
curl http://localhost:11434
# Should return: "Ollama is running"
```

### 3. Create a virtual environment and install Python dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

> **Note:** Always activate the venv (`source .venv/bin/activate`) before running the backend or tests.

### 4. Install frontend dependencies

```bash
cd frontend
npm install
cd ..
```

### 5. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` and set your Tavily API key:

```bash
# Required
TAVILY_API_KEY=tvly-your-actual-key-here

# Optional (defaults shown)
OLLAMA_BASE_URL=http://localhost:11434
OUTPUT_DIR=output
LOG_LEVEL=INFO
ORCHESTRATOR_MODEL=qwen3:latest
MEDICAL_MODEL=MedAIBase/MedGemma1.0:4b
```

## Running the Agent

### Start the backend

```bash
uvicorn src.api.app:create_app --factory --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`. Check health:

```bash
curl http://localhost:8000/api/health
```

### Start the frontend

In a separate terminal:

```bash
cd frontend
npm run dev
```

The UI will be available at `http://localhost:5173`.

### Using the application

1. Open `http://localhost:5173` in your browser
2. Check the health indicator (green = backend connected, models available)
3. Enter a medical research query (e.g., "What are the latest treatments for type 2 diabetes?")
4. Watch real-time progress as the agent searches, analyzes, and writes the report
5. View the completed markdown report in the main area
6. Browse past research in the sidebar

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/health` | Health check with model availability |
| `POST` | `/api/research` | Start research (SSE streaming response) |
| `GET` | `/api/reports` | List all saved reports |
| `GET` | `/api/reports/{id}` | Get a specific report by ID |

### Example: Start a research query

```bash
curl -X POST http://localhost:8000/api/research \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the latest treatments for type 2 diabetes?"}' \
  --no-buffer
```

The response is an SSE stream with events:

```
data: {"type": "progress", "data": "Planning research steps..."}
data: {"type": "progress", "data": "Searching for clinical trials..."}
data: {"type": "result", "data": "# Research Report\n\n...", "filename": "report-2025-01-15.md"}
```

## Project Structure

```
src/
├── config/settings.py          # Pydantic BaseSettings from .env
├── models/clients.py           # Qwen3 + MedGemma ChatOllama wrappers
├── tools/
│   ├── search.py               # Tavily search tool
│   └── medical.py              # MedGemma consultation tool
├── agent/research_agent.py     # Deep research agent assembly
├── services/report_service.py  # Report save/list/retrieve
└── api/
    ├── app.py                  # FastAPI app factory
    └── routes/
        ├── research.py         # POST /api/research (SSE)
        └── reports.py          # GET /api/reports

frontend/
├── src/
│   ├── App.tsx                 # Main app wiring
│   ├── components/
│   │   ├── Layout.tsx          # Header + sidebar + content
│   │   ├── HealthIndicator.tsx # Backend status indicator
│   │   ├── ResearchInput.tsx   # Query input with submit/stop
│   │   ├── ProgressLog.tsx     # Real-time progress messages
│   │   ├── ReportViewer.tsx    # Markdown report renderer
│   │   └── HistorySidebar.tsx  # Past research list
│   ├── hooks/
│   │   ├── useResearch.ts      # SSE streaming hook
│   │   └── useReportHistory.ts # Report history state
│   └── lib/
│       ├── api-client.ts       # Health API client
│       ├── research-api.ts     # SSE parsing utilities
│       └── reports-api.ts      # Reports API client
├── package.json
└── vite.config.ts
```

## Development

### Running tests

```bash
# Backend unit tests (with coverage)
make test-unit

# Frontend tests
make test-frontend

# All tests
make test-unit && make test-frontend

# Lint + type check
make lint

# Full CI (lint + tests)
make ci
```

### Environment variables reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `TAVILY_API_KEY` | Yes | — | API key for Tavily web search |
| `OLLAMA_BASE_URL` | No | `http://localhost:11434` | Ollama server URL |
| `OUTPUT_DIR` | No | `output` | Directory for saved research reports |
| `LOG_LEVEL` | No | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `ORCHESTRATOR_MODEL` | No | `qwen3:latest` | Ollama model for orchestration |
| `MEDICAL_MODEL` | No | `MedAIBase/MedGemma1.0:4b` | Ollama model for medical analysis |
| `VITE_API_URL` | No | `http://localhost:8000/api` | Backend API URL (frontend) |

## Tech Stack

| Layer | Technologies |
|-------|-------------|
| Backend | Python 3.12 / FastAPI / Uvicorn |
| Frontend | React 19 / TypeScript / Vite / Tailwind CSS v4 |
| AI Agent | LangChain Deep Agents / LangGraph |
| Orchestrator LLM | Qwen3 via Ollama (tool-calling) |
| Medical LLM | MedGemma 1.0 via Ollama |
| Web Search | Tavily API |
| Testing | pytest (backend) / Vitest (frontend) |
