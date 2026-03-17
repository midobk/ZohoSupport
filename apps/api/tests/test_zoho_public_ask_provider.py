from __future__ import annotations

import httpx

from app.openai_answer_composer import OpenAiAnswerComposer
from app.shared_contracts import AnswerKeyProfile, AnswerRequestMode
from app.zoho_public_ask_provider import ZohoPublicAskProvider


PORTAL_ID = "testportal123"


def build_provider() -> ZohoPublicAskProvider:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/portal/en/kb":
            return httpx.Response(
                200,
                text=f'<html><head><link href="https://help.zoho.com/portal/api/publicImages/1?portalId={PORTAL_ID}" /></head></html>',
            )

        if request.url.path == "/portal/api/kbRootCategories":
            return httpx.Response(
                200,
                json={
                    "data": [
                        {"id": "desk-root", "name": "Desk", "permalink": "desk"},
                        {"id": "mail-root", "name": "Mail", "permalink": "mail"},
                        {"id": "analytics-root", "name": "Analytics", "permalink": "analytics"},
                    ]
                },
            )

        if request.url.path == "/portal/api/kbArticles/search":
            return httpx.Response(
                200,
                json={
                    "data": [
                        {
                            "id": "article-1",
                            "title": "Reset MFA for users",
                            "summary": "Admins can reset MFA for users and they will be prompted to enroll again on the next sign-in.",
                            "webUrl": "https://help.zoho.com/portal/en/kb/one/admin-guide/users/managing-users/articles/reset-mfa-for-users",
                            "rootCategoryId": "desk-root",
                        },
                        {
                            "id": "article-2",
                            "title": "Mail MFA troubleshooting",
                            "summary": "Review authentication settings and verify the user's recovery channels.",
                            "webUrl": "https://help.zoho.com/portal/en/kb/mail/adminconsole/articles/mail-mfa-troubleshooting",
                            "rootCategoryId": "mail-root",
                        },
                        {
                            "id": "article-3",
                            "title": "Analytics unrelated result",
                            "summary": "This should be filtered out.",
                            "webUrl": "https://help.zoho.com/portal/en/kb/analytics/unrelated",
                            "rootCategoryId": "analytics-root",
                        },
                    ]
                },
            )

        if request.url.path == "/portal/api/communityCategory":
            return httpx.Response(
                200,
                json={
                    "data": [
                        {
                            "id": "desk-community-root",
                            "name": "Zoho Desk",
                            "permalink": "zoho-desk",
                            "child": [
                                {
                                    "id": "desk-community-child",
                                    "name": "Using Zoho Desk",
                                    "permalink": "using-zoho-desk",
                                    "child": [],
                                }
                            ],
                        },
                        {
                            "id": "analytics-community-root",
                            "name": "Analytics",
                            "permalink": "analytics",
                            "child": [],
                        },
                    ]
                },
            )

        if request.url.path == "/portal/api/communityTopics/search":
            return httpx.Response(
                200,
                json={
                    "data": [
                        {
                            "id": "topic-1",
                            "subject": "Desk admins discussing MFA edge cases",
                            "content": "Community members describe what happens when a user is locked out after MFA challenges fail.",
                            "permalink": "desk-admins-discussing-mfa-edge-cases",
                            "categoryId": "desk-community-child",
                        },
                        {
                            "id": "topic-2",
                            "subject": "Analytics thread",
                            "content": "This should not be included.",
                            "permalink": "analytics-thread",
                            "categoryId": "analytics-community-root",
                        },
                    ]
                },
            )

        raise AssertionError(f"Unexpected request: {request.method} {request.url}")

    transport = httpx.MockTransport(handler)
    client = httpx.Client(transport=transport, timeout=5.0)

    return ZohoPublicAskProvider(
        client=client,
        help_center_root="https://help.zoho.com/portal/en",
        allowed_products=("desk", "mail"),
        include_community=True,
        answer_composer=OpenAiAnswerComposer(enabled=False),
    )


def test_live_ask_provider_filters_to_allowed_products_and_marks_community_unverified() -> None:
    provider = build_provider()

    result = provider.answer_question("How do I reset MFA for a locked user?")

    assert result.confidenceLabel == "High"
    assert result.generation.mode == "Search"
    assert result.generation.label == "Search answer"
    assert "normal search was selected" in result.generation.description.lower()
    assert result.sources[0].sourceType == "OfficialKB"
    assert result.sources[1].sourceType == "OfficialKB"
    assert result.sources[2].sourceType == "CommunityPost"
    assert result.sources[2].trustLabel == "Unverified"
    assert "unverified" in result.answer.lower()
    assert "Analytics unrelated result" not in {source.title for source in result.sources}


def test_live_ask_provider_returns_low_confidence_when_only_community_matches() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/portal/en/kb":
            return httpx.Response(
                200,
                text=f'<html><head><link href="https://help.zoho.com/portal/api/publicImages/1?portalId={PORTAL_ID}" /></head></html>',
            )

        if request.url.path == "/portal/api/kbRootCategories":
            return httpx.Response(200, json={"data": [{"id": "desk-root", "name": "Desk", "permalink": "desk"}]})

        if request.url.path == "/portal/api/kbArticles/search":
            return httpx.Response(200, json={"data": []})

        if request.url.path == "/portal/api/communityCategory":
            return httpx.Response(
                200,
                json={
                    "data": [
                        {
                            "id": "desk-community-root",
                            "name": "Zoho Desk",
                            "permalink": "zoho-desk",
                            "child": [],
                        }
                    ]
                },
            )

        if request.url.path == "/portal/api/communityTopics/search":
            return httpx.Response(
                200,
                json={
                    "data": [
                        {
                            "id": "topic-1",
                            "subject": "Community-only discussion",
                            "content": "A community discussion with no official article match.",
                            "permalink": "community-only-discussion",
                            "categoryId": "desk-community-root",
                        }
                    ]
                },
            )

        raise AssertionError(f"Unexpected request: {request.method} {request.url}")

    provider = ZohoPublicAskProvider(
        client=httpx.Client(transport=httpx.MockTransport(handler), timeout=5.0),
        help_center_root="https://help.zoho.com/portal/en",
        allowed_products=("desk",),
        include_community=True,
        answer_composer=OpenAiAnswerComposer(enabled=False),
    )

    result = provider.answer_question("Community-only edge case")

    assert result.confidenceLabel == "Low"
    assert result.generation.mode == "Search"
    assert "strong official kb match" in result.generation.description.lower()
    assert result.sources[0].sourceType == "CommunityPost"
    assert "couldn't find a strong official" in result.answer.lower()


def test_live_ask_provider_uses_ai_composer_when_enabled() -> None:
    class StubComposer:
        def is_enabled(self, *, key_profile: AnswerKeyProfile | None = None) -> bool:
            assert key_profile == AnswerKeyProfile.PAID
            return True

        def describe(self, *, model: str | None = None, key_profile: AnswerKeyProfile | None = None):
            return type(
                "ComposerDescriptor",
                (),
                {
                    "providerLabel": "Google Gemini",
                    "modelLabel": model or "gemini-2.5-flash",
                    "keyProfileLabel": key_profile.value if key_profile else None,
                },
            )()

        def compose_answer(
            self,
            *,
            question: str,
            official_sources: list[dict[str, str]],
            community_sources: list[dict[str, str]],
            model: str | None = None,
            key_profile: AnswerKeyProfile | None = None,
        ):
            assert "locked user" in question
            assert official_sources[0]["source_type"] == "official_kb"
            assert community_sources[0]["source_type"] == "community_post"
            assert model == "gemini-2.5-flash-lite"
            assert key_profile == AnswerKeyProfile.PAID
            return type(
                "ComposedAnswer",
                (),
                {
                    "answer": "AI-composed answer grounded in official Zoho sources.",
                    "suggestedReply": "AI-composed customer-ready reply.",
                    "confidenceLabel": "High",
                },
            )()

    provider = build_provider()
    provider._answer_composer = StubComposer()  # type: ignore[attr-defined]

    result = provider.answer_question(
        "How do I reset MFA for a locked user?",
        mode=AnswerRequestMode.AI,
        model="gemini-2.5-flash-lite",
        key_profile=AnswerKeyProfile.PAID,
    )

    assert result.answer == "AI-composed answer grounded in official Zoho sources."
    assert result.suggestedReply == "AI-composed customer-ready reply."
    assert result.generation.mode == "AI"
    assert "google gemini" in result.generation.description.lower()
    assert "gemini-2.5-flash-lite" in result.generation.description
    assert "paid api key profile" in result.generation.description.lower()
    assert "normal search" in result.generation.description.lower()


def test_live_ask_provider_skips_ai_when_search_mode_is_selected() -> None:
    class StubComposer:
        def is_enabled(self, *, key_profile: AnswerKeyProfile | None = None) -> bool:
            return True

        def describe(self, *, model: str | None = None, key_profile: AnswerKeyProfile | None = None):
            return type(
                "ComposerDescriptor",
                (),
                {
                    "providerLabel": "Google Gemini",
                    "modelLabel": model or "gemini-2.5-flash",
                    "keyProfileLabel": key_profile.value if key_profile else None,
                },
            )()

        def compose_answer(self, **kwargs):
            raise AssertionError(f"compose_answer should not be called in search mode: {kwargs}")

    provider = build_provider()
    provider._answer_composer = StubComposer()  # type: ignore[attr-defined]

    result = provider.answer_question("How do I reset MFA for a locked user?", mode=AnswerRequestMode.SEARCH)

    assert result.generation.mode == "Search"
    assert "normal search was selected" in result.generation.description.lower()


def test_live_ask_provider_does_not_resolve_ai_composer_for_search_mode(monkeypatch) -> None:
    provider = ZohoPublicAskProvider(
        client=build_provider()._client,  # type: ignore[attr-defined]
        help_center_root="https://help.zoho.com/portal/en",
        allowed_products=("desk", "mail"),
        include_community=True,
        answer_composer=None,
    )

    def fail_if_called():
        raise AssertionError("resolve_answer_composer should not be called in search mode")

    monkeypatch.setattr("app.zoho_public_ask_provider.resolve_answer_composer", fail_if_called)

    result = provider.answer_question("How do I reset MFA for a locked user?", mode=AnswerRequestMode.SEARCH)

    assert result.generation.mode == "Search"
