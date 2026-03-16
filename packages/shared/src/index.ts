import { z } from "zod";

export const ConfidenceLabelSchema = z.enum(["high", "medium", "low"]);
export type ConfidenceLabel = z.infer<typeof ConfidenceLabelSchema>;

export const SourceResultSchema = z.object({
  id: z.string().min(1),
  title: z.string().min(1),
  summary: z.string().min(1),
  url: z.string().url(),
});
export type SourceResult = z.infer<typeof SourceResultSchema>;

export const DraftReplySchema = z.object({
  message: z.string().min(1),
  confidenceLabel: ConfidenceLabelSchema,
});
export type DraftReply = z.infer<typeof DraftReplySchema>;

export const AnswerRequestSchema = z.object({
  question: z.string().min(3),
});
export type AnswerRequest = z.infer<typeof AnswerRequestSchema>;

export const AnswerResponseSchema = z.object({
  answer: z.string().min(1),
  sources: z.array(SourceResultSchema),
  draftReply: DraftReplySchema,
});
export type AnswerResponse = z.infer<typeof AnswerResponseSchema>;

export const TicketSimilarityResultSchema = z.object({
  ticketId: z.string().min(1),
  subject: z.string().min(1),
  confidence: z.number().min(0).max(1),
  confidenceLabel: ConfidenceLabelSchema,
  snippet: z.string().min(1),
  resolution: z.string().min(1),
});
export type TicketSimilarityResult = z.infer<typeof TicketSimilarityResultSchema>;

export const SimilarTicketsRequestSchema = z.object({
  query: z.string().min(3),
});
export type SimilarTicketsRequest = z.infer<typeof SimilarTicketsRequestSchema>;

export const SimilarTicketsResponseSchema = z.object({
  tickets: z.array(TicketSimilarityResultSchema),
});
export type SimilarTicketsResponse = z.infer<typeof SimilarTicketsResponseSchema>;
