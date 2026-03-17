"use client";

import { useMemo, useState } from "react";
import { fetchAnswer, fetchSimilarTickets } from "@/lib/api";
import { Tabs, TabKey } from "@/components/Tabs";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card, CardTitle } from "@/components/ui/Card";
import { EmptyState } from "@/components/ui/EmptyState";
import { Skeleton } from "@/components/ui/Skeleton";
import { AnswerRequestMode, AnswerResponse, SimilarTicketsResponse } from "@zoho/shared";

const GEMINI_MODEL_OPTIONS = [
  {
    id: "gemini-2.5-flash-lite",
    label: "Gemini 2.5 Flash-Lite",
    requestsPerDayLabel: "1,000/day free tier",
    note: "Highest published daily limit in the current Gemini free-tier table.",
  },
  {
    id: "gemini-2.5-flash",
    label: "Gemini 2.5 Flash",
    requestsPerDayLabel: "250/day free tier",
    note: "Balanced speed and quality.",
  },
  {
    id: "gemini-2.5-pro",
    label: "Gemini 2.5 Pro",
    requestsPerDayLabel: "100/day free tier",
    note: "Best reasoning, lowest published daily cap in this list.",
  },
  {
    id: "gemini-3.1-flash-lite-preview",
    label: "Gemini 3.1 Flash-Lite Preview",
    requestsPerDayLabel: "RPD not published",
    note: "Preview model. Google does not currently publish a standard free-tier daily limit for it in the main quota table.",
  },
] as const;

export default function HomePage() {
  const [activeTab, setActiveTab] = useState<TabKey>("ask");

  const [askQuery, setAskQuery] = useState("How do I reset MFA for a locked user?");
  const [askMode, setAskMode] = useState<AnswerRequestMode>("search");
  const [askModel, setAskModel] = useState<string>("gemini-2.5-flash-lite");
  const [askData, setAskData] = useState<AnswerResponse | null>(null);
  const [askLoading, setAskLoading] = useState(false);
  const [askError, setAskError] = useState<string | null>(null);
  const [showAskGenerationInfo, setShowAskGenerationInfo] = useState(false);

  const [ticketQuery, setTicketQuery] = useState("MFA reset issue");
  const [ticketData, setTicketData] = useState<SimilarTicketsResponse | null>(null);
  const [ticketLoading, setTicketLoading] = useState(false);
  const [ticketError, setTicketError] = useState<string | null>(null);

  const sourceRailContent = useMemo(() => {
    if (activeTab === "ask") {
      return askData?.sources ?? [];
    }

    if (activeTab === "similar") {
      return (ticketData?.tickets ?? []).map((ticket) => ({
        id: ticket.ticketId,
        title: ticket.subject,
        snippet: ticket.snippet,
        url: `internal://ticket/${ticket.ticketId}`,
        sourceType: "HistoricalTicket" as const,
        trustLabel: "Unverified" as const,
      }));
    }

    return [];
  }, [activeTab, askData?.sources, ticketData?.tickets]);

  const askHasCommunitySources = (askData?.sources ?? []).some((source) => source.sourceType === "CommunityPost");

  const sourceRailBadge = activeTab === "similar"
    ? { label: "Historical", variant: "historical" as const }
    : askHasCommunitySources
      ? { label: "Official + Community", variant: "community" as const }
      : { label: "Official", variant: "official" as const };

  const sourceRailStyles: Record<
    AnswerResponse["sources"][number]["sourceType"],
    { article: string; badge: "official" | "community" | "historical"; label: string; link: string }
  > = {
    OfficialKB: {
      article: "border border-emerald-200 bg-emerald-50/40",
      badge: "official",
      label: "Official KB",
      link: "text-emerald-700",
    },
    CommunityPost: {
      article: "border border-amber-200 bg-amber-50/40",
      badge: "community",
      label: "Community",
      link: "text-amber-700",
    },
    HistoricalTicket: {
      article: "border border-indigo-200 bg-indigo-50/40",
      badge: "historical",
      label: "Historical Ticket",
      link: "text-indigo-700",
    },
  };

  const selectedAskModel = GEMINI_MODEL_OPTIONS.find((option) => option.id === askModel) ?? GEMINI_MODEL_OPTIONS[0];

  const handleAskModeChange = (mode: AnswerRequestMode) => {
    setAskMode(mode);
    setAskData(null);
    setAskError(null);
    setShowAskGenerationInfo(false);
  };

  const handleAskModelChange = (model: string) => {
    setAskModel(model);
    setAskData(null);
    setAskError(null);
    setShowAskGenerationInfo(false);
  };

  const handleAsk = async () => {
    const normalizedQuestion = askQuery.trim();

    if (!normalizedQuestion) {
      setAskData(null);
      setAskError("Please enter a customer question before requesting an answer.");
      return;
    }

    setAskLoading(true);
    setAskError(null);
    setShowAskGenerationInfo(false);

    try {
      const result = await fetchAnswer(normalizedQuestion, askMode, askMode === "ai" ? askModel : undefined);
      setAskData(result);
    } catch (err) {
      setAskData(null);
      setAskError(err instanceof Error ? err.message : "Unexpected error");
    } finally {
      setAskLoading(false);
    }
  };

  const handleTickets = async () => {
    const normalizedQuery = ticketQuery.trim();

    if (!normalizedQuery) {
      setTicketData(null);
      setTicketError("Please enter a search query before finding similar tickets.");
      return;
    }

    setTicketLoading(true);
    setTicketError(null);
    try {
      const result = await fetchSimilarTickets(normalizedQuery);
      setTicketData(result);
    } catch (err) {
      setTicketData(null);
      setTicketError(err instanceof Error ? err.message : "Unexpected error");
    } finally {
      setTicketLoading(false);
    }
  };

  return (
    <div className="space-y-5">
      <header className="rounded-xl border border-slate-200 bg-white px-6 py-4 shadow-sm">
        <p className="text-xs font-semibold uppercase tracking-wide text-blue-600">Zoho Support</p>
        <h1 className="mt-1 text-2xl font-semibold">Support Copilot Workspace</h1>
        <p className="mt-1 text-sm text-slate-600">Provide grounded answers with official documentation and historical case context.</p>
      </header>

      <div className="grid gap-4 lg:grid-cols-[220px_minmax(0,1fr)_320px]">
        <aside className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
          <p className="mb-3 text-xs font-semibold uppercase tracking-wide text-slate-500">Workflows</p>
          <Tabs active={activeTab} onChange={setActiveTab} />
        </aside>

        <main className="space-y-4">
          {activeTab === "ask" && (
            <Card>
              <div className="flex items-center justify-between">
                <CardTitle>Answer Assistant</CardTitle>
                <Badge variant={askHasCommunitySources ? "community" : "official"}>
                  {askHasCommunitySources ? "Official KB + Community" : "Official KB"}
                </Badge>
              </div>

              <label className="mt-4 block text-sm font-medium text-slate-700" htmlFor="ask-question">
                Customer question
              </label>
              <div className="mt-4">
                <p className="text-sm font-medium text-slate-700">Answer mode</p>
                <div className="mt-2 inline-flex rounded-full border border-slate-200 bg-slate-100 p-1">
                  <button
                    type="button"
                    className={`rounded-full px-3 py-1.5 text-sm font-medium transition ${
                      askMode === "search"
                        ? "bg-white text-slate-900 shadow-sm"
                        : "text-slate-600 hover:text-slate-900"
                    }`}
                    aria-pressed={askMode === "search"}
                    onClick={() => handleAskModeChange("search")}
                  >
                    Normal search
                  </button>
                  <button
                    type="button"
                    className={`rounded-full px-3 py-1.5 text-sm font-medium transition ${
                      askMode === "ai"
                        ? "bg-white text-slate-900 shadow-sm"
                        : "text-slate-600 hover:text-slate-900"
                    }`}
                    aria-pressed={askMode === "ai"}
                    onClick={() => handleAskModeChange("ai")}
                  >
                    AI-assisted
                  </button>
                </div>
                <p className="mt-2 text-xs text-slate-500">
                  {askMode === "search"
                    ? "Normal search uses Zoho search only. No AI is used for retrieval or wording."
                    : "AI-assisted uses the same Zoho search results, then an AI model drafts the answer text."}
                </p>
                {askMode === "ai" && (
                  <div className="mt-3">
                    <label className="block text-sm font-medium text-slate-700" htmlFor="ask-model">
                      Gemini model
                    </label>
                    <select
                      id="ask-model"
                      className="mt-2 w-full rounded-md border border-slate-300 bg-white p-3 text-sm"
                      value={askModel}
                      onChange={(e) => handleAskModelChange(e.target.value)}
                    >
                      {GEMINI_MODEL_OPTIONS.map((option) => (
                        <option key={option.id} value={option.id}>
                          {option.label} ({option.requestsPerDayLabel})
                        </option>
                      ))}
                    </select>
                    <p className="mt-2 text-xs text-slate-500">
                      {selectedAskModel.requestsPerDayLabel}. {selectedAskModel.note}
                    </p>
                  </div>
                )}
              </div>
              <textarea
                id="ask-question"
                className="mt-2 w-full rounded-md border border-slate-300 p-3"
                rows={4}
                value={askQuery}
                placeholder="Paste a customer's question or issue details"
                onChange={(e) => setAskQuery(e.target.value)}
              />
              <Button className="mt-3" onClick={handleAsk} disabled={askLoading}>
                {askLoading ? "Getting answer..." : "Get answer"}
              </Button>
              {askError && <p className="mt-3 text-sm text-red-600">{askError}</p>}

              {!askLoading && !askError && !askData && (
                <div className="mt-4">
                  <EmptyState
                    title="No answer generated yet"
                    description="Ask a question to generate a Zoho-grounded response for your customer."
                  />
                </div>
              )}

              {askLoading && (
                <div className="mt-4 space-y-2">
                  <Skeleton className="h-4 w-1/3" />
                  <Skeleton className="h-4 w-full" />
                  <Skeleton className="h-4 w-5/6" />
                </div>
              )}

              {askData && (
                <div className="mt-4 space-y-3">
                  <div className="rounded-lg border border-slate-200 bg-slate-50 p-3">
                    <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
                      <div className="flex items-center gap-2">
                        <p className="font-medium">Concise answer</p>
                        <Badge variant={askData.generation.mode === "AI" ? "official" : "neutral"}>
                          {askData.generation.label}
                        </Badge>
                      </div>
                    </div>
                    <p className="mt-1 text-sm">{askData.answer}</p>
                    <p className="mt-2 text-sm text-slate-600">
                      Confidence: <span className="font-medium">{askData.confidenceLabel}</span>
                    </p>
                  </div>

                  <div className="rounded-lg border border-slate-200 p-3">
                    <p className="font-medium">Suggested customer reply</p>
                    <p className="mt-1 text-sm text-slate-700">{askData.suggestedReply}</p>
                  </div>
                </div>
              )}
            </Card>
          )}

          {activeTab === "similar" && (
            <Card>
              <div className="flex items-center justify-between">
                <CardTitle>Historical Ticket Lookup</CardTitle>
                <Badge variant="historical">Historical Tickets</Badge>
              </div>

              <label className="mt-4 block text-sm font-medium text-slate-700" htmlFor="similar-issue">
                Issue or error text
              </label>
              <input
                id="similar-issue"
                className="mt-2 w-full rounded-md border border-slate-300 p-3"
                value={ticketQuery}
                placeholder="e.g. User is locked out after replacing their phone"
                onChange={(e) => setTicketQuery(e.target.value)}
              />
              <Button className="mt-3" onClick={handleTickets} disabled={ticketLoading}>
                {ticketLoading ? "Searching..." : "Find tickets"}
              </Button>
              {ticketError && <p className="mt-3 text-sm text-red-600">{ticketError}</p>}

              {!ticketLoading && !ticketError && !ticketData && (
                <div className="mt-4">
                  <EmptyState
                    title="No matches found yet"
                    description="Search by issue keywords to surface similar resolved tickets."
                  />
                </div>
              )}

              {ticketLoading && (
                <div className="mt-4 space-y-3">
                  {[1, 2].map((item) => (
                    <div key={item} className="space-y-2 rounded-md border border-slate-200 p-3">
                      <Skeleton className="h-4 w-2/3" />
                      <Skeleton className="h-4 w-full" />
                      <Skeleton className="h-4 w-4/5" />
                    </div>
                  ))}
                </div>
              )}

              {ticketData && ticketData.tickets.length === 0 && (
                <div className="mt-4">
                  <EmptyState
                    title="No similar tickets found"
                    description="Try broader keywords like MFA, OTP, login, or lockout to find relevant history."
                  />
                </div>
              )}

              {ticketData && ticketData.tickets.length > 0 && (
                <ul className="mt-4 space-y-3">
                  {ticketData.tickets.map((ticket) => (
                    <li key={ticket.ticketId} className="rounded-md border border-slate-200 p-3">
                      <div className="flex items-center justify-between gap-2">
                        <p className="font-medium">{ticket.subject}</p>
                        <Badge variant="historical">{Math.round(ticket.similarityScore * 100)}% match</Badge>
                      </div>
                      <p className="mt-1 text-sm text-slate-600">{ticket.snippet}</p>
                      <p className="mt-2 text-sm">Resolution summary: {ticket.resolutionSummary}</p>
                      <p className="mt-1 text-sm">Draft suggested answer: {ticket.draftSuggestedAnswer}</p>
                    </li>
                  ))}
                </ul>
              )}
            </Card>
          )}

          {activeTab === "live" && (
            <Card>
              <div className="flex items-center justify-between">
                <CardTitle>Live Assist</CardTitle>
                <Badge variant="neutral">Safe Placeholder</Badge>
              </div>
              <p className="mt-3 text-sm text-slate-600">
                Live Assist is intentionally disabled in this MVP to avoid unreliable real-time guidance.
              </p>
              <div className="mt-4 rounded-md border border-amber-200 bg-amber-50 p-3 text-sm text-amber-800">
                Agents should rely on Ask and Similar Tickets workflows for customer-facing responses during this demo.
              </div>
              <div className="mt-4">
                <EmptyState
                  title="Live Assist is coming soon"
                  description="Upcoming: real-time context panel, sentiment cues, and next best actions after reliability hardening."
                />
              </div>
            </Card>
          )}
        </main>

        <aside className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">Source Rail</p>
              {activeTab === "ask" && askData && (
                <button
                  type="button"
                  className="inline-flex h-5 w-5 items-center justify-center rounded-full border border-slate-300 bg-white text-[11px] font-semibold text-slate-600 transition hover:border-slate-400 hover:text-slate-900"
                  aria-label="How these results were built"
                  aria-expanded={showAskGenerationInfo}
                  title={askData.generation.description}
                  onClick={() => setShowAskGenerationInfo((open) => !open)}
                >
                  i
                </button>
              )}
            </div>
            <Badge variant={sourceRailBadge.variant}>{sourceRailBadge.label}</Badge>
          </div>

          <div className="mt-3 space-y-3">
            {activeTab === "ask" && askData && showAskGenerationInfo && (
              <div className="rounded-md border border-slate-200 bg-slate-50 px-3 py-2 text-xs leading-5 text-slate-600">
                {askData.generation.description}
              </div>
            )}
            {sourceRailContent.length > 0 ? (
              sourceRailContent.map((source) => {
                const styles = sourceRailStyles[source.sourceType];

                return (
                  <article
                    key={source.id}
                    className={`rounded-md p-3 ${styles.article}`}
                  >
                    <div className="flex items-center justify-between gap-2">
                      <p className="text-sm font-medium text-slate-900">{source.title}</p>
                      <Badge variant={styles.badge}>{source.trustLabel}</Badge>
                    </div>
                    <p className="mt-1 text-[11px] font-semibold uppercase tracking-wide text-slate-500">{styles.label}</p>
                    <p className="mt-1 text-xs text-slate-600">{source.snippet}</p>
                    {source.sourceType !== "HistoricalTicket" ? (
                      <a className={`mt-2 inline-block text-xs underline ${styles.link}`} href={source.url} target="_blank" rel="noreferrer noopener">
                        {source.url}
                      </a>
                    ) : (
                      <p className="mt-2 text-xs text-indigo-700">Historical ticket source: {source.id}</p>
                    )}
                  </article>
                );
              })
            ) : (
              <p className="text-sm text-slate-500">Sources and ticket references will appear here after running a workflow.</p>
            )}
          </div>
        </aside>
      </div>
    </div>
  );
}
