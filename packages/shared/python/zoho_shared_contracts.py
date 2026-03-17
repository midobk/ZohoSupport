from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, HttpUrl


class ConfidenceLabel(str, Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class AnswerRequestMode(str, Enum):
    AI = "ai"
    SEARCH = "search"


class AnswerKeyProfile(str, Enum):
    UNPAID = "unpaid"
    PAID = "paid"


class AnswerRequestContract(BaseModel):
    question: str = Field(..., min_length=3)
    mode: AnswerRequestMode = AnswerRequestMode.SEARCH
    model: Optional[str] = None
    keyProfile: Optional[AnswerKeyProfile] = None


class AnswerGenerationMode(str, Enum):
    AI = "AI"
    SEARCH = "Search"


class AnswerGenerationContract(BaseModel):
    mode: AnswerGenerationMode
    label: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)


class SourceType(str, Enum):
    OFFICIAL_KB = "OfficialKB"
    COMMUNITY_POST = "CommunityPost"
    HISTORICAL_TICKET = "HistoricalTicket"


class TrustLabel(str, Enum):
    VERIFIED = "Verified"
    UNVERIFIED = "Unverified"


class SourceResultContract(BaseModel):
    id: str = Field(..., min_length=1)
    title: str = Field(..., min_length=1)
    snippet: str = Field(..., min_length=1)
    url: HttpUrl
    sourceType: SourceType
    trustLabel: TrustLabel


class AnswerResponseContract(BaseModel):
    answer: str = Field(..., min_length=1)
    confidenceLabel: ConfidenceLabel
    suggestedReply: str = Field(..., min_length=1)
    generation: AnswerGenerationContract
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
