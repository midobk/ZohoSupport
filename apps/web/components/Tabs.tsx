export type TabKey = "ask" | "similar" | "live";

const tabs: { key: TabKey; label: string; description: string }[] = [
  { key: "ask", label: "Ask", description: "Generate grounded responses" },
  { key: "similar", label: "Similar Tickets", description: "Search historical resolutions" },
  { key: "live", label: "Live Assist", description: "Real-time guidance" },
];

export function Tabs({
  active,
  onChange,
}: {
  active: TabKey;
  onChange: (tab: TabKey) => void;
}) {
  return (
    <nav className="space-y-2" aria-label="Workflows">
      {tabs.map((tab) => (
        <button
          key={tab.key}
          type="button"
          className={`w-full rounded-md border px-3 py-2 text-left transition-colors ${
            active === tab.key
              ? "border-slate-900 bg-slate-900 text-white"
              : "border-slate-200 bg-white text-slate-700 hover:bg-slate-50"
          }`}
          onClick={() => onChange(tab.key)}
        >
          <p className="text-sm font-medium">{tab.label}</p>
          <p className={`text-xs ${active === tab.key ? "text-slate-200" : "text-slate-500"}`}>{tab.description}</p>
        </button>
      ))}
    </nav>
  );
}
