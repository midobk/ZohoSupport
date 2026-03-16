import {
  AnswerRequestSchema,
  AnswerResponse,
  AnswerResponseSchema,
  SimilarTicketsRequestSchema,
  SimilarTicketsResponse,
  SimilarTicketsResponseSchema,
} from "@zoho/shared/src";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export async function fetchAnswer(question: string): Promise<AnswerResponse> {
  const payload = AnswerRequestSchema.parse({ question });

  const res = await fetch(`${API_BASE_URL}/api/answer`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    throw new Error("Unable to fetch answer.");
  }

  const data = await res.json();
  return AnswerResponseSchema.parse(data);
}

export async function fetchSimilarTickets(query: string): Promise<SimilarTicketsResponse> {
  const payload = SimilarTicketsRequestSchema.parse({ query });

  const res = await fetch(`${API_BASE_URL}/api/similar-tickets`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    throw new Error("Unable to fetch similar tickets.");
  }

  const data = await res.json();
  return SimilarTicketsResponseSchema.parse(data);
}
