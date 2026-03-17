import httpx

from app.openai_answer_composer import OpenAiAnswerComposer


def test_openai_answer_composer_parses_structured_json_response() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/v1/responses"
        payload = request.read().decode("utf-8")
        assert "gpt-4.1-mini" in payload
        assert "Reset MFA for users" in payload

        return httpx.Response(
            200,
            json={
                "output": [
                    {
                        "type": "message",
                        "content": [
                            {
                                "type": "output_text",
                                "text": (
                                    '{"answer":"Reset MFA from Zoho One or Directory using the admin flow.",'
                                    '"suggestedReply":"I reset MFA for your account. Please sign in and enroll again.",'
                                    '"confidenceLabel":"High"}'
                                ),
                            }
                        ],
                    }
                ]
            },
        )

    composer = OpenAiAnswerComposer(
        client=httpx.Client(transport=httpx.MockTransport(handler), timeout=5.0),
        api_key="test-key",
        model="gpt-4.1-mini",
        base_url="https://api.openai.com/v1",
        enabled=True,
    )

    result = composer.compose_answer(
        question="How do I reset MFA for a locked user?",
        official_sources=[
            {
                "title": "Reset MFA for users",
                "summary": "Admins can reset MFA and force the user to enroll again.",
                "url": "https://help.zoho.com/portal/en/kb/one/admin-guide/users/managing-users/articles/reset-mfa-for-users",
                "source_type": "official_kb",
                "trust": "verified",
            }
        ],
        community_sources=[],
    )

    assert result.confidenceLabel == "High"
    assert "reset mfa" in result.answer.lower()


def test_openai_answer_composer_reports_disabled_without_key() -> None:
    composer = OpenAiAnswerComposer(api_key="", enabled=True)
    assert composer.is_enabled() is False
