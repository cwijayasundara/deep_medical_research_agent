# Requirements: Deep Medical Research Agent

## Problem Statement

Medical researchers, clinicians, students, and general users need a tool to efficiently research medical topics by searching the web for current information and getting expert-level medical analysis. Currently, this requires manually searching multiple sources and interpreting findings without domain-specific AI assistance. This agent combines internet search capabilities with a specialized medical AI model to deliver comprehensive, well-structured research outputs.

## Target Users

- **Researchers**: Academic and clinical researchers synthesizing medical literature
- **Clinicians**: Doctors and nurses seeking evidence-based answers to clinical questions
- **Students**: Medical students studying topics and needing comprehensive summaries
- **General users**: Anyone seeking well-researched, reliable medical information

## Functional Requirements

### FR-1: Dual-Model Architecture
The agent uses two local Ollama models:
- **Qwen3:latest** as the orchestrator/base model (supports function/tool calling)
- **MedAIBase/MedGemma1.0:4b** as the medical specialist (invoked as a tool for medical analysis)

### FR-2: Internet Search via Tavily
- The agent can search the web using the Tavily API
- Search results are filtered and prioritized for medical relevance
- Supports configuring trusted medical domains (e.g., PubMed, Nature, Lancet, NEJM)

### FR-3: Medical Expert Consultation
- The orchestrator routes medical content to MedGemma for domain-specific analysis
- MedGemma provides: medical Q&A, clinical reasoning, terminology explanation, research comprehension
- All MedGemma responses include a disclaimer that outputs are not clinical advice

### FR-4: Deep Agent Framework
- Built on LangChain's `deepagents` framework (`create_deep_agent()`)
- Leverages built-in planning (todo tracking), filesystem, and sub-agent capabilities
- The orchestrator plans multi-step research workflows autonomously

### FR-5: Flexible Output Formats
The agent produces outputs based on the type of query:
- **Structured research reports**: Comprehensive markdown reports with sections, citations, and key findings
- **Direct Q&A answers**: Concise answers to specific medical questions with supporting evidence
- **Paper/source summaries**: Summaries of relevant research sources found during search

### FR-6: Report Persistence
- Research reports are saved as markdown files to a configurable local output directory
- File naming includes timestamp and topic slug (e.g., `2026-02-08_cancer-immunotherapy.md`)
- Each report includes metadata: query, timestamp, sources consulted, models used

### FR-7: Web UI
- React 18 + TypeScript frontend for interacting with the agent
- Input field for research queries
- Streaming display of agent progress (planning, searching, analyzing)
- Rendered markdown output for final reports
- History sidebar showing past research sessions (loaded from saved files)

### FR-8: REST API
- FastAPI backend exposing the research agent as an API
- `POST /api/research` — Submit a research query, returns streaming response
- `GET /api/reports` — List saved research reports
- `GET /api/reports/{id}` — Retrieve a specific saved report
- `GET /api/health` — Health check endpoint

## Non-Functional Requirements

### NFR-1: Performance
- Agent should produce a research report within 2-5 minutes for typical queries
- Web UI should stream intermediate progress (not wait for full completion)
- Ollama models run locally — performance depends on hardware

### NFR-2: Reliability
- Graceful degradation: if MedGemma is unavailable, the agent continues with Qwen3 only and notes the limitation
- Tavily API failures are caught and reported without crashing the agent
- All external calls (Ollama, Tavily) have timeouts and retry logic

### NFR-3: Security
- API keys (Tavily) loaded from environment variables, never hardcoded
- No patient data accepted or stored
- All outputs include medical disclaimer

### NFR-4: Observability
- Structured logging with `logging.getLogger(__name__)` in every module
- Log agent planning steps, tool invocations, and model calls at INFO level
- Log errors with full context at ERROR level

## Constraints

| Constraint | Value |
|------------|-------|
| Language | Python 3.12 |
| Backend framework | FastAPI |
| Frontend framework | React 18 + TypeScript + Tailwind |
| Agent framework | LangChain Deep Agents (`deepagents`) |
| Orchestrator model | Qwen3:latest (via Ollama) |
| Medical model | MedAIBase/MedGemma1.0:4b (via Ollama) |
| Search provider | Tavily API (`langchain-tavily`) |
| Deployment | Local/development only (no cloud deployment for v1) |
| Testing | pytest, TDD workflow, minimum 80% coverage |
| Report storage | Local filesystem (markdown files) |

## Out of Scope

- **Clinical diagnosis**: The agent must NOT provide diagnoses or treatment recommendations
- **Patient data handling**: No real patient data — no HIPAA/compliance scope
- **Medical image analysis**: Not in v1 (MedGemma supports it but deferred)
- **PDF paper upload/analysis**: Not in v1
- **PubMed API integration**: Not in v1 (Tavily web search covers PubMed results)
- **User authentication**: Not needed for local deployment
- **Database persistence**: Reports saved as files, not in a database
- **Cloud deployment**: Local only for v1

## Open Questions

1. Should the agent support follow-up questions within the same research session (multi-turn conversation)?
2. What is the maximum number of Tavily search calls per research query (cost control)?
3. Should the React UI support dark mode?
