"use client";

import Link from "next/link";
import { useRef, useState } from "react";
import type { SchemeResult } from "../types";
import {
  streamExplanation,
  type ExplainMeta,
  type ExplainAlternative,
} from "../lib/api";

const ELIGIBILITY_COLOR = {
  yes: "bg-emerald-100 text-emerald-800 border-emerald-200",
  likely: "bg-amber-100 text-amber-800 border-amber-200",
  no: "bg-red-100 text-red-800 border-red-200",
};

const ELIGIBILITY_LABEL = {
  yes: "✅ Eligible",
  likely: "🟡 Likely Eligible",
  no: "❌ Not Eligible",
};

function formatAmount(amount: number): string {
  if (amount >= 10000000) return `₹${(amount / 10000000).toFixed(1)} Cr`;
  if (amount >= 100000) return `₹${(amount / 100000).toFixed(1)} L`;
  if (amount >= 1000) return `₹${(amount / 1000).toFixed(0)}K`;
  return `₹${amount}`;
}

interface SchemeCardProps {
  scheme: SchemeResult;
  language?: string;
  selected?: boolean;
  onToggleSelect?: () => void;
  compareDisabled?: boolean;
}

export function SchemeCard({ scheme, language = "en", selected = false, onToggleSelect, compareDisabled = false }: SchemeCardProps) {
  const [open, setOpen] = useState(false);
  const [explainText, setExplainText] = useState("");
  const [meta, setMeta] = useState<ExplainMeta | null>(null);
  const [loading, setLoading] = useState(false);
  const [explainError, setExplainError] = useState<string | null>(null);
  const abortRef = useRef<AbortController | null>(null);
  const didFetchRef = useRef(false);

  const runExplain = async () => {
    setLoading(true);
    setExplainText("");
    setMeta(null);
    setExplainError(null);

    const raw = typeof window !== "undefined" ? localStorage.getItem("ys_profile") : null;
    const profile = raw ? JSON.parse(raw) : {};

    abortRef.current = new AbortController();

    try {
      for await (const ev of streamExplanation(
        scheme.scheme_id,
        profile,
        language,
        abortRef.current.signal
      )) {
        if (ev.event === "meta") {
          setMeta(ev.data);
        } else if (ev.event === "token") {
          setExplainText((t) => t + ev.data.text);
        } else if (ev.event === "error") {
          setExplainError(ev.data.error);
        }
      }
    } catch (err) {
      if ((err as Error).name !== "AbortError") {
        setExplainError(err instanceof Error ? err.message : "Explanation failed");
      }
    } finally {
      setLoading(false);
    }
  };

  const togglePanel = () => {
    if (!open) {
      setOpen(true);
      if (!didFetchRef.current) {
        didFetchRef.current = true;
        runExplain();
      }
    } else {
      setOpen(false);
      abortRef.current?.abort();
    }
  };

  return (
    <div className={`bg-white rounded-xl border-2 shadow-sm hover:shadow-md transition-all ${
      selected ? "border-blue-500 ring-2 ring-blue-100" : "border-slate-200"
    }`}>
      <div className="p-5">
        {/* Header */}
        <div className="flex items-start justify-between gap-3 mb-3">
          <div className="flex items-start gap-2 flex-1 min-w-0">
            {/* Compare checkbox */}
            {onToggleSelect && (
              <button
                onClick={(e) => { e.stopPropagation(); if (!compareDisabled || selected) onToggleSelect(); }}
                title={compareDisabled ? "Max 3 schemes for comparison" : (selected ? "Remove from compare" : "Add to compare")}
                className={`mt-0.5 shrink-0 w-5 h-5 rounded border-2 flex items-center justify-center transition-colors ${
                  selected
                    ? "bg-blue-600 border-blue-600 text-white"
                    : compareDisabled
                    ? "border-slate-200 bg-slate-50 cursor-not-allowed"
                    : "border-slate-300 hover:border-blue-400"
                }`}
              >
                {selected && <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7"/></svg>}
              </button>
            )}
            <h3 className="font-semibold text-slate-900 text-base leading-snug">{scheme.title}</h3>
          </div>
          <span
            className={`shrink-0 text-xs font-medium px-2.5 py-1 rounded-full border ${
              ELIGIBILITY_COLOR[scheme.eligibility]
            }`}
          >
            {ELIGIBILITY_LABEL[scheme.eligibility]}
          </span>
        </div>

        {/* Metrics */}
        <div className="flex items-center gap-4 mb-3">
          <div>
            <p className="text-2xl font-bold text-blue-700">
              {formatAmount(scheme.funding_amount)}
            </p>
            <p className="text-xs text-slate-500">Funding</p>
          </div>
          <div>
            <p className="text-2xl font-bold text-emerald-700">{scheme.confidence}%</p>
            <p className="text-xs text-slate-500">Match</p>
          </div>
          {scheme.deadline && (
            <div>
              <p className="text-sm font-medium text-slate-700">{scheme.deadline}</p>
              <p className="text-xs text-slate-500">Deadline</p>
            </div>
          )}
        </div>

        {/* Categories */}
        {scheme.category.length > 0 && (
          <div className="flex flex-wrap gap-1.5 mb-3">
            {scheme.category.slice(0, 3).map((cat) => (
              <span
                key={cat}
                className="text-xs bg-slate-100 text-slate-600 px-2 py-0.5 rounded-full"
              >
                {cat}
              </span>
            ))}
          </div>
        )}

        <p className="text-sm text-slate-600 mb-4 line-clamp-2">{scheme.reasoning}</p>

        {/* Actions */}
        <div className="flex gap-2">
          <button
            onClick={togglePanel}
            className={`flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm font-medium transition-colors border ${
              open
                ? "bg-violet-50 border-violet-300 text-violet-700"
                : "bg-white border-slate-300 text-slate-600 hover:bg-slate-50"
            }`}
          >
            {open ? "▲" : "▼"} Why?
          </button>
          <Link
            href={`/schemes/${encodeURIComponent(scheme.scheme_id)}?lang=${language}`}
            className="flex-1 text-center py-2 px-3 rounded-lg border border-blue-600 text-blue-600 text-sm font-medium hover:bg-blue-50 transition-colors"
          >
            View Details
          </Link>
          <Link
            href={`/schemes/${encodeURIComponent(scheme.scheme_id)}?lang=${language}&apply=1`}
            className="flex-1 text-center py-2 px-3 rounded-lg bg-blue-600 text-white text-sm font-medium hover:bg-blue-700 transition-colors"
          >
            Auto-Apply
          </Link>
        </div>
      </div>

      {/* Why? Panel */}
      {open && (
        <div className="border-t border-slate-100 bg-slate-50 rounded-b-xl px-5 py-4 space-y-3">
          {/* Verdict chip */}
          {meta && (
            <div className="flex items-center gap-2">
              <span
                className={`text-xs font-semibold px-2.5 py-1 rounded-full border ${
                  ELIGIBILITY_COLOR[meta.verdict]
                }`}
              >
                {ELIGIBILITY_LABEL[meta.verdict]}
              </span>
              <span className="text-xs text-slate-400">{meta.confidence}% confidence</span>
            </div>
          )}

          {/* Streaming explanation text */}
          {explainError ? (
            <p className="text-sm text-red-600 bg-red-50 px-3 py-2 rounded-lg">
              ⚠️ {explainError}
            </p>
          ) : (
            <div className="text-sm text-slate-700 leading-relaxed whitespace-pre-wrap">
              {explainText}
              {loading && (
                <span className="inline-block w-1.5 h-4 bg-violet-500 ml-0.5 animate-pulse rounded-sm align-middle" />
              )}
              {!loading && !explainText && (
                <span className="text-slate-400 italic text-xs">Loading explanation…</span>
              )}
            </div>
          )}

          {/* Alternative schemes (RAG results) */}
          {meta && meta.alternatives.length > 0 && (
            <div className="pt-2 border-t border-slate-200">
              <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-2">
                You may qualify for
              </p>
              <div className="space-y-1.5">
                {meta.alternatives.map((alt: ExplainAlternative) => (
                  <Link
                    key={alt.scheme_id}
                    href={`/schemes/${encodeURIComponent(alt.scheme_id)}?lang=${language}`}
                    className="flex items-center justify-between px-3 py-2 rounded-lg bg-white border border-slate-200 hover:border-blue-300 hover:bg-blue-50 transition-colors group"
                  >
                    <span className="text-sm text-slate-700 group-hover:text-blue-700 font-medium">
                      {alt.title}
                    </span>
                    <span className="text-xs text-slate-400 shrink-0 ml-2">
                      {formatAmount(alt.funding_amount)} →
                    </span>
                  </Link>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
