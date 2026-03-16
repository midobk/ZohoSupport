from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_answer_endpoint_returns_shared_contract_shape() -> None:
    response = client.post("/api/answer", json={"question": "How do I reset MFA?"})
    body = response.json()

    assert response.status_code == 200
    assert isinstance(body["answer"], str)
    assert len(body["sources"]) >= 1
    assert body["draftReply"]["confidenceLabel"] in {"high", "medium", "low"}


def test_answer_endpoint_rejects_invalid_request() -> None:
    response = client.post("/api/answer", json={"question": "hi"})
    assert response.status_code == 422


def test_similar_tickets_response_contract() -> None:
    response = client.post("/api/similar-tickets", json={"query": "MFA"})
    body = response.json()

    assert response.status_code == 200
    assert len(body["tickets"]) >= 1
    for ticket in body["tickets"]:
        assert 0 <= ticket["confidence"] <= 1
        assert ticket["confidenceLabel"] in {"high", "medium", "low"}
