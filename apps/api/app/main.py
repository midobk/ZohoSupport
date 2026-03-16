from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .mock_data import ZOHO_SOURCES
from .mock_mcp_adapter import MockMcpSimilarTicketsAdapter
from .similar_tickets_adapter import SimilarTicketsAdapter

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


def get_similar_tickets_adapter() -> SimilarTicketsAdapter:
    return MockMcpSimilarTicketsAdapter()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/answer")
def answer(payload: AnswerRequest) -> dict:
    normalized_question = payload.question.lower()

    has_reset_context = any(
        token in normalized_question
        for token in ["mfa", "otp", "login", "locked", "reset", "authenticator"]
    )

    if has_reset_context:
        answer_text = (
            "Confirm the customer's identity, reset MFA in Zoho Directory, and ask them to sign in "
            "from a trusted device to complete new factor enrollment."
        )
        confidence_label = "High"
        suggested_reply = (
            "Thanks for reporting this. I have verified your account and reset your MFA setup. "
            "Please sign in again and complete the prompt to configure a new authenticator on your trusted device."
        )
    else:
        answer_text = (
            "Use the Zoho sign-in troubleshooting flow: verify identity, collect screenshots of the exact error, "
            "and apply the relevant recovery step from the KB before escalating."
        )
        confidence_label = "Medium"
        suggested_reply = (
            "I can help with this sign-in issue. Please share the exact error shown on screen, and I will guide "
            "you through the next recovery step."
        )

    return {
        "answer": answer_text,
        "confidenceLabel": confidence_label,
        "suggestedReply": suggested_reply,
        "sources": ZOHO_SOURCES,
    }


@app.post("/api/similar-tickets")
def similar_tickets(payload: SimilarTicketsRequest) -> dict:
    adapter = get_similar_tickets_adapter()
    tickets = adapter.find_similar_tickets(payload.query)

    return {
        "tickets": [
            {
                "ticketId": ticket.ticket_id,
                "subject": ticket.subject,
                "similarityScore": ticket.similarity_score,
                "snippet": ticket.snippet,
                "resolutionSummary": ticket.resolution_summary,
                "draftSuggestedAnswer": ticket.draft_suggested_answer,
            }
            for ticket in tickets
        ]
    }
