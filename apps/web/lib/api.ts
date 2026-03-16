import {
  AnswerResponse,
  SimilarTicketsResponse,
  answerRequestSchema,
  answerResponseSchema,
  similarTicketsRequestSchema,
  similarTicketsResponseSchema,
} from "@zoho/shared";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export async function fetchAnswer(question: string): Promise<AnswerResponse> {
  const payload = answerRequestSchema.parse({ question });

  const res = await fetch(`${API_BASE_URL}/api/answer`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    throw new Error("Unable to fetch answer.");
  }

  return answerResponseSchema.parse(await res.json());
}

export async function fetchSimilarTickets(query: string): Promise<SimilarTicketsResponse> {
  const payload = similarTicketsRequestSchema.parse({ query });

  const res = await fetch(`${API_BASE_URL}/api/similar-tickets`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    throw new Error("Unable to fetch similar tickets.");
  }

  return similarTicketsResponseSchema.parse(await res.json());
}
