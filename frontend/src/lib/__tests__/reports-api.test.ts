/**
 * Unit tests for reports API client — STORY-012.
 *
 * Tests cover:
 * - fetchReports returns list of report summaries
 * - fetchReports returns empty array on error
 * - fetchReportById returns full report detail
 * - fetchReportById returns null on 404
 * - fetchReportById returns null on network error
 */
import { fetchReportById, fetchReports } from "../reports-api";

const API_BASE_URL = "http://localhost:8000/api";

const MOCK_REPORTS = [
  { id: "report-001", query: "diabetes treatment", timestamp: "2025-01-15T10:30:00" },
  { id: "report-002", query: "heart disease", timestamp: "2025-01-14T08:00:00" },
];

const MOCK_REPORT_DETAIL = {
  id: "report-001",
  query: "diabetes treatment",
  timestamp: "2025-01-15T10:30:00",
  content: "# Diabetes Treatment\n\nResearch findings...",
  models_used: null,
};

describe("fetchReports", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("fetches and returns list of report summaries", async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(MOCK_REPORTS),
    });

    const result = await fetchReports();
    expect(result).toEqual(MOCK_REPORTS);
    expect(globalThis.fetch).toHaveBeenCalledWith(`${API_BASE_URL}/reports`);
  });

  it("returns empty array on network error", async () => {
    globalThis.fetch = vi.fn().mockRejectedValue(new Error("Network error"));

    const result = await fetchReports();
    expect(result).toEqual([]);
  });

  it("returns empty array on non-ok response", async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 500,
    });

    const result = await fetchReports();
    expect(result).toEqual([]);
  });
});

describe("fetchReportById", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("fetches and returns full report detail", async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(MOCK_REPORT_DETAIL),
    });

    const result = await fetchReportById("report-001");
    expect(result).toEqual(MOCK_REPORT_DETAIL);
    expect(globalThis.fetch).toHaveBeenCalledWith(
      `${API_BASE_URL}/reports/report-001`,
    );
  });

  it("returns null on 404", async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 404,
    });

    const result = await fetchReportById("nonexistent");
    expect(result).toBeNull();
  });

  it("returns null on network error", async () => {
    globalThis.fetch = vi.fn().mockRejectedValue(new Error("Network error"));

    const result = await fetchReportById("report-001");
    expect(result).toBeNull();
  });
});
