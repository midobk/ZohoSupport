from __future__ import annotations

from typing import Any, Protocol

from .shared_contracts import AnswerRequestMode, AnswerResponseContract


class AskProvider(Protocol):
    def answer_question(
        self,
        question: str,
        *,
        mode: AnswerRequestMode = AnswerRequestMode.SEARCH,
    ) -> AnswerResponseContract:
        """Return a grounded answer and supporting sources for the Ask flow."""


class AskProviderError(Exception):
    def __init__(
        self,
        code: str,
        message: str,
        *,
        status_code: int = 500,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}


class AskProviderConfigurationError(AskProviderError):
    def __init__(self, message: str, *, details: dict[str, Any] | None = None) -> None:
        super().__init__(
            code="ASK_PROVIDER_CONFIGURATION_ERROR",
            message=message,
            status_code=500,
            details=details,
        )


class AskProviderUnavailableError(AskProviderError):
    def __init__(self, message: str, *, details: dict[str, Any] | None = None) -> None:
        super().__init__(
            code="ASK_PROVIDER_UNAVAILABLE",
            message=message,
            status_code=502,
            details=details,
        )
