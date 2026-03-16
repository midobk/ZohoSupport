from __future__ import annotations

from .mock_data import MOCK_TICKETS
from .similar_tickets_adapter import SimilarTicketResult, SimilarTicketsAdapter


class MockMcpSimilarTicketsAdapter(SimilarTicketsAdapter):
    """Demo MCP adapter backed by in-memory ticket examples."""

    def find_similar_tickets(self, query: str) -> list[SimilarTicketResult]:
        normalized_tokens = [token for token in query.lower().split() if token]

        def score_ticket(ticket: dict) -> float:
            haystack = f"{ticket['subject']} {ticket['snippet']} {ticket['resolution']}".lower()
            matches = sum(1 for token in normalized_tokens if token in haystack)
            if not normalized_tokens:
                return 0.0
            keyword_score = matches / len(normalized_tokens)
            return round((keyword_score * 0.7) + (ticket["confidence"] * 0.3), 2)

        ranked = sorted(MOCK_TICKETS, key=score_ticket, reverse=True)

        return [
            SimilarTicketResult(
                ticket_id=ticket["ticketId"],
                subject=ticket["subject"],
                similarity_score=score_ticket(ticket),
                snippet=ticket["snippet"],
                resolution_summary=ticket["resolution"],
                draft_suggested_answer=(
                    "Thanks for the report. Based on a similar resolved case, we can "
                    f"{ticket['resolution'].lower()}"
                ),
            )
            for ticket in ranked
        ]
