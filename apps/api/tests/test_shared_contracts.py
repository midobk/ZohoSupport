import pytest
from pydantic import ValidationError

from app.shared_contracts import (
    AnswerResponseContract,
    TicketSimilarityResultContract,
)


def test_answer_response_contract_validates_confidence_label() -> None:
    with pytest.raises(ValidationError):
        AnswerResponseContract(
            answer="Use reset flow",
            confidenceLabel="Certain",
            suggestedReply="Please try this.",
            generation={
                "mode": "AI",
                "label": "AI answer",
                "description": "Generated with Google Gemini using gemini-2.5-flash.",
            },
            sources=[],
        )


def test_answer_response_contract_requires_source_trust_metadata() -> None:
    with pytest.raises(ValidationError):
        AnswerResponseContract(
            answer="Use reset flow",
            confidenceLabel="High",
            suggestedReply="Please try this.",
            generation={
                "mode": "Search",
                "label": "Search answer",
                "description": "Built from Zoho search results only.",
            },
            sources=[
                {
                    "id": "kb-1",
                    "title": "Reset MFA",
                    "snippet": "steps",
                    "url": "https://help.zoho.com/kb/mfa",
                }
            ],
        )


def test_answer_response_contract_requires_generation_metadata() -> None:
    with pytest.raises(ValidationError):
        AnswerResponseContract(
            answer="Use reset flow",
            confidenceLabel="High",
            suggestedReply="Please try this.",
            sources=[],
        )


def test_ticket_similarity_result_contract_enforces_score_range() -> None:
    with pytest.raises(ValidationError):
        TicketSimilarityResultContract(
            ticketId="T-1",
            subject="MFA issue",
            similarityScore=1.2,
            snippet="Issue",
            resolutionSummary="Resolved",
            draftSuggestedAnswer="Response",
        )
