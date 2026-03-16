from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class SimilarTicketResult:
    ticket_id: str
    subject: str
    similarity_score: float
    resolution_summary: str
    draft_suggested_answer: str


class SimilarTicketsAdapter(Protocol):
    def find_similar_tickets(self, issue_text: str) -> list[SimilarTicketResult]:
        """Return similar historical tickets for an issue text."""


class MockMcpSimilarTicketsAdapter:
    """Demo MCP adapter implementation that can be swapped for corporate MCP."""

    def __init__(self, mock_tickets: list[dict[str, str | float]]) -> None:
        self._mock_tickets = mock_tickets

    def find_similar_tickets(self, issue_text: str) -> list[SimilarTicketResult]:
        normalized_issue = issue_text.strip().lower()

        def calculate_similarity(ticket: dict[str, str | float]) -> float:
            subject = str(ticket["subject"]).lower()
            snippet = str(ticket["snippet"]).lower()
            base = float(ticket["confidence"])

            if normalized_issue and normalized_issue in f"{subject} {snippet}":
                return min(0.99, base + 0.07)
            return max(0.55, base - 0.08)

        ranked = sorted(self._mock_tickets, key=calculate_similarity, reverse=True)

        return [
            SimilarTicketResult(
                ticket_id=str(ticket["ticketId"]),
                subject=str(ticket["subject"]),
                similarity_score=round(calculate_similarity(ticket), 2),
                resolution_summary=str(ticket["resolution"]),
                draft_suggested_answer=(
                    "Based on a similar resolved case, "
                    f"{ticket['resolution']}"
                ),
            )
            for ticket in ranked
        ]
