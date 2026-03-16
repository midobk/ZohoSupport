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
    const fetchSpy = vi.spyOn(api, "fetchSimilarTickets").mockResolvedValue({
      tickets: [
        {
          ticketId: "TCK-1001",
          subject: "OTP expired for user",
          similarityScore: 0.92,
          resolutionSummary: "Reset MFA and synced device time",
          draftSuggestedAnswer: "A similar case was resolved by reset mfa and synced device time",
        },
      ],
    });

    render(<HomePage />);

    fireEvent.click(screen.getByRole("button", { name: "Similar Tickets" }));

    const input = screen.getByLabelText("Search issue or error text");
    fireEvent.change(input, { target: { value: "otp expired" } });
    fireEvent.click(screen.getByRole("button", { name: "Find tickets" }));

    expect(fetchSpy).toHaveBeenCalledWith("otp expired");
    expect(await screen.findByText("OTP expired for user")).toBeInTheDocument();
    expect(screen.getByText("Similarity score: 92%")).toBeInTheDocument();
    expect(screen.getByText(/Resolution summary:/)).toBeInTheDocument();
    expect(screen.getByText(/Draft suggested answer:/)).toBeInTheDocument();
  });

  it("shows validation error for short query", () => {
    const fetchSpy = vi.spyOn(api, "fetchSimilarTickets");
    render(<HomePage />);

    fireEvent.click(screen.getByRole("button", { name: "Similar Tickets" }));
    const input = screen.getByLabelText("Search issue or error text");
    fireEvent.change(input, { target: { value: "ot" } });
    fireEvent.click(screen.getByRole("button", { name: "Find tickets" }));

    expect(fetchSpy).not.toHaveBeenCalled();
    expect(screen.getByText("Please enter at least 3 characters.")).toBeInTheDocument();
  });
});
