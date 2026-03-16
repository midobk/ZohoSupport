export type ConfidenceLabel = "High" | "Medium" | "Low";
export type DraftReply = string;

export type SourceResult = {
  id: string;
  title: string;
  snippet: string;
  url: string;
};

export type AnswerRequest = {
  question: string;
};

export type AnswerResponse = {
  answer: string;
  confidenceLabel: ConfidenceLabel;
  suggestedReply: DraftReply;
  sources: SourceResult[];
};

export type TicketSimilarityResult = {
  ticketId: string;
  subject: string;
  similarityScore: number;
  snippet: string;
  resolutionSummary: string;
  draftSuggestedAnswer: DraftReply;
};

export type SimilarTicketsRequest = {
  query: string;
};

export type SimilarTicketsResponse = {
  tickets: TicketSimilarityResult[];
};

type Parser<T> = { parse: (value: unknown) => T };

const parseString = (value: unknown, fieldName: string, minLength = 1): string => {
  if (typeof value !== "string" || value.trim().length < minLength) {
    throw new Error(`Invalid field: ${fieldName}`);
  }
  return value;
};

const parseConfidenceLabel = (value: unknown): ConfidenceLabel => {
  if (value === "High" || value === "Medium" || value === "Low") {
    return value;
  }
  throw new Error("Invalid field: confidenceLabel");
};

const parseUrl = (value: unknown, fieldName: string): string => {
  const candidate = parseString(value, fieldName);
  try {
    // eslint-disable-next-line no-new
    new URL(candidate);
    return candidate;
  } catch {
    throw new Error(`Invalid field: ${fieldName}`);
  }
};

const parseSourceResult = (value: unknown): SourceResult => {
  if (!value || typeof value !== "object") {
    throw new Error("Invalid field: sourceResult");
  }

  return {
    id: parseString((value as Record<string, unknown>).id, "source.id"),
    title: parseString((value as Record<string, unknown>).title, "source.title"),
    snippet: parseString((value as Record<string, unknown>).snippet, "source.snippet"),
    url: parseUrl((value as Record<string, unknown>).url, "source.url"),
  };
};

export const answerRequestSchema: Parser<AnswerRequest> = {
  parse(value: unknown): AnswerRequest {
    if (!value || typeof value !== "object") {
      throw new Error("Invalid answer request");
    }

    return {
      question: parseString((value as Record<string, unknown>).question, "question", 3),
    };
  },
};

export const answerResponseSchema: Parser<AnswerResponse> = {
  parse(value: unknown): AnswerResponse {
    if (!value || typeof value !== "object") {
      throw new Error("Invalid answer response");
    }

    const raw = value as Record<string, unknown>;
    const sources = Array.isArray(raw.sources) ? raw.sources.map(parseSourceResult) : null;
    if (!sources) {
      throw new Error("Invalid field: sources");
    }

    return {
      answer: parseString(raw.answer, "answer"),
      confidenceLabel: parseConfidenceLabel(raw.confidenceLabel),
      suggestedReply: parseString(raw.suggestedReply, "suggestedReply"),
      sources,
    };
  },
};

const parseTicketSimilarityResult = (value: unknown): TicketSimilarityResult => {
  if (!value || typeof value !== "object") {
    throw new Error("Invalid field: ticketSimilarityResult");
  }

  const raw = value as Record<string, unknown>;
  const similarityScore = raw.similarityScore;
  if (typeof similarityScore !== "number" || similarityScore < 0 || similarityScore > 1) {
    throw new Error("Invalid field: similarityScore");
  }

  return {
    ticketId: parseString(raw.ticketId, "ticketId"),
    subject: parseString(raw.subject, "subject"),
    similarityScore,
    snippet: parseString(raw.snippet, "snippet"),
    resolutionSummary: parseString(raw.resolutionSummary, "resolutionSummary"),
    draftSuggestedAnswer: parseString(raw.draftSuggestedAnswer, "draftSuggestedAnswer"),
  };
};

export const similarTicketsRequestSchema: Parser<SimilarTicketsRequest> = {
  parse(value: unknown): SimilarTicketsRequest {
    if (!value || typeof value !== "object") {
      throw new Error("Invalid similar tickets request");
    }

    return {
      query: parseString((value as Record<string, unknown>).query, "query", 3),
    };
  },
};

export const similarTicketsResponseSchema: Parser<SimilarTicketsResponse> = {
  parse(value: unknown): SimilarTicketsResponse {
    if (!value || typeof value !== "object") {
      throw new Error("Invalid similar tickets response");
    }

    const ticketsValue = (value as Record<string, unknown>).tickets;
    if (!Array.isArray(ticketsValue)) {
      throw new Error("Invalid field: tickets");
    }

    return {
      tickets: ticketsValue.map(parseTicketSimilarityResult),
    };
  },
};
