/** Hook for managing research state with SSE streaming. */

import { useCallback, useRef, useState } from "react";
import {
  EVENT_TYPE_ERROR,
  EVENT_TYPE_PROGRESS,
  EVENT_TYPE_RESULT,
  buildResearchUrl,
  parseSSEEvent,
} from "../lib/research-api.ts";

const ABORT_ERROR_NAME = "AbortError";
const UNKNOWN_ERROR_MESSAGE = "An unexpected error occurred";

export interface ResearchReport {
  content: string;
  filename: string;
}

interface ResearchState {
  isLoading: boolean;
  progressMessages: string[];
  report: ResearchReport | null;
  error: string | null;
}

const INITIAL_STATE: ResearchState = {
  isLoading: false,
  progressMessages: [],
  report: null,
  error: null,
};

async function processSSEStream(
  reader: ReadableStreamDefaultReader<Uint8Array>,
  onProgress: (msg: string) => void,
  onResult: (report: ResearchReport) => void,
  onError: (msg: string) => void,
): Promise<void> {
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() ?? "";

    for (const line of lines) {
      const trimmed = line.trim();
      if (!trimmed) continue;

      const event = parseSSEEvent(trimmed);
      if (!event) continue;

      if (event.type === EVENT_TYPE_PROGRESS) {
        onProgress(event.data);
      } else if (event.type === EVENT_TYPE_RESULT) {
        onResult({ content: event.data, filename: event.filename ?? "" });
      } else if (event.type === EVENT_TYPE_ERROR) {
        onError(event.data);
      }
    }
  }
}

export function useResearch() {
  const [state, setState] = useState<ResearchState>(INITIAL_STATE);
  const abortRef = useRef<AbortController | null>(null);

  const startResearch = useCallback(async (query: string) => {
    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;

    setState({
      isLoading: true,
      progressMessages: [],
      report: null,
      error: null,
    });

    try {
      const response = await fetch(buildResearchUrl(), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query }),
        signal: controller.signal,
      });

      if (!response.ok || !response.body) {
        setState((prev) => ({
          ...prev,
          isLoading: false,
          error: `Request failed with status ${response.status}`,
        }));
        return;
      }

      const reader = response.body.getReader();

      await processSSEStream(
        reader,
        (msg) =>
          setState((prev) => ({
            ...prev,
            progressMessages: [...prev.progressMessages, msg],
          })),
        (report) =>
          setState((prev) => ({
            ...prev,
            isLoading: false,
            report,
          })),
        (errorMsg) =>
          setState((prev) => ({
            ...prev,
            isLoading: false,
            error: errorMsg,
          })),
      );

      setState((prev) => ({ ...prev, isLoading: false }));
    } catch (err) {
      if (err instanceof DOMException && err.name === ABORT_ERROR_NAME) {
        setState((prev) => ({ ...prev, isLoading: false }));
        return;
      }
      setState((prev) => ({
        ...prev,
        isLoading: false,
        error: err instanceof Error ? err.message : UNKNOWN_ERROR_MESSAGE,
      }));
    }
  }, []);

  const stopResearch = useCallback(() => {
    abortRef.current?.abort();
    setState((prev) => ({ ...prev, isLoading: false }));
  }, []);

  return {
    ...state,
    startResearch,
    stopResearch,
  };
}
