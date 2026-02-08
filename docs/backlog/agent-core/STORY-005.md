# STORY-005: Deep Research Agent Assembly

## Story
As a **user**, I want a research agent that plans multi-step research, searches the web, and consults a medical expert, so that I get comprehensive research reports on medical topics.

## Expertise
backend

## Story Points
5

## Dependencies
- STORY-002 (Ollama model clients)
- STORY-003 (Tavily search tool)
- STORY-004 (Medical expert consultation tool)

## Acceptance Criteria

### AC-1: Agent is created via create_deep_agent with all tools
- **Given** valid settings with Tavily API key and Ollama running
- **When** `create_research_agent(settings)` is called
- **Then** a compiled LangGraph agent is returned
- **And** it has the Tavily search tool and medical consultation tool bound
- **And** it uses Qwen3 as the orchestrator model

### AC-2: Agent plans research before executing
- **Given** a research query "What are the latest advances in CRISPR gene therapy?"
- **When** the agent is invoked
- **Then** the agent creates a research plan (using built-in todo tracking)
- **And** the plan includes steps like: search for information, analyze findings, synthesize report

### AC-3: Agent produces a structured research report
- **Given** a research query
- **When** the agent completes its research workflow
- **Then** the final output is a markdown-formatted report containing:
  - Title and query
  - Executive summary
  - Key findings (with citations/sources)
  - Detailed analysis
  - Sources consulted
  - Medical disclaimer

### AC-4: Agent system prompt enforces research-only behavior
- **Given** the agent's system prompt
- **When** a user asks for a clinical diagnosis or treatment recommendation
- **Then** the agent declines and explains it provides research information only
- **And** suggests consulting a healthcare professional

### AC-5: Agent handles tool failures without crashing
- **Given** Tavily search fails mid-research
- **When** the agent encounters the error
- **Then** the agent notes the limitation in its output
- **And** continues with available information rather than crashing

## Technical Notes
- Module: `src/agent/research_agent.py`
- Use `create_deep_agent()` from `deepagents`
- Define `RESEARCH_SYSTEM_PROMPT` constant with detailed research instructions
- The system prompt should include output format guidelines and anti-diagnosis rules
- Consider middleware: `ModelCallLimitMiddleware` to prevent runaway loops
