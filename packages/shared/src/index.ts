export type ConfidenceLabel = "High" | "Medium" | "Low";
export type DraftReply = string;
export type AnswerGenerationMode = "AI" | "Search";
export type AnswerRequestMode = "ai" | "search";

export type AnswerGeneration = {
  mode: AnswerGenerationMode;
  label: string;
  description: string;
};

export type SourceResult = {
  id: string;
  title: string;
  snippet: string;
  url: string;
  sourceType: "OfficialKB" | "CommunityPost" | "HistoricalTicket";
  trustLabel: "Verified" | "Unverified";
};

export type AnswerRequest = {
  question: string;
  mode: AnswerRequestMode;
  model?: string;
};

export type AnswerResponse = {
  answer: string;
  confidenceLabel: ConfidenceLabel;
  suggestedReply: DraftReply;
  generation: AnswerGeneration;
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

const parseAnswerRequestMode = (value: unknown): AnswerRequestMode => {
  if (value === "ai" || value === "search") {
    return value;
  }
  throw new Error("Invalid field: mode");
};

const parseAnswerGenerationMode = (value: unknown): AnswerGenerationMode => {
  if (value === "AI" || value === "Search") {
    return value;
  }
  throw new Error("Invalid field: generation.mode");
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
    sourceType: parseSourceType((value as Record<string, unknown>).sourceType),
    trustLabel: parseTrustLabel((value as Record<string, unknown>).trustLabel),
  };
};

const parseAnswerGeneration = (value: unknown): AnswerGeneration => {
  if (!value || typeof value !== "object") {
    throw new Error("Invalid field: generation");
  }

  const raw = value as Record<string, unknown>;
  return {
    mode: parseAnswerGenerationMode(raw.mode),
    label: parseString(raw.label, "generation.label"),
    description: parseString(raw.description, "generation.description"),
  };
};

const parseSourceType = (value: unknown): SourceResult["sourceType"] => {
  if (value === "OfficialKB" || value === "CommunityPost" || value === "HistoricalTicket") {
    return value;
  }
  throw new Error("Invalid field: sourceType");
};

const parseTrustLabel = (value: unknown): SourceResult["trustLabel"] => {
  if (value === "Verified" || value === "Unverified") {
    return value;
  }
  throw new Error("Invalid field: trustLabel");
};

export const answerRequestSchema: Parser<AnswerRequest> = {
  parse(value: unknown): AnswerRequest {
    if (!value || typeof value !== "object") {
      throw new Error("Invalid answer request");
    }

    const raw = value as Record<string, unknown>;
    const mode = "mode" in raw && raw.mode !== undefined
      ? parseAnswerRequestMode(raw.mode)
      : "search";

    return {
      question: parseString(raw.question, "question", 3),
      mode,
      model: mode === "ai" && "model" in raw && raw.model !== undefined && raw.model !== null
        ? parseString(raw.model, "model")
        : undefined,
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
      generation: parseAnswerGeneration(raw.generation),
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
