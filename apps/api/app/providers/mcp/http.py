from __future__ import annotations

from typing import Any

import httpx

from .base import McpProvider, with_timeout
from .errors import McpProviderUpstreamError


class HttpMcpProvider(McpProvider):
    def __init__(self, base_url: str, timeout_seconds: float = 3.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds

    async def _post(self, operation: str, endpoint: str, payload: dict[str, Any]) -> Any:
        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            response = await with_timeout(
                operation=operation,
                timeout_seconds=self.timeout_seconds,
                coro=client.post(f"{self.base_url}{endpoint}", json=payload),
            )

        if response.status_code >= 400:
            raise McpProviderUpstreamError(
                operation=operation,
                status_code=response.status_code,
                body=response.text,
            )

        return response.json()

    async def search_tickets(self, query: str) -> list[dict[str, Any]]:
        data = await self._post(
            operation="search_tickets",
            endpoint="/search_tickets",
            payload={"query": query},
        )
        return data.get("tickets", [])

    async def get_ticket_details(self, ticket_id: str) -> dict[str, Any]:
        data = await self._post(
            operation="get_ticket_details",
            endpoint="/get_ticket_details",
            payload={"ticketId": ticket_id},
        )
        return data

    async def find_similar_cases(self, query: str) -> list[dict[str, Any]]:
        data = await self._post(
            operation="find_similar_cases",
            endpoint="/find_similar_cases",
            payload={"query": query},
        )
        return data.get("tickets", [])
