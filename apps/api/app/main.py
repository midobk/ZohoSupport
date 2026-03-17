from __future__ import annotations

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .ask_provider import AskProvider, AskProviderError
from .ask_provider_factory import resolve_ask_provider
from .mcp_provider import McpProvider, McpProviderError
from .mcp_provider_factory import (
    get_provider_timeout_ms,
    resolve_mcp_provider,
    run_with_timeout,
)
from .shared_contracts import (
    AnswerRequestContract,
    AnswerResponseContract,
    SimilarTicketsRequestContract,
    SimilarTicketsResponseContract,
    TicketSimilarityResultContract,
)

app = FastAPI(title="Zoho Support Copilot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)



class TicketSearchRequest(BaseModel):
    query: str = Field(..., min_length=3)



def get_mcp_provider() -> McpProvider:
    return resolve_mcp_provider()


def get_ask_provider() -> AskProvider:
    return resolve_ask_provider()


def _raise_http_from_provider_error(exc: McpProviderError) -> None:
    raise HTTPException(
        status_code=exc.status_code,
        detail={
            "code": exc.code,
            "message": exc.message,
            "details": exc.details,
        },
    ) from exc


def _raise_http_from_ask_provider_error(exc: AskProviderError) -> None:
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


@app.post("/api/answer", response_model=AnswerResponseContract)
def answer(
    payload: AnswerRequestContract,
    provider: AskProvider = Depends(get_ask_provider),
) -> AnswerResponseContract:
    try:
        return provider.answer_question(payload.question, mode=payload.mode, model=payload.model)
    except AskProviderError as exc:
        _raise_http_from_ask_provider_error(exc)


@app.post("/api/similar-tickets", response_model=SimilarTicketsResponseContract)
def similar_tickets(
    payload: SimilarTicketsRequestContract,
    provider: McpProvider = Depends(get_mcp_provider),
) -> SimilarTicketsResponseContract:
    timeout_ms = get_provider_timeout_ms()

    try:
        tickets = run_with_timeout(
            lambda: provider.find_similar_cases(payload.query), timeout_ms=timeout_ms
        )
    except McpProviderError as exc:
        _raise_http_from_provider_error(exc)

    return SimilarTicketsResponseContract(
        tickets=[
            TicketSimilarityResultContract(
                ticketId=ticket.ticket_id,
                subject=ticket.subject,
                similarityScore=ticket.similarity_score,
                snippet=ticket.snippet,
                resolutionSummary=ticket.resolution_summary,
                draftSuggestedAnswer=ticket.draft_suggested_answer,
            )
            for ticket in tickets
        ]
    )


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
