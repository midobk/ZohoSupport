"use client";

import { useState } from "react";
import { fetchAnswer, fetchSimilarTickets } from "@/lib/api";
import { Tabs, TabKey } from "@/components/Tabs";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card, CardTitle } from "@/components/ui/Card";
import { EmptyState } from "@/components/ui/EmptyState";
import { Skeleton } from "@/components/ui/Skeleton";
import { AnswerResponse, SimilarTicketsResponse } from "@zoho/shared";

export default function HomePage() {
  const [activeTab, setActiveTab] = useState<TabKey>("ask");

  const [askQuery, setAskQuery] = useState("How do I reset MFA for a locked user?");
  const [askData, setAskData] = useState<AnswerResponse | null>(null);
  const [askLoading, setAskLoading] = useState(false);
  const [askError, setAskError] = useState<string | null>(null);

  const [ticketQuery, setTicketQuery] = useState("MFA reset issue");
  const [ticketData, setTicketData] = useState<SimilarTicketsResponse | null>(null);
  const [ticketLoading, setTicketLoading] = useState(false);
  const [ticketError, setTicketError] = useState<string | null>(null);

  const handleAsk = async () => {
    const normalizedQuestion = askQuery.trim();

    if (!normalizedQuestion) {
      setAskData(null);
      setAskError("Please enter a customer question before requesting an answer.");
      return;
    }

    setAskLoading(true);
    setAskError(null);

    try {
      const result = await fetchAnswer(normalizedQuestion);
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
                <Badge variant="official">Official Sources Only</Badge>
              </div>

              <label className="mt-4 block text-sm font-medium text-slate-700" htmlFor="ask-question">
                Customer question
              </label>
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
                    <p className="font-medium">Concise answer</p>
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

              {ticketData && (
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
              <CardTitle>Live Assist</CardTitle>
              <p className="mt-3 text-sm text-slate-600">
                This panel will host real-time guided responses, follow-up prompts, and handoff suggestions.
              </p>
              <div className="mt-4">
                <EmptyState
                  title="Live Assist is coming soon"
                  description="Upcoming: live context panel, sentiment cues, and next best actions."
                />
              </div>
            </Card>
          )}
        </main>

        <aside className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
          <div className="flex items-center justify-between">
            <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">Source Rail</p>
            <Badge variant={activeTab === "similar" ? "historical" : "official"}>
              {activeTab === "similar" ? "Historical" : "Official"}
            </Badge>
          </div>

          <div className="mt-3 space-y-3">
            {activeTab === "ask" && askData?.sources.length ? (
              askData.sources.map((source) => (
                <article key={source.id} className="rounded-md border border-emerald-200 bg-emerald-50/40 p-3">
                  <p className="text-sm font-medium text-slate-900">{source.title}</p>
                  <p className="mt-1 text-xs text-slate-600">{source.snippet}</p>
                  <a className="mt-2 inline-block text-xs text-emerald-700 underline" href={source.url} target="_blank" rel="noreferrer noopener">
                    {source.url}
                  </a>
                </article>
              ))
            ) : activeTab === "similar" && ticketData?.tickets.length ? (
              ticketData.tickets.map((ticket) => (
                <article key={ticket.ticketId} className="rounded-md border border-indigo-200 bg-indigo-50/40 p-3">
                  <p className="text-sm font-medium text-slate-900">{ticket.ticketId}</p>
                  <p className="mt-1 text-xs text-slate-600">{ticket.subject}</p>
                </article>
              ))
            ) : (
              <p className="text-sm text-slate-500">Sources and ticket references will appear here after running a workflow.</p>
            )}
          </div>
        </aside>
      </div>
    </div>
  );
}
