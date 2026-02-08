/**
 * Unit tests for research API streaming client — STORY-011 AC-1/AC-2/AC-4.
 *
 * Tests cover:
 * - parseSSEEvent parses valid SSE data lines
 * - parseSSEEvent returns null for non-data lines
 * - StreamEvent type definitions
 */
import type { StreamEvent } from "../research-api";
import { parseSSEEvent } from "../research-api";

describe("parseSSEEvent", () => {
  it("parses a valid SSE data line", () => {
    const line = 'data: {"type":"progress","data":"Searching..."}';
    const event = parseSSEEvent(line);

    expect(event).not.toBeNull();
    expect(event?.type).toBe("progress");
    expect(event?.data).toBe("Searching...");
  });

  it("parses a result event with filename", () => {
    const line =
      'data: {"type":"result","data":"# Report","filename":"2026-02-08_test.md"}';
    const event = parseSSEEvent(line);

    expect(event?.type).toBe("result");
    expect(event?.data).toBe("# Report");
    expect(event?.filename).toBe("2026-02-08_test.md");
  });

  it("parses an error event", () => {
    const line = 'data: {"type":"error","data":"Research failed: timeout"}';
    const event = parseSSEEvent(line);

    expect(event?.type).toBe("error");
    expect(event?.data).toContain("Research failed");
  });

  it("returns null for non-data lines", () => {
    expect(parseSSEEvent("")).toBeNull();
    expect(parseSSEEvent("event: message")).toBeNull();
    expect(parseSSEEvent(": comment")).toBeNull();
  });

  it("returns null for invalid JSON", () => {
    expect(parseSSEEvent("data: not-json")).toBeNull();
  });
});

describe("StreamEvent type", () => {
  it("accepts progress, result, and error types", () => {
    const events: StreamEvent[] = [
      { type: "progress", data: "Working..." },
      { type: "result", data: "# Report", filename: "report.md" },
      { type: "error", data: "Failed" },
    ];
    expect(events).toHaveLength(3);
  });
});
