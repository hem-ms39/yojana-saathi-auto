"use client";

import { useCallback, useEffect, useRef, useState, Suspense } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { AgentPanel } from "../../components/agent-panel";
import { SchemeCard } from "../../components/scheme-card";
import { streamChat } from "../../lib/api";
import type { AgentStep, SchemeResult } from "../../types";

const MAX_COMPARE = 3;

function ResultsContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const query = searchParams.get("q") ?? "";
  const lang = (searchParams.get("lang") ?? "en") as "en" | "hi" | "kn";

  const [steps, setSteps] = useState<AgentStep[]>([]);
  const [schemes, setSchemes] = useState<SchemeResult[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [totalEligible, setTotalEligible] = useState<number | undefined>();
  const [elapsedMs, setElapsedMs] = useState<number | undefined>();
  const [selected, setSelected] = useState<string[]>([]);
  const startTimeRef = useRef<number>(0);
  const didRun = useRef(false);

  const runStream = useCallback(async () => {
    if (!query || didRun.current) return;
    didRun.current = true;
    setIsStreaming(true);
    setSteps([]);
    setSchemes([]);
    setError(null);
    startTimeRef.current = Date.now();

    try {
      for await (const ev of streamChat(query, lang)) {
        if (ev.event === "agent_step") {
          const step = ev.data as AgentStep;
          setSteps((prev) => [...prev, step]);
          if (step.agent === "profile" && step.status === "complete" && step.data) {
            localStorage.setItem("ys_profile", JSON.stringify(step.data));
          }
        } else if (ev.event === "scheme_result") {
          setSchemes((prev) => [...prev, ev.data as SchemeResult]);
        } else if (ev.event === "done") {
          const doneData = ev.data as { total_eligible: number };
          setTotalEligible(doneData.total_eligible);
          setElapsedMs(Date.now() - startTimeRef.current);
          setIsStreaming(false);
        } else if (ev.event === "error") {
          const errData = ev.data as { error: string };
          setError(errData.error);
          setIsStreaming(false);
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
      setIsStreaming(false);
    }
  }, [query, lang]);

  useEffect(() => { runStream(); }, [runStream]);

  const toggleSelect = (schemeId: string) => {
    setSelected((prev) => {
      if (prev.includes(schemeId)) return prev.filter((id) => id !== schemeId);
      if (prev.length >= MAX_COMPARE) return prev; // max 3
      return [...prev, schemeId];
    });
  };

  const handleCompare = () => {
    const ids = selected.join(",");
    router.push(`/compare?ids=${encodeURIComponent(ids)}&lang=${lang}`);
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 py-8">
      {/* Query header */}
      <div className="mb-6">
        <a href="/" className="text-sm text-blue-600 hover:underline mb-2 inline-block">
          ← New search
        </a>
        <h2 className="text-lg font-semibold text-slate-800">
          Results for: <span className="text-slate-600 font-normal">&ldquo;{query}&rdquo;</span>
        </h2>
        {isStreaming && (
          <p className="text-sm text-amber-600 mt-1 flex items-center gap-1">
            <span className="inline-block w-2 h-2 bg-amber-500 rounded-full animate-pulse" />
            Agents working…
          </p>
        )}
        {!isStreaming && totalEligible !== undefined && (
          <p className="text-sm text-emerald-600 mt-1">
            ✅ Found {schemes.length} schemes in{" "}
            {elapsedMs !== undefined ? `${(elapsedMs / 1000).toFixed(1)}s` : ""}
            {schemes.length >= 2 && (
              <span className="ml-2 text-slate-500">
                · Select up to {MAX_COMPARE} to compare side-by-side
              </span>
            )}
          </p>
        )}
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-xl text-red-700 text-sm">
          <strong>Error:</strong> {error}
          <br />
          <span className="text-xs text-red-500">
            Make sure the backend is running at localhost:8000
          </span>
        </div>
      )}

      <div className="flex flex-col lg:flex-row gap-6">
        {/* Left: scheme cards */}
        <div className="flex-1 min-w-0">
          {schemes.length === 0 && isStreaming && (
            <div className="space-y-4">
              {[1, 2, 3].map((i) => (
                <div key={i} className="h-48 bg-slate-100 rounded-xl animate-pulse" />
              ))}
            </div>
          )}

          {schemes.length === 0 && !isStreaming && !error && (
            <div className="text-center py-16 text-slate-400">
              <p className="text-4xl mb-3">🔍</p>
              <p>No schemes found for your query.</p>
              <a href="/" className="text-blue-600 text-sm hover:underline mt-2 block">
                Try a different query
              </a>
            </div>
          )}

          <div className="grid gap-4 sm:grid-cols-2">
            {schemes.map((scheme) => (
              <SchemeCard
                key={scheme.scheme_id}
                scheme={scheme}
                language={lang}
                selected={selected.includes(scheme.scheme_id)}
                onToggleSelect={() => toggleSelect(scheme.scheme_id)}
                compareDisabled={selected.length >= MAX_COMPARE && !selected.includes(scheme.scheme_id)}
              />
            ))}
          </div>
        </div>

        {/* Right: agent panel */}
        <div className="lg:w-80 xl:w-96 shrink-0">
          <AgentPanel
            steps={steps}
            isStreaming={isStreaming}
            totalEligible={totalEligible}
            elapsedMs={elapsedMs}
          />
        </div>
      </div>

      {/* Floating compare bar */}
      {selected.length >= 2 && (
        <div className="fixed bottom-6 left-1/2 -translate-x-1/2 z-50">
          <div className="flex items-center gap-3 bg-slate-900 text-white px-5 py-3 rounded-2xl shadow-2xl border border-slate-700">
            <div className="flex items-center gap-1.5">
              {selected.map((id) => {
                const s = schemes.find((sc) => sc.scheme_id === id);
                return (
                  <span
                    key={id}
                    className="text-xs bg-blue-600 px-2 py-1 rounded-lg max-w-[120px] truncate"
                    title={s?.title}
                  >
                    {s?.title?.split(" ").slice(0, 3).join(" ")}…
                  </span>
                );
              })}
            </div>
            <button
              onClick={handleCompare}
              className="px-4 py-1.5 bg-blue-500 hover:bg-blue-400 rounded-xl text-sm font-semibold transition-colors whitespace-nowrap"
            >
              ⚖️ Compare {selected.length}
            </button>
            <button
              onClick={() => setSelected([])}
              className="text-slate-400 hover:text-white text-sm"
            >
              ✕
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default function ResultsPage() {
  return (
    <Suspense
      fallback={
        <div className="flex items-center justify-center min-h-[60vh]">
          <p className="text-slate-500">Loading…</p>
        </div>
      }
    >
      <ResultsContent />
    </Suspense>
  );
}
