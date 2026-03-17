from __future__ import annotations

from typing import Iterable, Protocol

from pydantic import BaseModel, Field

from .shared_contracts import ConfidenceLabel


class ComposedAnswer(BaseModel):
    answer: str = Field(..., min_length=1)
    suggestedReply: str = Field(..., min_length=1)
    confidenceLabel: ConfidenceLabel


class ComposerDescriptor(BaseModel):
    providerLabel: str = Field(..., min_length=1)
    modelLabel: str = Field(..., min_length=1)


class AnswerComposer(Protocol):
    def is_enabled(self) -> bool:
        """Return True when the composer is configured and should be used."""

    def describe(self, *, model: str | None = None) -> ComposerDescriptor:
        """Return user-facing information about the active composer."""

    def compose_answer(
        self,
        *,
        question: str,
        official_sources: Iterable[dict[str, str]],
        community_sources: Iterable[dict[str, str]],
        model: str | None = None,
    ) -> ComposedAnswer:
        """Compose a grounded answer from retrieved sources."""
