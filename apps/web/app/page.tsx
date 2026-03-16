"use client";

import { useMemo, useState } from "react";
import { fetchAnswer, fetchSimilarTickets } from "@/lib/api";
import { AnswerResponse, SimilarTicketsResponse } from "@zoho/shared/src";
import { Badge, Button, Card, EmptyState, LoadingSkeleton } from "@/components/ui";

type ViewKey = "ask" | "similar" | "live";

const navItems: { key: ViewKey; label: string; helper: string }[] = [
  { key: "ask", label: "Ask Copilot", helper: "Generate grounded responses" },
  { key: "similar", label: "Historical Tickets", helper: "Find prior resolutions" },
  { key: "live", label: "Live Assist", helper: "Assist in real-time" },
];

export default function HomePage() {
  const [activeView, setActiveView] = useState<ViewKey>("ask");

  const [askQuery, setAskQuery] = useState("How do I reset MFA for a locked user?");
  const [askData, setAskData] = useState<AnswerResponse | null>(null);
  const [askLoading, setAskLoading] = useState(false);
  const [askError, setAskError] = useState<string | null>(null);

  const [ticketQuery, setTicketQuery] = useState("MFA reset issue");
  const [ticketData, setTicketData] = useState<SimilarTicketsResponse | null>(null);
  const [ticketLoading, setTicketLoading] = useState(false);
  const [ticketError, setTicketError] = useState<string | null>(null);

  const officialSources = useMemo(() => askData?.sources ?? [], [askData]);

  const handleAsk = async () => {
    setAskLoading(true);
    setAskError(null);
    try {
      const result = await fetchAnswer(askQuery);
      setAskData(result);
    } catch (err) {
      setAskError(err instanceof Error ? err.message : "Unexpected error");
    } finally {
      setAskLoading(false);
    }
  };

  const handleTickets = async () => {
    setTicketLoading(true);
    setTicketError(null);
    try {
      const result = await fetchSimilarTickets(ticketQuery);
      setTicketData(result);
    } catch (err) {
      setTicketError(err instanceof Error ? err.message : "Unexpected error");
    } finally {
      setTicketLoading(false);
    }
  };

  return (
    <div className="space-y-5">
      <header className="rounded-xl border border-slate-200 bg-white px-6 py-4 shadow-sm">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-xs uppercase tracking-wide text-slate-500">Support Workspace</p>
            <h1 className="text-2xl font-semibold text-slate-900">Zoho Support Copilot</h1>
          </div>
          <Badge tone="official">Official sources required</Badge>
        </div>
      </header>

      <div className="grid gap-5 lg:grid-cols-[220px_minmax(0,1fr)_320px]">
        <aside className="space-y-3">
          {navItems.map((item) => (
            <button
              key={item.key}
              type="button"
              onClick={() => setActiveView(item.key)}
              className={`w-full rounded-xl border p-3 text-left transition ${
                item.key === activeView
                  ? "border-slate-900 bg-slate-900 text-white"
                  : "border-slate-200 bg-white text-slate-700 hover:border-slate-300"
              }`}
            >
              <p className="text-sm font-medium">{item.label}</p>
              <p className={`mt-1 text-xs ${item.key === activeView ? "text-slate-200" : "text-slate-500"}`}>{item.helper}</p>
            </button>
          ))}
        </aside>

        <main className="space-y-4">
          {activeView === "ask" && (
            <Card className="p-5">
              <div className="mb-4 flex items-center justify-between">
                <h2 className="text-lg font-semibold">Compose Answer</h2>
                <Badge tone="official">Grounded Output</Badge>
              </div>
              <textarea
                className="w-full rounded-md border border-slate-300 p-3 text-sm"
                rows={5}
                value={askQuery}
                onChange={(e) => setAskQuery(e.target.value)}
              />
              <div className="mt-3">
                <Button onClick={handleAsk} disabled={askLoading}>
                  {askLoading ? "Generating answer..." : "Generate answer"}
                </Button>
              </div>
              {askError && <p className="mt-3 text-sm text-red-600">{askError}</p>}
              <div className="mt-4">
                {askLoading ? (
                  <LoadingSkeleton lines={5} />
                ) : askData ? (
                  <div className="rounded-lg bg-slate-50 p-4 text-sm text-slate-700">{askData.answer}</div>
                ) : (
                  <EmptyState
                    title="No generated answer yet"
                    description="Run an Ask Copilot query to generate a response backed by official sources."
                  />
                )}
              </div>
            </Card>
          )}

          {activeView === "similar" && (
            <Card className="p-5">
              <div className="mb-4 flex items-center justify-between">
                <h2 className="text-lg font-semibold">Historical Ticket Matches</h2>
                <Badge tone="historical">Historical Tickets</Badge>
              </div>
              <input
                className="w-full rounded-md border border-slate-300 p-3 text-sm"
                value={ticketQuery}
                onChange={(e) => setTicketQuery(e.target.value)}
              />
              <div className="mt-3">
                <Button onClick={handleTickets} disabled={ticketLoading}>
                  {ticketLoading ? "Searching tickets..." : "Search tickets"}
                </Button>
              </div>
              {ticketError && <p className="mt-3 text-sm text-red-600">{ticketError}</p>}

              <div className="mt-4 space-y-3">
                {ticketLoading && <LoadingSkeleton lines={6} />}
                {!ticketLoading && !ticketData?.tickets.length && (
                  <EmptyState
                    title="No ticket matches"
                    description="Search for a customer problem to see similar historical resolutions."
                  />
                )}
                {ticketData?.tickets.map((ticket) => (
                  <div key={ticket.ticketId} className="rounded-lg border border-amber-200 bg-amber-50 p-4 text-sm">
                    <div className="mb-2 flex items-center justify-between">
                      <p className="font-medium text-slate-900">{ticket.subject}</p>
                      <Badge tone="historical">{Math.round(ticket.confidence * 100)}% match</Badge>
                    </div>
                    <p className="text-slate-700">{ticket.snippet}</p>
                    <p className="mt-2 text-slate-600">Resolution: {ticket.resolution}</p>
                  </div>
                ))}
              </div>
            </Card>
          )}

          {activeView === "live" && (
            <Card className="p-5">
              <h2 className="text-lg font-semibold">Live Assist</h2>
              <p className="mt-2 text-sm text-slate-600">Live support co-pilot actions will appear here.</p>
              <div className="mt-4">
                <EmptyState
                  title="Live session not started"
                  description="Start a live support conversation to unlock next-best-action guidance."
                />
              </div>
            </Card>
          )}
        </main>

        <aside className="space-y-4">
          <Card className="p-4">
            <div className="mb-3 flex items-center justify-between">
              <h3 className="font-semibold text-slate-900">Official Sources</h3>
              <Badge tone="official">Verified</Badge>
            </div>
            <div className="space-y-3">
              {askLoading && <LoadingSkeleton lines={4} />}
              {!askLoading && officialSources.length === 0 && (
                <EmptyState
                  title="No official sources yet"
                  description="Generate an answer to review Zoho official citations and summaries."
                />
              )}
              {!askLoading &&
                officialSources.map((source) => (
                  <article key={source.id} className="rounded-lg border border-blue-200 bg-blue-50 p-3 text-sm">
                    <p className="font-medium text-slate-900">{source.title}</p>
                    <p className="mt-1 text-slate-700">{source.summary}</p>
                    <a className="mt-2 inline-block text-xs font-medium text-blue-700 underline" href={source.url} target="_blank">
                      Open source
                    </a>
                  </article>
                ))}
            </div>
          </Card>

          <Card className="p-4">
            <h3 className="mb-2 font-semibold text-slate-900">Workspace Status</h3>
            <p className="text-sm text-slate-600">Desktop-optimized layout with independent rails for navigation and source review.</p>
          </Card>
        </aside>
      </div>
    </div>
  );
}
