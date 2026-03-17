import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import HomePage from "../app/page";
import { fetchAnswer, fetchSimilarTickets } from "../lib/api";

vi.mock("../lib/api", async () => {
  const actual = await vi.importActual<typeof import("../lib/api")>("../lib/api");
  return {
    ...actual,
    fetchAnswer: vi.fn(),
    fetchSimilarTickets: vi.fn(),
  };
});

describe("Home page", () => {
  it("renders workspace heading and workflows", () => {
    render(<HomePage />);
    expect(screen.getByText("Support Copilot Workspace")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Ask/ })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Similar Tickets/ })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Live Assist/ })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Normal search" })).toHaveAttribute("aria-pressed", "true");
    expect(screen.getByRole("button", { name: "AI-assisted" })).toHaveAttribute("aria-pressed", "false");
    expect(screen.queryByLabelText("Gemini model")).not.toBeInTheDocument();
  });

  it("shows ask validation error when question is empty", async () => {
    render(<HomePage />);

    fireEvent.change(screen.getByLabelText("Customer question"), { target: { value: "   " } });
    fireEvent.click(screen.getByRole("button", { name: "Get answer" }));

    expect(await screen.findByText("Please enter a customer question before requesting an answer.")).toBeInTheDocument();
  });

  it("renders ask results including confidence, sources, and suggested reply", async () => {
    vi.mocked(fetchAnswer).mockResolvedValueOnce({
      answer: "Reset MFA from Zoho Directory and re-enroll from a trusted device.",
      confidenceLabel: "High",
      suggestedReply: "I reset MFA. Please sign in and set up a new authenticator.",
      generation: {
        mode: "AI",
        label: "AI answer",
        description: "The results were retrieved from Zoho's normal search first. Then Google Gemini using the gemini-2.5-flash model drafted the answer text.",
      },
      sources: [
        {
          id: "kb-101",
          title: "Reset Multi-Factor Authentication for Locked Users",
          snippet: "Identity verification and MFA re-enrollment process.",
          url: "https://help.zoho.com/portal/en/kb/accounts/security/mfa-reset",
          sourceType: "OfficialKB",
          trustLabel: "Verified",
        },
        {
          id: "community-201",
          title: "Admin discussion about MFA lockouts",
          snippet: "Community members discuss MFA reset edge cases for locked users.",
          url: "https://help.zoho.com/portal/en/community/topic/admin-discussion-about-mfa-lockouts",
          sourceType: "CommunityPost",
          trustLabel: "Unverified",
        },
      ],
    });

    render(<HomePage />);
    fireEvent.click(screen.getByRole("button", { name: "Get answer" }));

    await waitFor(() => expect(fetchAnswer).toHaveBeenCalledWith("How do I reset MFA for a locked user?", "search", undefined));
    expect(await screen.findByText("Concise answer")).toBeInTheDocument();
    expect(screen.getByText("Confidence:", { exact: false })).toBeInTheDocument();
    expect(screen.getByText("Source Rail")).toBeInTheDocument();
    expect(screen.getByText("Verified")).toBeInTheDocument();
    expect(screen.getByText("Unverified")).toBeInTheDocument();
    expect(screen.getByText("Official + Community")).toBeInTheDocument();
    expect(screen.getByText("Suggested customer reply")).toBeInTheDocument();
    expect(screen.getByText("AI answer")).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "How these results were built" }));
    expect(screen.getByText(/Then Google Gemini using the gemini-2.5-flash model drafted the answer text/i)).toBeInTheDocument();
  });

  it("sends ai mode when the AI toggle is selected", async () => {
    vi.mocked(fetchAnswer).mockResolvedValueOnce({
      answer: "AI answer",
      confidenceLabel: "High",
      suggestedReply: "AI suggested reply",
      generation: {
        mode: "AI",
        label: "AI answer",
        description: "The results were retrieved from Zoho's normal search first. Then Google Gemini using the gemini-2.5-flash model drafted the answer text.",
      },
      sources: [
        {
          id: "kb-101",
          title: "Reset MFA article",
          snippet: "Reset steps",
          url: "https://help.zoho.com/portal/en/kb/accounts/security/mfa-reset",
          sourceType: "OfficialKB",
          trustLabel: "Verified",
        },
      ],
    });

    render(<HomePage />);
    fireEvent.click(screen.getByRole("button", { name: "AI-assisted" }));
    expect(screen.getByLabelText("Gemini model")).toHaveValue("gemini-2.5-flash-lite");
    fireEvent.click(screen.getByRole("button", { name: "Get answer" }));

    await waitFor(() => expect(fetchAnswer).toHaveBeenCalledWith("How do I reset MFA for a locked user?", "ai", "gemini-2.5-flash-lite"));
  });

  it("lets the user choose a different Gemini model", async () => {
    vi.mocked(fetchAnswer).mockResolvedValueOnce({
      answer: "AI answer",
      confidenceLabel: "High",
      suggestedReply: "AI suggested reply",
      generation: {
        mode: "AI",
        label: "AI answer",
        description: "The results were retrieved from Zoho's normal search first. Then Google Gemini using the gemini-2.5-pro model drafted the answer text.",
      },
      sources: [
        {
          id: "kb-101",
          title: "Reset MFA article",
          snippet: "Reset steps",
          url: "https://help.zoho.com/portal/en/kb/accounts/security/mfa-reset",
          sourceType: "OfficialKB",
          trustLabel: "Verified",
        },
      ],
    });

    render(<HomePage />);
    fireEvent.click(screen.getByRole("button", { name: "AI-assisted" }));
    fireEvent.change(screen.getByLabelText("Gemini model"), { target: { value: "gemini-2.5-pro" } });
    fireEvent.click(screen.getByRole("button", { name: "Get answer" }));

    await waitFor(() => expect(fetchAnswer).toHaveBeenCalledWith("How do I reset MFA for a locked user?", "ai", "gemini-2.5-pro"));
  });

  it("shows similar tickets validation error when query is empty", async () => {
    render(<HomePage />);

    fireEvent.click(screen.getByRole("button", { name: /Similar Tickets/ }));
    fireEvent.change(screen.getByLabelText("Issue or error text"), { target: { value: "   " } });
    fireEvent.click(screen.getByRole("button", { name: "Find tickets" }));

    expect(await screen.findByText("Please enter a search query before finding similar tickets.")).toBeInTheDocument();
    expect(fetchSimilarTickets).not.toHaveBeenCalled();
  });

  it("renders similar ticket score, resolution summary, and draft answer", async () => {
    vi.mocked(fetchSimilarTickets).mockResolvedValueOnce({
      tickets: [
        {
          ticketId: "T-123",
          subject: "MFA reset request",
          snippet: "User unable to complete MFA challenge.",
          resolutionSummary: "Reset MFA and ask user to enroll again.",
          draftSuggestedAnswer: "I reset your MFA. Please enroll your authenticator again.",
          similarityScore: 0.9,
        },
      ],
    });

    render(<HomePage />);
    fireEvent.click(screen.getByRole("button", { name: /Similar Tickets/ }));
    fireEvent.change(screen.getByLabelText("Issue or error text"), { target: { value: "  MFA reset issue  " } });
    fireEvent.click(screen.getByRole("button", { name: "Find tickets" }));

    await waitFor(() => expect(fetchSimilarTickets).toHaveBeenCalledWith("MFA reset issue"));
    expect(await screen.findAllByText("MFA reset request")).toHaveLength(2);
    expect(screen.getByText("Resolution summary: Reset MFA and ask user to enroll again.")).toBeInTheDocument();
    expect(screen.getByText("Draft suggested answer: I reset your MFA. Please enroll your authenticator again.")).toBeInTheDocument();
    expect(screen.getByText("90% match")).toBeInTheDocument();
  });
});
