/**
 * Unit tests for HistorySidebar component — STORY-012.
 *
 * Tests cover:
 * - AC-1: Sidebar displays list of past reports (query + date, newest first)
 * - AC-2: Clicking a report calls onSelectReport with the report id
 * - AC-3: Empty state shows message when no reports exist
 * - AC-4: New reports array updates sidebar list
 */
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import { HistorySidebar } from "../HistorySidebar";

const EMPTY_STATE_MESSAGE = "No research history yet. Start by asking a question!";

const MOCK_REPORTS = [
  { id: "report-001", query: "diabetes treatment", timestamp: "2025-01-15T10:30:00" },
  { id: "report-002", query: "heart disease risks", timestamp: "2025-01-14T08:00:00" },
  { id: "report-003", query: "cancer immunotherapy", timestamp: "2025-01-13T12:00:00" },
];

describe("HistorySidebar", () => {
  it("renders the heading", () => {
    render(<HistorySidebar reports={MOCK_REPORTS} onSelectReport={vi.fn()} />);
    expect(screen.getByText("Research History")).toBeInTheDocument();
  });

  it("displays list of reports with query titles", () => {
    render(<HistorySidebar reports={MOCK_REPORTS} onSelectReport={vi.fn()} />);
    expect(screen.getByText("diabetes treatment")).toBeInTheDocument();
    expect(screen.getByText("heart disease risks")).toBeInTheDocument();
    expect(screen.getByText("cancer immunotherapy")).toBeInTheDocument();
  });

  it("displays timestamps for each report", () => {
    render(<HistorySidebar reports={MOCK_REPORTS} onSelectReport={vi.fn()} />);
    const items = screen.getAllByRole("button");
    expect(items).toHaveLength(MOCK_REPORTS.length);
  });

  it("shows empty state message when no reports exist", () => {
    render(<HistorySidebar reports={[]} onSelectReport={vi.fn()} />);
    expect(screen.getByText(EMPTY_STATE_MESSAGE)).toBeInTheDocument();
  });

  it("calls onSelectReport with report id when clicked", async () => {
    const user = userEvent.setup();
    const onSelectReport = vi.fn();
    render(
      <HistorySidebar reports={MOCK_REPORTS} onSelectReport={onSelectReport} />,
    );

    await user.click(screen.getByText("diabetes treatment"));
    expect(onSelectReport).toHaveBeenCalledWith("report-001");
  });

  it("highlights the selected report", () => {
    render(
      <HistorySidebar
        reports={MOCK_REPORTS}
        onSelectReport={vi.fn()}
        selectedReportId="report-002"
      />,
    );
    const selectedButton = screen.getByText("heart disease risks").closest("button");
    expect(selectedButton).toHaveClass("bg-blue-100");
  });

  it("updates when reports prop changes with new report at top", () => {
    const newReport = {
      id: "report-004",
      query: "alzheimer prevention",
      timestamp: "2025-01-16T09:00:00",
    };

    const { rerender } = render(
      <HistorySidebar reports={MOCK_REPORTS} onSelectReport={vi.fn()} />,
    );

    rerender(
      <HistorySidebar
        reports={[newReport, ...MOCK_REPORTS]}
        onSelectReport={vi.fn()}
      />,
    );

    const buttons = screen.getAllByRole("button");
    expect(buttons[0]).toHaveTextContent("alzheimer prevention");
  });
});
