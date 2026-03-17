from __future__ import annotations

import json
import os
from typing import Any, Iterable

import httpx
from pydantic import ValidationError

from .answer_composer import AnswerComposer, ComposerDescriptor, ComposedAnswer
from .ask_provider import AskProviderConfigurationError, AskProviderUnavailableError
from .shared_contracts import AnswerKeyProfile

DEFAULT_GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta"
DEFAULT_GEMINI_MODEL = "gemini-2.5-flash"
SUPPORTED_GEMINI_MODELS = {
    "gemini-2.5-flash-lite",
    "gemini-2.5-flash",
    "gemini-2.5-pro",
    "gemini-3-flash-preview",
    "gemini-3.1-flash-lite-preview",
}


class GeminiAnswerComposer(AnswerComposer):
    def __init__(
        self,
        *,
        client: httpx.Client | None = None,
        api_key: str | None = None,
        model: str | None = None,
        base_url: str | None = None,
        enabled: bool | None = None,
    ) -> None:
        self._default_api_key = api_key if api_key is not None else os.getenv("GEMINI_API_KEY")
        self._model = model or os.getenv("GEMINI_MODEL_ANSWER", DEFAULT_GEMINI_MODEL)
        self._base_url = (base_url or os.getenv("GEMINI_BASE_URL", DEFAULT_GEMINI_BASE_URL)).rstrip("/")
        self._enabled = enabled if enabled is not None else self._parse_bool(os.getenv("ASK_ENABLE_AI"), True)
        self._client = client or httpx.Client(timeout=20.0)

    def is_enabled(self, *, key_profile: AnswerKeyProfile | None = None) -> bool:
        return self._enabled and bool(self._resolve_api_key(key_profile))

    def describe(
        self,
        *,
        model: str | None = None,
        key_profile: AnswerKeyProfile | None = None,
    ) -> ComposerDescriptor:
        return ComposerDescriptor(
            providerLabel="Google Gemini",
            modelLabel=self._resolve_model(model),
            keyProfileLabel=self._resolve_key_profile_label(key_profile),
        )

    def compose_answer(
        self,
        *,
        question: str,
        official_sources: Iterable[dict[str, str]],
        community_sources: Iterable[dict[str, str]],
        model: str | None = None,
        key_profile: AnswerKeyProfile | None = None,
    ) -> ComposedAnswer:
        if not self.is_enabled(key_profile=key_profile):
            raise AskProviderConfigurationError("Gemini answer composition is not enabled")

        resolved_model = self._resolve_model(model)
        api_key = self._resolve_api_key(key_profile)

        system_prompt = (
            "You are a support copilot for Zoho products. "
            "Use only the provided sources. "
            "Official knowledge-base sources are authoritative. "
            "Community sources are unverified context only and must not be presented as policy."
        )

        user_payload = {
            "question": question,
            "official_sources": list(official_sources),
            "community_sources": list(community_sources),
            "output_requirements": {
                "confidence_labels": ["High", "Medium", "Low"],
                "notes": [
                    "High requires clear official support for the answer.",
                    "Medium means official evidence exists but is partial or indirect.",
                    "Low means the answer should be cautious and ask for clarification.",
                ],
            },
        }

        request_body = {
            "systemInstruction": {"parts": [{"text": system_prompt}]},
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": json.dumps(user_payload)}],
                }
            ],
            "generationConfig": {
                "responseMimeType": "application/json",
                "responseJsonSchema": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "answer": {"type": "string"},
                        "suggestedReply": {"type": "string"},
                        "confidenceLabel": {
                            "type": "string",
                            "enum": ["High", "Medium", "Low"],
                        },
                    },
                    "required": ["answer", "suggestedReply", "confidenceLabel"],
                },
                "temperature": 0.2,
                "maxOutputTokens": 500,
            },
        }

        try:
            response = self._client.post(
                f"{self._base_url}/models/{resolved_model}:generateContent",
                params={"key": api_key},
                headers={"Content-Type": "application/json"},
                json=request_body,
            )
        except httpx.HTTPError as exc:
            raise AskProviderUnavailableError(
                "Gemini answer composition request failed",
                details={"error": str(exc)},
            ) from exc

        if response.status_code >= 400:
            raise AskProviderUnavailableError(
                "Gemini answer composition returned an error",
                details={"statusCode": response.status_code, "body": response.text},
            )

        payload = response.json()
        try:
            composed = self._parse_json_payload(self._extract_output_text(payload))
            return ComposedAnswer.model_validate(composed)
        except (json.JSONDecodeError, ValidationError, ValueError) as exc:
            raise AskProviderUnavailableError(
                "Gemini answer composition returned an invalid payload",
                details={"error": str(exc)},
            ) from exc

    @staticmethod
    def _extract_output_text(payload: dict[str, Any]) -> str:
        for candidate in payload.get("candidates", []):
            if not isinstance(candidate, dict):
                continue
            content = candidate.get("content")
            if not isinstance(content, dict):
                continue
            for part in content.get("parts", []):
                if not isinstance(part, dict):
                    continue
                text = part.get("text")
                if isinstance(text, str) and text.strip():
                    return text

        raise ValueError("Missing text in Gemini response payload")

    @classmethod
    def _parse_json_payload(cls, raw_text: str) -> dict[str, Any]:
        try:
            return json.loads(raw_text)
        except json.JSONDecodeError:
            return json.loads(cls._escape_control_chars_in_strings(raw_text))

    @staticmethod
    def _escape_control_chars_in_strings(raw_text: str) -> str:
        escaped: list[str] = []
        in_string = False
        escape_next = False

        for char in raw_text:
            if escape_next:
                escaped.append(char)
                escape_next = False
                continue

            if char == "\\":
                escaped.append(char)
                escape_next = True
                continue

            if char == '"':
                escaped.append(char)
                in_string = not in_string
                continue

            if in_string and char in {"\n", "\r", "\t"}:
                escaped.append({
                    "\n": "\\n",
                    "\r": "\\r",
                    "\t": "\\t",
                }[char])
                continue

            escaped.append(char)

        return "".join(escaped)

    @staticmethod
    def _parse_bool(raw_value: str | None, default: bool) -> bool:
        if raw_value is None:
            return default
        return raw_value.strip().lower() in {"1", "true", "yes", "on"}

    def _resolve_model(self, requested_model: str | None) -> str:
        candidate = (requested_model or self._model).strip()
        if candidate in SUPPORTED_GEMINI_MODELS:
            return candidate

        raise AskProviderConfigurationError(
            f"Unsupported Gemini model '{candidate}'",
            details={
                "requestedModel": candidate,
                "supportedModels": sorted(SUPPORTED_GEMINI_MODELS),
            },
        )

    def _resolve_api_key(self, key_profile: AnswerKeyProfile | None) -> str | None:
        if key_profile == AnswerKeyProfile.PAID:
            return os.getenv("GEMINI_API_KEY_PAID")

        if key_profile == AnswerKeyProfile.UNPAID:
            return os.getenv("GEMINI_API_KEY_UNPAID") or self._default_api_key

        return self._default_api_key or os.getenv("GEMINI_API_KEY_UNPAID") or os.getenv("GEMINI_API_KEY_PAID")

    @staticmethod
    def _resolve_key_profile_label(key_profile: AnswerKeyProfile | None) -> str | None:
        if key_profile == AnswerKeyProfile.PAID:
            return "paid"
        if key_profile == AnswerKeyProfile.UNPAID:
            return "unpaid"
        return None
