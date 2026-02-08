# Architecture: Deep Medical Research Agent

## C4 Context Diagram

```mermaid
C4Context
    title System Context — Deep Medical Research Agent

    Person(user, "User", "Researcher, clinician, student, or general user")

    System(agent, "Deep Medical Research Agent", "Plans and executes multi-step medical research using web search and specialized medical AI")

    System_Ext(ollama, "Ollama", "Local LLM server hosting Qwen3 and MedGemma models")
    System_Ext(tavily, "Tavily API", "Web search API for finding medical literature and information")

    Rel(user, agent, "Submits research queries, views reports", "HTTPS / Browser")
    Rel(agent, ollama, "Sends prompts, receives completions", "HTTP localhost")
    Rel(agent, tavily, "Sends search queries, receives results", "HTTPS")
```

## C4 Container Diagram

```mermaid
C4Container
    title Container Diagram — Deep Medical Research Agent

    Person(user, "User")

    Container_Boundary(system, "Deep Medical Research Agent") {
        Container(frontend, "React Frontend", "React 18, TypeScript, Tailwind", "Research query input, streaming progress, report viewer, history sidebar")
        Container(api, "FastAPI Backend", "Python 3.12, FastAPI, Uvicorn", "REST API with SSE streaming, serves research requests and report management")
        Container(agent, "Research Agent", "LangChain Deep Agents, LangGraph", "Orchestrates research: planning, searching, medical analysis, report generation")
        Container(reports, "Report Storage", "Local filesystem", "Markdown files with YAML front matter")
    }

    System_Ext(ollama, "Ollama Server", "Qwen3:latest + MedGemma1.0:4b")
    System_Ext(tavily, "Tavily API", "Web search")

    Rel(user, frontend, "Uses", "Browser")
    Rel(frontend, api, "API calls + SSE", "HTTP :8000")
    Rel(api, agent, "Invokes", "In-process")
    Rel(agent, ollama, "LLM calls", "HTTP :11434")
    Rel(agent, tavily, "Search", "HTTPS")
    Rel(agent, reports, "Saves reports", "Filesystem")
    Rel(api, reports, "Lists/reads reports", "Filesystem")
```

## C4 Component Diagram — Backend

```mermaid
C4Component
    title Component Diagram — Backend

    Container_Boundary(api_layer, "API Layer") {
        Component(app, "FastAPI App", "app.py", "CORS, lifespan, error handlers")
        Component(research_route, "Research Route", "routes/research.py", "POST /api/research — SSE streaming")
        Component(reports_route, "Reports Route", "routes/reports.py", "GET /api/reports, GET /api/reports/{id}")
        Component(health_route, "Health Route", "routes/health.py", "GET /api/health")
    }

    Container_Boundary(agent_layer, "Agent Layer") {
        Component(research_agent, "Research Agent", "agent/research_agent.py", "create_deep_agent() with tools and system prompt")
        Component(search_tool, "Tavily Search Tool", "tools/search.py", "Web search with medical domain filtering")
        Component(medical_tool, "Medical Expert Tool", "tools/medical.py", "MedGemma consultation with fallback")
    }

    Container_Boundary(service_layer, "Service Layer") {
        Component(report_svc, "Report Service", "services/report_service.py", "Save, list, retrieve markdown reports")
        Component(model_clients, "Model Clients", "models/clients.py", "Qwen3 + MedGemma ChatOllama wrappers")
    }

    Container_Boundary(config_layer, "Configuration") {
        Component(settings, "Settings", "config/settings.py", "Pydantic BaseSettings from .env")
    }

    Rel(research_route, research_agent, "Invokes and streams")
    Rel(research_route, report_svc, "Saves completed reports")
    Rel(reports_route, report_svc, "Lists and retrieves")
    Rel(research_agent, search_tool, "Tool call")
    Rel(research_agent, medical_tool, "Tool call")
    Rel(research_agent, model_clients, "Uses orchestrator LLM")
    Rel(medical_tool, model_clients, "Uses medical LLM")
    Rel(model_clients, settings, "Reads config")
    Rel(search_tool, settings, "Reads API key")
    Rel(report_svc, settings, "Reads output dir")
```

## Data Flow

```
User Query
    │
    ▼
┌─────────────┐    SSE Stream    ┌──────────────────┐
│  React UI   │ ◄──────────────► │  FastAPI Backend  │
│  :5173      │    POST /api/    │  :8000            │
└─────────────┘    research      └────────┬─────────┘
                                          │
                                          ▼
                                ┌─────────────────────┐
                                │  Deep Research Agent │
                                │  (LangGraph loop)    │
                                └──┬──────┬──────┬────┘
                                   │      │      │
                          ┌────────┘      │      └────────┐
                          ▼               ▼               ▼
                   ┌───────────┐  ┌────────────┐  ┌──────────┐
                   │  Tavily   │  │  MedGemma  │  │  Report  │
                   │  Search   │  │  Expert    │  │  Storage │
                   │  (HTTPS)  │  │  (Ollama)  │  │  (files) │
                   └───────────┘  └────────────┘  └──────────┘
```

## Key Architectural Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Agent framework | LangChain Deep Agents | Built-in planning, sub-agents, filesystem; built on LangGraph |
| Orchestrator model | Qwen3 via Ollama | Supports tool calling, runs locally, free |
| Medical specialist | MedGemma via Ollama | Purpose-built for medical text, no tool calling needed |
| Search provider | Tavily | LangChain integration, domain filtering, structured results |
| API streaming | Server-Sent Events | Simpler than WebSockets for unidirectional streaming |
| Report storage | Markdown files | Simple, portable, human-readable, no database needed |
| Frontend | React + Vite | Fast dev experience, TypeScript support, Tailwind for styling |

## Module Structure

```
src/
├── __init__.py
├── __main__.py              # Entry point
├── config/
│   ├── __init__.py
│   └── settings.py          # Pydantic BaseSettings
├── models/
│   ├── __init__.py
│   └── clients.py           # Qwen3 + MedGemma client factories
├── tools/
│   ├── __init__.py
│   ├── search.py            # Tavily search tool
│   └── medical.py           # Medical expert consultation tool
├── agent/
│   ├── __init__.py
│   └── research_agent.py    # create_deep_agent() assembly
├── services/
│   ├── __init__.py
│   └── report_service.py    # Report save/list/retrieve
└── api/
    ├── __init__.py
    ├── app.py               # FastAPI app factory
    ├── schemas.py            # Pydantic request/response models
    └── routes/
        ├── __init__.py
        ├── health.py         # GET /api/health
        ├── research.py       # POST /api/research (SSE)
        └── reports.py        # GET /api/reports

frontend/
├── src/
│   ├── App.tsx
│   ├── components/
│   │   ├── ResearchInput.tsx
│   │   ├── ProgressLog.tsx
│   │   ├── ReportViewer.tsx
│   │   └── HistorySidebar.tsx
│   ├── api/
│   │   └── client.ts
│   └── types/
│       └── index.ts
├── package.json
├── tsconfig.json
├── tailwind.config.js
└── vite.config.ts
```
