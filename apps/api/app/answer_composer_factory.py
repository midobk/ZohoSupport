from __future__ import annotations

import os
from functools import lru_cache

from .answer_composer import AnswerComposer, ComposerDescriptor
from .gemini_answer_composer import GeminiAnswerComposer
from .openai_answer_composer import OpenAiAnswerComposer


class DisabledAnswerComposer:
    def is_enabled(self, *, key_profile=None) -> bool:
        return False

    def describe(self, *, model=None, key_profile=None) -> ComposerDescriptor:
        raise RuntimeError("Answer composer is disabled")

    def compose_answer(self, **_: object) -> None:
        raise RuntimeError("Answer composer is disabled")


@lru_cache(maxsize=1)
def resolve_answer_composer() -> AnswerComposer:
    provider = os.getenv("ANSWER_COMPOSER_PROVIDER", "auto").strip().lower()

    if provider == "none":
        return DisabledAnswerComposer()

    if provider == "openai":
        return OpenAiAnswerComposer()

    if provider == "gemini":
        return GeminiAnswerComposer()

    if provider == "auto":
        if any(
            os.getenv(variable)
            for variable in ("GEMINI_API_KEY", "GEMINI_API_KEY_UNPAID", "GEMINI_API_KEY_PAID")
        ):
            return GeminiAnswerComposer()
        if os.getenv("OPENAI_API_KEY"):
            return OpenAiAnswerComposer()
        return DisabledAnswerComposer()

    return DisabledAnswerComposer()
