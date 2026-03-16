"use client";

import { useState } from "react";
import { fetchAnswer, fetchSimilarTickets } from "@/lib/api";
import { Tabs, TabKey } from "@/components/Tabs";
import { AnswerResponse, SimilarTicketsResponse } from "@zoho/shared/src";

export default function HomePage() {
  const [activeTab, setActiveTab] = useState<TabKey>("ask");

  const [askQuery, setAskQuery] = useState("How do I reset MFA for a locked user?");
  const [askData, setAskData] = useState<AnswerResponse | null>(null);
  const [askLoading, setAskLoading] = useState(false);
  const [askError, setAskError] = useState<string | null>(null);

  const [ticketQuery, setTicketQuery] = useState("User sees invalid OTP error");
  const [ticketData, setTicketData] = useState<SimilarTicketsResponse | null>(null);
  const [ticketLoading, setTicketLoading] = useState(false);
  const [ticketError, setTicketError] = useState<string | null>(null);

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
    <section>
      <h1 className="mb-2 text-3xl font-semibold">Zoho Support Copilot</h1>
      <p className="mb-8 text-slate-600">Mocked assistant for answer generation and similar ticket lookup.</p>

      <Tabs active={activeTab} onChange={setActiveTab} />

      {activeTab === "ask" && (
        <div className="rounded-xl bg-white p-5 shadow-sm">
          <h2 className="mb-3 text-xl font-medium">Ask</h2>
          <textarea
            className="w-full rounded-md border border-slate-300 p-3"
            rows={4}
            value={askQuery}
            onChange={(e) => setAskQuery(e.target.value)}
          />
          <button className="mt-3 rounded-md bg-blue-600 px-4 py-2 text-white" onClick={handleAsk}>
            {askLoading ? "Getting answer..." : "Get answer"}
          </button>
          {askError && <p className="mt-3 text-red-600">{askError}</p>}
          {askData && (
            <div className="mt-4 space-y-3">
              <p>{askData.answer}</p>
              <ul className="list-disc pl-5 text-sm text-slate-700">
                {askData.sources.map((source) => (
                  <li key={source.id}>
                    <a className="text-blue-700 underline" href={source.url} target="_blank">
                      {source.title}
                    </a>
                    <span className="ml-2">{source.summary}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {activeTab === "similar" && (
        <div className="rounded-xl bg-white p-5 shadow-sm">
          <h2 className="mb-3 text-xl font-medium">Similar Tickets</h2>
          <label htmlFor="similar-search" className="mb-2 block text-sm font-medium text-slate-700">
            Search issue or error text
          </label>
          <input
            id="similar-search"
            className="w-full rounded-md border border-slate-300 p-3"
            placeholder="e.g. user gets OTP expired error"
            value={ticketQuery}
            onChange={(e) => setTicketQuery(e.target.value)}
          />
          <button className="mt-3 rounded-md bg-blue-600 px-4 py-2 text-white" onClick={handleTickets}>
            {ticketLoading ? "Searching..." : "Find tickets"}
          </button>
          {ticketError && <p className="mt-3 text-red-600">{ticketError}</p>}
          {ticketData && (
            <ul className="mt-4 space-y-3">
              {ticketData.tickets.map((ticket) => (
                <li key={ticket.ticketId} className="rounded-md border border-slate-200 p-3">
                  <p className="font-medium">{ticket.subject}</p>
                  <p className="text-sm text-slate-600">Similarity score: {Math.round(ticket.similarityScore * 100)}%</p>
                  <p className="mt-2 text-sm">Resolution summary: {ticket.resolutionSummary}</p>
                  <p className="mt-1 text-sm text-slate-700">Draft suggested answer: {ticket.draftSuggestedAnswer}</p>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}

      {activeTab === "live" && (
        <div className="rounded-xl bg-white p-5 shadow-sm">
          <h2 className="mb-3 text-xl font-medium">Live Assist</h2>
          <p className="text-slate-600">
            Live Assist UI placeholder. This panel will host real-time guided responses, follow-up prompts,
            and handoff suggestions.
          </p>
          <div className="mt-4 rounded-md border border-dashed border-slate-300 p-4 text-sm text-slate-500">
            Coming soon: live context panel, sentiment cues, and next best actions.
          </div>
        </div>
      )}
    </section>
  );
}
