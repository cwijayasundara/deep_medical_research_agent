/**
 * Unit tests for ResearchInput component — STORY-011 AC-1.
 *
 * Tests cover:
 * - Renders input field and submit button
 * - Calls onSubmit with query text
 * - Submit via Enter key
 * - Input disabled when loading
 * - Stop button visible when loading
 * - Empty query does not trigger submit
 */
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { ResearchInput } from "../ResearchInput";

describe("ResearchInput", () => {
  it("renders a text input and Research button", () => {
    render(<ResearchInput onSubmit={() => {}} onStop={() => {}} isLoading={false} />);
    expect(screen.getByRole("textbox")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /research/i })).toBeInTheDocument();
  });

  it("calls onSubmit with the query when button is clicked", async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn();
    render(<ResearchInput onSubmit={onSubmit} onStop={() => {}} isLoading={false} />);

    await user.type(screen.getByRole("textbox"), "CRISPR gene therapy");
    await user.click(screen.getByRole("button", { name: /research/i }));

    expect(onSubmit).toHaveBeenCalledWith("CRISPR gene therapy");
  });

  it("calls onSubmit when Enter is pressed", async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn();
    render(<ResearchInput onSubmit={onSubmit} onStop={() => {}} isLoading={false} />);

    await user.type(screen.getByRole("textbox"), "cancer immunotherapy{Enter}");

    expect(onSubmit).toHaveBeenCalledWith("cancer immunotherapy");
  });

  it("disables input when isLoading is true", () => {
    render(<ResearchInput onSubmit={() => {}} onStop={() => {}} isLoading={true} />);
    expect(screen.getByRole("textbox")).toBeDisabled();
  });

  it("shows Stop button when isLoading is true", () => {
    render(<ResearchInput onSubmit={() => {}} onStop={() => {}} isLoading={true} />);
    expect(screen.getByRole("button", { name: /stop/i })).toBeInTheDocument();
  });

  it("hides Research button when isLoading is true", () => {
    render(<ResearchInput onSubmit={() => {}} onStop={() => {}} isLoading={true} />);
    expect(screen.queryByRole("button", { name: /research/i })).not.toBeInTheDocument();
  });

  it("calls onStop when Stop button is clicked", async () => {
    const user = userEvent.setup();
    const onStop = vi.fn();
    render(<ResearchInput onSubmit={() => {}} onStop={onStop} isLoading={true} />);

    await user.click(screen.getByRole("button", { name: /stop/i }));

    expect(onStop).toHaveBeenCalled();
  });

  it("does not submit empty query", async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn();
    render(<ResearchInput onSubmit={onSubmit} onStop={() => {}} isLoading={false} />);

    await user.click(screen.getByRole("button", { name: /research/i }));

    expect(onSubmit).not.toHaveBeenCalled();
  });
});
