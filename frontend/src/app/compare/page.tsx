"use client";

import { useEffect, useState, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";

const BACKEND_URL =
  process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000/v1";

interface SchemeNormalized {
  id: string;
  title: string;
  funding: string;
  funding_amount: number;
  documents_needed_count: number;
  documents_needed: string[];
  timeline: string;
  benefits: string;
  eligibility_difficulty: "Easy" | "Medium" | "Hard";
  why_it_stands_out: string;
  best_for: string;
  ministry: string | null;
  application_url: string | null;
  category: string[];
  min_age: number | null;
  max_age: number | null;
  max_income: number | null;
}

interface CompareRow {
  field: string;
  [schemeId: string]: string;
}

interface CompareResult {
  scheme_ids: string[];
  schemes: SchemeNormalized[];
  comparison: CompareRow[];
  reasoning_summary: string;
  llm_used: boolean;
}

const DIFFICULTY_COLOR = {
  Easy: "text-emerald-700 bg-emerald-50 border-emerald-200",
  Medium: "text-amber-700 bg-amber-50 border-amber-200",
  Hard: "text-red-700 bg-red-50 border-red-200",
};

const COLORS = [
  "border-blue-500 bg-blue-50",
  "border-violet-500 bg-violet-50",
  "border-emerald-500 bg-emerald-50",
];
const HEADER_COLORS = [
  "bg-blue-600",
  "bg-violet-600",
  "bg-emerald-600",
];

function CompareContent() {
  const searchParams = useSearchParams();
  const ids = searchParams.get("ids")?.split(",").filter(Boolean) ?? [];
  const lang = searchParams.get("lang") ?? "en";

  const [result, setResult] = useState<CompareResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (ids.length < 2) { setLoading(false); return; }
    fetch(`${BACKEND_URL}/schemes/compare`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ scheme_ids: ids, language: lang }),
    })
      .then((r) => r.json())
      .then((data) => { setResult(data); setLoading(false); })
      .catch((e) => { setError(e.message); setLoading(false); });
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  if (ids.length < 2) {
    return (
      <div className="max-w-lg mx-auto px-4 py-24 text-center space-y-4">
        <div className="text-5xl">⚖️</div>
        <h1 className="text-2xl font-bold text-slate-900">Select schemes to compare</h1>
        <p className="text-slate-500 text-sm">
          Go to search results, check 2–3 schemes, then click "Compare".
        </p>
        <Link href="/" className="inline-block mt-2 px-5 py-2.5 bg-blue-600 text-white rounded-xl text-sm font-semibold hover:bg-blue-700 transition-colors">
          ← Back to Search
        </Link>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="max-w-5xl mx-auto px-4 py-12 space-y-6">
        <div className="h-8 bg-slate-100 rounded-lg animate-pulse w-64" />
        <div className="grid gap-4" style={{ gridTemplateColumns: `repeat(${ids.length + 1}, 1fr)` }}>
          {Array.from({ length: (ids.length + 1) * 7 }).map((_, i) => (
            <div key={i} className="h-12 bg-slate-100 rounded-lg animate-pulse" />
          ))}
        </div>
        <p className="text-center text-slate-400 text-sm animate-pulse">
          🤖 AI is analyzing schemes…
        </p>
      </div>
    );
  }

  if (error || !result) {
    return (
      <div className="max-w-lg mx-auto px-4 py-16 text-center space-y-3">
        <p className="text-red-600 bg-red-50 px-4 py-3 rounded-xl text-sm">
          ⚠️ {error || "Comparison failed"}
        </p>
        <Link href="/" className="text-blue-600 hover:underline text-sm">← Back to search</Link>
      </div>
    );
  }

  const { schemes, comparison, reasoning_summary } = result;

  return (
    <div className="max-w-6xl mx-auto px-4 py-8 space-y-8">
      {/* Header */}
      <div>
        <Link href="/" className="text-sm text-blue-600 hover:underline">← Back to search</Link>
        <h1 className="text-2xl font-bold text-slate-900 mt-2">Scheme Comparison</h1>
        <p className="text-slate-500 text-sm mt-1">
          Comparing {schemes.length} schemes side-by-side
          {result.llm_used && (
            <span className="ml-2 text-xs bg-violet-100 text-violet-700 px-2 py-0.5 rounded-full">
              🤖 AI-powered
            </span>
          )}
        </p>
      </div>

      {/* AI Summary */}
      {reasoning_summary && (
        <div className="bg-gradient-to-r from-violet-50 to-blue-50 border border-violet-200 rounded-2xl p-5">
          <div className="flex items-start gap-3">
            <span className="text-2xl shrink-0">🤖</span>
            <div>
              <p className="text-sm font-semibold text-violet-800 mb-1">AI Comparison Summary</p>
              <p className="text-sm text-slate-700 leading-relaxed">{reasoning_summary}</p>
            </div>
          </div>
        </div>
      )}

      {/* Scheme header cards */}
      <div className={`grid gap-4`} style={{ gridTemplateColumns: `repeat(${schemes.length}, 1fr)` }}>
        {schemes.map((scheme, idx) => (
          <div key={scheme.id} className={`rounded-2xl border-2 overflow-hidden ${COLORS[idx]}`}>
            <div className={`px-4 py-3 text-white ${HEADER_COLORS[idx]}`}>
              <p className="font-bold text-sm leading-snug">{scheme.title}</p>
              {scheme.ministry && (
                <p className="text-xs text-white/80 mt-0.5">{scheme.ministry}</p>
              )}
            </div>
            <div className="px-4 py-3 space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-xs text-slate-500">Funding</span>
                <span className="font-bold text-slate-900 text-sm">{scheme.funding}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-xs text-slate-500">Difficulty</span>
                <span className={`text-xs font-semibold px-2 py-0.5 rounded-full border ${DIFFICULTY_COLOR[scheme.eligibility_difficulty] || DIFFICULTY_COLOR.Medium}`}>
                  {scheme.eligibility_difficulty}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-xs text-slate-500">Best for</span>
                <span className="text-xs text-slate-700 font-medium text-right max-w-[60%]">{scheme.best_for}</span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Comparison Table */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="bg-slate-50 border-b border-slate-200">
              <th className="text-left px-5 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wide w-40">
                Criteria
              </th>
              {schemes.map((scheme, idx) => (
                <th key={scheme.id} className="text-left px-4 py-3 text-xs font-semibold text-slate-700">
                  <span className={`inline-block w-2.5 h-2.5 rounded-full mr-1.5 ${HEADER_COLORS[idx]}`} />
                  {scheme.title.split(" ").slice(0, 4).join(" ")}…
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {comparison.map((row, i) => (
              <tr key={row.field} className={i % 2 === 0 ? "bg-white" : "bg-slate-50/50"}>
                <td className="px-5 py-3.5 font-medium text-slate-600 text-xs uppercase tracking-wide whitespace-nowrap">
                  {row.field}
                </td>
                {schemes.map((scheme) => (
                  <td key={scheme.id} className="px-4 py-3.5 text-slate-700">
                    {row[scheme.id] ?? "—"}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Why it stands out */}
      <div>
        <h2 className="text-sm font-semibold text-slate-500 uppercase tracking-wide mb-3">
          Why each scheme stands out
        </h2>
        <div className={`grid gap-4`} style={{ gridTemplateColumns: `repeat(${schemes.length}, 1fr)` }}>
          {schemes.map((scheme, idx) => (
            <div key={scheme.id} className="bg-white rounded-xl border border-slate-200 p-4 shadow-sm">
              <div className="flex items-center gap-2 mb-2">
                <span className={`w-3 h-3 rounded-full ${HEADER_COLORS[idx]}`} />
                <p className="text-xs font-semibold text-slate-700">{scheme.title.split(" ").slice(0, 5).join(" ")}</p>
              </div>
              <p className="text-sm text-slate-600 leading-relaxed">{scheme.why_it_stands_out}</p>
              {scheme.application_url && (
                <a
                  href={scheme.application_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-block mt-3 text-xs text-blue-600 hover:underline"
                >
                  Apply on official portal →
                </a>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default function ComparePage() {
  return (
    <Suspense fallback={
      <div className="flex items-center justify-center min-h-[60vh]">
        <p className="text-slate-500">Loading comparison…</p>
      </div>
    }>
      <CompareContent />
    </Suspense>
  );
}
