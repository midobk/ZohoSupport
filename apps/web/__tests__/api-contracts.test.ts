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

    await expect(fetchAnswer("How do I reset MFA?")).resolves.toMatchObject({
      confidenceLabel: "High",
    });
  });

  it("rejects invalid answer response", async () => {
    vi.spyOn(global, "fetch").mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        answer: "missing fields",
      }),
    } as Response);

    await expect(fetchAnswer("How do I reset MFA?")).rejects.toThrow();
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
