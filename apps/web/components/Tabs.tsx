import React from "react";

export type TabKey = "ask" | "similar" | "live";

const tabs: { key: TabKey; label: string }[] = [
  { key: "ask", label: "Ask" },
  { key: "similar", label: "Similar Tickets" },
  { key: "live", label: "Live Assist" },
];

export function Tabs({
  active,
  onChange,
}: {
  active: TabKey;
  onChange: (tab: TabKey) => void;
}) {
  return (
    <div className="mb-6 flex gap-2 border-b border-slate-200 pb-2">
      {tabs.map((tab) => (
        <button
          key={tab.key}
          type="button"
          className={`rounded-md px-4 py-2 text-sm font-medium ${
            active === tab.key ? "bg-slate-900 text-white" : "bg-white text-slate-700"
          }`}
          onClick={() => onChange(tab.key)}
        >
          {tab.label}
        </button>
      ))}
    </div>
  );
}
