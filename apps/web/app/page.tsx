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
    <section>
      <h1 className="mb-2 text-3xl font-semibold">Zoho Support Copilot</h1>
      <p className="mb-8 text-slate-600">Mocked assistant for answer generation and similar ticket lookup.</p>

      <Tabs active={activeTab} onChange={setActiveTab} />

      {activeTab === "ask" && (
        <div className="rounded-xl bg-white p-5 shadow-sm">
          <h2 className="mb-3 text-xl font-medium">Ask</h2>
          <label className="mb-2 block text-sm font-medium text-slate-700" htmlFor="ask-question">
            Customer question
          </label>
          <textarea
            id="ask-question"
            className="w-full rounded-md border border-slate-300 p-3"
            rows={4}
            value={askQuery}
            placeholder="Paste a customer's question or issue details"
            onChange={(e) => setAskQuery(e.target.value)}
          />
          <button className="mt-3 rounded-md bg-blue-600 px-4 py-2 text-white" onClick={handleAsk} disabled={askLoading}>
            {askLoading ? "Getting answer..." : "Get answer"}
          </button>
          {askError && <p className="mt-3 text-red-600">{askError}</p>}

          {!askLoading && !askError && !askData && (
            <p className="mt-3 text-sm text-slate-600">Ask a customer question to generate a Zoho-grounded response.</p>
          )}

          {askLoading && <p className="mt-3 text-sm text-slate-600">Reviewing official Zoho guidance...</p>}

          {askData && (
            <div className="mt-4 space-y-4">
              <div className="rounded-md border border-slate-200 bg-slate-50 p-3">
                <h3 className="font-medium">Concise answer</h3>
                <p className="mt-1">{askData.answer}</p>
                <p className="mt-2 text-sm text-slate-600">
                  Confidence: <span className="font-medium">{askData.confidenceLabel}</span>
                </p>
              </div>

              <div>
                <h3 className="font-medium">Official sources</h3>
                <ul className="mt-2 space-y-3">
                  {askData.sources.map((source) => (
                    <li key={source.id} className="rounded-md border border-slate-200 p-3">
                      <p className="font-medium">{source.title}</p>
                      <p className="mt-1 text-sm text-slate-600">{source.snippet}</p>
                      <a
                        className="mt-2 inline-block text-sm text-blue-700 underline"
                        href={source.url}
                        target="_blank"
                        rel="noreferrer noopener"
                      >
                        {source.url}
                      </a>
                    </li>
                  ))}
                </ul>
              </div>

              <div className="rounded-md border border-slate-200 p-3">
                <h3 className="font-medium">Suggested customer reply</h3>
                <p className="mt-1 text-sm text-slate-700">{askData.suggestedReply}</p>
              </div>
            </div>
          )}
        </div>
      )}

      {activeTab === "similar" && (
        <div className="rounded-xl bg-white p-5 shadow-sm">
          <h2 className="mb-3 text-xl font-medium">Similar Tickets</h2>
          <input
            className="w-full rounded-md border border-slate-300 p-3"
            value={ticketQuery}
            onChange={(e) => setTicketQuery(e.target.value)}
          />
          <button
            className="mt-3 rounded-md bg-blue-600 px-4 py-2 text-white"
            onClick={handleTickets}
            disabled={ticketLoading}
          >
            {ticketLoading ? "Searching..." : "Find tickets"}
          </button>
          {ticketError && <p className="mt-3 text-red-600">{ticketError}</p>}

          {!ticketLoading && !ticketError && !ticketData && (
            <p className="mt-3 text-sm text-slate-600">Search by issue keywords to find similar resolved tickets.</p>
          )}

          {ticketLoading && <p className="mt-3 text-sm text-slate-600">Looking up similar historical tickets...</p>}

          {ticketData && (
            <ul className="mt-4 space-y-3">
              {ticketData.tickets.map((ticket) => (
                <li key={ticket.ticketId} className="rounded-md border border-slate-200 p-3">
                  <p className="font-medium">{ticket.subject}</p>
                  <p className="text-sm text-slate-600">{ticket.snippet}</p>
                  <p className="mt-1 text-sm">Resolution: {ticket.resolution}</p>
                  <p className="text-xs text-slate-500">Confidence: {Math.round(ticket.confidence * 100)}%</p>
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
