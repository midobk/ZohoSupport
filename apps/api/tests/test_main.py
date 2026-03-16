from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_answer_endpoint_returns_sources() -> None:
    response = client.post("/api/answer", json={"question": "How do I reset MFA?"})
    body = response.json()

    assert response.status_code == 200
    assert "answer" in body
    assert len(body["sources"]) >= 1


def test_similar_tickets_endpoint_returns_similarity_fields() -> None:
    response = client.post("/api/similar-tickets", json={"query": "otp expired"})
    body = response.json()

    assert response.status_code == 200
    assert len(body["tickets"]) >= 1
    first = body["tickets"][0]
    assert "similarityScore" in first
    assert "resolutionSummary" in first
    assert "draftSuggestedAnswer" in first


def test_similar_tickets_endpoint_rejects_short_query() -> None:
    response = client.post("/api/similar-tickets", json={"query": "ot"})

    assert response.status_code == 422
