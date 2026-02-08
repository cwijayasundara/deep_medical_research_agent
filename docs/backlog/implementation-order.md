# Implementation Order

Stories are ordered by dependency layer: foundation -> core -> integration -> UI.
Within each layer, stories are ordered by priority and dependency readiness.

## Layer 1: Foundation (no dependencies)

| Order | Story | Points | Epic | Description |
|-------|-------|--------|------|-------------|
| 1 | STORY-001 | 2 | foundation | Project configuration, dependencies, Settings class |

## Layer 2: Infrastructure (depends on Layer 1)

| Order | Story | Points | Epic | Description |
|-------|-------|--------|------|-------------|
| 2 | STORY-002 | 3 | foundation | Ollama model clients (Qwen3 + MedGemma) |
| 3 | STORY-003 | 2 | agent-core | Tavily search tool |
| 4 | STORY-006 | 2 | agent-core | Report persistence service |
| 5 | STORY-007 | 2 | api | FastAPI app and health endpoint |

## Layer 3: Core Agent (depends on Layer 2)

| Order | Story | Points | Epic | Description |
|-------|-------|--------|------|-------------|
| 6 | STORY-004 | 3 | agent-core | Medical expert consultation tool |
| 7 | STORY-005 | 5 | agent-core | Deep research agent assembly |

## Layer 4: API Integration (depends on Layer 3)

| Order | Story | Points | Epic | Description |
|-------|-------|--------|------|-------------|
| 8 | STORY-008 | 5 | api | Research API endpoint with streaming |
| 9 | STORY-009 | 2 | api | Reports API endpoints |

## Layer 5: Frontend (depends on Layer 4)

| Order | Story | Points | Epic | Description |
|-------|-------|--------|------|-------------|
| 10 | STORY-010 | 2 | frontend | React project setup and layout |
| 11 | STORY-011 | 5 | frontend | Research query input and streaming results |
| 12 | STORY-012 | 3 | frontend | Research history sidebar |

## Summary

| Metric | Value |
|--------|-------|
| Total stories | 12 |
| Total story points | 36 |
| Epics | 4 (foundation, agent-core, api, frontend) |
| Layers | 5 |
| Critical path | STORY-001 → 002 → 004 → 005 → 008 → 011 (23 points) |

## Parallelization Opportunities

After STORY-001 completes, the following can be worked in parallel:
- STORY-002 (model clients) and STORY-003 (search tool) and STORY-006 (reports) and STORY-007 (FastAPI app)

After STORY-005 and STORY-007 complete:
- STORY-008 (research endpoint) and STORY-009 (reports endpoint)

After STORY-008 and STORY-010 complete:
- STORY-011 (streaming UI) and STORY-012 (history sidebar)
