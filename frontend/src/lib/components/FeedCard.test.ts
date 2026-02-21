import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/svelte";
import FeedCard from "./FeedCard.svelte";

describe("FeedCard", () => {
  const mockData = {
    data: {
      id: 1,
      title: "Test Post Title",
      excerpt: "This is a test excerpt for the post",
      author: "Test Author",
      publishedAt: "2025-01-10",
      thumbnailUrl: "https://example.com/image.jpg",
      url: "/community/feed/test-post-1",
    },
  };

  it("should render feed card with all data", () => {
    render(FeedCard, { props: mockData });

    // Check title
    expect(screen.getByText("Test Post Title")).toBeInTheDocument();

    // Check excerpt
    expect(
      screen.getByText("This is a test excerpt for the post"),
    ).toBeInTheDocument();

    // Check author
    expect(screen.getByText("Test Author")).toBeInTheDocument();

    // Check published date
    expect(screen.getByText("2025-01-10")).toBeInTheDocument();
  });

  it("should render thumbnail image with correct src", () => {
    render(FeedCard, { props: mockData });

    const image = document.querySelector("img");
    expect(image).toBeInTheDocument();
    expect(image).toHaveAttribute("src", "https://example.com/image.jpg");
  });

  it("should render as a link with correct href", () => {
    render(FeedCard, { props: mockData });

    const link = screen.getByRole("link", { name: /Post Card/i });
    expect(link).toBeInTheDocument();
    expect(link).toHaveAttribute("href", "/community/feed/test-post-1");
  });

  it("should have accessible aria-label", () => {
    render(FeedCard, { props: mockData });

    const link = screen.getByLabelText(/Post Card/i);
    expect(link).toBeInTheDocument();
  });

  it("should display author and date with separator", () => {
    render(FeedCard, { props: mockData });

    // Check if separator is present
    const separator = screen.getByText("·");
    expect(separator).toBeInTheDocument();
  });

  it("should render with minimal data", () => {
    const minimalData = {
      data: {
        id: 2,
        title: "Minimal Title",
        excerpt: "",
        author: "",
        publishedAt: "",
        thumbnailUrl: "",
        url: "/test",
      },
    };

    render(FeedCard, { props: minimalData });

    expect(screen.getByText("Minimal Title")).toBeInTheDocument();
  });

  it("should have correct CSS classes for styling", () => {
    const { container } = render(FeedCard, { props: mockData });

    // Check main container has correct classes
    const link = container.querySelector("a");
    expect(link).toHaveClass("flex", "h-40", "items-center", "w-full");
  });
});
