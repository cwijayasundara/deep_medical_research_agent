# STORY-010: React Project Setup and Layout

## Story
As a **frontend developer**, I want the React project initialized with TypeScript, Tailwind, and a basic layout, so that I can build the research UI on a solid foundation.

## Expertise
frontend

## Story Points
2

## Dependencies
- STORY-007 (FastAPI app running for API proxy)

## Acceptance Criteria

### AC-1: React project is bootstrapped with Vite
- **Given** the repository
- **When** a developer runs `npm install && npm run dev` in the `frontend/` directory
- **Then** the React app starts on `http://localhost:5173`
- **And** TypeScript strict mode is enabled
- **And** Tailwind CSS is configured

### AC-2: Basic layout is rendered
- **Given** the app is running
- **When** the user visits the root URL
- **Then** a layout with a header ("Deep Medical Research Agent"), main content area, and sidebar is displayed
- **And** the layout is responsive

### AC-3: API client is configured
- **Given** the frontend project
- **When** the API client module is imported
- **Then** it points to `http://localhost:8000/api` by default
- **And** the base URL is configurable via environment variable `VITE_API_URL`

### AC-4: Health check is displayed
- **Given** the backend is running
- **When** the frontend loads
- **Then** a status indicator shows the backend connection status (green = connected, red = disconnected)

## Technical Notes
- Directory: `frontend/`
- Use Vite for React 18 + TypeScript
- Tailwind CSS v4
- API client: simple fetch wrapper (no heavy HTTP library needed)
- Define `API_BASE_URL` constant from `import.meta.env.VITE_API_URL`
