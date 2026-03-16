import { AnswerResponse, SimilarTicketsResponse } from "@zoho/shared/src";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export async function fetchAnswer(question: string): Promise<AnswerResponse> {
  const res = await fetch(`${API_BASE_URL}/api/answer`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });

  if (!res.ok) {
    throw new Error("Unable to fetch answer.");
  }

  return res.json();
}

export async function fetchSimilarTickets(query: string): Promise<SimilarTicketsResponse> {
  const res = await fetch(`${API_BASE_URL}/api/similar-tickets`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query }),
  });

  if (!res.ok) {
    throw new Error("Unable to fetch similar tickets.");
  }

  return res.json();
}
