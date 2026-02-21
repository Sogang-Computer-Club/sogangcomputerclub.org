import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/svelte";
import Footer from "./Footer.svelte";

describe("Footer", () => {
  it("should render the footer with main content", () => {
    render(Footer);

    // Check if "Made By SGCC" text is rendered
    const madeByText = screen.getAllByText(/Made By SGCC/i);
    expect(madeByText.length).toBeGreaterThan(0);
  });

  it("should display contact information", () => {
    render(Footer);

    // Check email
    expect(
      screen.getAllByText(/sgccofficial2024@gmail.com/i).length,
    ).toBeGreaterThan(0);

    // Check president info
    expect(screen.getAllByText(/회장 강현우/i).length).toBeGreaterThan(0);
    expect(screen.getAllByText(/010-5572-0278/i).length).toBeGreaterThan(0);

    // Check vice president info
    expect(screen.getAllByText(/부회장 김무영/i).length).toBeGreaterThan(0);
    expect(screen.getAllByText(/010-8609-3075/i).length).toBeGreaterThan(0);
  });

  it("should display address information", () => {
    render(Footer);

    // Check address (different formats for desktop and mobile)
    const addressElements = screen.getAllByText(/서강대학교/i);
    expect(addressElements.length).toBeGreaterThan(0);
  });

  it("should display 2025 version creators", () => {
    render(Footer);

    // Check 2025 version text
    expect(screen.getAllByText(/2025 버전 제작자/i).length).toBeGreaterThan(0);

    // Check creators names
    expect(
      screen.getAllByText(/김대원 김주희 정주원 조인영 허완/i).length,
    ).toBeGreaterThan(0);
  });

  it("should have footer element", () => {
    render(Footer);

    const footer = document.querySelector("footer");
    expect(footer).toBeInTheDocument();
  });

  it("should have both desktop and mobile versions", () => {
    const { container } = render(Footer);

    // Desktop version should have specific class
    const desktopFooter = container.querySelector(".desktop\\:flex");
    expect(desktopFooter).toBeInTheDocument();

    // Mobile version should have specific class
    const mobileFooter = container.querySelector(".desktop\\:hidden");
    expect(mobileFooter).toBeInTheDocument();
  });
});
