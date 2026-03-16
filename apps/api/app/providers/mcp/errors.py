from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class McpProviderError(Exception):
    code: str
    message: str
    status_code: int = 500
    details: dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        return f"{self.code}: {self.message}"


class McpProviderTimeoutError(McpProviderError):
    def __init__(self, operation: str, timeout_seconds: float) -> None:
        super().__init__(
            code="MCP_TIMEOUT",
            message=f"MCP operation '{operation}' timed out",
            status_code=504,
            details={"operation": operation, "timeoutSeconds": timeout_seconds},
        )


class McpProviderUpstreamError(McpProviderError):
    def __init__(self, operation: str, status_code: int, body: str | None = None) -> None:
        super().__init__(
            code="MCP_UPSTREAM_ERROR",
            message=f"MCP upstream request failed for '{operation}'",
            status_code=502,
            details={
                "operation": operation,
                "upstreamStatusCode": status_code,
                "upstreamBody": body,
            },
        )


class McpProviderConfigurationError(McpProviderError):
    def __init__(self, message: str) -> None:
        super().__init__(
            code="MCP_CONFIGURATION_ERROR",
            message=message,
            status_code=500,
        )
