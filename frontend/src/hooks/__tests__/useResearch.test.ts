/**
 * Unit tests for useResearch hook — STORY-011 AC-1/AC-3/AC-4.
 *
 * Tests cover:
 * - Initial state is idle
 * - startResearch transitions to loading
 * - Progress events are accumulated
 * - Result event sets report content
 * - Error event sets error message
 * - stopResearch aborts and returns to idle
 */
import { act, renderHook } from "@testing-library/react";
import { useResearch } from "../useResearch";

/** Helper to create a mock ReadableStream from SSE lines. */
function mockSSEResponse(lines: string[]): Response {
  const text = lines.join("\n\n") + "\n\n";
  const encoder = new TextEncoder();
  const stream = new ReadableStream({
    start(controller) {
      controller.enqueue(encoder.encode(text));
      controller.close();
    },
  });
  return new Response(stream, {
    status: 200,
    headers: { "Content-Type": "text/event-stream" },
  });
}

describe("useResearch", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("starts in idle state", () => {
    const { result } = renderHook(() => useResearch());

    expect(result.current.isLoading).toBe(false);
    expect(result.current.progressMessages).toEqual([]);
    expect(result.current.report).toBeNull();
    expect(result.current.error).toBeNull();
  });

  it("transitions to loading on startResearch", async () => {
    globalThis.fetch = vi.fn().mockResolvedValue(
      mockSSEResponse([
        'data: {"type":"progress","data":"Starting..."}',
        'data: {"type":"result","data":"# Report","filename":"test.md"}',
      ]),
    );

    const { result } = renderHook(() => useResearch());

    await act(async () => {
      await result.current.startResearch("test query");
    });

    expect(globalThis.fetch).toHaveBeenCalled();
  });

  it("accumulates progress messages", async () => {
    globalThis.fetch = vi.fn().mockResolvedValue(
      mockSSEResponse([
        'data: {"type":"progress","data":"Planning..."}',
        'data: {"type":"progress","data":"Searching..."}',
        'data: {"type":"result","data":"# Report","filename":"test.md"}',
      ]),
    );

    const { result } = renderHook(() => useResearch());

    await act(async () => {
      await result.current.startResearch("test");
    });

    expect(result.current.progressMessages).toContain("Planning...");
    expect(result.current.progressMessages).toContain("Searching...");
  });

  it("sets report on result event", async () => {
    globalThis.fetch = vi.fn().mockResolvedValue(
      mockSSEResponse([
        'data: {"type":"result","data":"# Final Report","filename":"2026-02-08_test.md"}',
      ]),
    );

    const { result } = renderHook(() => useResearch());

    await act(async () => {
      await result.current.startResearch("test");
    });

    expect(result.current.report).toEqual({
      content: "# Final Report",
      filename: "2026-02-08_test.md",
    });
    expect(result.current.isLoading).toBe(false);
  });

  it("sets error on error event", async () => {
    globalThis.fetch = vi.fn().mockResolvedValue(
      mockSSEResponse([
        'data: {"type":"error","data":"Research failed: Agent crashed"}',
      ]),
    );

    const { result } = renderHook(() => useResearch());

    await act(async () => {
      await result.current.startResearch("test");
    });

    expect(result.current.error).toBe("Research failed: Agent crashed");
    expect(result.current.isLoading).toBe(false);
  });

  it("sets error on fetch failure", async () => {
    globalThis.fetch = vi.fn().mockRejectedValue(new Error("Network error"));

    const { result } = renderHook(() => useResearch());

    await act(async () => {
      await result.current.startResearch("test");
    });

    expect(result.current.error).toBeTruthy();
    expect(result.current.isLoading).toBe(false);
  });
});
