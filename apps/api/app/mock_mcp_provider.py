from __future__ import annotations

from .mcp_provider import (
    McpProvider,
    McpProviderNotFoundError,
    SimilarCaseResult,
    TicketRecord,
)
from .mock_data import MOCK_TICKETS


class MockMcpProvider(McpProvider):
    """In-memory MCP provider for local development and tests."""

    def search_tickets(self, query: str) -> list[TicketRecord]:
        tokens = self._tokenize(query)

        def score(ticket: dict) -> int:
            haystack = self._ticket_haystack(ticket)
            return sum(1 for token in tokens if token in haystack)

        ranked = sorted(MOCK_TICKETS, key=score, reverse=True)
        return [self._to_ticket_record(ticket) for ticket in ranked]

    def get_ticket_details(self, ticket_id: str) -> TicketRecord:
        for ticket in MOCK_TICKETS:
            if ticket["ticketId"] == ticket_id:
                return self._to_ticket_record(ticket)
        raise McpProviderNotFoundError(ticket_id)

    def find_similar_cases(self, query: str) -> list[SimilarCaseResult]:
        tokens = self._tokenize(query)

        def score(ticket: dict) -> float:
            haystack = self._ticket_haystack(ticket)
            matches = sum(1 for token in tokens if token in haystack)
            if not tokens:
                return round(ticket["confidence"] * 0.3, 2)
            keyword_score = matches / len(tokens)
            return round((keyword_score * 0.7) + (ticket["confidence"] * 0.3), 2)

        ranked = sorted(MOCK_TICKETS, key=score, reverse=True)
        return [
            SimilarCaseResult(
                ticket_id=ticket["ticketId"],
                subject=ticket["subject"],
                similarity_score=score(ticket),
                snippet=ticket["snippet"],
                resolution_summary=ticket["resolution"],
                draft_suggested_answer=(
                    "Thanks for the report. Based on a similar resolved case, we can "
                    f"{ticket['resolution'].lower()}"
                ),
            )
            for ticket in ranked
        ]

    @staticmethod
    def _tokenize(value: str) -> list[str]:
        return [token for token in value.lower().split() if token]

    @staticmethod
    def _ticket_haystack(ticket: dict) -> str:
        return f"{ticket['subject']} {ticket['snippet']} {ticket['resolution']}".lower()

    @staticmethod
    def _to_ticket_record(ticket: dict) -> TicketRecord:
        return TicketRecord(
            ticket_id=ticket["ticketId"],
            subject=ticket["subject"],
            snippet=ticket["snippet"],
            resolution_summary=ticket["resolution"],
            confidence=ticket["confidence"],
        )
