from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .mock_data import MOCK_TICKETS, ZOHO_SOURCES

app = FastAPI(title="Zoho Support Copilot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnswerRequest(BaseModel):
    question: str = Field(..., min_length=3)


class SimilarTicketsRequest(BaseModel):
    query: str = Field(..., min_length=3)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/answer")
def answer(payload: AnswerRequest) -> dict:
    return {
        "answer": (
            f"For '{payload.question}', start by validating the user identity, "
            "then run the MFA reset workflow in Zoho Directory and ask the user "
            "to complete login from a trusted device."
        ),
        "sources": ZOHO_SOURCES,
    }


@app.post("/api/similar-tickets")
def similar_tickets(payload: SimilarTicketsRequest) -> dict:
    q = payload.query.lower()

    ranked = sorted(
        MOCK_TICKETS,
        key=lambda t: (q in t["subject"].lower()) or (q in t["snippet"].lower()),
        reverse=True,
    )

    return {"tickets": ranked}
