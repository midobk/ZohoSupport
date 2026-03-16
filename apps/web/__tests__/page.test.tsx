import React from "react";
import { fireEvent, render, screen } from "@testing-library/react";
import HomePage from "../app/page";
import * as api from "../lib/api";

describe("Home page", () => {
  it("renders app heading and tabs", () => {
    render(<HomePage />);
    expect(screen.getByText("Zoho Support Copilot")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Ask" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Similar Tickets" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Live Assist" })).toBeInTheDocument();
  });

  it("renders similar ticket fields after search", async () => {
    vi.spyOn(api, "fetchSimilarTickets").mockResolvedValue({
      tickets: [
        {
          ticketId: "TCK-1001",
          subject: "OTP expired for user",
          similarityScore: 0.92,
          resolutionSummary: "Reset MFA and synced device time.",
          draftSuggestedAnswer: "Please reset MFA and sync the device clock.",
        },
      ],
    });

    render(<HomePage />);

    fireEvent.click(screen.getByRole("button", { name: "Similar Tickets" }));
    expect(screen.getByLabelText("Search issue or error text")).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "Find tickets" }));

    expect(await screen.findByText("OTP expired for user")).toBeInTheDocument();
    expect(screen.getByText("Similarity score: 92%")).toBeInTheDocument();
    expect(screen.getByText(/Resolution summary:/)).toBeInTheDocument();
    expect(screen.getByText(/Draft suggested answer:/)).toBeInTheDocument();
  });
});
