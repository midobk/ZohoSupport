import time

import pytest
from app.main import app, get_mcp_provider
from app.mcp_provider import McpProviderError, TicketRecord
from app.mcp_provider_factory import (
    get_provider_timeout_ms,
    resolve_mcp_provider,
    run_with_timeout,
)
from app.mock_mcp_provider import MockMcpProvider
from fastapi.testclient import TestClient


class SlowProvider(MockMcpProvider):
    def find_similar_cases(self, query: str):
        time.sleep(0.05)
        return super().find_similar_cases(query)


def test_resolve_mcp_provider_defaults_to_mock(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("MCP_PROVIDER", raising=False)

    provider = resolve_mcp_provider()

    assert isinstance(provider, MockMcpProvider)


def test_resolve_mcp_provider_rejects_unsupported_value(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("MCP_PROVIDER", "unknown")

    with pytest.raises(McpProviderError) as exc:
        resolve_mcp_provider()

    assert exc.value.code == "MCP_PROVIDER_CONFIGURATION_ERROR"


def test_timeout_env_rejects_invalid_value(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MCP_PROVIDER_TIMEOUT_MS", "abc")

    with pytest.raises(McpProviderError) as exc:
        get_provider_timeout_ms()

    assert exc.value.code == "MCP_PROVIDER_CONFIGURATION_ERROR"


def test_run_with_timeout_raises_timeout_error() -> None:
    with pytest.raises(McpProviderError) as exc:
        run_with_timeout(lambda: time.sleep(0.02), timeout_ms=5)

    assert exc.value.code == "MCP_PROVIDER_TIMEOUT"


def test_endpoint_returns_structured_error_on_timeout(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("MCP_PROVIDER_TIMEOUT_MS", "10")
    app.dependency_overrides[get_mcp_provider] = lambda: SlowProvider()
    client = TestClient(app)

    response = client.post("/api/similar-tickets", json={"query": "mfa"})

    app.dependency_overrides.clear()

    assert response.status_code == 504
    body = response.json()
    assert body["detail"]["code"] == "MCP_PROVIDER_TIMEOUT"


def test_endpoint_returns_structured_error_on_missing_ticket() -> None:
    app.dependency_overrides[get_mcp_provider] = lambda: MockMcpProvider()
    client = TestClient(app)

    response = client.get("/api/tickets/does-not-exist")

    app.dependency_overrides.clear()

    assert response.status_code == 404
    body = response.json()
    assert body["detail"]["code"] == "MCP_TICKET_NOT_FOUND"


def test_provider_get_ticket_details_returns_ticket_record() -> None:
    provider = MockMcpProvider()

    ticket = provider.get_ticket_details("TCK-4401")

    assert isinstance(ticket, TicketRecord)
    assert ticket.ticket_id == "TCK-4401"
