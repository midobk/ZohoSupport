from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_answer_endpoint_returns_ask_flow_payload() -> None:
    response = client.post("/api/answer", json={"question": "How do I reset MFA?"})
    body = response.json()

    assert response.status_code == 200
    assert "answer" in body
    assert body["confidenceLabel"] in {"High", "Medium", "Low"}
    assert isinstance(body["suggestedReply"], str)
    assert len(body["sources"]) >= 1
    assert {"title", "snippet", "url"}.issubset(body["sources"][0])


def test_answer_endpoint_validates_input() -> None:
    response = client.post("/api/answer", json={"question": ""})
    assert response.status_code == 422
