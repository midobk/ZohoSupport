import httpx

from app.gemini_answer_composer import GeminiAnswerComposer


def test_gemini_answer_composer_parses_structured_json_response() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path.endswith(":generateContent")
        assert request.url.params["key"] == "gemini-test-key"
        payload = request.read().decode("utf-8")
        assert "Reset MFA for users" in payload

        return httpx.Response(
            200,
            json={
                "candidates": [
                    {
                        "content": {
                            "parts": [
                                {
                                    "text": (
                                        '{"answer":"Use the admin flow to reset MFA and re-enroll the user.",'
                                        '"suggestedReply":"I reset MFA for your account. Please sign in and enroll again.",'
                                        '"confidenceLabel":"High"}'
                                    )
                                }
                            ]
                        }
                    }
                ]
            },
        )

    composer = GeminiAnswerComposer(
        client=httpx.Client(transport=httpx.MockTransport(handler), timeout=5.0),
        api_key="gemini-test-key",
        model="gemini-2.5-flash",
        base_url="https://generativelanguage.googleapis.com/v1beta",
        enabled=True,
    )

    result = composer.compose_answer(
        question="How do I reset MFA for a locked user?",
        official_sources=[
            {
                "title": "Reset MFA for users",
                "summary": "Admins can reset MFA and force re-enrollment.",
                "url": "https://help.zoho.com/portal/en/kb/one/admin-guide/users/managing-users/articles/reset-mfa-for-users",
                "source_type": "official_kb",
                "trust": "verified",
            }
        ],
        community_sources=[],
    )

    assert result.confidenceLabel == "High"
    assert "reset mfa" in result.answer.lower()


def test_gemini_answer_composer_repairs_newlines_inside_json_strings() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "candidates": [
                    {
                        "content": {
                            "parts": [
                                {
                                    "text": (
                                        '{\n'
                                        '  "answer": "Admins can reset MFA for locked users.\nUsers will re-enroll on next sign-in.",\n'
                                        '  "suggestedReply": "I reset MFA for your account.\nPlease sign in and enroll again.",\n'
                                        '  "confidenceLabel": "High"\n'
                                        '}'
                                    )
                                }
                            ]
                        }
                    }
                ]
            },
        )

    composer = GeminiAnswerComposer(
        client=httpx.Client(transport=httpx.MockTransport(handler), timeout=5.0),
        api_key="gemini-test-key",
        model="gemini-2.5-flash",
        base_url="https://generativelanguage.googleapis.com/v1beta",
        enabled=True,
    )

    result = composer.compose_answer(
        question="How do I reset MFA for a locked user?",
        official_sources=[
            {
                "title": "Reset MFA for users",
                "summary": "Admins can reset MFA and force re-enrollment.",
                "url": "https://help.zoho.com/portal/en/kb/one/admin-guide/users/managing-users/articles/reset-mfa-for-users",
                "source_type": "official_kb",
                "trust": "verified",
            }
        ],
        community_sources=[],
    )

    assert result.confidenceLabel == "High"
    assert "\n" in result.answer
