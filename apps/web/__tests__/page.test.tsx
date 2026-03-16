import { render, screen } from "@testing-library/react";
import HomePage from "../app/page";

describe("Home page", () => {
  it("renders app heading and tabs", () => {
    render(<HomePage />);
    expect(screen.getByText("Zoho Support Copilot")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Ask" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Similar Tickets" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Live Assist" })).toBeInTheDocument();
  });
});
