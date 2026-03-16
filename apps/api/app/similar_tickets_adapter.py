from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class SimilarTicketResult:
    ticket_id: str
    subject: str
    similarity_score: float
    snippet: str
    resolution_summary: str
    draft_suggested_answer: str


class SimilarTicketsAdapter(Protocol):
    def find_similar_tickets(self, query: str) -> list[SimilarTicketResult]:
        """Return similar ticket matches for the provided issue text."""
