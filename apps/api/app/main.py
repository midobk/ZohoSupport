from typing import Literal

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, HttpUrl

from .mock_data import MOCK_TICKETS, ZOHO_SOURCES

app = FastAPI(title="Zoho Support Copilot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

ConfidenceLabel = Literal["high", "medium", "low"]


class SourceResult(BaseModel):
    id: str = Field(..., min_length=1)
    title: str = Field(..., min_length=1)
    summary: str = Field(..., min_length=1)
    url: HttpUrl


class DraftReply(BaseModel):
    message: str = Field(..., min_length=1)
    confidenceLabel: ConfidenceLabel


class AnswerRequest(BaseModel):
    question: str = Field(..., min_length=3)


class AnswerResponse(BaseModel):
    answer: str = Field(..., min_length=1)
    sources: list[SourceResult]
    draftReply: DraftReply


class SimilarTicketsRequest(BaseModel):
    query: str = Field(..., min_length=3)


class TicketSimilarityResult(BaseModel):
    ticketId: str = Field(..., min_length=1)
    subject: str = Field(..., min_length=1)
    confidence: float = Field(..., ge=0, le=1)
    confidenceLabel: ConfidenceLabel
    snippet: str = Field(..., min_length=1)
    resolution: str = Field(..., min_length=1)


class SimilarTicketsResponse(BaseModel):
    tickets: list[TicketSimilarityResult]


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/answer", response_model=AnswerResponse)
def answer(payload: AnswerRequest) -> AnswerResponse:
    return AnswerResponse(
        answer=(
            f"For '{payload.question}', start by validating the user identity, "
            "then run the MFA reset workflow in Zoho Directory and ask the user "
            "to complete login from a trusted device."
        ),
        sources=ZOHO_SOURCES,
        draftReply=DraftReply(
            message=(
                "Thanks for contacting Zoho Support. I have validated your account access issue "
                "and can help reset MFA after identity verification."
            ),
            confidenceLabel="high",
        ),
    )


@app.post("/api/similar-tickets", response_model=SimilarTicketsResponse)
def similar_tickets(payload: SimilarTicketsRequest) -> SimilarTicketsResponse:
    q = payload.query.lower()

    ranked = sorted(
        MOCK_TICKETS,
        key=lambda t: (q in t["subject"].lower()) or (q in t["snippet"].lower()),
        reverse=True,
    )

    return SimilarTicketsResponse(tickets=ranked)
