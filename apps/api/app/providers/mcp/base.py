from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from collections.abc import Awaitable
from typing import Any

from .errors import McpProviderTimeoutError


class McpProvider(ABC):
    @abstractmethod
    async def search_tickets(self, query: str) -> list[dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    async def get_ticket_details(self, ticket_id: str) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    async def find_similar_cases(self, query: str) -> list[dict[str, Any]]:
        raise NotImplementedError


async def with_timeout(
    operation: str,
    timeout_seconds: float,
    coro: Awaitable[Any],
) -> Any:
    try:
        return await asyncio.wait_for(coro, timeout=timeout_seconds)
    except asyncio.TimeoutError as exc:
        raise McpProviderTimeoutError(operation=operation, timeout_seconds=timeout_seconds) from exc
