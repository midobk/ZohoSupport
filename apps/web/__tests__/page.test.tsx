import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import HomePage from "../app/page";
import { fetchAnswer } from "../lib/api";

vi.mock("../lib/api", async () => {
  const actual = await vi.importActual<typeof import("../lib/api")>("../lib/api");
  return {
    ...actual,
    fetchAnswer: vi.fn(),
  };
});

describe("Home page", () => {
  it("renders app heading and tabs", () => {
    render(<HomePage />);
    expect(screen.getByText("Zoho Support Copilot")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Ask" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Similar Tickets" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Live Assist" })).toBeInTheDocument();
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
      sources: [
        {
          id: "kb-101",
          title: "Reset Multi-Factor Authentication for Locked Users",
          snippet: "Identity verification and MFA re-enrollment process.",
          url: "https://help.zoho.com/portal/en/kb/accounts/security/mfa-reset",
        },
      ],
    });

    render(<HomePage />);
    fireEvent.click(screen.getByRole("button", { name: "Get answer" }));

    await waitFor(() => expect(fetchAnswer).toHaveBeenCalled());
    expect(await screen.findByText("Concise answer")).toBeInTheDocument();
    expect(screen.getByText("Confidence:", { exact: false })).toBeInTheDocument();
    expect(screen.getByText("Official sources")).toBeInTheDocument();
    expect(screen.getByText("Suggested customer reply")).toBeInTheDocument();
  });
});
