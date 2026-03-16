from app.main import app
from app.mock_mcp_adapter import MockMcpSimilarTicketsAdapter
from fastapi.testclient import TestClient


client = TestClient(app)


def test_mock_mcp_adapter_ranks_keyword_matches_higher() -> None:
    adapter = MockMcpSimilarTicketsAdapter()

    results = adapter.find_similar_tickets("locked account mfa reset")

    assert len(results) >= 2
    assert results[0].similarity_score >= results[1].similarity_score
    assert results[0].ticket_id == "TCK-4387"
    assert "thanks for the report" in results[0].draft_suggested_answer.lower()


def test_similar_tickets_endpoint_returns_mcp_shaped_ticket_results() -> None:
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
