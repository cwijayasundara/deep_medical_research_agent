/**
 * Unit tests for ProgressLog component — STORY-011 AC-2.
 *
 * Tests cover:
 * - Renders progress messages
 * - Shows loading spinner when active
 * - Hides spinner when not active
 * - Renders empty state gracefully
 */
import { render, screen } from "@testing-library/react";
import { ProgressLog } from "../ProgressLog";

describe("ProgressLog", () => {
  it("renders progress messages", () => {
    const messages = ["Planning research...", "Searching for papers..."];
    render(<ProgressLog messages={messages} isActive={true} />);

    expect(screen.getByText("Planning research...")).toBeInTheDocument();
    expect(screen.getByText("Searching for papers...")).toBeInTheDocument();
  });

  it("shows loading spinner when active", () => {
    render(<ProgressLog messages={["Working..."]} isActive={true} />);
    expect(screen.getByTestId("progress-spinner")).toBeInTheDocument();
  });

  it("hides spinner when not active", () => {
    render(<ProgressLog messages={["Done"]} isActive={false} />);
    expect(screen.queryByTestId("progress-spinner")).not.toBeInTheDocument();
  });

  it("renders empty state without errors", () => {
    render(<ProgressLog messages={[]} isActive={false} />);
    expect(screen.queryByRole("list")).toBeInTheDocument();
  });

  it("renders messages as list items", () => {
    const messages = ["Step 1", "Step 2", "Step 3"];
    render(<ProgressLog messages={messages} isActive={false} />);
    expect(screen.getAllByRole("listitem")).toHaveLength(3);
  });
});
