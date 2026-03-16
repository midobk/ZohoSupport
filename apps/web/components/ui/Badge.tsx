import { ReactNode } from "react";

type BadgeVariant = "official" | "historical" | "neutral";

const variantClasses: Record<BadgeVariant, string> = {
  official: "border border-emerald-200 bg-emerald-50 text-emerald-700",
  historical: "border border-indigo-200 bg-indigo-50 text-indigo-700",
  neutral: "border border-slate-200 bg-slate-100 text-slate-700",
};

export function Badge({ children, variant = "neutral" }: { children: ReactNode; variant?: BadgeVariant }) {
  return (
    <span className={`inline-flex items-center rounded-full px-2.5 py-1 text-xs font-semibold ${variantClasses[variant]}`}>
      {children}
    </span>
  );
}
