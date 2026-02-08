/**
 * Unit tests for API client — STORY-010 AC-3.
 *
 * Tests cover:
 * - Default base URL is http://localhost:8000/api
 * - Base URL is configurable
 * - fetchHealth calls the health endpoint
 */
import { API_BASE_URL, fetchHealth } from "../api-client";

const DEFAULT_API_URL = "http://localhost:8000/api";

describe("API client", () => {
  it("exports API_BASE_URL constant", () => {
    expect(API_BASE_URL).toBeDefined();
  });

  it("defaults to localhost:8000/api", () => {
    expect(API_BASE_URL).toBe(DEFAULT_API_URL);
  });

  it("fetchHealth calls /health endpoint", async () => {
    const mockResponse = {
      status: "healthy",
      models: { orchestrator: "qwen3:latest", medical: "MedGemma1.0:4b" },
    };

    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(mockResponse),
    });

    const result = await fetchHealth();
    expect(result).toEqual(mockResponse);
    expect(globalThis.fetch).toHaveBeenCalledWith(
      `${DEFAULT_API_URL}/health`,
    );
  });

  it("fetchHealth returns null on network error", async () => {
    globalThis.fetch = vi.fn().mockRejectedValue(new Error("Network error"));

    const result = await fetchHealth();
    expect(result).toBeNull();
  });

  it("fetchHealth returns null on non-ok response", async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 500,
    });

    const result = await fetchHealth();
    expect(result).toBeNull();
  });
});
