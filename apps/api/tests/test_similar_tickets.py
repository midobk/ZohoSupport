from app.main import app
from app.mock_mcp_provider import MockMcpProvider
from fastapi.testclient import TestClient


client = TestClient(app)


def test_mock_mcp_provider_ranks_keyword_matches_higher() -> None:
    provider = MockMcpProvider()

    results = provider.find_similar_cases("locked account mfa reset")

    assert len(results) >= 2
    assert results[0].similarity_score >= results[1].similarity_score
    assert results[0].ticket_id == "TCK-4387"
    assert "thanks for the report" in results[0].draft_suggested_answer.lower()


def test_similar_tickets_endpoint_returns_provider_shaped_ticket_results() -> None:
    response = client.post("/api/similar-tickets", json={"query": "mfa locked account"})

    assert response.status_code == 200
    payload = response.json()
    assert len(payload["tickets"]) >= 1

    first_ticket = payload["tickets"][0]
    assert {
        "ticketId",
        "subject",
        "similarityScore",
        "snippet",
        "resolutionSummary",
        "draftSuggestedAnswer",
    }.issubset(first_ticket)
    assert isinstance(first_ticket["similarityScore"], float)


def test_similar_tickets_endpoint_validates_input() -> None:
    response = client.post("/api/similar-tickets", json={"query": ""})
    assert response.status_code == 422


def test_search_tickets_endpoint_returns_ticket_records() -> None:
    response = client.post("/api/tickets/search", json={"query": "phone replacement"})

    assert response.status_code == 200
    payload = response.json()
    assert len(payload["tickets"]) >= 1
    assert {
        "ticketId",
        "subject",
        "snippet",
        "resolutionSummary",
        "confidence",
    }.issubset(payload["tickets"][0])


def test_get_ticket_details_endpoint_returns_single_ticket() -> None:
    response = client.get("/api/tickets/TCK-4401")

    assert response.status_code == 200
    payload = response.json()
    assert payload["ticketId"] == "TCK-4401"
    assert isinstance(payload["confidence"], float)
