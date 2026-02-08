/** Research API streaming client for SSE consumption. */

import { API_BASE_URL } from "./api-client.ts";

const SSE_DATA_PREFIX = "data: ";
const RESEARCH_ENDPOINT = "/research";

export const EVENT_TYPE_PROGRESS = "progress" as const;
export const EVENT_TYPE_RESULT = "result" as const;
export const EVENT_TYPE_ERROR = "error" as const;

export interface StreamEvent {
  type: typeof EVENT_TYPE_PROGRESS | typeof EVENT_TYPE_RESULT | typeof EVENT_TYPE_ERROR;
  data: string;
  filename?: string;
}

export function parseSSEEvent(line: string): StreamEvent | null {
  if (!line.startsWith(SSE_DATA_PREFIX)) {
    return null;
  }

  const jsonStr = line.slice(SSE_DATA_PREFIX.length).trim();
  try {
    return JSON.parse(jsonStr) as StreamEvent;
  } catch {
    return null;
  }
}

export function buildResearchUrl(): string {
  return `${API_BASE_URL}${RESEARCH_ENDPOINT}`;
}
