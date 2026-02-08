# STORY-003: Tavily Search Tool

## Story
As a **researcher**, I want the agent to search the internet for medical information, so that I get current, relevant results from trusted medical sources.

## Expertise
backend

## Story Points
2

## Dependencies
- STORY-001 (Settings with TAVILY_API_KEY)

## Acceptance Criteria

### AC-1: Tavily search tool is created with medical domain filtering
- **Given** a valid Tavily API key in settings
- **When** the search tool factory `create_search_tool(settings)` is called
- **Then** a `TavilySearch` tool is returned configured with `max_results=5`, `search_depth="advanced"`
- **And** trusted medical domains are included by default (PubMed, Nature, Lancet, NEJM)

### AC-2: Search returns structured results
- **Given** a configured Tavily search tool
- **When** it is invoked with query "latest cancer immunotherapy research"
- **Then** results include title, URL, and content snippet for each result
- **And** results are returned as a formatted string suitable for LLM consumption

### AC-3: Search handles API errors gracefully
- **Given** an invalid or expired Tavily API key
- **When** the search tool is invoked
- **Then** a clear error message is returned (not a raw exception)
- **And** the error is logged at ERROR level with the exception details

### AC-4: Domain filtering is configurable
- **Given** settings with `TAVILY_INCLUDE_DOMAINS` set to a custom list
- **When** the search tool factory is called
- **Then** the tool uses the custom domain list instead of defaults

## Technical Notes
- Module: `src/tools/search.py`
- Use `TavilySearch` from `langchain_tavily`
- Define `DEFAULT_MEDICAL_DOMAINS` constant with trusted sources
- Define `DEFAULT_MAX_RESULTS = 5` and `DEFAULT_SEARCH_DEPTH = "advanced"`
