from __future__ import annotations

import asyncio
from typing import Any

from app.mock_data import MOCK_TICKETS

from .base import McpProvider, with_timeout
from .errors import McpProviderError


class MockMcpProvider(McpProvider):
    def __init__(self, timeout_seconds: float = 3.0, simulated_latency_ms: int = 0) -> None:
        self.timeout_seconds = timeout_seconds
        self.simulated_latency_ms = simulated_latency_ms

    async def _simulate_latency(self) -> None:
        if self.simulated_latency_ms > 0:
            await asyncio.sleep(self.simulated_latency_ms / 1000)

    async def search_tickets(self, query: str) -> list[dict[str, Any]]:
        return await with_timeout(
            operation="search_tickets",
            timeout_seconds=self.timeout_seconds,
            coro=self._search_tickets_impl(query=query),
        )

    async def _search_tickets_impl(self, query: str) -> list[dict[str, Any]]:
        await self._simulate_latency()
        needle = query.lower().strip()
        return [
            ticket
            for ticket in MOCK_TICKETS
            if needle in ticket["subject"].lower() or needle in ticket["snippet"].lower()
        ]

    async def get_ticket_details(self, ticket_id: str) -> dict[str, Any]:
        return await with_timeout(
            operation="get_ticket_details",
            timeout_seconds=self.timeout_seconds,
            coro=self._get_ticket_details_impl(ticket_id=ticket_id),
        )

    async def _get_ticket_details_impl(self, ticket_id: str) -> dict[str, Any]:
        await self._simulate_latency()
        for ticket in MOCK_TICKETS:
            if ticket["ticketId"] == ticket_id:
                return ticket

        raise McpProviderError(
            code="TICKET_NOT_FOUND",
            message=f"Ticket '{ticket_id}' not found",
            status_code=404,
            details={"ticketId": ticket_id},
        )

    async def find_similar_cases(self, query: str) -> list[dict[str, Any]]:
        return await with_timeout(
            operation="find_similar_cases",
            timeout_seconds=self.timeout_seconds,
            coro=self._find_similar_cases_impl(query=query),
        )

    async def _find_similar_cases_impl(self, query: str) -> list[dict[str, Any]]:
        await self._simulate_latency()
        q = query.lower().strip()

        ranked = sorted(
            MOCK_TICKETS,
            key=lambda ticket: (
                q in ticket["subject"].lower() or q in ticket["snippet"].lower(),
                ticket["confidence"],
            ),
            reverse=True,
        )
        return ranked
