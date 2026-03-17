from __future__ import annotations

from .ask_provider import AskProvider
from .mock_data import ZOHO_SOURCES
from .shared_contracts import (
    AnswerGenerationContract,
    AnswerGenerationMode,
    AnswerRequestMode,
    AnswerResponseContract,
    ConfidenceLabel,
    SourceResultContract,
)


class MockAskProvider(AskProvider):
    def answer_question(
        self,
        question: str,
        *,
        mode: AnswerRequestMode = AnswerRequestMode.SEARCH,
        model: str | None = None,
    ) -> AnswerResponseContract:
        normalized_question = question.lower()

        has_reset_context = any(
            token in normalized_question
            for token in ["mfa", "otp", "login", "locked", "reset", "authenticator"]
        )

        if has_reset_context:
            answer_text = (
                "Confirm the customer's identity, reset MFA in Zoho Directory, and ask them to sign in "
                "from a trusted device to complete new factor enrollment."
            )
            confidence_label = ConfidenceLabel.HIGH
            suggested_reply = (
                "Thanks for reporting this. I have verified your account and reset your MFA setup. "
                "Please sign in again and complete the prompt to configure a new authenticator on your trusted device."
            )
        else:
            answer_text = (
                "Use the Zoho sign-in troubleshooting flow: verify identity, collect screenshots of the exact error, "
                "and apply the relevant recovery step from the KB before escalating."
            )
            confidence_label = ConfidenceLabel.MEDIUM
            suggested_reply = (
                "I can help with this sign-in issue. Please share the exact error shown on screen, and I will guide "
                "you through the next recovery step."
            )

        return AnswerResponseContract(
            answer=answer_text,
            confidenceLabel=confidence_label,
            suggestedReply=suggested_reply,
            generation=AnswerGenerationContract(
                mode=AnswerGenerationMode.SEARCH,
                label="Search answer",
                description="This answer was built from the local mock knowledge sources only. No AI model wrote the wording.",
            ),
            sources=[SourceResultContract.model_validate(source) for source in ZOHO_SOURCES],
        )
