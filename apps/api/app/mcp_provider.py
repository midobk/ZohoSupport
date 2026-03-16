from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


@dataclass(frozen=True)
class TicketRecord:
    ticket_id: str
    subject: str
    snippet: str
    resolution_summary: str
    confidence: float


@dataclass(frozen=True)
class SimilarCaseResult:
    ticket_id: str
    subject: str
    similarity_score: float
    snippet: str
    resolution_summary: str
    draft_suggested_answer: str


class McpProvider(Protocol):
    def search_tickets(self, query: str) -> list[TicketRecord]:
        """Find tickets matching the free-text query."""

    def get_ticket_details(self, ticket_id: str) -> TicketRecord:
        """Return detailed ticket information by identifier."""

    def find_similar_cases(self, query: str) -> list[SimilarCaseResult]:
        """Return similar historical cases for the provided query."""


class McpProviderError(Exception):
    def __init__(
        self,
        code: str,
        message: str,
        *,
        status_code: int = 500,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}


class McpProviderTimeoutError(McpProviderError):
    def __init__(self, timeout_ms: int) -> None:
        super().__init__(
            code="MCP_PROVIDER_TIMEOUT",
            message="MCP provider operation timed out",
            status_code=504,
            details={"timeoutMs": timeout_ms},
        )


class McpProviderNotFoundError(McpProviderError):
    def __init__(self, ticket_id: str) -> None:
        super().__init__(
            code="MCP_TICKET_NOT_FOUND",
            message=f"Ticket '{ticket_id}' was not found",
            status_code=404,
            details={"ticketId": ticket_id},
        )
