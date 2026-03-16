from __future__ import annotations

import os
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
from typing import Callable, TypeVar

from .mcp_provider import McpProvider, McpProviderError, McpProviderTimeoutError
from .mock_mcp_provider import MockMcpProvider

T = TypeVar("T")

SUPPORTED_PROVIDER_BUILDERS: dict[str, Callable[[], McpProvider]] = {
    "mock": MockMcpProvider,
}


def resolve_mcp_provider() -> McpProvider:
    provider_name = os.getenv("MCP_PROVIDER", "mock").lower()
    builder = SUPPORTED_PROVIDER_BUILDERS.get(provider_name)
    if builder is None:
        raise McpProviderError(
            code="MCP_PROVIDER_CONFIGURATION_ERROR",
            message=f"Unsupported MCP_PROVIDER '{provider_name}'",
            status_code=500,
            details={"provider": provider_name, "supported": sorted(SUPPORTED_PROVIDER_BUILDERS)},
        )
    return builder()


def get_provider_timeout_ms() -> int:
    raw_timeout = os.getenv("MCP_PROVIDER_TIMEOUT_MS", "1500")
    try:
        timeout = int(raw_timeout)
    except ValueError as exc:
        raise McpProviderError(
            code="MCP_PROVIDER_CONFIGURATION_ERROR",
            message="MCP_PROVIDER_TIMEOUT_MS must be an integer",
            status_code=500,
            details={"value": raw_timeout},
        ) from exc

    if timeout <= 0:
        raise McpProviderError(
            code="MCP_PROVIDER_CONFIGURATION_ERROR",
            message="MCP_PROVIDER_TIMEOUT_MS must be greater than zero",
            status_code=500,
            details={"value": timeout},
        )
    return timeout


def run_with_timeout(operation: Callable[[], T], *, timeout_ms: int) -> T:
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(operation)
        try:
            return future.result(timeout=timeout_ms / 1000)
        except FuturesTimeoutError as exc:
            raise McpProviderTimeoutError(timeout_ms) from exc
