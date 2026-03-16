export type ZohoSource = {
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
  confidenceLabel: "High" | "Medium" | "Low";
  suggestedReply: string;
  sources: ZohoSource[];
};

export type SimilarTicketsRequest = {
  query: string;
};

export type TicketMatch = {
  ticketId: string;
  subject: string;
  similarityScore: number;
  snippet: string;
  resolutionSummary: string;
  draftSuggestedAnswer: string;
};

export type SimilarTicketsResponse = {
  tickets: TicketMatch[];
};
