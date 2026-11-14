import type { Scheme } from "@/lib/types";
import { GlassCard } from "@/components/fx/GlassCard";
import { Link } from "@tanstack/react-router";
import { ArrowUpRight, Calendar, Sparkles } from "lucide-react";

export function SchemeCard({ scheme }: { scheme: Scheme }) {
  const r = 18;
  const c = 2 * Math.PI * r;
  const dash = c * scheme.confidence;

  return (
    <GlassCard className="group flex h-full flex-col gap-4">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-[10px] font-medium uppercase tracking-wider text-muted-foreground">{scheme.ministry}</p>
          <h3 className="mt-1 text-base font-semibold leading-tight">{scheme.name}</h3>
        </div>
        {/* confidence ring */}
        <div className="relative h-12 w-12 shrink-0">
          <svg viewBox="0 0 44 44" className="h-12 w-12 -rotate-90">
            <circle cx="22" cy="22" r={r} stroke="oklch(1 0 0 / 8%)" strokeWidth="3" fill="none" />
            <circle
              cx="22" cy="22" r={r}
              stroke="url(#g1)"
              strokeWidth="3" fill="none" strokeLinecap="round"
              strokeDasharray={`${dash} ${c}`}
            />
            <defs>
              <linearGradient id="g1" x1="0" x2="1" y1="0" y2="1">
                <stop offset="0%" stopColor="oklch(0.85 0.16 165)" />
                <stop offset="100%" stopColor="oklch(0.75 0.17 240)" />
              </linearGradient>
            </defs>
          </svg>
          <span className="absolute inset-0 flex items-center justify-center text-[10px] font-semibold">
            {Math.round(scheme.confidence * 100)}%
          </span>
        </div>
      </div>

      <p className="line-clamp-2 text-xs text-muted-foreground">{scheme.description}</p>

      <div className="flex flex-wrap items-center gap-2 text-xs">
        <span className="inline-flex items-center gap-1 rounded-full border border-emerald/30 bg-emerald/10 px-2 py-0.5 font-medium" style={{ color: "oklch(0.88 0.14 165)", background: "oklch(0.78 0.18 165 / 12%)", borderColor: "oklch(0.78 0.18 165 / 30%)" }}>
          <Sparkles className="h-3 w-3" />
          {scheme.matchPercent}% match
        </span>
        <span className="inline-flex items-center gap-1 rounded-full bg-white/5 px-2 py-0.5 text-muted-foreground">
          <Calendar className="h-3 w-3" />
          {scheme.deadline}
        </span>
      </div>

      <div className="flex flex-wrap gap-1.5">
        {scheme.tags.map((t) => (
          <span key={t} className="rounded-md bg-white/5 px-1.5 py-0.5 text-[10px] text-muted-foreground">
            {t}
          </span>
        ))}
      </div>

      <div className="mt-auto flex items-end justify-between gap-3 pt-2">
        <div>
          <p className="text-[10px] uppercase tracking-wider text-muted-foreground">Funding</p>
          <p className="text-sm font-semibold text-gradient">{scheme.fundingAmount}</p>
        </div>
        <Link
          to="/apply/$schemeId"
          params={{ schemeId: scheme.id }}
          className="bg-gradient-primary inline-flex items-center gap-1.5 rounded-full px-3.5 py-2 text-xs font-semibold text-primary-foreground shadow-glow transition-transform hover:scale-105"
        >
          Auto Apply
          <ArrowUpRight className="h-3.5 w-3.5" />
        </Link>
      </div>
    </GlassCard>
  );
}
