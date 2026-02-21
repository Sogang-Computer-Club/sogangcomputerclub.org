import { describe, it, expect } from "vitest";
import { slugify } from "./slugify";

describe("slugify", () => {
  it("should convert English title to slug with id", () => {
    const result = slugify("Hello World", 123);
    expect(result).toBe("hello-world-123");
  });

  it("should convert Korean title to slug with id", () => {
    const result = slugify("안녕하세요 세상", 456);
    expect(result).toBe("안녕하세요-세상-456");
  });

  it("should handle multiple spaces", () => {
    const result = slugify("Hello    World", 789);
    expect(result).toBe("hello-world-789");
  });

  it("should remove special characters except Korean and hyphens", () => {
    const result = slugify("Hello! @World# $Test%", 111);
    expect(result).toBe("hello-world-test-111");
  });

  it("should trim leading and trailing spaces", () => {
    const result = slugify("  Hello World  ", 222);
    expect(result).toBe("hello-world-222");
  });

  it("should remove leading and trailing hyphens", () => {
    const result = slugify("---Hello World---", 333);
    expect(result).toBe("hello-world-333");
  });

  it("should handle mixed Korean and English", () => {
    const result = slugify("안녕 Hello 세상 World", 444);
    expect(result).toBe("안녕-hello-세상-world-444");
  });

  it("should handle empty string", () => {
    const result = slugify("", 555);
    expect(result).toBe("-555");
  });

  it("should handle only special characters", () => {
    const result = slugify("!@#$%^&*()", 666);
    expect(result).toBe("-666");
  });
});
