from __future__ import annotations

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .mcp_provider import McpProvider, McpProviderError
from .mcp_provider_factory import (
    get_provider_timeout_ms,
    resolve_mcp_provider,
    run_with_timeout,
)
from .mock_data import ZOHO_SOURCES

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


class TicketSearchRequest(BaseModel):
    query: str = Field(..., min_length=3)


def get_mcp_provider() -> McpProvider:
    return resolve_mcp_provider()


def _raise_http_from_provider_error(exc: McpProviderError) -> None:
    raise HTTPException(
        status_code=exc.status_code,
        detail={
            "code": exc.code,
            "message": exc.message,
            "details": exc.details,
        },
    ) from exc


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
def similar_tickets(
    payload: SimilarTicketsRequest,
    provider: McpProvider = Depends(get_mcp_provider),
) -> dict:
    timeout_ms = get_provider_timeout_ms()

    try:
        tickets = run_with_timeout(
            lambda: provider.find_similar_cases(payload.query), timeout_ms=timeout_ms
        )
    except McpProviderError as exc:
        _raise_http_from_provider_error(exc)

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


@app.post("/api/tickets/search")
def search_tickets(
    payload: TicketSearchRequest,
    provider: McpProvider = Depends(get_mcp_provider),
) -> dict:
    timeout_ms = get_provider_timeout_ms()

    try:
        tickets = run_with_timeout(
            lambda: provider.search_tickets(payload.query), timeout_ms=timeout_ms
        )
    except McpProviderError as exc:
        _raise_http_from_provider_error(exc)

    return {
        "tickets": [
            {
                "ticketId": ticket.ticket_id,
                "subject": ticket.subject,
                "snippet": ticket.snippet,
                "resolutionSummary": ticket.resolution_summary,
                "confidence": ticket.confidence,
            }
            for ticket in tickets
        ]
    }


@app.get("/api/tickets/{ticket_id}")
def get_ticket_details(
    ticket_id: str,
    provider: McpProvider = Depends(get_mcp_provider),
) -> dict:
    timeout_ms = get_provider_timeout_ms()

    try:
        ticket = run_with_timeout(
            lambda: provider.get_ticket_details(ticket_id), timeout_ms=timeout_ms
        )
    except McpProviderError as exc:
        _raise_http_from_provider_error(exc)

    return {
        "ticketId": ticket.ticket_id,
        "subject": ticket.subject,
        "snippet": ticket.snippet,
        "resolutionSummary": ticket.resolution_summary,
        "confidence": ticket.confidence,
    }
