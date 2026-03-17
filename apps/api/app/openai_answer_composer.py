from __future__ import annotations

import json
import os
from typing import Any, Iterable

import httpx
from pydantic import ValidationError

from .answer_composer import AnswerComposer, ComposerDescriptor, ComposedAnswer
from .ask_provider import AskProviderConfigurationError, AskProviderUnavailableError

DEFAULT_OPENAI_BASE_URL = "https://api.openai.com/v1"
DEFAULT_OPENAI_MODEL = "gpt-4.1-mini"


class OpenAiAnswerComposer(AnswerComposer):
    def __init__(
        self,
        *,
        client: httpx.Client | None = None,
        api_key: str | None = None,
        model: str | None = None,
        base_url: str | None = None,
        enabled: bool | None = None,
    ) -> None:
        self._api_key = api_key if api_key is not None else os.getenv("OPENAI_API_KEY")
        self._model = model or os.getenv("LLM_MODEL_ANSWER", DEFAULT_OPENAI_MODEL)
        self._base_url = (base_url or os.getenv("OPENAI_BASE_URL", DEFAULT_OPENAI_BASE_URL)).rstrip("/")
        self._enabled = enabled if enabled is not None else self._parse_bool(os.getenv("ASK_ENABLE_AI"), True)
        self._client = client or httpx.Client(timeout=20.0)

    def is_enabled(self) -> bool:
        return self._enabled and bool(self._api_key)

    def describe(self, *, model: str | None = None) -> ComposerDescriptor:
        return ComposerDescriptor(providerLabel="OpenAI", modelLabel=self._model)

    def compose_answer(
        self,
        *,
        question: str,
        official_sources: Iterable[dict[str, str]],
        community_sources: Iterable[dict[str, str]],
        model: str | None = None,
    ) -> ComposedAnswer:
        if not self.is_enabled():
            raise AskProviderConfigurationError("OpenAI answer composition is not enabled")

        system_prompt = (
            "You are a support copilot for Zoho products. "
            "Use only the provided sources. "
            "Treat official knowledge base sources as authoritative. "
            "Treat community sources as unverified supporting context only and never present them as policy. "
            "If official evidence is limited or conflicting, be cautious. "
            "Keep the answer concise and useful for a support agent. "
            "The suggestedReply must be customer-ready, professional, and grounded only in the supplied sources."
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
            "model": self._model,
            "store": False,
            "input": [
                {
                    "role": "system",
                    "content": [{"type": "input_text", "text": system_prompt}],
                },
                {
                    "role": "user",
                    "content": [{"type": "input_text", "text": json.dumps(user_payload)}],
                },
            ],
            "text": {
                "format": {
                    "type": "json_schema",
                    "name": "zoho_support_answer",
                    "strict": True,
                    "schema": {
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
                }
            },
            "max_output_tokens": 500,
        }

        try:
            response = self._client.post(
                f"{self._base_url}/responses",
                headers={
                    "Authorization": f"Bearer {self._api_key}",
                    "Content-Type": "application/json",
                },
                json=request_body,
            )
        except httpx.HTTPError as exc:
            raise AskProviderUnavailableError(
                "OpenAI answer composition request failed",
                details={"error": str(exc)},
            ) from exc

        if response.status_code >= 400:
            raise AskProviderUnavailableError(
                "OpenAI answer composition returned an error",
                details={"statusCode": response.status_code, "body": response.text},
            )

        payload = response.json()
        try:
            composed = json.loads(self._extract_output_text(payload))
            return ComposedAnswer.model_validate(composed)
        except (json.JSONDecodeError, ValidationError, ValueError) as exc:
            raise AskProviderUnavailableError(
                "OpenAI answer composition returned an invalid payload",
                details={"error": str(exc)},
            ) from exc

    @staticmethod
    def _extract_output_text(payload: dict[str, Any]) -> str:
        direct_text = payload.get("output_text")
        if isinstance(direct_text, str) and direct_text.strip():
            return direct_text

        for item in payload.get("output", []):
            if not isinstance(item, dict):
                continue
            for content in item.get("content", []):
                if not isinstance(content, dict):
                    continue
                text = content.get("text")
                if isinstance(text, str) and text.strip():
                    return text
                output_text = content.get("output_text")
                if isinstance(output_text, str) and output_text.strip():
                    return output_text
                json_value = content.get("json")
                if isinstance(json_value, dict):
                    return json.dumps(json_value)

        raise ValueError("Missing output text in OpenAI response payload")

    @staticmethod
    def _parse_bool(raw_value: str | None, default: bool) -> bool:
        if raw_value is None:
            return default
        return raw_value.strip().lower() in {"1", "true", "yes", "on"}
