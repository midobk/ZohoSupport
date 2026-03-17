from __future__ import annotations

import html
import os
import re
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlparse

import httpx

from .answer_composer import AnswerComposer
from .answer_composer_factory import resolve_answer_composer
from .ask_provider import AskProvider, AskProviderConfigurationError, AskProviderUnavailableError
from .shared_contracts import (
    AnswerGenerationContract,
    AnswerGenerationMode,
    AnswerRequestMode,
    AnswerResponseContract,
    ConfidenceLabel,
    SourceResultContract,
    SourceType,
    TrustLabel,
)

DEFAULT_HELP_CENTER_ROOT = "https://help.zoho.com/portal/en"
DEFAULT_ALLOWED_PRODUCTS = (
    "desk",
    "one",
    "crm-plus",
    "crm",
    "projects",
    "mail",
    "directory",
    "accounts",
)
DEFAULT_INCLUDE_COMMUNITY = True
OFFICIAL_SOURCE_LIMIT = 4
COMMUNITY_SOURCE_LIMIT = 3
QUESTION_STOP_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "do",
    "for",
    "how",
    "i",
    "in",
    "is",
    "my",
    "of",
    "on",
    "the",
    "to",
}

PRODUCT_ALIASES: dict[str, set[str]] = {
    "desk": {"desk", "zohodesk"},
    "one": {"one", "zohoone"},
    "crm-plus": {"crmplus", "zohocrmplus"},
    "crm": {"crm", "zohocrm"},
    "projects": {"projects", "zohoprojects"},
    "mail": {"mail", "zohomail"},
    "directory": {"directory", "zohodirectory"},
    "accounts": {"accounts", "zohoaccounts"},
}

PORTAL_ID_PATTERN = re.compile(r"portalId=([A-Za-z0-9]+)")
WHITESPACE_PATTERN = re.compile(r"\s+")


@dataclass(frozen=True)
class KbArticleSearchResult:
    article_id: str
    title: str
    summary: str
    web_url: str
    root_category_id: str


@dataclass(frozen=True)
class CommunityTopicSearchResult:
    topic_id: str
    subject: str
    content: str
    permalink: str
    category_id: str


class ZohoPublicAskProvider(AskProvider):
    def __init__(
        self,
        *,
        client: httpx.Client | None = None,
        help_center_root: str | None = None,
        allowed_products: tuple[str, ...] | None = None,
        include_community: bool | None = None,
        answer_composer: AnswerComposer | None = None,
    ) -> None:
        self._client = client or httpx.Client(timeout=10.0, follow_redirects=True)
        self._help_center_root = (help_center_root or os.getenv("ZOHO_HELP_CENTER_ROOT", DEFAULT_HELP_CENTER_ROOT)).rstrip("/")
        self._kb_root_url = f"{self._help_center_root}/kb"
        self._community_root_url = f"{self._help_center_root}/community"
        self._locale = self._extract_locale(self._help_center_root)
        self._allowed_products = tuple(
            self._canonicalize_product(product)
            for product in (
                allowed_products
                or self._parse_allowed_products(os.getenv("ZOHO_ALLOWED_PRODUCTS"))
            )
        )
        self._include_community = (
            include_community
            if include_community is not None
            else self._parse_bool(os.getenv("ZOHO_INCLUDE_COMMUNITY"), DEFAULT_INCLUDE_COMMUNITY)
        )
        self._portal_id: str | None = None
        self._selected_kb_root_ids: set[str] | None = None
        self._selected_community_category_ids: set[str] | None = None
        self._answer_composer = answer_composer or resolve_answer_composer()

    def answer_question(
        self,
        question: str,
        *,
        mode: AnswerRequestMode = AnswerRequestMode.SEARCH,
    ) -> AnswerResponseContract:
        official_sources = self._search_kb_articles(question)
        community_sources = self._search_community_topics(question) if self._include_community else []

        if not official_sources:
            sources = [self._to_community_source(result) for result in community_sources]
            answer = (
                "I couldn't find a strong official Zoho Knowledge Base match in the selected product areas for this question."
            )
            if community_sources:
                answer += " I did find community discussions that may help, but they are unverified."

            return AnswerResponseContract(
                answer=answer,
                confidenceLabel=ConfidenceLabel.LOW,
                suggestedReply=(
                    "I couldn't find an exact official article for this issue yet. Please share the exact Zoho product, "
                    "feature area, and any on-screen error so I can narrow it down with the right documentation."
                ),
                generation=self._build_search_generation(
                    requested_mode=mode,
                    community_used=bool(community_sources),
                    official_match_found=False,
                ),
                sources=sources,
            )

        top_official = official_sources[0]
        sources = [self._to_official_source(result) for result in official_sources]
        sources.extend(self._to_community_source(result) for result in community_sources)

        if mode == AnswerRequestMode.AI and self._answer_composer.is_enabled():
            try:
                composed_answer = self._answer_composer.compose_answer(
                    question=question,
                    official_sources=[self._source_payload(result) for result in official_sources],
                    community_sources=[self._community_payload(result) for result in community_sources],
                )
                return AnswerResponseContract(
                    answer=composed_answer.answer,
                    confidenceLabel=composed_answer.confidenceLabel,
                    suggestedReply=composed_answer.suggestedReply,
                    generation=self._build_ai_generation(community_used=bool(community_sources)),
                    sources=sources,
                )
            except AskProviderUnavailableError:
                # Fallback to deterministic composition so Ask remains available when AI is unavailable.
                return AnswerResponseContract(
                    answer=self._build_search_answer(official_sources, community_sources),
                    confidenceLabel=ConfidenceLabel.HIGH if len(official_sources) > 1 else ConfidenceLabel.MEDIUM,
                    suggestedReply=self._build_suggested_reply(top_official),
                    generation=self._build_search_generation(
                        requested_mode=mode,
                        community_used=bool(community_sources),
                        ai_fallback=True,
                    ),
                    sources=sources,
                )

        return AnswerResponseContract(
            answer=self._build_search_answer(official_sources, community_sources),
            confidenceLabel=ConfidenceLabel.HIGH if len(official_sources) > 1 else ConfidenceLabel.MEDIUM,
            suggestedReply=self._build_suggested_reply(top_official),
            generation=self._build_search_generation(
                requested_mode=mode,
                community_used=bool(community_sources),
                ai_fallback=mode == AnswerRequestMode.AI and not self._answer_composer.is_enabled(),
            ),
            sources=sources,
        )

    def _build_ai_generation(self, *, community_used: bool) -> AnswerGenerationContract:
        descriptor = self._answer_composer.describe()
        description = (
            "The results were retrieved from Zoho's normal search first. "
            f"Then {descriptor.providerLabel} using the {descriptor.modelLabel} model drafted the answer text."
        )
        if community_used:
            description += " Community posts were used only as extra context and were not treated as official policy."

        return AnswerGenerationContract(
            mode=AnswerGenerationMode.AI,
            label="AI answer",
            description=description,
        )

    def _build_search_generation(
        self,
        *,
        requested_mode: AnswerRequestMode,
        community_used: bool,
        official_match_found: bool = True,
        ai_fallback: bool = False,
    ) -> AnswerGenerationContract:
        if ai_fallback:
            description = "AI was requested, but it was unavailable for this run, so both the results and the answer fell back to normal Zoho search only."
        elif requested_mode == AnswerRequestMode.SEARCH:
            description = "Normal search was selected, so both the results and the answer were built from Zoho search without using AI."
        else:
            description = "Both the results and the answer were built from Zoho search only. No AI was used."

        if not official_match_found:
            description += " I could not find a strong official KB match, so this result stays search-based."

        if community_used:
            description += " Community posts were treated as extra, unverified context."

        return AnswerGenerationContract(
            mode=AnswerGenerationMode.SEARCH,
            label="Search answer",
            description=description,
        )

    @staticmethod
    def _build_search_answer(
        official_sources: list[KbArticleSearchResult],
        community_sources: list[CommunityTopicSearchResult],
    ) -> str:
        top_official = official_sources[0]
        answer = f"Based on Zoho's official documentation, {top_official.summary}"
        if len(official_sources) > 1:
            answer += f" A related official article to review is '{official_sources[1].title}'."
        if community_sources:
            answer += (
                " I also found community discussions that may add context, but they are unverified and should be treated as supporting information only."
            )
        return answer

    @staticmethod
    def _build_suggested_reply(top_official: KbArticleSearchResult) -> str:
        return (
            f"Based on Zoho's official documentation, {top_official.summary} "
            "Please review the linked article(s), and if the issue continues, reply with the exact Zoho product area and the full error text so we can narrow it down further."
        )

    def _search_kb_articles(self, question: str) -> list[KbArticleSearchResult]:
        payload = self._get_json(
            "https://help.zoho.com/portal/api/kbArticles/search",
            params={"portalId": self._resolve_portal_id(), "searchStr": question},
        )
        allowed_root_ids = self._resolve_selected_kb_root_ids()
        filtered_results: list[KbArticleSearchResult] = []

        for item in payload.get("data", []):
            if item.get("rootCategoryId") not in allowed_root_ids:
                continue

            filtered_results.append(
                KbArticleSearchResult(
                    article_id=str(item["id"]),
                    title=self._clean_text(item.get("title")),
                    summary=self._clean_text(item.get("summary")),
                    web_url=str(item["webUrl"]),
                    root_category_id=str(item["rootCategoryId"]),
                )
            )

        return self._rerank_kb_results(question, filtered_results)[:OFFICIAL_SOURCE_LIMIT]

    def _search_community_topics(self, question: str) -> list[CommunityTopicSearchResult]:
        payload = self._get_json(
            "https://help.zoho.com/portal/api/communityTopics/search",
            params={"portalId": self._resolve_portal_id(), "searchStr": question},
        )
        allowed_category_ids = self._resolve_selected_community_category_ids()
        filtered_results: list[CommunityTopicSearchResult] = []

        for item in payload.get("data", []):
            if item.get("categoryId") not in allowed_category_ids:
                continue

            filtered_results.append(
                CommunityTopicSearchResult(
                    topic_id=str(item["id"]),
                    subject=self._clean_text(item.get("subject")),
                    content=self._clean_text(item.get("content")),
                    permalink=str(item["permalink"]),
                    category_id=str(item["categoryId"]),
                )
            )

        return self._rerank_community_results(question, filtered_results)[:COMMUNITY_SOURCE_LIMIT]

    def _to_official_source(self, result: KbArticleSearchResult) -> SourceResultContract:
        return SourceResultContract(
            id=result.article_id,
            title=result.title,
            snippet=result.summary,
            url=result.web_url,
            sourceType=SourceType.OFFICIAL_KB,
            trustLabel=TrustLabel.VERIFIED,
        )

    def _to_community_source(self, result: CommunityTopicSearchResult) -> SourceResultContract:
        return SourceResultContract(
            id=result.topic_id,
            title=result.subject,
            snippet=result.content,
            url=f"{self._community_root_url}/topic/{result.permalink}",
            sourceType=SourceType.COMMUNITY_POST,
            trustLabel=TrustLabel.UNVERIFIED,
        )

    @staticmethod
    def _source_payload(result: KbArticleSearchResult) -> dict[str, str]:
        return {
            "title": result.title,
            "summary": result.summary,
            "url": result.web_url,
            "source_type": "official_kb",
            "trust": "verified",
        }

    def _community_payload(self, result: CommunityTopicSearchResult) -> dict[str, str]:
        return {
            "title": result.subject,
            "summary": result.content,
            "url": f"{self._community_root_url}/topic/{result.permalink}",
            "source_type": "community_post",
            "trust": "unverified",
        }

    def _resolve_portal_id(self) -> str:
        if self._portal_id is not None:
            return self._portal_id

        response = self._client.get(self._kb_root_url)
        if response.status_code >= 400:
            raise AskProviderUnavailableError(
                "Unable to load the Zoho Knowledge Base homepage",
                details={"statusCode": response.status_code, "url": self._kb_root_url},
            )

        match = PORTAL_ID_PATTERN.search(response.text)
        if match is None:
            raise AskProviderConfigurationError(
                "Unable to determine the Zoho Help Center portal identifier",
                details={"url": self._kb_root_url},
            )

        self._portal_id = match.group(1)
        return self._portal_id

    def _resolve_selected_kb_root_ids(self) -> set[str]:
        if self._selected_kb_root_ids is not None:
            return self._selected_kb_root_ids

        payload = self._get_json(
            "https://help.zoho.com/portal/api/kbRootCategories",
            params={"portalId": self._resolve_portal_id(), "limit": 500, "locale": self._locale},
        )

        requested_products = set(self._allowed_products)
        selected_ids = {
            str(item["id"])
            for item in payload.get("data", [])
            if self._matches_product(item.get("name"), item.get("permalink"), requested_products)
        }

        if not selected_ids:
            raise AskProviderConfigurationError(
                "None of the configured Zoho KB product scopes matched the public root categories",
                details={"products": sorted(requested_products)},
            )

        self._selected_kb_root_ids = selected_ids
        return selected_ids

    def _resolve_selected_community_category_ids(self) -> set[str]:
        if self._selected_community_category_ids is not None:
            return self._selected_community_category_ids

        payload = self._get_json(
            "https://help.zoho.com/portal/api/communityCategory",
            params={"portalId": self._resolve_portal_id()},
        )
        requested_products = set(self._allowed_products)
        selected_ids: set[str] = set()

        for category in payload.get("data", []):
            if self._matches_product(category.get("name"), category.get("permalink"), requested_products):
                self._collect_category_ids(category, selected_ids)

        self._selected_community_category_ids = selected_ids
        return selected_ids

    def _get_json(self, url: str, *, params: dict[str, Any]) -> dict[str, Any]:
        try:
            response = self._client.get(url, params=params)
        except httpx.HTTPError as exc:
            raise AskProviderUnavailableError(
                "Unable to reach Zoho's public help center",
                details={"url": url, "error": str(exc)},
            ) from exc

        if response.status_code >= 400:
            raise AskProviderUnavailableError(
                "Zoho's public help center returned an unexpected error",
                details={"statusCode": response.status_code, "url": str(response.request.url)},
            )

        return response.json()

    def _rerank_kb_results(
        self,
        question: str,
        results: list[KbArticleSearchResult],
    ) -> list[KbArticleSearchResult]:
        question_tokens = self._tokenize_question(question)
        return sorted(
            results,
            key=lambda result: self._score_text_match(question_tokens, result.title, result.summary),
            reverse=True,
        )

    def _rerank_community_results(
        self,
        question: str,
        results: list[CommunityTopicSearchResult],
    ) -> list[CommunityTopicSearchResult]:
        question_tokens = self._tokenize_question(question)
        return sorted(
            results,
            key=lambda result: self._score_text_match(question_tokens, result.subject, result.content),
            reverse=True,
        )

    @staticmethod
    def _tokenize_question(question: str) -> list[str]:
        return [
            token
            for token in re.findall(r"[a-z0-9]+", question.lower())
            if len(token) > 2 and token not in QUESTION_STOP_WORDS
        ]

    @staticmethod
    def _score_text_match(question_tokens: list[str], title: str, body: str) -> int:
        if not question_tokens:
            return 0

        normalized_title = ZohoPublicAskProvider._normalize_value(title)
        title_tokens = set(re.findall(r"[a-z0-9]+", title.lower()))
        body_tokens = set(re.findall(r"[a-z0-9]+", body.lower()))
        score = sum(5 for token in question_tokens if token in title_tokens)
        score += sum(2 for token in question_tokens if token in body_tokens)

        if "reset" in question_tokens and "mfa" in question_tokens and "resetmfa" in normalized_title:
            score += 8

        return score

    @staticmethod
    def _collect_category_ids(category: dict[str, Any], category_ids: set[str]) -> None:
        category_ids.add(str(category["id"]))
        for child in category.get("child", []):
            ZohoPublicAskProvider._collect_category_ids(child, category_ids)

    @staticmethod
    def _matches_product(name: Any, permalink: Any, requested_products: set[str]) -> bool:
        normalized_name = ZohoPublicAskProvider._normalize_value(name)
        normalized_permalink = ZohoPublicAskProvider._normalize_value(permalink)

        for product in requested_products:
            aliases = PRODUCT_ALIASES.get(product, {product})
            if normalized_name in aliases or normalized_permalink in aliases:
                return True

        return False

    @staticmethod
    def _parse_allowed_products(raw_products: str | None) -> tuple[str, ...]:
        if not raw_products:
            return DEFAULT_ALLOWED_PRODUCTS
        return tuple(product.strip() for product in raw_products.split(",") if product.strip())

    @staticmethod
    def _parse_bool(raw_value: str | None, default: bool) -> bool:
        if raw_value is None:
            return default
        return raw_value.strip().lower() in {"1", "true", "yes", "on"}

    @staticmethod
    def _extract_locale(help_center_root: str) -> str:
        path_segments = [segment for segment in urlparse(help_center_root).path.split("/") if segment]
        if len(path_segments) >= 2 and path_segments[0] == "portal":
            return path_segments[1]
        return "en"

    @staticmethod
    def _canonicalize_product(raw_product: str) -> str:
        normalized = ZohoPublicAskProvider._normalize_value(raw_product)
        for canonical_name, aliases in PRODUCT_ALIASES.items():
            if normalized in aliases:
                return canonical_name
        return normalized

    @staticmethod
    def _normalize_value(value: Any) -> str:
        return re.sub(r"[^a-z0-9]+", "", str(value or "").lower())

    @staticmethod
    def _clean_text(value: Any) -> str:
        text = html.unescape(str(value or ""))
        text = re.sub(r"<[^>]+>", " ", text)
        text = WHITESPACE_PATTERN.sub(" ", text).strip()
        if len(text) <= 280:
            return text
        return f"{text[:277].rstrip()}..."
