/**
 * Unit tests for Layout component — STORY-010 AC-2.
 *
 * Tests cover:
 * - Header displays app title
 * - Main content area is rendered
 * - Sidebar is rendered
 * - Layout uses semantic HTML elements
 */
import { render, screen } from "@testing-library/react";
import { Layout } from "../Layout";

const APP_TITLE = "Deep Medical Research Agent";

describe("Layout", () => {
  it("renders the app title in the header", () => {
    render(<Layout />);
    expect(screen.getByText(APP_TITLE)).toBeInTheDocument();
  });

  it("renders a header element", () => {
    render(<Layout />);
    expect(screen.getByRole("banner")).toBeInTheDocument();
  });

  it("renders a main content area", () => {
    render(<Layout />);
    expect(screen.getByRole("main")).toBeInTheDocument();
  });

  it("renders a sidebar", () => {
    render(<Layout />);
    expect(screen.getByRole("complementary")).toBeInTheDocument();
  });

  it("renders children in the main content area", () => {
    render(
      <Layout>
        <p>Test content</p>
      </Layout>,
    );
    const main = screen.getByRole("main");
    expect(main).toHaveTextContent("Test content");
  });
});
