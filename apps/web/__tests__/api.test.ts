import { describe, expect, it, vi, beforeEach, afterEach } from "vitest";
import { fetchAnswer, fetchSimilarTickets } from "../lib/api";

describe("api contract validation", () => {
  const mockFetch = vi.fn();

  beforeEach(() => {
    mockFetch.mockReset();
    vi.stubGlobal("fetch", mockFetch);
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("parses valid answer responses", async () => {
    mockFetch.mockResolvedValue({
      ok: true,
      json: async () => ({
        answer: "Resolved",
        sources: [
          {
            id: "kb-1",
            title: "Title",
            summary: "Summary",
            url: "https://help.zoho.com/kb",
          },
        ],
        draftReply: {
          message: "Draft message",
          confidenceLabel: "high",
        },
      }),
    });

    const result = await fetchAnswer("How do I reset MFA?");
    expect(result.draftReply.confidenceLabel).toBe("high");
  });

  it("throws on invalid ticket contract payload", async () => {
    mockFetch.mockResolvedValue({
      ok: true,
      json: async () => ({
        tickets: [{ ticketId: "1" }],
      }),
    });

    await expect(fetchSimilarTickets("mfa reset")).rejects.toThrow();
  });
});
