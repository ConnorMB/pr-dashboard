import { describe, expect, it } from "vitest";
import { parseRepoInput } from "./parseRepoInput";

describe("parseRepoInput", () => {
  it("parses an owner/repo shorthand", () => {
    expect(parseRepoInput("facebook/react")).toEqual({ owner: "facebook", name: "react" });
  });

  it("parses a full github.com URL", () => {
    expect(parseRepoInput("https://github.com/facebook/react")).toEqual({
      owner: "facebook",
      name: "react",
    });
  });

  it("parses a github.com URL with a trailing slash", () => {
    expect(parseRepoInput("https://github.com/facebook/react/")).toEqual({
      owner: "facebook",
      name: "react",
    });
  });

  it("parses a github.com URL with a .git suffix", () => {
    expect(parseRepoInput("https://github.com/facebook/react.git")).toEqual({
      owner: "facebook",
      name: "react",
    });
  });

  it("trims surrounding whitespace", () => {
    expect(parseRepoInput("  facebook/react  ")).toEqual({ owner: "facebook", name: "react" });
  });

  it("returns null for input with no slash", () => {
    expect(parseRepoInput("react")).toBeNull();
  });

  it("returns null for empty input", () => {
    expect(parseRepoInput("")).toBeNull();
  });
});