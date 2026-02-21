import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/svelte";
import NavigationBar from "./NavigationBar.svelte";

describe("NavigationBar", () => {
  it("should render main navigation items", () => {
    render(NavigationBar);

    // Check main menu items
    expect(screen.getByText("About Us")).toBeInTheDocument();
    expect(screen.getByText("Notice")).toBeInTheDocument();
    expect(screen.getByText("Community")).toBeInTheDocument();

    // "Study" appears multiple times (main nav + submenu), check for at least one
    const studyElements = screen.getAllByText("Study");
    expect(studyElements.length).toBeGreaterThan(0);

    expect(screen.getByText("Library")).toBeInTheDocument();
  });

  it("should render About Us submenu links", () => {
    render(NavigationBar);

    // Check About Us submenu
    expect(screen.getByRole("link", { name: /인사말/i })).toBeInTheDocument();
    expect(
      screen.getByRole("link", { name: /활동\/행사/i }),
    ).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /SNS/i })).toBeInTheDocument();
  });

  it("should render Notice submenu links with correct hrefs", () => {
    render(NavigationBar);

    // Check Notice submenu links
    const noticeLinks = [
      { name: /공지/i, href: "/notice/announcements" },
      { name: /동아리방/i, href: "/notice/lighthouse" },
      { name: /달력/i, href: "/notice/calendar" },
      { name: /모집 안내/i, href: "/notice/recruitment" },
    ];

    noticeLinks.forEach(({ name, href }) => {
      const link = screen.getByRole("link", { name });
      expect(link).toBeInTheDocument();
      expect(link).toHaveAttribute("href", href);
    });
  });

  it("should render Community submenu links", () => {
    render(NavigationBar);

    // Check Community submenu
    const mediaLink = screen.getByRole("link", { name: /미디어관/i });
    expect(mediaLink).toBeInTheDocument();
    expect(mediaLink).toHaveAttribute("href", "/community/media");

    const feedLink = screen.getByRole("link", { name: /피드/i });
    expect(feedLink).toBeInTheDocument();
    expect(feedLink).toHaveAttribute("href", "/community/feed");
  });

  it("should render Study submenu link", () => {
    render(NavigationBar);

    const studyLinks = screen.getAllByRole("link", { name: /Study/i });
    expect(studyLinks.length).toBeGreaterThan(0);

    // Check at least one has the correct href
    const studyLink = studyLinks.find(
      (link) => link.getAttribute("href") === "/study",
    );
    expect(studyLink).toBeDefined();
  });

  it("should render Library submenu link", () => {
    render(NavigationBar);

    const libraryLink = screen.getByRole("link", { name: /SGCS Library/i });
    expect(libraryLink).toBeInTheDocument();
    expect(libraryLink).toHaveAttribute("href", "/library");
  });

  it("should render Login button", () => {
    render(NavigationBar);

    const loginLink = screen.getByRole("link", { name: /Login/i });
    expect(loginLink).toBeInTheDocument();
    expect(loginLink).toHaveAttribute("href", "/login");
  });

  it("should have navigation role", () => {
    render(NavigationBar);

    const nav = screen.getByRole("navigation");
    expect(nav).toBeInTheDocument();
  });

  it("should have all submenu links accessible", () => {
    render(NavigationBar);

    // Get all links
    const links = screen.getAllByRole("link");

    // Should have multiple links (main + submenu + login)
    expect(links.length).toBeGreaterThan(10);
  });
});
