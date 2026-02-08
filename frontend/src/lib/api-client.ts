/** API client for communicating with the backend. */

const DEFAULT_API_URL = "http://localhost:8000/api";

export const API_BASE_URL: string =
  import.meta.env.VITE_API_URL ?? DEFAULT_API_URL;

export interface HealthResponse {
  status: string;
  models: {
    orchestrator: string;
    medical: string;
  };
}

export async function fetchHealth(): Promise<HealthResponse | null> {
  try {
    const response = await fetch(`${API_BASE_URL}/health`);
    if (!response.ok) {
      return null;
    }
    return (await response.json()) as HealthResponse;
  } catch {
    return null;
  }
}
