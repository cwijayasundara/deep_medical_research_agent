/**
 * Unit tests for HealthIndicator component — STORY-010 AC-4.
 *
 * Tests cover:
 * - Shows "Connected" when backend is healthy
 * - Shows "Disconnected" when backend is unreachable
 * - Displays a green indicator for connected state
 * - Displays a red indicator for disconnected state
 */
import { render, screen, waitFor } from "@testing-library/react";
import * as apiClient from "../../lib/api-client";
import { HealthIndicator } from "../HealthIndicator";

describe("HealthIndicator", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("shows connected when health check succeeds", async () => {
    vi.spyOn(apiClient, "fetchHealth").mockResolvedValue({
      status: "healthy",
      models: { orchestrator: "qwen3:latest", medical: "MedGemma1.0:4b" },
    });

    render(<HealthIndicator />);

    await waitFor(() => {
      expect(screen.getByText(/connected/i)).toBeInTheDocument();
    });
  });

  it("shows disconnected when health check fails", async () => {
    vi.spyOn(apiClient, "fetchHealth").mockResolvedValue(null);

    render(<HealthIndicator />);

    await waitFor(() => {
      expect(screen.getByText(/disconnected/i)).toBeInTheDocument();
    });
  });

  it("renders a status indicator element", async () => {
    vi.spyOn(apiClient, "fetchHealth").mockResolvedValue({
      status: "healthy",
      models: { orchestrator: "qwen3:latest", medical: "MedGemma1.0:4b" },
    });

    render(<HealthIndicator />);

    await waitFor(() => {
      expect(screen.getByTestId("health-indicator")).toBeInTheDocument();
    });
  });

  it("applies green styling when connected", async () => {
    vi.spyOn(apiClient, "fetchHealth").mockResolvedValue({
      status: "healthy",
      models: { orchestrator: "qwen3:latest", medical: "MedGemma1.0:4b" },
    });

    render(<HealthIndicator />);

    await waitFor(() => {
      const indicator = screen.getByTestId("health-dot");
      expect(indicator.className).toMatch(/green/);
    });
  });

  it("applies red styling when disconnected", async () => {
    vi.spyOn(apiClient, "fetchHealth").mockResolvedValue(null);

    render(<HealthIndicator />);

    await waitFor(() => {
      const indicator = screen.getByTestId("health-dot");
      expect(indicator.className).toMatch(/red/);
    });
  });
});
