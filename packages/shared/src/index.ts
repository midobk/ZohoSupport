export type ZohoSource = {
  id: string;
  title: string;
  summary: string;
  url: string;
};

export type AnswerRequest = {
  question: string;
};

export type AnswerResponse = {
  answer: string;
  sources: ZohoSource[];
};

export type SimilarTicketsRequest = {
  query: string;
};

export type TicketMatch = {
  ticketId: string;
  subject: string;
  confidence: number;
  snippet: string;
  resolution: string;
};

export type SimilarTicketsResponse = {
  tickets: TicketMatch[];
};
