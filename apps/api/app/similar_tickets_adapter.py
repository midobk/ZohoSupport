from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, TypedDict


class HistoricalTicket(TypedDict):
    ticketId: str
    subject: str
    confidence: float
    snippet: str
    resolution: str


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

    def __init__(self, mock_tickets: list[HistoricalTicket]) -> None:
        self._mock_tickets = mock_tickets

    def find_similar_tickets(self, issue_text: str) -> list[SimilarTicketResult]:
        query_tokens = _tokenize(issue_text)

        def rank_ticket(ticket: HistoricalTicket) -> float:
            searchable_tokens = _tokenize(f"{ticket['subject']} {ticket['snippet']}")
            overlap = len(query_tokens.intersection(searchable_tokens))
            token_boost = min(0.25, overlap * 0.08)
            return min(0.99, max(0.0, float(ticket["confidence"]) + token_boost))

        ranked = sorted(self._mock_tickets, key=rank_ticket, reverse=True)

        return [
            SimilarTicketResult(
                ticket_id=ticket["ticketId"],
                subject=ticket["subject"],
                similarity_score=round(rank_ticket(ticket), 2),
                resolution_summary=_summarize_resolution(ticket["resolution"]),
                draft_suggested_answer=(
                    "A similar case was resolved by "
                    f"{_summarize_resolution(ticket['resolution']).lower()}"
                ),
            )
            for ticket in ranked
        ]


def _tokenize(text: str) -> set[str]:
    return {token for token in text.lower().replace("-", " ").split() if token}


def _summarize_resolution(resolution: str) -> str:
    first_sentence = resolution.split(".")[0].strip()
    summary = first_sentence if first_sentence else resolution.strip()
    if len(summary) <= 120:
        return summary
    return f"{summary[:117].rstrip()}..."
