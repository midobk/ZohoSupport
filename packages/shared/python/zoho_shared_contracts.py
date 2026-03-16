from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field, HttpUrl


class ConfidenceLabel(str, Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class AnswerRequestContract(BaseModel):
    question: str = Field(..., min_length=3)


class SourceResultContract(BaseModel):
    id: str = Field(..., min_length=1)
    title: str = Field(..., min_length=1)
    snippet: str = Field(..., min_length=1)
    url: HttpUrl


class AnswerResponseContract(BaseModel):
    answer: str = Field(..., min_length=1)
    confidenceLabel: ConfidenceLabel
    suggestedReply: str = Field(..., min_length=1)
    sources: list[SourceResultContract]


class SimilarTicketsRequestContract(BaseModel):
    query: str = Field(..., min_length=3)


class TicketSimilarityResultContract(BaseModel):
    ticketId: str = Field(..., min_length=1)
    subject: str = Field(..., min_length=1)
    similarityScore: float = Field(..., ge=0, le=1)
    snippet: str = Field(..., min_length=1)
    resolutionSummary: str = Field(..., min_length=1)
    draftSuggestedAnswer: str = Field(..., min_length=1)


class SimilarTicketsResponseContract(BaseModel):
    tickets: list[TicketSimilarityResultContract]
