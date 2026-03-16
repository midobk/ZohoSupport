import asyncio

import pytest

from app.providers.mcp.errors import McpProviderConfigurationError, McpProviderTimeoutError
from app.providers.mcp.factory import build_mcp_provider
from app.providers.mcp.http import HttpMcpProvider
from app.providers.mcp.mock import MockMcpProvider


@pytest.fixture(autouse=True)
def reset_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("MCP_PROVIDER", raising=False)
    monkeypatch.delenv("MCP_TIMEOUT_SECONDS", raising=False)
    monkeypatch.delenv("MCP_MOCK_LATENCY_MS", raising=False)
    monkeypatch.delenv("MCP_HTTP_BASE_URL", raising=False)


def test_factory_defaults_to_mock_provider() -> None:
    provider = build_mcp_provider()
    assert isinstance(provider, MockMcpProvider)


def test_factory_builds_http_provider(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MCP_PROVIDER", "http")
    monkeypatch.setenv("MCP_HTTP_BASE_URL", "http://mcp.local")

    provider = build_mcp_provider()

    assert isinstance(provider, HttpMcpProvider)
    assert provider.base_url == "http://mcp.local"


def test_factory_raises_for_unsupported_provider(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MCP_PROVIDER", "invalid")

    with pytest.raises(McpProviderConfigurationError):
        build_mcp_provider()


def test_mock_provider_timeout() -> None:
    provider = MockMcpProvider(timeout_seconds=0.01, simulated_latency_ms=30)

    with pytest.raises(McpProviderTimeoutError):
        asyncio.run(provider.find_similar_cases("mfa"))
