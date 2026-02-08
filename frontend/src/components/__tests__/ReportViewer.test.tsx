/**
 * Unit tests for ReportViewer component — STORY-011 AC-3.
 *
 * Tests cover:
 * - Renders markdown content
 * - Renders headings
 * - Shows nothing when content is empty
 * - Displays filename
 */
import { render, screen } from "@testing-library/react";
import { ReportViewer } from "../ReportViewer";

describe("ReportViewer", () => {
  it("renders markdown content", () => {
    render(<ReportViewer content="# Research Report" filename="report.md" />);
    expect(screen.getByText("Research Report")).toBeInTheDocument();
  });

  it("renders heading elements from markdown", () => {
    render(<ReportViewer content="# Main Title" filename="report.md" />);
    expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent(
      "Main Title",
    );
  });

  it("renders nothing when content is empty", () => {
    const { container } = render(
      <ReportViewer content="" filename="report.md" />,
    );
    expect(container.querySelector("article")).not.toBeInTheDocument();
  });

  it("renders nothing when content is null", () => {
    const { container } = render(
      <ReportViewer content={null} filename="report.md" />,
    );
    expect(container.querySelector("article")).not.toBeInTheDocument();
  });

  it("displays the filename", () => {
    render(
      <ReportViewer
        content="# Report"
        filename="2026-02-08_crispr-advances.md"
      />,
    );
    expect(
      screen.getByText(/2026-02-08_crispr-advances\.md/),
    ).toBeInTheDocument();
  });
});
