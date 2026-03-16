import { ReactNode } from "react";

type CardProps = {
  children: ReactNode;
  className?: string;
};

export function Card({ children, className = "" }: CardProps) {
  return <div className={`rounded-xl border border-slate-200 bg-white shadow-sm ${className}`}>{children}</div>;
}

export function Badge({ children, tone = "neutral" }: { children: ReactNode; tone?: "neutral" | "official" | "historical" }) {
  const toneClass =
    tone === "official"
      ? "bg-blue-100 text-blue-700 border-blue-200"
      : tone === "historical"
        ? "bg-amber-100 text-amber-700 border-amber-200"
        : "bg-slate-100 text-slate-700 border-slate-200";

  return <span className={`inline-flex items-center rounded-full border px-2.5 py-1 text-xs font-medium ${toneClass}`}>{children}</span>;
}

export function Button({
  children,
  onClick,
  disabled,
  variant = "primary",
}: {
  children: ReactNode;
  onClick?: () => void;
  disabled?: boolean;
  variant?: "primary" | "secondary";
}) {
  const variantClass =
    variant === "primary"
      ? "bg-slate-900 text-white hover:bg-slate-700"
      : "bg-white text-slate-700 border border-slate-300 hover:bg-slate-50";

  return (
    <button
      type="button"
      disabled={disabled}
      onClick={onClick}
      className={`rounded-md px-4 py-2 text-sm font-medium transition ${variantClass} disabled:cursor-not-allowed disabled:opacity-60`}
    >
      {children}
    </button>
  );
}

export function LoadingSkeleton({ lines = 3 }: { lines?: number }) {
  return (
    <div className="animate-pulse space-y-2">
      {Array.from({ length: lines }).map((_, index) => (
        <div key={index} className="h-4 rounded bg-slate-200" />
      ))}
    </div>
  );
}

export function EmptyState({ title, description }: { title: string; description: string }) {
  return (
    <div className="rounded-lg border border-dashed border-slate-300 bg-slate-50 p-6 text-center">
      <p className="font-medium text-slate-800">{title}</p>
      <p className="mt-1 text-sm text-slate-500">{description}</p>
    </div>
  );
}
