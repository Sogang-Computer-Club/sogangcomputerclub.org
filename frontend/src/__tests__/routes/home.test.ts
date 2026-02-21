import { describe, it, expect } from "vitest";
import { render } from "@testing-library/svelte";
import Page from "../../routes/+page.svelte";

describe("Home Page (+page.svelte)", () => {
  it("should render the home page", () => {
    const { container } = render(Page);

    // Check if page is rendered
    expect(container).toBeTruthy();
  });

  it("should have a main element or content container", () => {
    const { container } = render(Page);

    // Most pages should have some content
    expect(container.firstChild).toBeTruthy();
  });
});
