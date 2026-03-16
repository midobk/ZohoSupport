import { render, screen } from "@testing-library/react";
import HomePage from "../app/page";

describe("Home page", () => {
  it("renders enterprise shell areas", () => {
    render(<HomePage />);

    expect(screen.getByText("Zoho Support Copilot")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Ask Copilot/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Historical Tickets/i })).toBeInTheDocument();
    expect(screen.getByText("Official Sources")).toBeInTheDocument();
  });

  it("shows empty state before queries run", () => {
    render(<HomePage />);
    expect(screen.getByText("No generated answer yet")).toBeInTheDocument();
    expect(screen.getByText("No official sources yet")).toBeInTheDocument();
  });
});
