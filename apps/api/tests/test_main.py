from fastapi.testclient import TestClient

from app.main import app, get_ask_provider
from app.shared_contracts import AnswerRequestMode, AnswerResponseContract


class StubAskProvider:
    def __init__(self) -> None:
        self.last_mode = AnswerRequestMode.SEARCH

    def answer_question(
        self,
        question: str,
        *,
        mode: AnswerRequestMode = AnswerRequestMode.SEARCH,
    ) -> AnswerResponseContract:
        self.last_mode = mode
        return AnswerResponseContract.model_validate(
            {
                "answer": f"Grounded answer for: {question}",
                "confidenceLabel": "High",
                "suggestedReply": "Customer-ready reply",
                "generation": {
                    "mode": "AI" if mode == AnswerRequestMode.AI else "Search",
                    "label": "AI answer" if mode == AnswerRequestMode.AI else "Search answer",
                    "description": "Generated for test coverage.",
                },
                "sources": [
                    {
                        "id": "kb-1",
                        "title": "Official article",
                        "snippet": "Official guidance",
                        "url": "https://help.zoho.com/portal/en/kb/desk/example",
                        "sourceType": "OfficialKB",
                        "trustLabel": "Verified",
                    },
                    {
                        "id": "community-1",
                        "title": "Community thread",
                        "snippet": "Unverified community context",
                        "url": "https://help.zoho.com/portal/en/community/topic/example",
                        "sourceType": "CommunityPost",
                        "trustLabel": "Unverified",
                    },
                ],
            }
        )


stub_provider = StubAskProvider()
app.dependency_overrides[get_ask_provider] = lambda: stub_provider


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
    assert body["generation"]["mode"] in {"AI", "Search"}
    assert isinstance(body["generation"]["description"], str)
    assert stub_provider.last_mode == AnswerRequestMode.SEARCH
    assert len(body["sources"]) == 2
    assert {"title", "snippet", "url", "sourceType", "trustLabel"}.issubset(body["sources"][0])
    assert {source["sourceType"] for source in body["sources"]} == {"OfficialKB", "CommunityPost"}


def test_answer_endpoint_validates_input() -> None:
    response = client.post("/api/answer", json={"question": ""})
    assert response.status_code == 422


def test_answer_endpoint_passes_ai_mode_to_provider() -> None:
    response = client.post("/api/answer", json={"question": "How do I reset MFA?", "mode": "ai"})

    assert response.status_code == 200
    assert response.json()["generation"]["mode"] == "AI"
    assert stub_provider.last_mode == AnswerRequestMode.AI
