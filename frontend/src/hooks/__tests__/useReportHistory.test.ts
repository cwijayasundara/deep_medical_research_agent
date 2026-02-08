/**
 * Unit tests for useReportHistory hook — STORY-012.
 *
 * Tests cover:
 * - Fetches reports on mount
 * - Loads a single report by id
 * - Handles fetch errors gracefully
 * - Adds new report to history optimistically
 */
import { act, renderHook, waitFor } from "@testing-library/react";

import { useReportHistory } from "../useReportHistory";

const MOCK_SUMMARIES = [
  { id: "report-001", query: "diabetes treatment", timestamp: "2025-01-15T10:30:00" },
  { id: "report-002", query: "heart disease", timestamp: "2025-01-14T08:00:00" },
];

const MOCK_DETAIL = {
  id: "report-001",
  query: "diabetes treatment",
  timestamp: "2025-01-15T10:30:00",
  content: "# Diabetes Treatment\n\nResearch findings...",
  models_used: null,
};

describe("useReportHistory", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("fetches reports on mount", async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(MOCK_SUMMARIES),
    });

    const { result } = renderHook(() => useReportHistory());

    await waitFor(() => {
      expect(result.current.reports).toEqual(MOCK_SUMMARIES);
    });
  });

  it("sets isLoading true while fetching", () => {
    globalThis.fetch = vi.fn().mockReturnValue(new Promise(() => {}));

    const { result } = renderHook(() => useReportHistory());
    expect(result.current.isLoadingHistory).toBe(true);
  });

  it("handles fetch error gracefully", async () => {
    globalThis.fetch = vi.fn().mockRejectedValue(new Error("Network error"));

    const { result } = renderHook(() => useReportHistory());

    await waitFor(() => {
      expect(result.current.isLoadingHistory).toBe(false);
    });
    expect(result.current.reports).toEqual([]);
  });

  it("loads a report by id via selectReport", async () => {
    globalThis.fetch = vi
      .fn()
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(MOCK_SUMMARIES),
      })
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(MOCK_DETAIL),
      });

    const { result } = renderHook(() => useReportHistory());

    await waitFor(() => {
      expect(result.current.reports).toHaveLength(2);
    });

    await act(async () => {
      await result.current.selectReport("report-001");
    });

    expect(result.current.selectedReport).toEqual(MOCK_DETAIL);
    expect(result.current.selectedReportId).toBe("report-001");
  });

  it("sets selectedReport to null when selectReport fails", async () => {
    globalThis.fetch = vi
      .fn()
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(MOCK_SUMMARIES),
      })
      .mockResolvedValueOnce({
        ok: false,
        status: 404,
      });

    const { result } = renderHook(() => useReportHistory());

    await waitFor(() => {
      expect(result.current.reports).toHaveLength(2);
    });

    await act(async () => {
      await result.current.selectReport("nonexistent");
    });

    expect(result.current.selectedReport).toBeNull();
  });

  it("adds new report to history via addReport", async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(MOCK_SUMMARIES),
    });

    const { result } = renderHook(() => useReportHistory());

    await waitFor(() => {
      expect(result.current.reports).toHaveLength(2);
    });

    const newReport = {
      id: "report-003",
      query: "cancer immunotherapy",
      timestamp: "2025-01-16T09:00:00",
    };

    act(() => {
      result.current.addReport(newReport);
    });

    expect(result.current.reports[0]).toEqual(newReport);
    expect(result.current.reports).toHaveLength(3);
  });

  it("clears selected report via clearSelection", async () => {
    globalThis.fetch = vi
      .fn()
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(MOCK_SUMMARIES),
      })
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(MOCK_DETAIL),
      });

    const { result } = renderHook(() => useReportHistory());

    await waitFor(() => {
      expect(result.current.reports).toHaveLength(2);
    });

    await act(async () => {
      await result.current.selectReport("report-001");
    });
    expect(result.current.selectedReport).not.toBeNull();

    act(() => {
      result.current.clearSelection();
    });

    expect(result.current.selectedReport).toBeNull();
    expect(result.current.selectedReportId).toBeNull();
  });
});
