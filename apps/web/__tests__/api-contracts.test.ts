import { fetchAnswer, fetchSimilarTickets } from "../lib/api";

describe("API contract validation", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("parses valid answer response", async () => {
    vi.spyOn(global, "fetch").mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        answer: "Use Zoho directory reset",
        confidenceLabel: "High",
        suggestedReply: "I've reset MFA for your account.",
        generation: {
          mode: "AI",
          label: "AI answer",
          description: "This answer was drafted with Google Gemini using the gemini-2.5-flash model after searching Zoho's official knowledge base.",
        },
        sources: [
          {
            id: "kb-101",
            title: "MFA reset",
            snippet: "Reset steps",
            url: "https://help.zoho.com/kb/mfa",
            sourceType: "OfficialKB",
            trustLabel: "Verified",
          },
        ],
      }),
    } as Response);

    await expect(fetchAnswer("How do I reset MFA?", "ai", "gemini-2.5-flash-lite", "unpaid")).resolves.toMatchObject({
      confidenceLabel: "High",
    });

    expect(global.fetch).toHaveBeenCalledWith(
      "/backend/api/answer",
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({
          question: "How do I reset MFA?",
          mode: "ai",
          model: "gemini-2.5-flash-lite",
          keyProfile: "unpaid",
        }),
      }),
    );
  });

  it("omits model from search-only answer requests", async () => {
    vi.spyOn(global, "fetch").mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        answer: "Use Zoho search results only",
        confidenceLabel: "Medium",
        suggestedReply: "Here is the official guidance I found.",
        generation: {
          mode: "Search",
          label: "Search answer",
          description: "Normal search was selected, so both the results and the answer were built from Zoho search without using AI.",
        },
        sources: [
          {
            id: "kb-201",
            title: "Search-only article",
            snippet: "Official search result",
            url: "https://help.zoho.com/portal/en/kb/desk/example",
            sourceType: "OfficialKB",
            trustLabel: "Verified",
          },
        ],
      }),
    } as Response);

    await expect(fetchAnswer("How do I reset MFA?", "search", "gemini-2.5-flash-lite", "paid")).resolves.toMatchObject({
      generation: { mode: "Search" },
    });

    expect(global.fetch).toHaveBeenCalledWith(
      "/backend/api/answer",
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({ question: "How do I reset MFA?", mode: "search" }),
      }),
    );
  });

  it("rejects invalid answer response", async () => {
    vi.spyOn(global, "fetch").mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        answer: "missing fields",
      }),
    } as Response);

    await expect(fetchAnswer("How do I reset MFA?", "search")).rejects.toThrow();
  });

  it("rejects invalid similar tickets response", async () => {
    vi.spyOn(global, "fetch").mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        tickets: [
          {
            ticketId: "T-100",
            subject: "Bad score",
            similarityScore: 2,
            snippet: "x",
            resolutionSummary: "y",
            draftSuggestedAnswer: "z",
          },
        ],
      }),
    } as Response);

    await expect(fetchSimilarTickets("MFA")).rejects.toThrow();
  });
});
