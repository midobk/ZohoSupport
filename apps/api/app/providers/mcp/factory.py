from __future__ import annotations

import os

from .base import McpProvider
from .errors import McpProviderConfigurationError
from .http import HttpMcpProvider
from .mock import MockMcpProvider


def _read_timeout() -> float:
    raw = os.getenv("MCP_TIMEOUT_SECONDS", "3")
    try:
        timeout = float(raw)
    except ValueError as exc:
        raise McpProviderConfigurationError("MCP_TIMEOUT_SECONDS must be numeric") from exc

    if timeout <= 0:
        raise McpProviderConfigurationError("MCP_TIMEOUT_SECONDS must be > 0")

    return timeout


def build_mcp_provider() -> McpProvider:
    provider_name = os.getenv("MCP_PROVIDER", "mock").lower().strip()
    timeout_seconds = _read_timeout()

    if provider_name == "mock":
        simulated_latency_ms = int(os.getenv("MCP_MOCK_LATENCY_MS", "0"))
        return MockMcpProvider(
            timeout_seconds=timeout_seconds,
            simulated_latency_ms=simulated_latency_ms,
        )

    if provider_name == "http":
        base_url = os.getenv("MCP_HTTP_BASE_URL")
        if not base_url:
            raise McpProviderConfigurationError(
                "MCP_HTTP_BASE_URL is required when MCP_PROVIDER=http"
            )

        return HttpMcpProvider(base_url=base_url, timeout_seconds=timeout_seconds)

    raise McpProviderConfigurationError(
        f"Unsupported MCP_PROVIDER '{provider_name}'. Supported values: mock, http"
    )
