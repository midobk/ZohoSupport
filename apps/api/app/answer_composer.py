from __future__ import annotations

from typing import Iterable, Optional, Protocol

from pydantic import BaseModel, Field

from .shared_contracts import AnswerKeyProfile, ConfidenceLabel


class ComposedAnswer(BaseModel):
    answer: str = Field(..., min_length=1)
    suggestedReply: str = Field(..., min_length=1)
    confidenceLabel: ConfidenceLabel


class ComposerDescriptor(BaseModel):
    providerLabel: str = Field(..., min_length=1)
    modelLabel: str = Field(..., min_length=1)
    keyProfileLabel: Optional[str] = None


class AnswerComposer(Protocol):
    def is_enabled(self, *, key_profile: AnswerKeyProfile | None = None) -> bool:
        """Return True when the composer is configured and should be used."""

    def describe(
        self,
        *,
        model: str | None = None,
        key_profile: AnswerKeyProfile | None = None,
    ) -> ComposerDescriptor:
        """Return user-facing information about the active composer."""

    def compose_answer(
        self,
        *,
        question: str,
        official_sources: Iterable[dict[str, str]],
        community_sources: Iterable[dict[str, str]],
        model: str | None = None,
        key_profile: AnswerKeyProfile | None = None,
    ) -> ComposedAnswer:
        """Compose a grounded answer from retrieved sources."""
