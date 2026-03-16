from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .mock_data import ZOHO_SOURCES
from .providers.mcp import McpProviderError, build_mcp_provider

app = FastAPI(title="Zoho Support Copilot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

mcp_provider = build_mcp_provider()


class AnswerRequest(BaseModel):
    question: str = Field(..., min_length=3)


class SimilarTicketsRequest(BaseModel):
    query: str = Field(..., min_length=3)


class SearchTicketsRequest(BaseModel):
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
async def similar_tickets(payload: SimilarTicketsRequest) -> dict:
    try:
        tickets = await mcp_provider.find_similar_cases(query=payload.query)
        return {"tickets": tickets}
    except McpProviderError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail={
                "code": exc.code,
                "message": exc.message,
                "details": exc.details,
            },
        ) from exc


@app.post("/api/tickets/search")
async def search_tickets(payload: SearchTicketsRequest) -> dict:
    try:
        tickets = await mcp_provider.search_tickets(query=payload.query)
        return {"tickets": tickets}
    except McpProviderError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail={
                "code": exc.code,
                "message": exc.message,
                "details": exc.details,
            },
        ) from exc


@app.get("/api/tickets/{ticket_id}")
async def get_ticket_details(ticket_id: str) -> dict:
    try:
        ticket = await mcp_provider.get_ticket_details(ticket_id=ticket_id)
        return {"ticket": ticket}
    except McpProviderError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail={
                "code": exc.code,
                "message": exc.message,
                "details": exc.details,
            },
        ) from exc
